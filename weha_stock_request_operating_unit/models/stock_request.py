# -*- coding: utf-8 -*-
# Copyright 2026 Weha
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl-3.0).

from odoo import api, fields, models, _


class StockRequest(models.Model):
    _inherit = 'stock.request'

    operating_unit_id = fields.Many2one(
        'operating.unit',
        string='Operating Unit',
        domain="[('company_id', '=', company_id)]",
        default=lambda self: self._get_default_operating_unit(),
        index=True,
        help='Operating unit for this stock request. All stock moves and pickings will be assigned to this operating unit.'
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

    def _prepare_procurement_group_values(self):
        """Override to add operating unit to procurement group"""
        res = super()._prepare_procurement_group_values()
        if self.operating_unit_id:
            res['operating_unit_id'] = self.operating_unit_id.id
        return res

    def _prepare_stock_move_values(self):
        """Override to add operating unit to stock move"""
        res = super()._prepare_stock_move_values()
        if self.operating_unit_id:
            res['operating_unit_id'] = self.operating_unit_id.id
        return res

    def _action_confirm(self):
        """Override to ensure operating unit is set on moves"""
        res = super()._action_confirm()
        for request in self:
            if request.operating_unit_id and request.move_ids:
                request.move_ids.filtered(
                    lambda m: not m.operating_unit_id
                ).write({'operating_unit_id': request.operating_unit_id.id})
        return res
