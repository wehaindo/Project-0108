# -*- coding: utf-8 -*-
# Copyright 2026 Weha
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl-3.0).

from odoo import api, fields, models, _


class RevenueSharingEntry(models.Model):
    """Revenue Sharing Entry (Aggregated Summary)"""
    _name = 'revenue.sharing.entry'
    _description = 'Revenue Sharing Entry (Aggregated)'
    _order = 'date desc, id desc'

    name = fields.Char(
        string='Reference',
        compute='_compute_name',
        store=True
    )
    period_id = fields.Many2one(
        'revenue.sharing.period',
        string='Period',
        required=True,
        ondelete='cascade',
        index=True,
        help='Monthly revenue sharing period'
    )
    
    # Aggregated entry - removed order line references for efficiency
    # One entry represents: Period + Source OU + Target OU + Rule
    # This reduces entries from thousands to tens per month
    
    order_count = fields.Integer(
        string='Order Count',
        default=0,
        help='Number of orders aggregated in this entry'
    )
    line_count = fields.Integer(
        string='Line Count',
        default=0,
        help='Number of order lines aggregated in this entry'
    )
    
    # Operating Units
    source_ou_id = fields.Many2one(
        'operating.unit',
        string='Selling OU',
        required=True,
        help='Operating unit that made the sale'
    )
    target_ou_id = fields.Many2one(
        'operating.unit',
        string='Receiving OU',
        required=True,
        help='Operating unit receiving revenue share'
    )
    
    # Revenue Sharing Rule
    rule_id = fields.Many2one(
        'revenue.sharing.rule',
        string='Sharing Rule',
        required=True,
        index=True,
        help='Revenue sharing rule applied'
    )
    rule_line_id = fields.Many2one(
        'revenue.sharing.rule.line',
        string='Rule Line',
        required=True,
        help='Specific rule line for this OU type'
    )
    
    # Amounts (Aggregated)
    total_amount = fields.Monetary(
        string='Total Revenue',
        required=True,
        currency_field='currency_id',
        help='Total aggregated revenue from all orders/lines in this period'
    )
    share_percentage = fields.Float(
        string='Share %',
        required=True,
        help='Percentage of revenue for this OU'
    )
    share_amount = fields.Monetary(
        string='Share Amount',
        required=True,
        currency_field='currency_id',
        help='Amount of revenue for this OU'
    )
    currency_id = fields.Many2one(
        'res.currency',
        string='Currency',
        required=True
    )
    
    # Date and State
    date = fields.Datetime(
        string='Date',
        required=True,
        help='Date of the original sale'
    )
    state = fields.Selection([
        ('draft', 'Draft'),
        ('validated', 'Validated'),
        ('posted', 'Posted'),
    ], string='Status', default='draft', required=True)
    
    # Accounting
    move_id = fields.Many2one(
        'account.move',
        string='Journal Entry',
        readonly=True,
        help='Accounting entry for this revenue share'
    )
    
    company_id = fields.Many2one(
        'res.company',
        string='Company',
        related='period_id.company_id',
        store=True
    )
    
    @api.depends('period_id', 'source_ou_id', 'target_ou_id', 'share_amount')
    def _compute_name(self):
        """Generate reference name"""
        for entry in self:
            if entry.period_id and entry.source_ou_id and entry.target_ou_id:
                entry.name = '%s: %s → %s (%.2f)' % (
                    entry.period_id.name,
                    entry.source_ou_id.code or entry.source_ou_id.name,
                    entry.target_ou_id.code or entry.target_ou_id.name,
                    entry.share_amount
                )
            else:
                entry.name = '/'
