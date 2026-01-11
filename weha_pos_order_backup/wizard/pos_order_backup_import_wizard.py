# -*- coding: utf-8 -*-
from odoo import fields, models, api, _
from odoo.exceptions import UserError
import logging

_logger = logging.getLogger(__name__)


class PosOrderBackupImportWizard(models.TransientModel):
    _name = 'pos.order.backup.import.wizard'
    _description = 'Batch Import POS Order Backups'

    session_id = fields.Many2one('pos.session', string='Session', help='Filter backups by session')
    date_from = fields.Datetime('From Date')
    date_to = fields.Datetime('To Date')
    
    filter_type = fields.Selection([
        ('all_missing', 'All Missing Orders'),
        ('by_session', 'By Session'),
        ('by_date', 'By Date Range'),
        ('selected', 'Selected Records'),
    ], string='Filter Type', default='selected', required=True)
    
    backup_ids = fields.Many2many(
        'pos.order.backup', 
        string='Backups to Import',
        domain=[('state', 'not in', ['imported', 'duplicate'])]
    )
    
    backup_count = fields.Integer('Backups Count', compute='_compute_backup_count')
    only_missing = fields.Boolean('Only Missing on Server', default=True, help='Only import orders that are missing on server')
    
    # Results
    import_count = fields.Integer('Imported', readonly=True)
    duplicate_count = fields.Integer('Duplicates', readonly=True)
    error_count = fields.Integer('Errors', readonly=True)
    result_message = fields.Html('Results', readonly=True)
    
    @api.depends('filter_type', 'session_id', 'date_from', 'date_to', 'backup_ids', 'only_missing')
    def _compute_backup_count(self):
        for wizard in self:
            domain = wizard._get_backup_domain()
            wizard.backup_count = self.env['pos.order.backup'].search_count(domain)
    
    def _get_backup_domain(self):
        """Build domain based on filter type"""
        domain = [('state', 'not in', ['imported', 'duplicate'])]
        
        if self.filter_type == 'all_missing':
            # Will filter programmatically for missing orders
            pass
        elif self.filter_type == 'by_session' and self.session_id:
            domain.append(('session_id', '=', self.session_id.id))
        elif self.filter_type == 'by_date':
            if self.date_from:
                domain.append(('backup_date', '>=', self.date_from))
            if self.date_to:
                domain.append(('backup_date', '<=', self.date_to))
        elif self.filter_type == 'selected' and self.backup_ids:
            domain.append(('id', 'in', self.backup_ids.ids))
        
        return domain
    
    def action_preview_backups(self):
        """Preview backups that will be imported"""
        self.ensure_one()
        
        domain = self._get_backup_domain()
        backups = self.env['pos.order.backup'].search(domain)
        
        # Filter for missing orders if needed
        if self.only_missing:
            backups = backups.filtered(lambda b: b.is_missing)
        
        return {
            'name': _('Backups to Import'),
            'type': 'ir.actions.act_window',
            'res_model': 'pos.order.backup',
            'view_mode': 'list,form',
            'domain': [('id', 'in', backups.ids)],
            'context': {'create': False},
        }
    
    def action_import_backups(self):
        """Execute batch import"""
        self.ensure_one()
        
        domain = self._get_backup_domain()
        backups = self.env['pos.order.backup'].search(domain)
        
        # Filter for missing orders if needed
        if self.only_missing:
            backups = backups.filtered(lambda b: b.is_missing)
        
        if not backups:
            raise UserError(_('No backups found to import with the selected criteria.'))
        
        # Import backups
        imported = 0
        duplicates = 0
        errors = 0
        error_details = []
        
        for backup in backups:
            try:
                result = backup.action_import_order()
                if result and result.get('params', {}).get('type') == 'success':
                    imported += 1
                else:
                    errors += 1
                    error_details.append(f"{backup.pos_reference}: Unknown error")
            except UserError as e:
                if 'already exists' in str(e):
                    duplicates += 1
                else:
                    errors += 1
                    error_details.append(f"{backup.pos_reference}: {str(e)}")
            except Exception as e:
                errors += 1
                error_details.append(f"{backup.pos_reference}: {str(e)}")
                _logger.error(f"Error importing backup {backup.id}: {str(e)}", exc_info=True)
        
        # Build result message
        result_html = f"""
        <div class="alert alert-info">
            <h4>Import Results</h4>
            <ul>
                <li><strong>Successfully Imported:</strong> {imported}</li>
                <li><strong>Duplicates (Already Exist):</strong> {duplicates}</li>
                <li><strong>Errors:</strong> {errors}</li>
            </ul>
        """
        
        if error_details:
            result_html += "<h5>Error Details:</h5><ul>"
            for error in error_details[:10]:  # Show first 10 errors
                result_html += f"<li>{error}</li>"
            if len(error_details) > 10:
                result_html += f"<li>... and {len(error_details) - 10} more errors</li>"
            result_html += "</ul>"
        
        result_html += "</div>"
        
        # Update wizard with results
        self.write({
            'import_count': imported,
            'duplicate_count': duplicates,
            'error_count': errors,
            'result_message': result_html,
        })
        
        # Return form view to show results
        return {
            'name': _('Import Results'),
            'type': 'ir.actions.act_window',
            'res_model': 'pos.order.backup.import.wizard',
            'res_id': self.id,
            'view_mode': 'form',
            'target': 'new',
            'context': {'show_results': True},
        }
    
    @api.model
    def default_get(self, fields_list):
        """Set default values from context"""
        res = super().default_get(fields_list)
        
        # If called from tree view with selected records
        active_ids = self.env.context.get('active_ids', [])
        if active_ids and 'backup_ids' in fields_list:
            res['backup_ids'] = [(6, 0, active_ids)]
            res['filter_type'] = 'selected'
        
        return res
