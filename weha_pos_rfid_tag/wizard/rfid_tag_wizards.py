# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import UserError


class RfidTagLocationUpdateWizard(models.TransientModel):
    _name = 'rfid.tag.location.update.wizard'
    _description = 'Bulk Update RFID Tag Locations'
    
    location_id = fields.Many2one(
        'stock.location',
        string='New Location',
        required=True,
        help='Move all selected tags to this location'
    )
    
    notes = fields.Text(
        string='Notes',
        help='Reason for location change'
    )
    
    def action_update_location(self):
        """Update location for all selected RFID tags"""
        self.ensure_one()
        
        # Get selected RFID tags from context
        active_ids = self.env.context.get('active_ids', [])
        if not active_ids:
            raise UserError(_('No RFID tags selected'))
        
        rfid_tags = self.env['product.rfid.tag'].browse(active_ids)
        
        # Update each tag's location
        for tag in rfid_tags:
            tag.update_location(
                self.location_id.id,
                notes=self.notes or f'Bulk location update to {self.location_id.complete_name}'
            )
        
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': _('Success'),
                'message': _('%d RFID tags moved to %s') % (len(rfid_tags), self.location_id.complete_name),
                'type': 'success',
                'sticky': False,
            }
        }


class RfidTagSearchWizard(models.TransientModel):
    _name = 'rfid.tag.search.wizard'
    _description = 'Search RFID Tag by Tag ID'
    
    tag_name = fields.Char(
        string='RFID Tag ID',
        required=True,
        help='Enter the RFID tag identifier to search'
    )
    
    def action_search_tag(self):
        """Search for RFID tag and display its information"""
        self.ensure_one()
        
        tag = self.env['product.rfid.tag'].search([
            ('name', '=', self.tag_name)
        ], limit=1)
        
        if not tag:
            raise UserError(_('RFID Tag "%s" not found') % self.tag_name)
        
        # Open the tag form view
        return {
            'name': _('RFID Tag: %s') % tag.name,
            'type': 'ir.actions.act_window',
            'res_model': 'product.rfid.tag',
            'res_id': tag.id,
            'view_mode': 'form',
            'target': 'current',
        }


