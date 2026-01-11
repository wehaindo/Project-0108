# -*- coding: utf-8 -*-
from odoo import models, api, fields, _


class PosSession(models.Model):
    _inherit = 'pos.session'

    backup_count = fields.Integer('Backup Count', compute='_compute_backup_count')
    missing_order_count = fields.Integer('Missing Orders', compute='_compute_missing_order_count')

    def _compute_backup_count(self):
        """Count backups for this session"""
        for session in self:
            session.backup_count = self.env['pos.order.backup'].search_count([
                ('session_id', '=', session.id)
            ])

    def _compute_missing_order_count(self):
        """Count missing orders for this session"""
        for session in self:
            backups = self.env['pos.order.backup'].search([
                ('session_id', '=', session.id)
            ])
            session.missing_order_count = len(backups.filtered(lambda b: b.is_missing))

    def action_view_backup_stats(self):
        """View backup statistics for this session"""
        self.ensure_one()
        
        stats = self.env['pos.order.backup'].get_backup_statistics(self.id)
        
        return {
            'name': _('Backup Statistics - %s') % self.name,
            'type': 'ir.actions.act_window',
            'res_model': 'pos.order.backup',
            'view_mode': 'graph,pivot,list',
            'domain': [('session_id', '=', self.id)],
            'context': {
                'search_default_group_state': 1,
                'backup_stats': stats,
            },
        }

    @api.model
    def sync_order_backups(self, backups,):
        """Sync order backups from POS UI to server"""
        results = {
            'success': [],
            'failed': [],
            'duplicates': []
        }
        
        for backup_data in backups:
            # Use new pos.order.backup model
            result = self.env['pos.order.backup'].save_order_backup(
                backup_data
            )
            
            if result.get('success'):
                if result.get('existing'):
                    results['duplicates'].append(backup_data.get('access_token'))
                else:
                    results['success'].append(backup_data.get('access_token'))
            else:
                results['failed'].append({
                    'access_token': backup_data.get('access_token'),
                    'error': result.get('error')
                })
        
        return results

    @api.model
    def check_missing_orders(self, session_id, order_uids):
        """Check for missing orders and return backup data if available"""
        # Get actual orders on server
        existing_orders = self.env['pos.order'].search([
            ('session_id', '=', session_id),
            ('pos_reference', 'in', order_uids)
        ])
        
        existing_refs = set(existing_orders.mapped('pos_reference'))
        missing_refs = [ref for ref in order_uids if ref not in existing_refs]
        
        result = {
            'missing_count': len(missing_refs),
            'missing_uids': missing_refs,
            'total_checked': len(order_uids)
        }
        
        if result['missing_count'] > 0:
            # Get backup data for missing orders using new model
            backups = self.env['pos.order.backup'].search([
                ('session_id', '=', session_id),
                ('pos_reference', 'in', result['missing_uids']),
                ('state', 'not in', ['imported', 'duplicate'])
            ])
            
            result['backups_available'] = backups.ids
            result['can_restore'] = len(backups) > 0
        
        return result
