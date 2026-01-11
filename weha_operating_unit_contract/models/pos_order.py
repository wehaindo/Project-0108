# -*- coding: utf-8 -*-
# Copyright 2026 Weha
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl-3.0).

from odoo import api, fields, models, _


class PosOrder(models.Model):
    """Extend POS Order with Revenue Sharing"""
    _inherit = 'pos.order'

    revenue_sharing_period_id = fields.Many2one(
        'revenue.sharing.period',
        string='Revenue Sharing Period',
        help='Monthly period for revenue sharing calculation',
        compute='_compute_revenue_sharing_period',
        store=True
    )
    
    @api.depends('date_order')
    def _compute_revenue_sharing_period(self):
        """Auto-assign to revenue sharing period based on order date"""
        for order in self:
            if order.date_order and order.operating_unit_id:
                period = self.env['revenue.sharing.period'].get_or_create_period(
                    order.date_order,
                    order.operating_unit_id.company_id
                )
                order.revenue_sharing_period_id = period.id
            else:
                order.revenue_sharing_period_id = False


class PosOrderLine(models.Model):
    """Extend POS Order Line - no changes needed for monthly calculation"""
    _inherit = 'pos.order.line'
