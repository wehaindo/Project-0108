# -*- coding: utf-8 -*-
from odoo import api, models


class AccountPayment(models.Model):
    _inherit = 'account.payment'

    @api.depends('journal_id', 'pos_session_id')
    def _compute_operating_unit_id(self):
        """Override to get operating unit from POS session if available"""
        for payment in self:
            # If from POS session, use session's operating unit
            if payment.pos_session_id and payment.pos_session_id.operating_unit_id:
                payment.operating_unit_id = payment.pos_session_id.operating_unit_id
            # Otherwise, use journal's operating unit (standard OCA behavior)
            elif payment.journal_id and payment.journal_id.operating_unit_id:
                payment.operating_unit_id = payment.journal_id.operating_unit_id
            else:
                payment.operating_unit_id = False
