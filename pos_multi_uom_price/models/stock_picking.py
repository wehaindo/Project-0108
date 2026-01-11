# -*- coding: utf-8 -*-
# © 2025 ehuerta _at_ ixer.mx
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl-3.0.html).

import logging

from odoo import models, fields, api, _
from itertools import groupby

_logger = logging.getLogger(__name__)
    
class StockPicking(models.Model):
    _inherit='stock.picking'

    def _prepare_stock_move_vals(self, first_line, order_lines):
        res = super()._prepare_stock_move_vals(first_line, order_lines)
        
        # Get the sale UOM from the POS order line
        sale_uom = first_line.product_uom_id
        # Get the product's stock/reference UOM
        product_uom = first_line.product_id.uom_id
        
        # Convert quantity from sale UOM to product's stock UOM
        if sale_uom and sale_uom != product_uom:
            # Get the total quantity in sale UOM
            qty_in_sale_uom = sum(order_lines.mapped('qty'))
            
            # Convert to product's stock UOM
            qty_in_stock_uom = sale_uom._compute_quantity(
                qty_in_sale_uom,
                product_uom,
                rounding_method='HALF-UP'
            )
            
            # Update the stock move with converted quantity and stock UOM
            res.update({
                'product_uom_qty': qty_in_stock_uom,
                'product_uom': product_uom.id,
            })
            
            _logger.info(
                "UOM Conversion for product %s: %.2f %s -> %.2f %s",
                first_line.product_id.display_name,
                qty_in_sale_uom,
                sale_uom.name,
                qty_in_stock_uom,
                product_uom.name
            )
        else:
            # Same UOM, just use the sale UOM
            res.update({'product_uom': sale_uom.id})
        
        return res

    def _create_move_from_pos_order_lines(self, lines):
        self.ensure_one()
        lines_by_product = groupby(sorted(lines, key=lambda l: (l.product_id.id,l.product_uom_id.id)), key=lambda l: (l.product_id.id,l.product_uom_id.id))
        move_vals = []
        for dummy, olines in lines_by_product:
            order_lines = self.env['pos.order.line'].concat(*olines)
            move_vals.append(self._prepare_stock_move_vals(order_lines[0], order_lines))
        moves = self.env['stock.move'].create(move_vals)
        confirmed_moves = moves._action_confirm()
        confirmed_moves._add_mls_related_to_order(lines, are_qties_done=True)
        confirmed_moves.picked = True
        self._link_owner_on_return_picking(lines)
