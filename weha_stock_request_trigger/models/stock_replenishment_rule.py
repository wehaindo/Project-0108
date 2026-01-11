# -*- coding: utf-8 -*-
# Copyright 2026 Weha
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl-3.0).

from odoo import api, fields, models, _
from odoo.exceptions import ValidationError, UserError
import logging

_logger = logging.getLogger(__name__)


class StockReplenishmentRule(models.Model):
    """Stock Replenishment Rule per Operating Unit"""
    _name = 'stock.replenishment.rule'
    _description = 'Stock Replenishment Rule'
    _order = 'operating_unit_id, product_id'

    name = fields.Char(
        string='Rule Name',
        compute='_compute_name',
        store=True
    )
    active = fields.Boolean(
        string='Active',
        default=True
    )
    
    # Operating Unit and Location
    operating_unit_id = fields.Many2one(
        'operating.unit',
        string='Operating Unit',
        required=True,
        help='Operating unit where this rule applies (the DESTINATION - e.g., Store requesting stock)'
    )
    warehouse_id = fields.Many2one(
        'stock.warehouse',
        string='Warehouse',
        required=True,
        domain="[('operating_unit_id', '=', operating_unit_id)]",
        help='Warehouse for stock replenishment (must belong to the requesting OU - Store warehouse)'
    )
    location_id = fields.Many2one(
        'stock.location',
        string='Location',
        required=True,
        domain="[('usage', '=', 'internal'), ('warehouse_id', '=', warehouse_id)]",
        help='Stock location to monitor (destination location in Store warehouse)'
    )
    
    # Product
    product_id = fields.Many2one(
        'product.product',
        string='Product',
        required=True,
        domain="[('type', '=', 'consu')]",
        help='Product to replenish'
    )
    product_uom_id = fields.Many2one(
        'uom.uom',
        string='Unit of Measure',
        related='product_id.uom_id',
        readonly=True
    )
    
    # Stock Levels
    current_qty = fields.Float(
        string='Current Qty',
        compute='_compute_current_qty',
        help='Current stock quantity in location'
    )
    minimum_qty = fields.Float(
        string='Minimum Quantity',
        required=True,
        default=0.0,
        help='Minimum stock level (reorder point)'
    )
    maximum_qty = fields.Float(
        string='Maximum Quantity',
        required=True,
        default=0.0,
        help='Maximum stock level (optimal quantity)'
    )
    reorder_qty = fields.Float(
        string='Reorder Quantity',
        compute='_compute_reorder_qty',
        store=True,
        help='Quantity to order to reach maximum'
    )
    
    # Trigger Settings
    auto_trigger = fields.Boolean(
        string='Auto Trigger',
        default=True,
        help='Automatically create stock request when below minimum'
    )
    trigger_date = fields.Datetime(
        string='Last Trigger Date',
        readonly=True,
        help='Last time stock request was created'
    )
    
    # Source Settings (from hierarchy)
    source_ou_id = fields.Many2one(
        'operating.unit',
        string='Source Operating Unit',
        compute='_compute_source_ou',
        store=True,
        help='Source OU from hierarchy (usually parent DC) - where stock will come FROM'
    )
    source_location_id = fields.Many2one(
        'stock.location',
        string='Source Location',
        help='Source location for stock request (optional, determined by route)'
    )
    
    # Route Settings
    route_id = fields.Many2one(
        'stock.route',
        string='Route',
        help='Route for stock transfer from source (DC) to destination (Store). REQUIRED for automatic transfers!'
    )
    
    # Status
    below_minimum = fields.Boolean(
        string='Below Minimum',
        compute='_compute_below_minimum',
        search='_search_below_minimum',
        help='Current stock is below minimum'
    )
    
    company_id = fields.Many2one(
        'res.company',
        string='Company',
        related='operating_unit_id.company_id',
        store=True
    )
    
    _sql_constraints = [
        ('product_ou_unique', 'UNIQUE(product_id, operating_unit_id, location_id)', 
         'Only one rule per product per operating unit per location!'),
        ('minimum_positive', 'CHECK(minimum_qty >= 0)', 'Minimum quantity must be positive!'),
        ('maximum_greater', 'CHECK(maximum_qty >= minimum_qty)', 
         'Maximum quantity must be greater than or equal to minimum!'),
    ]
    
    @api.depends('operating_unit_id', 'product_id')
    def _compute_name(self):
        """Generate rule name"""
        for rule in self:
            if rule.operating_unit_id and rule.product_id:
                rule.name = '%s - %s' % (rule.operating_unit_id.name, rule.product_id.name)
            else:
                rule.name = 'New Rule'
    
    @api.depends('product_id', 'location_id')
    def _compute_current_qty(self):
        """Compute current stock quantity"""
        for rule in self:
            if rule.product_id and rule.location_id:
                quants = self.env['stock.quant'].search([
                    ('product_id', '=', rule.product_id.id),
                    ('location_id', '=', rule.location_id.id),
                ])
                rule.current_qty = sum(quants.mapped('quantity'))
            else:
                rule.current_qty = 0.0
    
    @api.depends('current_qty', 'maximum_qty')
    def _compute_reorder_qty(self):
        """Compute quantity to reorder"""
        for rule in self:
            if rule.maximum_qty > rule.current_qty:
                rule.reorder_qty = rule.maximum_qty - rule.current_qty
            else:
                rule.reorder_qty = 0.0
    
    @api.depends('operating_unit_id')
    def _compute_source_ou(self):
        """Get source OU from hierarchy"""
        for rule in self:
            if rule.operating_unit_id:
                # Use default_source_ou_id if set, otherwise get parent
                if rule.operating_unit_id.default_source_ou_id:
                    rule.source_ou_id = rule.operating_unit_id.default_source_ou_id
                elif rule.operating_unit_id.parent_id:
                    rule.source_ou_id = rule.operating_unit_id.parent_id
                else:
                    rule.source_ou_id = False
            else:
                rule.source_ou_id = False
    
    @api.depends('current_qty', 'minimum_qty')
    def _compute_below_minimum(self):
        """Check if below minimum"""
        for rule in self:
            rule.below_minimum = rule.current_qty < rule.minimum_qty
    
    def _search_below_minimum(self, operator, value):
        """Search for rules below minimum"""
        # This is a simplified search - compute will be used
        if operator == '=' and value:
            # Find rules where current < minimum
            all_rules = self.search([])
            below_rules = all_rules.filtered(lambda r: r.below_minimum)
            return [('id', 'in', below_rules.ids)]
        return []
    
    @api.constrains('minimum_qty', 'maximum_qty')
    def _check_quantities(self):
        """Validate quantities"""
        for rule in self:
            if rule.minimum_qty < 0:
                raise ValidationError(_('Minimum quantity cannot be negative!'))
            if rule.maximum_qty < rule.minimum_qty:
                raise ValidationError(_('Maximum quantity must be >= minimum quantity!'))
    
    def action_create_stock_request(self):
        """Manually create stock request"""
        self.ensure_one()
        
        if not self.source_ou_id:
            raise UserError(_('No source operating unit configured for %s!') % self.operating_unit_id.name)
        
        if self.reorder_qty <= 0:
            raise UserError(_('Reorder quantity must be positive!'))
        
        # Create stock request
        stock_request = self.env['stock.request'].create({
            'product_id': self.product_id.id,
            'product_uom_id': self.product_uom_id.id,
            'product_uom_qty': self.reorder_qty,
            'operating_unit_id': self.operating_unit_id.id,
            'warehouse_id': self.warehouse_id.id,
            'location_id': self.location_id.id,
            'route_id': self.route_id.id if self.route_id else False,
            'expected_date': fields.Datetime.now(),
            'replenishment_rule_id': self.id,
            'is_auto_generated': False,  # Manual creation from button
        })
        
        # Update trigger date
        self.trigger_date = fields.Datetime.now()
        
        _logger.info('Created stock request %s for rule %s', stock_request.name, self.name)
        
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'stock.request',
            'res_id': stock_request.id,
            'view_mode': 'form',
            'target': 'current',
        }
    
    @api.model
    def _cron_check_replenishment(self):
        """Scheduled action to check and create stock requests"""
        _logger.info('Running automatic stock replenishment check...')
        
        # Find all active rules with auto_trigger enabled
        rules = self.search([
            ('active', '=', True),
            ('auto_trigger', '=', True),
        ])
        
        created_count = 0
        
        for rule in rules:
            # Check if below minimum
            if rule.below_minimum and rule.reorder_qty > 0:
                try:
                    if rule.source_ou_id:
                        # Create stock request
                        stock_request = self.env['stock.request'].create({
                            'product_id': rule.product_id.id,
                            'product_uom_id': rule.product_uom_id.id,
                            'product_uom_qty': rule.reorder_qty,
                            'operating_unit_id': rule.operating_unit_id.id,
                            'warehouse_id': rule.warehouse_id.id,
                            'location_id': rule.location_id.id,
                            'route_id': rule.route_id.id if rule.route_id else False,
                            'expected_date': fields.Datetime.now(),
                            'replenishment_rule_id': rule.id,
                            'is_auto_generated': True,  # Automatic creation from cron
                        })
                        
                        rule.trigger_date = fields.Datetime.now()
                        created_count += 1
                        
                        _logger.info('Auto-created stock request %s for %s', 
                                   stock_request.name, rule.name)
                    else:
                        _logger.warning('No source OU for rule %s', rule.name)
                        
                except Exception as e:
                    _logger.error('Failed to create stock request for %s: %s', rule.name, str(e))
                    continue
        
        _logger.info('Automatic replenishment completed: %d stock requests created', created_count)
        return created_count
    
    def action_view_stock_requests(self):
        """View stock requests created from this rule"""
        self.ensure_one()
        
        return {
            'name': _('Stock Requests'),
            'type': 'ir.actions.act_window',
            'res_model': 'stock.request',
            'view_mode': 'list,form',
            'domain': [('replenishment_rule_id', '=', self.id)],
            'context': {'default_operating_unit_id': self.operating_unit_id.id},
        }
