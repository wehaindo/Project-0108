# -*- coding: utf-8 -*-
from odoo import models, fields, api


class ProductRfidTagLocationHistory(models.Model):
    _name = 'product.rfid.tag.location.history'
    _description = 'RFID Tag Location History'
    _order = 'create_date desc'
    
    rfid_tag_id = fields.Many2one(
        'product.rfid.tag',
        string='RFID Tag',
        required=True,
        ondelete='cascade',
        index=True
    )
    
    rfid_tag_name = fields.Char(
        related='rfid_tag_id.name',
        string='Tag Name',
        store=True,
        readonly=True
    )
    
    product_id = fields.Many2one(
        'product.product',
        string='Product',
        required=True,
        index=True
    )
    
    from_location_id = fields.Many2one(
        'stock.location',
        string='From Location',
        help='Previous location'
    )
    
    to_location_id = fields.Many2one(
        'stock.location',
        string='To Location',
        required=True,
        help='New location'
    )
    
    move_date = fields.Datetime(
        string='Move Date',
        default=fields.Datetime.now,
        required=True,
        index=True
    )
    
    stock_move_id = fields.Many2one(
        'stock.move',
        string='Related Stock Move',
        help='Stock move that triggered this location change'
    )
    
    user_id = fields.Many2one(
        'res.users',
        string='User',
        default=lambda self: self.env.user,
        help='User who performed the location change'
    )
    
    notes = fields.Text(string='Notes')
    
    create_date = fields.Datetime(string='Created On', readonly=True)
    
    def name_get(self):
        """Display format for location history"""
        result = []
        for record in self:
            from_loc = record.from_location_id.complete_name if record.from_location_id else 'N/A'
            to_loc = record.to_location_id.complete_name
            name = f"{record.rfid_tag_name}: {from_loc} → {to_loc}"
            result.append((record.id, name))
        return result
