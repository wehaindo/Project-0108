# -*- coding: utf-8 -*-
# Copyright 2026 Weha
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl-3.0).

from odoo import models, fields


class StockMove(models.Model):
    _inherit = 'stock.move'

    stock_request_id = fields.Many2one(
        'stock.request',
        string='Stock Request',
        compute='_compute_stock_request_id',
        store=True,
        help='Related stock request for this move'
    )

    def _compute_stock_request_id(self):
        """Compute stock request from allocation"""
        for move in self:
            allocation = self.env['stock.request.allocation'].search([
                ('stock_move_id', '=', move.id)
            ], limit=1)
            move.stock_request_id = allocation.stock_request_id if allocation else False
