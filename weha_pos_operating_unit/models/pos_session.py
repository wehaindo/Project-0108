# -*- coding: utf-8 -*-
from collections import defaultdict
from datetime import timedelta
from itertools import groupby, starmap
from markupsafe import Markup

from odoo import api, fields, models, _, Command
from odoo.exceptions import AccessDenied, AccessError, UserError, ValidationError
from odoo.tools import float_is_zero, float_compare, convert, plaintext2html
from odoo.service.common import exp_version
from odoo.osv.expression import AND

import logging
_logger = logging.getLogger(__name__)

class PosSession(models.Model):
    _inherit = 'pos.session'

    operating_unit_id = fields.Many2one(
        'operating.unit',
        string='Operating Unit',
        related='config_id.operating_unit_id',
        store=True,
        readonly=True,
        help='Operating unit from POS configuration.'
    )
    
    def _create_account_move(self, balancing_account=False, amount_to_balance=0, bank_payment_method_diffs=None):
        """ Create account.move and account.move.line records for this session.

        Side-effects include:
            - setting self.move_id to the created account.move record
            - reconciling cash receivable lines, invoice receivable lines and stock output lines
        """
        move_vals = {
            'journal_id': self.config_id.journal_id.id,
            'date': fields.Date.context_today(self),
            'ref': self.name,
        }
        
        # Add operating unit if configured
        if self.operating_unit_id:
            move_vals['operating_unit_id'] = self.operating_unit_id.id
        
        account_move = self.env['account.move'].create(move_vals)
        self.write({'move_id': account_move.id})

        data = {'bank_payment_method_diffs': bank_payment_method_diffs or {}}
        data = self._accumulate_amounts(data)
        data = self._create_non_reconciliable_move_lines(data)
        data = self._create_bank_payment_moves(data)
        data = self._create_pay_later_receivable_lines(data)
        data = self._create_cash_statement_lines_and_cash_move_lines(data)
        data = self._create_invoice_receivable_lines(data)
        data = self._create_stock_output_lines(data)
        if balancing_account and amount_to_balance:
            data = self._create_balancing_line(data, balancing_account, amount_to_balance)

        return data

    def _create_combine_account_payment(self, payment_method, amounts, diff_amount):
        """Override to add operating unit to bank payment"""
        outstanding_account = payment_method.outstanding_account_id
        destination_account = self._get_receivable_account(payment_method)
        
        payment_vals = {
            'amount': abs(amounts['amount']),
            'journal_id': payment_method.journal_id.id,
            'force_outstanding_account_id': outstanding_account.id,
            'destination_account_id': destination_account.id,
            'memo': _('Combine %(payment_method)s POS payments from %(session)s', 
                     payment_method=payment_method.name, session=self.name),
            'pos_payment_method_id': payment_method.id,
            'pos_session_id': self.id,
            'company_id': self.company_id.id,
        }
        
        # Add operating unit if configured
        if self.operating_unit_id:
            payment_vals['operating_unit_id'] = self.operating_unit_id.id
        
        account_payment = self.env['account.payment'].with_context(pos_payment=True).create(payment_vals)
        
        # Rest of the original logic
        accounting_installed = self.env['account.move']._get_invoice_in_payment_state() == 'in_payment'
        if not account_payment.outstanding_account_id and accounting_installed:
            account_payment.outstanding_account_id = account_payment._get_outstanding_account(account_payment.payment_type)
        
        if float_compare(amounts['amount'], 0, precision_rounding=self.currency_id.rounding) < 0:
            account_payment.write({
                'outstanding_account_id': account_payment.destination_account_id,
                'destination_account_id': account_payment.outstanding_account_id,
                'payment_type': 'outbound',
            })
        
        account_payment.action_post()
        
        diff_amount_compare_to_zero = self.currency_id.compare_amounts(diff_amount, 0)
        if diff_amount_compare_to_zero != 0:
            self._apply_diff_on_account_payment_move(account_payment, payment_method, diff_amount)
        
        return account_payment.move_id.line_ids.filtered(
            lambda line: line.account_id == self._get_receivable_account(payment_method)
        )

    def _create_split_account_payment(self, payment, amounts):
        """Override to add operating unit to split bank payment"""
        payment_method = payment.payment_method_id
        if not payment_method.journal_id:
            return self.env['account.move.line']
        
        outstanding_account = payment_method.outstanding_account_id
        accounting_partner = self.env["res.partner"]._find_accounting_partner(payment.partner_id)
        destination_account = accounting_partner.property_account_receivable_id
        
        if float_compare(amounts['amount'], 0, precision_rounding=self.currency_id.rounding) < 0:
            outstanding_account, destination_account = destination_account, outstanding_account
        
        payment_vals = {
            'amount': abs(amounts['amount']),
            'partner_id': accounting_partner.id,
            'journal_id': payment_method.journal_id.id,
            'force_outstanding_account_id': outstanding_account.id,
            'destination_account_id': destination_account.id,
            'memo': _('%(payment_method)s POS payment of %(partner)s in %(session)s',
                     payment_method=payment_method.name,
                     partner=payment.partner_id.display_name,
                     session=self.name),
            'pos_payment_method_id': payment_method.id,
            'pos_session_id': self.id,
        }
        
        # Add operating unit if configured
        if self.operating_unit_id:
            payment_vals['operating_unit_id'] = self.operating_unit_id.id
        
        account_payment = self.env['account.payment'].create(payment_vals)
        account_payment.action_post()
        
        return account_payment.move_id.line_ids.filtered(
            lambda line: line.account_id == accounting_partner.property_account_receivable_id
        )
