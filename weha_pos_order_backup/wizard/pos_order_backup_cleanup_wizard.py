# -*- coding: utf-8 -*-
from odoo import fields, models, api, _
from odoo.exceptions import UserError


class PosOrderBackupCleanupWizard(models.TransientModel):
    _name = 'pos.order.backup.cleanup.wizard'
    _description = 'Cleanup Old POS Order Backups'

    retention_days = fields.Integer(
        'Retention Days', 
        default=30, 
        required=True,
        help='Delete backups older than this many days'
    )
    
    states_to_clean = fields.Many2many(
        'pos.order.backup.state',
        string='States to Clean',
        default=lambda self: self._default_states(),
        help='Only delete backups with these states'
    )
    
    cleanup_verified = fields.Boolean('Verified Orders', default=True)
    cleanup_imported = fields.Boolean('Imported Orders', default=True)
    cleanup_duplicate = fields.Boolean('Duplicate Orders', default=True)
    cleanup_error = fields.Boolean('Error Orders', default=False)
    
    preview_count = fields.Integer('Records to Delete', compute='_compute_preview_count')
    
    def _default_states(self):
        return ['verified', 'imported', 'duplicate']
    
    @api.depends('retention_days', 'cleanup_verified', 'cleanup_imported', 'cleanup_duplicate', 'cleanup_error')
    def _compute_preview_count(self):
        for wizard in self:
            domain = wizard._get_cleanup_domain()
            wizard.preview_count = self.env['pos.order.backup'].search_count(domain)
    
    def _get_cleanup_domain(self):
        """Build domain for cleanup"""
        cutoff_date = fields.Datetime.subtract(fields.Datetime.now(), days=self.retention_days)
        
        states = []
        if self.cleanup_verified:
            states.append('verified')
        if self.cleanup_imported:
            states.append('imported')
        if self.cleanup_duplicate:
            states.append('duplicate')
        if self.cleanup_error:
            states.append('error')
        
        domain = [
            ('backup_date', '<', cutoff_date),
            ('state', 'in', states),
        ]
        
        return domain
    
    def action_preview_cleanup(self):
        """Preview records that will be deleted"""
        self.ensure_one()
        
        domain = self._get_cleanup_domain()
        
        return {
            'name': _('Records to Delete'),
            'type': 'ir.actions.act_window',
            'res_model': 'pos.order.backup',
            'view_mode': 'list',
            'domain': domain,
            'context': {'create': False},
        }
    
    def action_cleanup(self):
        """Execute cleanup"""
        self.ensure_one()
        
        if self.retention_days < 7:
            raise UserError(_('Retention days must be at least 7 days for safety.'))
        
        domain = self._get_cleanup_domain()
        backups = self.env['pos.order.backup'].search(domain)
        
        count = len(backups)
        
        if count == 0:
            raise UserError(_('No records found to delete with the selected criteria.'))
        
        backups.unlink()
        
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'message': _('%s backup record(s) deleted successfully') % count,
                'type': 'success',
                'next': {'type': 'ir.actions.act_window_close'},
            }
        }
