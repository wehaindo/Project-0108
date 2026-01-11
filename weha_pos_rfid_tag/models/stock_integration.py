# -*- coding: utf-8 -*-
from odoo import models, fields, api


class StockMove(models.Model):
    _inherit = 'stock.move'
    
    def _action_done(self, cancel_backorder=False):
        """Override to update RFID tag locations when stock moves are done"""
        result = super(StockMove, self)._action_done(cancel_backorder=cancel_backorder)
        
        # Update RFID tag locations for completed moves
        for move in self:
            if move.state == 'done' and move.location_dest_id:
                # Find RFID tags for this product
                rfid_tags = self.env['product.rfid.tag'].search([
                    ('product_id', '=', move.product_id.id),
                    ('status', '=', 'active'),
                    ('location_id', '=', move.location_id.id)
                ], limit=int(move.product_uom_qty))
                
                for tag in rfid_tags:
                    tag.update_location(
                        move.location_dest_id.id,
                        notes=f'Stock move: {move.reference or move.name}'
                    )
        
        return result


class StockQuant(models.Model):
    _inherit = 'stock.quant'
    
    rfid_tag_id = fields.Many2one(
        'product.rfid.tag',
        string='RFID Tag',
        help='RFID tag associated with this stock quantity',
        index=True
    )
    
    def _get_rfid_tags_at_location(self):
        """Get RFID tags for this quant's product at this location"""
        self.ensure_one()
        return self.env['product.rfid.tag'].search([
            ('product_id', '=', self.product_id.id),
            ('location_id', '=', self.location_id.id),
            ('status', '=', 'active')
        ])
    
    rfid_tag_count = fields.Integer(
        string='RFID Tags',
        compute='_compute_rfid_tag_count',
        help='Number of RFID tags at this location'
    )
    
    @api.depends('product_id', 'location_id', 'lot_id')
    def _compute_rfid_tag_count(self):
        for quant in self:
            domain = [
                ('product_id', '=', quant.product_id.id),
                ('location_id', '=', quant.location_id.id),
                ('status', '=', 'active')
            ]
            if quant.lot_id:
                domain.append(('lot_id', '=', quant.lot_id.id))
            
            tags = self.env['product.rfid.tag'].search_count(domain)
            quant.rfid_tag_count = tags


class StockPicking(models.Model):
    _inherit = 'stock.picking'
    
    def button_validate(self):
        """Override to handle RFID tag location updates"""
        result = super(StockPicking, self).button_validate()
        
        # Update RFID tags when picking is validated
        for picking in self:
            if picking.state == 'done':
                for move in picking.move_ids_without_package:
                    if move.state == 'done':
                        # Update RFID tags
                        rfid_tags = self.env['product.rfid.tag'].search([
                            ('product_id', '=', move.product_id.id),
                            ('location_id', '=', move.location_id.id),
                            ('status', '=', 'active')
                        ], limit=int(move.product_uom_qty))
                        
                        for tag in rfid_tags:
                            tag.update_location(
                                move.location_dest_id.id,
                                notes=f'Picking: {picking.name}'
                            )
        
        return result