class RfidInventoryCountWizard(models.TransientModel):
    _name = 'rfid.inventory.count.wizard'
    _description = 'RFID Physical Inventory Count (Stock Opname)'
    
    location_id = fields.Many2one(
        'stock.location',
        string='Location',
        required=True,
        domain=[('usage', '=', 'internal')],
        help='Location to perform inventory count'
    )
    
    product_ids = fields.Many2many(
        'product.product',
        string='Products',
        help='Limit count to specific products (leave empty for all products)'
    )
    
    scanned_tag_ids = fields.One2many(
        'rfid.inventory.count.line',
        'wizard_id',
        string='Scanned Tags'
    )
    
    count_date = fields.Datetime(
        string='Count Date',
        default=fields.Datetime.now,
        required=True
    )
    
    state = fields.Selection([
        ('draft', 'Draft'),
        ('counting', 'Counting'),
        ('done', 'Done'),
    ], default='draft', string='State')
    
    total_scanned = fields.Integer(
        string='Total Scanned',
        compute='_compute_totals'
    )
    
    total_system = fields.Integer(
        string='Total in System',
        compute='_compute_totals'
    )
    
    discrepancy_count = fields.Integer(
        string='Discrepancies',
        compute='_compute_totals'
    )
    
    @api.depends('scanned_tag_ids')
    def _compute_totals(self):
        for record in self:
            record.total_scanned = len(record.scanned_tag_ids)
            
            # Get system count
            domain = [
                ('location_id', '=', record.location_id.id),
                ('status', '=', 'active')
            ]
            if record.product_ids:
                domain.append(('product_id', 'in', record.product_ids.ids))
            
            record.total_system = self.env['product.rfid.tag'].search_count(domain)
            record.discrepancy_count = abs(record.total_system - record.total_scanned)
    
    def action_start_counting(self):
        """Start the counting process"""
        self.write({'state': 'counting'})
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'rfid.inventory.count.wizard',
            'res_id': self.id,
            'view_mode': 'form',
            'target': 'new',
        }
    
    def action_scan_tag(self, tag_name):
        """Add a scanned tag to the count"""
        self.ensure_one()
        
        tag = self.env['product.rfid.tag'].search([
            ('name', '=', tag_name)
        ], limit=1)
        
        if not tag:
            return {'warning': f'Tag {tag_name} not found in system'}
        
        # Check if already scanned
        existing = self.scanned_tag_ids.filtered(lambda l: l.rfid_tag_id == tag)
        if existing:
            return {'warning': f'Tag {tag_name} already scanned'}
        
        # Add to scanned list
        self.env['rfid.inventory.count.line'].create({
            'wizard_id': self.id,
            'rfid_tag_id': tag.id,
            'product_id': tag.product_id.id,
            'location_id': tag.location_id.id or self.location_id.id,
            'lot_id': tag.lot_id.id if tag.lot_id else False,
        })
        
        return {'success': True, 'product_name': tag.product_id.display_name}
    
    def action_generate_adjustment(self):
        """Generate inventory adjustment based on count"""
        self.ensure_one()
        
        # Create inventory adjustment
        inventory = self.env['stock.inventory'].create({
            'name': f'RFID Count - {self.location_id.name} - {fields.Date.today()}',
            'location_ids': [(4, self.location_id.id)],
            'product_ids': [(6, 0, self.product_ids.ids)] if self.product_ids else False,
        })
        
        # Process scanned tags to create inventory lines
        scanned_products = {}
        for line in self.scanned_tag_ids:
            key = (line.product_id.id, line.lot_id.id if line.lot_id else False)
            if key not in scanned_products:
                scanned_products[key] = 0
            scanned_products[key] += 1
        
        # Create inventory lines
        for (product_id, lot_id), qty in scanned_products.items():
            self.env['stock.inventory.line'].create({
                'inventory_id': inventory.id,
                'product_id': product_id,
                'location_id': self.location_id.id,
                'prod_lot_id': lot_id if lot_id else False,
                'product_qty': qty,
            })
        
        self.write({'state': 'done'})
        
        return {
            'name': _('Inventory Adjustment'),
            'type': 'ir.actions.act_window',
            'res_model': 'stock.inventory',
            'res_id': inventory.id,
            'view_mode': 'form',
            'target': 'current',
        }
    
    def action_view_discrepancies(self):
        """Show discrepancies between scanned and system"""
        self.ensure_one()
        
        # Get tags in system
        domain = [
            ('location_id', '=', self.location_id.id),
            ('status', '=', 'active')
        ]
        if self.product_ids:
            domain.append(('product_id', 'in', self.product_ids.ids))
        
        system_tags = self.env['product.rfid.tag'].search(domain)
        scanned_tags = self.scanned_tag_ids.mapped('rfid_tag_id')
        
        # Find missing and extra tags
        missing_tags = system_tags - scanned_tags
        extra_tags = scanned_tags - system_tags
        
        return {
            'name': _('Inventory Discrepancies'),
            'type': 'ir.actions.act_window',
            'res_model': 'product.rfid.tag',
            'view_mode': 'tree,form',
            'domain': [('id', 'in', (missing_tags | extra_tags).ids)],
            'context': {
                'search_default_group_status': 1,
            },
        }


class RfidInventoryCountLine(models.TransientModel):
    _name = 'rfid.inventory.count.line'
    _description = 'RFID Inventory Count Line'
    
    wizard_id = fields.Many2one(
        'rfid.inventory.count.wizard',
        string='Wizard',
        required=True,
        ondelete='cascade'
    )
    
    rfid_tag_id = fields.Many2one(
        'product.rfid.tag',
        string='RFID Tag',
        required=True
    )
    
    product_id = fields.Many2one(
        'product.product',
        string='Product',
        required=True
    )
    
    location_id = fields.Many2one(
        'stock.location',
        string='Found Location',
        help='Location where this tag was found during count'
    )
    
    lot_id = fields.Many2one(
        'stock.lot',
        string='Lot/Serial'
    )
    
    scan_time = fields.Datetime(
        string='Scan Time',
        default=fields.Datetime.now
    )
