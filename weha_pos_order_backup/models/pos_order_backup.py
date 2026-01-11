# -*- coding: utf-8 -*-
from odoo import fields, models, api, _
from odoo.exceptions import UserError, ValidationError
import json
import logging

_logger = logging.getLogger(__name__)


class PosOrderBackup(models.Model):
    _name = 'pos.order.backup'
    _description = 'POS Order Backup'
    _order = 'backup_date desc'
    _rec_name = 'pos_reference'

    # Basic Information
    pos_reference = fields.Char('Order Reference', required=True, index=True)
    access_token = fields.Char('Access Token', index=True, help='Unique order identifier from POS')
    backup_date = fields.Datetime('Backup Date', default=fields.Datetime.now, required=True, index=True)
    order_date = fields.Datetime('Order Date', index=True)
    
    # Session & Config
    session_id = fields.Many2one('pos.session', string='Session', index=True, ondelete='cascade')
    config_id = fields.Many2one('pos.config', string='POS Config', related='session_id.config_id', store=True, index=True)
    user_id = fields.Many2one('res.users', string='Salesperson', index=True)
    
    # Partner Information
    partner_id = fields.Many2one('res.partner', string='Customer', index=True)
    partner_name = fields.Char('Customer Name', help='Customer name at time of order')
    
    # Financial Information
    amount_total = fields.Float('Total Amount', digits='Product Price')
    amount_tax = fields.Float('Tax Amount', digits='Product Price')
    amount_paid = fields.Float('Amount Paid', digits='Product Price')
    amount_return = fields.Float('Amount Returned', digits='Product Price')
    
    # State Management
    state = fields.Selection([
        ('backup', 'Backup Only'),
        ('synced', 'Synced to Server'),
        ('verified', 'Verified on Server'),
        ('imported', 'Imported to POS'),
        ('duplicate', 'Duplicate'),
        ('error', 'Import Error'),
    ], default='backup', string='Status', index=True, required=True)
    
    # Data Storage
    order_data = fields.Text('Order Data (JSON)', required=True, help='Complete order data in JSON format')
    receipt_data = fields.Text('Receipt Data (HTML)', help='Receipt HTML for reprinting')
    
    # Import Tracking
    imported_order_id = fields.Many2one('pos.order', string='Imported Order', readonly=True, ondelete='set null')
    import_date = fields.Datetime('Import Date', readonly=True)
    import_user_id = fields.Many2one('res.users', string='Imported By', readonly=True)
    error_message = fields.Text('Error Message', readonly=True)
    
    # Technical Fields
    lines_count = fields.Integer('Lines Count', help='Number of order lines')
    payments_count = fields.Integer('Payments Count', help='Number of payments')
    
    # Computed Fields
    is_missing = fields.Boolean('Missing on Server', compute='_compute_is_missing', store=False)
    can_import = fields.Boolean('Can Import', compute='_compute_can_import', store=False)
    
    _sql_constraints = [
        ('unique_access_token', 'unique(access_token)', 'This order backup already exists!'),
    ]
    
    @api.depends('state', 'pos_reference', 'session_id')
    def _compute_is_missing(self):
        """Check if order exists on server"""
        for record in self:
            if record.state in ('imported', 'duplicate'):
                record.is_missing = False
            elif record.pos_reference and record.session_id:
                exists = self.env['pos.order'].search_count([
                    ('pos_reference', '=', record.pos_reference),
                    ('session_id', '=', record.session_id.id)
                ], limit=1)
                record.is_missing = not exists
            else:
                record.is_missing = False
    
    @api.depends('state', 'is_missing')
    def _compute_can_import(self):
        """Determine if order can be imported"""
        for record in self:
            record.can_import = (
                record.state not in ('imported', 'duplicate') and
                record.is_missing
            )
    
    @api.model
    def save_order_backup(self, order_data):
        """Save order backup from POS UI"""
        try:
            # Extract order identifier
            access_token = order_data.get('access_token')
            pos_reference = order_data.get('pos_reference') or order_data.get('name')
            
            if not access_token:
                raise ValidationError(_("Order access_token is required for backup"))
            
            # Check if backup already exists
            existing_backup = self.search([
                ('access_token', '=', access_token),
            ], limit=1)
            
            if existing_backup:
                _logger.info(f"Backup already exists for order {pos_reference}, updating")
                existing_backup.write({
                    'order_data': json.dumps(order_data),
                    'backup_date': fields.Datetime.now(),
                })
                return {
                    'success': True,
                    'id': existing_backup.id,
                    'existing': True,
                }
            
            # Prepare values
            vals = self._prepare_backup_vals(order_data)
            
            # Create backup
            backup = self.create(vals)
            _logger.info(f"Order backup created: {backup.id} for order {pos_reference}")
            
            # Verify if order exists on server
            backup._verify_order_on_server()
            
            return {
                'success': True,
                'id': backup.id,
                'existing': False,
            }
            
        except Exception as e:
            _logger.error(f"Error saving order backup: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def _prepare_backup_vals(self, order_data):
        """Prepare values for creating backup record"""
        # Extract financial data
        amount_total = order_data.get('amount_total', 0)
        amount_tax = order_data.get('amount_tax', 0)
        amount_paid = order_data.get('amount_paid', 0)
        amount_return = order_data.get('amount_return', 0)
        
        # Count lines and payments
        lines = order_data.get('lines', [])
        payments = order_data.get('payment_ids', [])
        lines_count = len([l for l in lines if isinstance(l, (list, dict))])
        payments_count = len([p for p in payments if isinstance(p, (list, dict))])
        
        # Extract receipt data if available
        receipt_data = order_data.pop('receipt_html', None)
        
        return {
            'pos_reference': order_data.get('pos_reference') or order_data.get('name'),
            'access_token': order_data.get('access_token'),
            'backup_date': fields.Datetime.now(),
            'order_date': order_data.get('creation_date') or order_data.get('date_order'),
            'session_id': order_data.get('session_id'),
            'user_id': order_data.get('user_id'),
            'partner_id': order_data.get('partner_id'),
            'amount_total': amount_total,
            'amount_tax': amount_tax,
            'amount_paid': amount_paid,
            'amount_return': amount_return,
            'order_data': json.dumps(order_data),
            'receipt_data': receipt_data,
            'state': 'synced',
            'lines_count': lines_count,
            'payments_count': payments_count,
        }
    
    def _verify_order_on_server(self):
        """Check if order exists on server and update state"""
        for record in self:
            if record.pos_reference and record.session_id:
                order = self.env['pos.order'].search([
                    ('pos_reference', '=', record.pos_reference),
                    ('session_id', '=', record.session_id.id)
                ], limit=1)
                
                if order:
                    record.write({
                        'state': 'verified',
                        'imported_order_id': order.id,
                    })
                    _logger.info(f"Order {record.pos_reference} verified on server")
    
    def action_import_order(self):
        """Import backed up order to pos.order"""
        self.ensure_one()
        
        if self.state == 'imported':
            raise UserError(_('This order has already been imported.'))
        
        if self.state == 'duplicate':
            raise UserError(_('This order is marked as duplicate.'))
        
        try:
            # Parse JSON data
            order_data = json.loads(self.order_data)
            
            # Remove backup-specific keys
            for key in ("uid", "backup_date", "synced", "config_id"):
                order_data.pop(key, None)
            
            # Verify session
            if not self.session_id or not self.session_id.exists():
                raise UserError(_('Session not found. Cannot import order.'))
            
            # Check for duplicate
            existing_order = self.env['pos.order'].search([
                ('pos_reference', '=', self.pos_reference),
                ('session_id', '=', self.session_id.id)
            ], limit=1)
            
            if existing_order:
                self.write({
                    'state': 'duplicate',
                    'imported_order_id': existing_order.id,
                })
                raise UserError(_('Order %s already exists on server.') % self.pos_reference)
            
            # Process order using POS standard method
            _logger.info(f"Importing order: {self.pos_reference}")
            order_list = self.env['pos.order']._process_order(order_data, False)
            
            if order_list and len(order_list) > 0:
                order = self.env['pos.order'].browse(order_list[0]['id'])
                
                # Update backup record
                self.write({
                    'state': 'imported',
                    'imported_order_id': order.id,
                    'import_date': fields.Datetime.now(),
                    'import_user_id': self.env.user.id,
                    'error_message': False,
                })
                
                _logger.info(f"Order imported successfully: {order.name}")
                
                return {
                    'type': 'ir.actions.client',
                    'tag': 'display_notification',
                    'params': {
                        'message': _('Order imported successfully: %s') % order.name,
                        'type': 'success',
                        'next': {'type': 'ir.actions.act_window_close'},
                    }
                }
            else:
                raise UserError(_('Order processing returned no results'))
            
        except UserError as e:
            raise e
        except Exception as e:
            _logger.error(f"Error importing order: {str(e)}", exc_info=True)
            self.write({
                'state': 'error',
                'error_message': str(e),
            })
            raise UserError(_('Error importing order: %s') % str(e))
    
    def action_verify_on_server(self):
        """Manually verify if orders exist on server"""
        for record in self:
            record._verify_order_on_server()
        
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'message': _('%s order(s) verified') % len(self),
                'type': 'info',
            }
        }
    
    def action_reprint_receipt(self):
        """Reprint receipt from backup"""
        self.ensure_one()
        
        if not self.receipt_data:
            raise UserError(_('No receipt data available for this order.'))
        
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': _('Receipt'),
                'message': self.receipt_data,
                'type': 'info',
                'sticky': True,
            }
        }
    
    def action_mark_as_duplicate(self):
        """Mark selected backups as duplicate"""
        self.write({'state': 'duplicate'})
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'message': _('Marked as duplicate'),
                'type': 'info',
            }
        }
    
    @api.model
    def get_backup_statistics(self, session_id=None):
        """Get backup statistics for dashboard"""
        domain = []
        if session_id:
            domain.append(('session_id', '=', session_id))
        
        all_backups = self.search(domain)
        
        stats = {
            'total': len(all_backups),
            'synced': len(all_backups.filtered(lambda r: r.state == 'synced')),
            'verified': len(all_backups.filtered(lambda r: r.state == 'verified')),
            'imported': len(all_backups.filtered(lambda r: r.state == 'imported')),
            'duplicate': len(all_backups.filtered(lambda r: r.state == 'duplicate')),
            'error': len(all_backups.filtered(lambda r: r.state == 'error')),
            'missing': len(all_backups.filtered(lambda r: r.is_missing)),
        }
        
        return stats
    
    @api.model
    def cleanup_old_backups(self, days=30):
        """Archive/delete old verified and imported backups"""
        cutoff_date = fields.Datetime.subtract(fields.Datetime.now(), days=days)
        
        old_backups = self.search([
            ('backup_date', '<', cutoff_date),
            ('state', 'in', ['verified', 'imported', 'duplicate']),
        ])
        
        count = len(old_backups)
        old_backups.unlink()
        
        _logger.info(f"Cleaned up {count} old backup records")
        return count
