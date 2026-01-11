# -*- coding: utf-8 -*-
from odoo import fields, models, api, _
import json
import logging

_logger = logging.getLogger(__name__)


class PosDataLog(models.Model):
    _name = 'pos.data.log'
    _description = 'POS Data Backup Log'
    _order = 'create_date desc'

    name = fields.Datetime('Sync Date', default=fields.Datetime.now, required=True)
    pos_data = fields.Text('POS Data (JSON)', required=True)
    type = fields.Char('Type', default='order', required=True)
    order_uid = fields.Char('Order UID', index=True, help='Unique identifier (access_token) for the order')
    session_id = fields.Many2one('pos.session', string='Session', index=True)
    state = fields.Selection([
        ('backup', 'Backup Only'),
        ('synced', 'Synced'),
        ('imported', 'Imported'),
        ('duplicate', 'Duplicate'),
    ], default='backup', string='Status')

    @api.model
    def save_order_backup(self, order_data):
        """Save order backup from POS UI"""
        try:
            # Extract order identifier (use access_token as primary identifier)
            order_uid = order_data.get('access_token') or order_data.get('pos_reference')
            session_id = order_data.get('session_id')
            
            if not order_uid:
                raise ValueError("Order access_token is required for backup")
            
            # Check if backup already exists
            existing_backup = self.search([
                ('order_uid', '=', order_uid),
                ('session_id', '=', session_id),
            ], limit=1)
            
            if existing_backup:
                _logger.info(f"Backup already exists for order {order_uid}, skipping")
                return {
                    'success': True,
                    'id': existing_backup.id,
                    'existing': True,
                }
            
            vals = {
                'name': fields.Datetime.now(),
                'pos_data': json.dumps(order_data),
                'type': 'order',
                'order_uid': order_uid,
                'session_id': session_id,
                'state': 'synced',
            }
            
            backup = self.create(vals)
            _logger.info(f"Order backup created: {backup.id} for order {order_uid}")
            
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

    @api.model
    def get_missing_orders(self, session_id, order_uids):
        """Check which orders are missing from pos.order table"""
        existing_orders = self.env['pos.order'].search([
            ('session_id', '=', session_id),
            ('pos_reference', 'in', order_uids)
        ])
        
        existing_uids = set(existing_orders.mapped('pos_reference'))
        missing_uids = [uid for uid in order_uids if uid not in existing_uids]
        
        return {
            'missing_count': len(missing_uids),
            'missing_uids': missing_uids,
            'total_checked': len(order_uids)
        }

    def action_import_order(self):
        """Import backed up order to pos.order using sync_from_ui"""
        self.ensure_one()
        
        try:
            # Parse JSON data
            order_data = json.loads(self.pos_data)
            for key in ("uid", "backup_date", "synced", "config_id"):
                order_data.pop(key, None)
            # _logger.info(f"Importing order backup, raw data type: {type(order_data)}")
            # _logger.info(f"Order data keys: {order_data.keys() if isinstance(order_data, dict) else 'Not a dict'}")
            
            # # Prepare order data for _process_order
            # # Convert [0, 0, {...}] format to just {...} for lines and payments
            # if 'lines' in order_data and order_data['lines']:
            #     processed_lines = []
            #     for line in order_data['lines']:
            #         if isinstance(line, list) and len(line) == 3:
            #             # Extract the dict from [0, 0, {...}] format
            #             processed_lines.append([0, 0, line[2]])
            #         else:
            #             processed_lines.append(line)
            #     order_data['lines'] = processed_lines
            
            # if 'payment_ids' in order_data and order_data['payment_ids']:
            #     processed_payments = []
            #     for payment in order_data['payment_ids']:
            #         if isinstance(payment, list) and len(payment) == 3:
            #             # Extract the dict from [0, 0, {...}] format
            #             processed_payments.append([0, 0, payment[2]])
            #         else:
            #             processed_payments.append(payment)
            #     order_data['payment_ids'] = processed_payments
            
            # _logger.info(f"Importing order: {order_data.get('pos_reference') or order_data.get('uid')}")
            
            # Get session
            session_id = order_data.get('session_id')
            if not session_id:
                raise ValueError("No session_id in order data")
            
            session = self.env['pos.session'].browse(session_id)
            if not session.exists():
                raise ValueError(f"Session {session_id} not found")
            
            # Process order using _process_order (proper POS order creation)
            order_list = self.env['pos.order']._process_order(order_data, False)
            
            if order_list and len(order_list) > 0:
                order = self.env['pos.order'].browse(order_list[0]['id'])
                
                # Update backup log
                self.write({
                    'state': 'imported'
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
                raise ValueError("Order processing returned no results")
            
        except Exception as e:
            _logger.error(f"Error importing order: {str(e)}")
            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'message': _('Error importing order: %s') % str(e),
                    'type': 'danger',
                    'sticky': True,
                }
            }

    def _prepare_order_vals(self, order_data):
        """Prepare values for creating pos.order"""
        # Prepare order lines
        line_vals = []
        for line in order_data.get('lines', []):
            line_vals.append((0, 0, {
                'product_id': line.get('product_id'),
                'qty': line.get('qty'),
                'price_unit': line.get('price_unit'),
                'discount': line.get('discount', 0),
                'tax_ids': [(6, 0, line.get('tax_ids', []))],
                'price_subtotal': line.get('price_subtotal'),
                'price_subtotal_incl': line.get('price_subtotal_incl'),
            }))
        
        # Prepare payments
        payment_vals = []
        for payment in order_data.get('payment_ids', []):
            payment_vals.append((0, 0, {
                'payment_method_id': payment.get('payment_method_id'),
                'amount': payment.get('amount'),
                'payment_date': payment.get('payment_date'),
            }))
        
        return {
            'session_id': order_data.get('session_id'),
            'pos_reference': order_data.get('pos_reference') or order_data.get('uid'),
            'partner_id': order_data.get('partner_id'),
            'date_order': order_data.get('date_order'),
            'amount_total': order_data.get('amount_total'),
            'amount_tax': order_data.get('amount_tax'),
            'amount_paid': order_data.get('amount_paid'),
            'amount_return': order_data.get('amount_return', 0),
            'lines': line_vals,
            'payment_ids': payment_vals,
            'state': 'paid',
            'to_invoice': order_data.get('to_invoice', False),
        }
