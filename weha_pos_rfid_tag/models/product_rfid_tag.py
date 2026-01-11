# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import ValidationError


class ProductRfidTag(models.Model):
    _name = 'product.rfid.tag'
    _description = 'Product RFID Tag'
    _order = 'create_date desc'
    
    name = fields.Char(
        string='RFID Tag ID',
        required=True,
        copy=False,
        index=True,
        help='Unique RFID tag identifier'
    )
    
    product_tmpl_id = fields.Many2one(
        'product.template',
        string='Product Template',
        ondelete='cascade',
        index=True
    )
    
    product_id = fields.Many2one(
        'product.product',
        string='Product',
        required=True,
        ondelete='cascade',
        index=True,
        help='Product variant this RFID tag is assigned to'
    )
    
    status = fields.Selection([
        ('active', 'Active'),
        ('sold', 'Sold'),
        ('inactive', 'Inactive'),
    ], string='Status', default='active', required=True, index=True,
        help='Active: Available for scanning\n'
             'Sold: Already sold, will not be added to cart\n'
             'Inactive: Disabled, will not be recognized')
    
    notes = fields.Text(string='Notes')
    
    create_date = fields.Datetime(string='Created On', readonly=True)
    
    # Track when the tag was used
    last_scanned_date = fields.Datetime(string='Last Scanned', readonly=True)
    scan_count = fields.Integer(string='Scan Count', default=0, readonly=True)
    
    # Stock/Location tracking
    location_id = fields.Many2one(
        'stock.location',
        string='Current Location',
        help='Current physical location of this RFID-tagged item',
        index=True
    )
    
    lot_id = fields.Many2one(
        'stock.lot',
        string='Lot/Serial Number',
        help='Associated lot or serial number for traceability',
        index=True,
        ondelete='restrict'
    )
    
    quant_ids = fields.One2many(
        'stock.quant',
        'rfid_tag_id',
        string='Stock Quants',
        help='Stock quantities associated with this RFID tag'
    )
    
    on_hand_qty = fields.Float(
        string='On Hand',
        compute='_compute_stock_qty',
        help='Current quantity on hand for this tag'
    )
    
    available_qty = fields.Float(
        string='Available',
        compute='_compute_stock_qty',
        help='Available quantity (on hand - reserved)'
    )
    
    tracking = fields.Selection(
        related='product_id.tracking',
        string='Tracking',
        store=True
    )
    
    location_history_ids = fields.One2many(
        'product.rfid.tag.location.history',
        'rfid_tag_id',
        string='Location History',
        help='History of location movements for this tag'
    )
    
    last_location_update = fields.Datetime(
        string='Last Location Update',
        readonly=True,
        help='Last time the location was updated'
    )
    
    _sql_constraints = [
        ('name_unique', 'UNIQUE(name)', 'RFID Tag ID must be unique!')
    ]
    
    @api.depends('quant_ids.quantity', 'quant_ids.reserved_quantity')
    def _compute_stock_qty(self):
        """Compute on hand and available quantities"""
        for record in self:
            on_hand = 0
            reserved = 0
            for quant in record.quant_ids:
                on_hand += quant.quantity
                reserved += quant.reserved_quantity
            record.on_hand_qty = on_hand
            record.available_qty = on_hand - reserved
    
    @api.model
    def create(self, vals):
        # Auto-set product_tmpl_id from product_id
        if vals.get('product_id') and not vals.get('product_tmpl_id'):
            product = self.env['product.product'].browse(vals['product_id'])
            vals['product_tmpl_id'] = product.product_tmpl_id.id
            
            # Auto-create lot/serial number if product is tracked and no lot_id provided
            if not vals.get('lot_id') and product.tracking in ['serial', 'lot']:
                lot_vals = {
                    'name': vals.get('name'),  # Use RFID tag as serial/lot number
                    'product_id': vals['product_id'],
                    'company_id': self.env.company.id,
                }
                lot = self.env['stock.lot'].create(lot_vals)
                vals['lot_id'] = lot.id
            
            # Auto-create lot/serial number if product is tracked and no lot_id provided
            if not vals.get('lot_id') and product.tracking in ['serial', 'lot']:
                lot_vals = {
                    'name': vals.get('name'),  # Use RFID tag as serial/lot number
                    'product_id': vals['product_id'],
                    'company_id': self.env.company.id,
                }
                lot = self.env['stock.lot'].create(lot_vals)
                vals['lot_id'] = lot.id
                
        return super(ProductRfidTag, self).create(vals)
    
    def write(self, vals):
        # Auto-update product_tmpl_id if product_id changes
        if vals.get('product_id'):
            product = self.env['product.product'].browse(vals['product_id'])
            vals['product_tmpl_id'] = product.product_tmpl_id.id
        return super(ProductRfidTag, self).write(vals)
    
    @api.constrains('name')
    def _check_name_unique(self):
        """Ensure RFID tag name is unique"""
        for record in self:
            if record.name:
                duplicate = self.search([
                    ('name', '=', record.name),
                    ('id', '!=', record.id)
                ], limit=1)
                if duplicate:
                    raise ValidationError(_(
                        'RFID Tag "%s" is already assigned to product "%s". '
                        'Each RFID tag must be unique across all products.'
                    ) % (record.name, duplicate.product_id.display_name))
    
    def update_scan_info(self):
        """Update scan information when tag is read"""
        self.ensure_one()
        self.write({
            'last_scanned_date': fields.Datetime.now(),
            'scan_count': self.scan_count + 1
        })
    
    def action_mark_as_sold(self):
        """Mark tag as sold"""
        self.write({'status': 'sold'})
    
    def action_mark_as_active(self):
        """Mark tag as active"""
        self.write({'status': 'active'})
    
    def action_mark_as_inactive(self):
        """Mark tag as inactive"""
        self.write({'status': 'inactive'})
    
    def name_get(self):
        """Display tag name with product name"""
        result = []
        for record in self:
            name = f"{record.name} - {record.product_id.display_name}"
            if record.location_id:
                name += f" [{record.location_id.complete_name}]"
            result.append((record.id, name))
        return result
    
    def update_location(self, location_id, notes=None):
        """Update the location of this RFID tag and record history"""
        self.ensure_one()
        
        old_location = self.location_id
        
        # Update current location
        self.write({
            'location_id': location_id,
            'last_location_update': fields.Datetime.now(),
        })
        
        # Create history record
        self.env['product.rfid.tag.location.history'].create({
            'rfid_tag_id': self.id,
            'product_id': self.product_id.id,
            'from_location_id': old_location.id if old_location else False,
            'to_location_id': location_id,
            'notes': notes or f'Location updated to {self.env["stock.location"].browse(location_id).complete_name}',
        })
        
        return True
    
    def action_view_location_history(self):
        """Open location history for this tag"""
        self.ensure_one()
        return {
            'name': f'Location History: {self.name}',
            'type': 'ir.actions.act_window',
            'res_model': 'product.rfid.tag.location.history',
            'view_mode': 'tree,form',
            'domain': [('rfid_tag_id', '=', self.id)],
            'context': {'default_rfid_tag_id': self.id},
        }
