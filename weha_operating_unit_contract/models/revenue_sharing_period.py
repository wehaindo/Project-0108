# -*- coding: utf-8 -*-
# Copyright 2026 Weha
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl-3.0).

from odoo import api, fields, models, _
from odoo.exceptions import ValidationError, UserError
from datetime import datetime
from dateutil.relativedelta import relativedelta
import logging

_logger = logging.getLogger(__name__)


class RevenueSharingPeriod(models.Model):
    """Monthly Revenue Sharing Period"""
    _name = 'revenue.sharing.period'
    _description = 'Revenue Sharing Period'
    _order = 'date_from desc'

    name = fields.Char(
        string='Period Name',
        required=True,
        help='Period name (e.g., January 2026)'
    )
    company_id = fields.Many2one(
        'res.company',
        string='Company',
        required=True,
        default=lambda self: self.env.company
    )
    date_from = fields.Date(
        string='Date From',
        required=True,
        help='Start date of the period'
    )
    date_to = fields.Date(
        string='Date To',
        required=True,
        help='End date of the period'
    )
    state = fields.Selection([
        ('draft', 'Draft'),
        ('calculated', 'Calculated'),
        ('validated', 'Validated'),
        ('posted', 'Posted'),
        ('closed', 'Closed'),
    ], string='Status', default='draft', required=True)
    
    entry_ids = fields.One2many(
        'revenue.sharing.entry',
        'period_id',
        string='Revenue Sharing Entries'
    )
    entry_count = fields.Integer(
        string='Entry Count',
        compute='_compute_entry_count'
    )
    
    total_revenue = fields.Monetary(
        string='Total Revenue',
        compute='_compute_totals',
        store=True,
        currency_field='currency_id'
    )
    total_shared = fields.Monetary(
        string='Total Shared',
        compute='_compute_totals',
        store=True,
        currency_field='currency_id'
    )
    currency_id = fields.Many2one(
        'res.currency',
        string='Currency',
        related='company_id.currency_id',
        readonly=True
    )
    
    notes = fields.Text(
        string='Notes'
    )
    
    _sql_constraints = [
        ('date_check', 'CHECK(date_to >= date_from)', 'End date must be after start date!'),
    ]
    
    @api.depends('entry_ids')
    def _compute_entry_count(self):
        """Count entries"""
        for period in self:
            period.entry_count = len(period.entry_ids)
    
    @api.depends('entry_ids.total_amount', 'entry_ids.share_amount')
    def _compute_totals(self):
        """Calculate totals"""
        for period in self:
            period.total_revenue = sum(period.entry_ids.mapped('total_amount'))
            period.total_shared = sum(period.entry_ids.mapped('share_amount'))
    
    @api.model
    def get_or_create_period(self, date, company):
        """Get or create period for a date"""
        # Calculate period dates (first and last day of month)
        date_from = date.replace(day=1)
        date_to = (date_from + relativedelta(months=1)) - relativedelta(days=1)
        
        # Try to find existing period
        period = self.search([
            ('date_from', '=', date_from),
            ('date_to', '=', date_to),
            ('company_id', '=', company.id),
        ], limit=1)
        
        if not period:
            # Create new period
            period_name = date.strftime('%B %Y')
            period = self.create({
                'name': period_name,
                'company_id': company.id,
                'date_from': date_from,
                'date_to': date_to,
            })
            _logger.info('Created revenue sharing period: %s', period_name)
        
        return period
    
    def action_calculate_revenue_sharing(self):
        """Calculate revenue sharing for this period"""
        self.ensure_one()
        
        if self.state not in ['draft']:
            raise UserError(_('Can only calculate revenue sharing for draft periods!'))
        
        # Delete existing entries
        self.entry_ids.unlink()
        
        # Convert dates to datetime for proper comparison with date_order (which is datetime field)
        date_from_dt = fields.Datetime.to_datetime(self.date_from)
        # Add 1 day and use < instead of <= to include all orders on last day
        date_to_dt = fields.Datetime.to_datetime(self.date_to) + relativedelta(days=1)
        
        # Get all POS orders in this period
        pos_orders = self.env['pos.order'].search([
            ('date_order', '>=', date_from_dt),
            ('date_order', '<', date_to_dt),
            ('state', 'in', ['paid', 'done', 'invoiced']),
            ('operating_unit_id', '!=', False),
            ('company_id', '=', self.company_id.id),
        ])
        
        _logger.info('Processing %d POS orders for period %s (from %s to %s)', 
                     len(pos_orders), self.name, date_from_dt, date_to_dt)
        
        # OPTIMIZED: Aggregate entries to reduce data volume
        # Instead of one entry per line, aggregate by: source_ou + target_ou + rule
        # This reduces entries from thousands to tens per month
        
        RevenueSharingEntry = self.env['revenue.sharing.entry']
        
        # Dictionary to accumulate amounts: (source_ou, target_ou, rule) -> amounts
        aggregated_data = {}
        orders_processed = 0
        lines_processed = 0
        
        for order in pos_orders:
            selling_ou = order.operating_unit_id
            
            # Skip if auto_share_revenue is disabled
            if not selling_ou.auto_share_revenue:
                continue
            
            # Get parent hierarchy
            parent_ous = selling_ou.get_all_parents()
            
            if not parent_ous:
                continue
            
            orders_processed += 1
            
            # Process each order line
            for line in order.lines:
                if line.qty <= 0 or line.price_subtotal_incl <= 0:
                    continue
                
                lines_processed += 1
                
                # Get revenue sharing rule with OU and date
                order_date = order.date_order.date() if order.date_order else fields.Date.today()
                rule = self.env['revenue.sharing.rule'].get_sharing_for_product(
                    line.product_id,
                    operating_unit=selling_ou,
                    date=order_date
                )
                
                if not rule:
                    _logger.warning('No revenue sharing rule for product %s, OU %s, date %s', 
                                    line.product_id.name, selling_ou.name, order_date)
                    continue
                
                # Aggregate amounts by rule line
                total_amount = line.price_subtotal_incl
                
                for rule_line in rule.line_ids:
                    # Find target OU
                    target_ou = None
                    
                    if selling_ou.ou_type_id == rule_line.ou_type_id:
                        target_ou = selling_ou
                    else:
                        for parent_ou in parent_ous:
                            if parent_ou.ou_type_id == rule_line.ou_type_id:
                                target_ou = parent_ou
                                break
                    
                    if not target_ou:
                        continue
                    
                    # Calculate share
                    share_amount = total_amount * (rule_line.percentage / 100.0)
                    
                    # Aggregate key: (source_ou, target_ou, rule, rule_line)
                    key = (selling_ou.id, target_ou.id, rule.id, rule_line.id)
                    
                    if key not in aggregated_data:
                        aggregated_data[key] = {
                            'source_ou_id': selling_ou.id,
                            'target_ou_id': target_ou.id,
                            'rule_id': rule.id,
                            'rule_line_id': rule_line.id,
                            'total_amount': 0.0,
                            'share_amount': 0.0,
                            'share_percentage': rule_line.percentage,
                            'currency_id': order.currency_id.id,
                            'order_count': 0,
                            'line_count': 0,
                        }
                    
                    # Accumulate amounts
                    aggregated_data[key]['total_amount'] += total_amount
                    aggregated_data[key]['share_amount'] += share_amount
                    aggregated_data[key]['order_count'] += 1
                    aggregated_data[key]['line_count'] += 1
        
        # Create aggregated entries
        entries_created = 0
        for key, data in aggregated_data.items():
            RevenueSharingEntry.create({
                'period_id': self.id,
                'source_ou_id': data['source_ou_id'],
                'target_ou_id': data['target_ou_id'],
                'rule_id': data['rule_id'],
                'rule_line_id': data['rule_line_id'],
                'total_amount': data['total_amount'],
                'share_percentage': data['share_percentage'],
                'share_amount': data['share_amount'],
                'currency_id': data['currency_id'],
                'date': self.date_from,  # Use period start date
                'state': 'draft',
                'order_count': data['order_count'],
                'line_count': data['line_count'],
            })
            entries_created += 1
        
        _logger.info('Revenue sharing calculated: %d orders, %d lines processed → %d aggregated entries created',
                     orders_processed, lines_processed, entries_created)
        
        self.state = 'calculated'
        
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': _('Success'),
                'message': _('Created %d revenue sharing entries') % entries_created,
                'sticky': False,
                'type': 'success',
            }
        }
    
    def action_validate(self):
        """Validate revenue sharing entries"""
        self.ensure_one()
        if self.state != 'calculated':
            raise UserError(_('Can only validate calculated periods!'))
        
        self.entry_ids.write({'state': 'validated'})
        self.state = 'validated'
    
    def action_post_accounting(self):
        """Post accounting entries for revenue sharing"""
        self.ensure_one()
        if self.state != 'validated':
            raise UserError(_('Can only post validated periods!'))
        
        # TODO: Create accounting entries (journal entries for inter-OU transfers)
        # This will be implemented in account_move.py
        
        self.entry_ids.write({'state': 'posted'})
        self.state = 'posted'
    
    def action_close_period(self):
        """Close the period"""
        self.ensure_one()
        if self.state != 'posted':
            raise UserError(_('Can only close posted periods!'))
        
        self.state = 'closed'
    
    def action_reset_to_draft(self):
        """Reset to draft"""
        self.ensure_one()
        self.entry_ids.write({'state': 'draft'})
        self.state = 'draft'
    
    def action_view_entries(self):
        """View revenue sharing entries"""
        self.ensure_one()
        return {
            'name': _('Revenue Sharing Entries'),
            'type': 'ir.actions.act_window',
            'res_model': 'revenue.sharing.entry',
            'view_mode': 'list,form,pivot,graph',
            'domain': [('period_id', '=', self.id)],
            'context': {'default_period_id': self.id},
        }
