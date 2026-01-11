# -*- coding: utf-8 -*-
from . import rfid_tag_wizards
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
