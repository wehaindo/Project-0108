# -*- coding: utf-8 -*-

from odoo import models, fields, api
import json
import logging

_logger = logging.getLogger(__name__)


class PosLog(models.Model):
    _name = 'pos.log'
    _description = 'POS Activity Log'
    _order = 'create_date desc, id desc'
    _rec_name = 'event_type'

    # Core Fields
    event_type = fields.Selection([
        ('login', 'Cashier Login'),
        ('logout', 'Cashier Logout'),
        ('session_open', 'Session Opened'),
        ('session_close', 'Session Closed'),
        ('order_create', 'Order Created'),
        ('order_paid', 'Order Paid'),
        ('order_cancel', 'Order Cancelled'),
        ('payment', 'Payment Made'),
        ('refund', 'Refund Processed'),
        ('cash_in', 'Cash In'),
        ('cash_out', 'Cash Out'),
        ('error', 'Error Occurred'),
        ('sync', 'Data Sync'),
        ('other', 'Other Event'),
    ], string='Event Type', required=True, index=True,
        help="Type of event being logged. Can be extended by other modules.")

    user_id = fields.Many2one(
        'res.users', 
        string='User', 
        required=True, 
        index=True,
        default=lambda self: self.env.user,
        help="User who triggered the event"
    )

    session_id = fields.Many2one(
        'pos.session', 
        string='POS Session', 
        index=True,
        ondelete='set null',
        help="Related POS session if applicable"
    )

    config_id = fields.Many2one(
        'pos.config', 
        string='POS Config', 
        index=True,
        ondelete='set null',
        help="POS configuration where event occurred"
    )

    # Timestamp and Sync
    create_date = fields.Datetime(
        string='Event Time', 
        readonly=True, 
        index=True,
        help="When the event occurred"
    )

    is_synced = fields.Boolean(
        string='Synced to Server', 
        default=False, 
        index=True,
        help="Whether this log has been synced to server"
    )

    sync_date = fields.Datetime(
        string='Sync Date',
        readonly=True,
        help="When the log was synced to server"
    )

    # Data Storage
    event_data = fields.Text(
        string='Event Data (JSON)',
        help="Additional event data stored as JSON"
    )

    description = fields.Text(
        string='Description',
        help="Human-readable description of the event"
    )

    # Related Fields (for easier searching)
    company_id = fields.Many2one(
        'res.company',
        string='Company',
        default=lambda self: self.env.company,
        index=True
    )

    order_id = fields.Many2one(
        'pos.order',
        string='POS Order',
        index=True,
        ondelete='set null',
        help="Related POS order if applicable"
    )

    # Computed Fields
    event_data_parsed = fields.Char(
        string='Event Data',
        compute='_compute_event_data_parsed',
        store=False,
        help="Parsed event data for display"
    )

    @api.depends('event_data')
    def _compute_event_data_parsed(self):
        """Parse JSON data for display"""
        for record in self:
            if record.event_data:
                try:
                    data = json.loads(record.event_data)
                    record.event_data_parsed = ', '.join([f"{k}: {v}" for k, v in data.items()])
                except:
                    record.event_data_parsed = record.event_data
            else:
                record.event_data_parsed = ''

    @api.model
    def create_log(self, event_type, user_id=None, session_id=None, config_id=None, 
                   order_id=None, description=None, event_data=None):
        """
        Helper method to create log entries
        
        Args:
            event_type (str): Type of event from selection field
            user_id (int): User ID (defaults to current user)
            session_id (int): POS Session ID
            config_id (int): POS Config ID
            order_id (int): POS Order ID
            description (str): Human-readable description
            event_data (dict): Additional data to store as JSON
            
        Returns:
            pos.log: Created log record
        """
        vals = {
            'event_type': event_type,
            'user_id': user_id or self.env.user.id,
            'description': description,
        }
        
        if session_id:
            vals['session_id'] = session_id
        if config_id:
            vals['config_id'] = config_id
        if order_id:
            vals['order_id'] = order_id
        if event_data:
            vals['event_data'] = json.dumps(event_data)
            
        try:
            return self.create(vals)
        except Exception as e:
            _logger.error(f"Failed to create POS log: {str(e)}")
            return False

    def mark_as_synced(self):
        """Mark log entries as synced"""
        self.write({
            'is_synced': True,
            'sync_date': fields.Datetime.now(),
        })
        return True

    @api.model
    def get_pending_logs(self, limit=100):
        """
        Get logs that haven't been synced yet
        
        Args:
            limit (int): Maximum number of records to return
            
        Returns:
            list: List of log dictionaries
        """
        logs = self.search([
            ('is_synced', '=', False)
        ], limit=limit, order='create_date asc')
        
        return logs.read([
            'event_type', 'user_id', 'session_id', 'config_id',
            'order_id', 'description', 'event_data', 'create_date'
        ])

    @api.model
    def sync_logs_from_pos(self, log_data_list):
        """
        Sync logs from POS client to server
        
        Args:
            log_data_list (list): List of log dictionaries from POS
            
        Returns:
            dict: Result with success count
        """
        success_count = 0
        for log_data in log_data_list:
            try:
                # Create log with synced flag
                log_data['is_synced'] = True
                log_data['sync_date'] = fields.Datetime.now()
                self.create(log_data)
                success_count += 1
            except Exception as e:
                _logger.error(f"Failed to sync log: {str(e)}")
                
        return {
            'success': success_count,
            'total': len(log_data_list)
        }

    def action_view_related_session(self):
        """Open related POS session"""
        self.ensure_one()
        if not self.session_id:
            return
        
        return {
            'type': 'ir.actions.act_window',
            'name': 'POS Session',
            'res_model': 'pos.session',
            'res_id': self.session_id.id,
            'view_mode': 'form',
            'target': 'current',
        }

    def action_view_related_order(self):
        """Open related POS order"""
        self.ensure_one()
        if not self.order_id:
            return
        
        return {
            'type': 'ir.actions.act_window',
            'name': 'POS Order',
            'res_model': 'pos.order',
            'res_id': self.order_id.id,
            'view_mode': 'form',
            'target': 'current',
        }
