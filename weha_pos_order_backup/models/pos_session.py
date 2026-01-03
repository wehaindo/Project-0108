# -*- coding: utf-8 -*-
from odoo import models, api, _


class PosSession(models.Model):
    _inherit = 'pos.session'

    @api.model
    def sync_order_backups(self, backups,):
        """Sync order backups from POS UI to server"""
        results = {
            'success': [],
            'failed': [],
            'duplicates': []
        }
        
        for backup_data in backups:
            result = self.env['pos.data.log'].save_order_backup(
                backup_data
            )
            
            if result.get('success'):
                if result.get('existing'):
                    results['duplicates'].append(backup_data.get('uid'))
                else:
                    results['success'].append(backup_data.get('uid'))
            else:
                results['failed'].append({
                    'uid': backup_data.get('uid'),
                    'error': result.get('error')
                })
        
        return results

    @api.model
    def check_missing_orders(self, session_id, order_uids):
        """Check for missing orders and return backup data if available"""
        result = self.env['pos.data.log'].get_missing_orders(session_id, order_uids)
        
        if result['missing_count'] > 0:
            # Get backup data for missing orders
            backups = self.env['pos.data.log'].search([
                ('session_id', '=', session_id),
                ('order_uid', 'in', result['missing_uids']),
                ('state', '!=', 'imported')
            ])
            
            result['backups_available'] = backups.ids
            result['can_restore'] = len(backups) > 0
        
        return result
