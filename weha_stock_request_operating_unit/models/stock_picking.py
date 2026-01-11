# -*- coding: utf-8 -*-
# Copyright 2026 Weha
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl-3.0).

from odoo import models, fields, api


class StockPicking(models.Model):
    _inherit = 'stock.picking'

    stock_request_ids = fields.Many2many(
        'stock.request',
        string='Stock Requests',
        compute='_compute_stock_request_ids',
        store=True,
        help='Related stock requests for this picking'
    )
    stock_request_count = fields.Integer(
        string='Stock Request Count',
        compute='_compute_stock_request_ids',
        store=True
    )

    @api.depends('move_ids', 'move_ids.stock_request_id')
    def _compute_stock_request_ids(self):
        """Compute stock requests from moves"""
        for picking in self:
            stock_requests = picking.move_ids.mapped('stock_request_id')
            picking.stock_request_ids = [(6, 0, stock_requests.ids)]
            picking.stock_request_count = len(stock_requests)

    def action_view_stock_requests(self):
        """Smart button to view related stock requests"""
        self.ensure_one()
        action = self.env.ref('stock_request.action_stock_request_form').read()[0]
        
        if len(self.stock_request_ids) > 1:
            action['domain'] = [('id', 'in', self.stock_request_ids.ids)]
        elif self.stock_request_ids:
            action['views'] = [(self.env.ref('stock_request.stock_request_view_form').id, 'form')]
            action['res_id'] = self.stock_request_ids.id
        else:
            action = {'type': 'ir.actions.act_window_close'}
        
        return action
