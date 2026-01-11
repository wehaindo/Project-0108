# -*- coding: utf-8 -*-
# Copyright 2026 Weha
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl-3.0).

from odoo import api, fields, models, _


class StockRequestOrder(models.Model):
    _inherit = 'stock.request.order'

    operating_unit_id = fields.Many2one(
        'operating.unit',
        string='Operating Unit',
        domain="[('company_id', '=', company_id)]",
        default=lambda self: self._get_default_operating_unit(),
        index=True,
        help='Operating unit for this stock request order. All stock requests under this order will inherit this operating unit.'
    )

    @api.model
    def _get_default_operating_unit(self):
        """Get default operating unit from user"""
        return self.env.user.default_operating_unit_id

    @api.onchange('company_id')
    def _onchange_company_id_operating_unit(self):
        """Reset operating unit when company changes"""
        if self.operating_unit_id and self.operating_unit_id.company_id != self.company_id:
            self.operating_unit_id = False

    @api.model
    def create(self, vals):
        """Override to propagate operating unit to stock requests"""
        order = super().create(vals)
        if order.operating_unit_id and order.stock_request_ids:
            order.stock_request_ids.write({'operating_unit_id': order.operating_unit_id.id})
        return order

    def write(self, vals):
        """Override to propagate operating unit changes to stock requests"""
        res = super().write(vals)
        if 'operating_unit_id' in vals:
            for order in self:
                if order.stock_request_ids:
                    order.stock_request_ids.write({'operating_unit_id': vals['operating_unit_id']})
        return res
