# -*- coding: utf-8 -*-
# Copyright 2026 Weha
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl-3.0).

from odoo import api, fields, models, _
from odoo.exceptions import ValidationError


class RevenueSharingRule(models.Model):
    """Revenue Sharing Rules for Operating Unit Hierarchy"""
    _name = 'revenue.sharing.rule'
    _description = 'Revenue Sharing Rule'
    _order = 'sequence, name'

    name = fields.Char(
        string='Rule Name',
        required=True,
        help='Name of the revenue sharing rule'
    )
    sequence = fields.Integer(
        string='Sequence',
        default=10,
        help='Order of rule application (lower = higher priority)'
    )
    active = fields.Boolean(
        string='Active',
        default=True
    )
    company_id = fields.Many2one(
        'res.company',
        string='Company',
        required=True,
        default=lambda self: self.env.company
    )
    
    # Operating Unit (NEW)
    operating_unit_id = fields.Many2one(
        'operating.unit',
        string='Operating Unit',
        help='Specific Operating Unit for this rule. Leave empty for global rules.'
    )
    
    # Effective Date Range (NEW)
    date_from = fields.Date(
        string='Valid From',
        help='Rule is effective from this date. Leave empty for no start limit.'
    )
    date_to = fields.Date(
        string='Valid To',
        help='Rule is effective until this date. Leave empty for no end limit.'
    )
    
    # Rule Application
    apply_to = fields.Selection([
        ('all', 'All Products'),
        ('category', 'Product Category'),
        ('product', 'Specific Product'),
    ], string='Apply To', required=True, default='all',
        help='What this rule applies to')
    
    categ_id = fields.Many2one(
        'product.category',
        string='Product Category',
        help='Product category for this rule'
    )
    product_id = fields.Many2one(
        'product.product',
        string='Product',
        help='Specific product for this rule'
    )
    
    # Sharing Configuration
    line_ids = fields.One2many(
        'revenue.sharing.rule.line',
        'rule_id',
        string='Sharing Lines',
        help='Revenue sharing percentages for each OU type'
    )
    
    total_percentage = fields.Float(
        string='Total Percentage',
        compute='_compute_total_percentage',
        store=True,
        help='Total percentage (should equal 100%)'
    )
    
    @api.depends('line_ids.percentage')
    def _compute_total_percentage(self):
        """Calculate total percentage"""
        for rule in self:
            rule.total_percentage = sum(rule.line_ids.mapped('percentage'))
    
    @api.constrains('line_ids')
    def _check_total_percentage(self):
        """Validate total percentage equals 100%"""
        for rule in self:
            if not rule.line_ids:
                continue  # Allow saving empty rule during creation
                
            total = sum(rule.line_ids.mapped('percentage'))
            
            # Use tolerance of 0.01 for floating point precision
            if abs(total - 100.0) > 0.01:
                raise ValidationError(
                    _('Total revenue sharing percentage must equal 100%%!\n\n'
                      'Current total: %.2f%%\n'
                      'Difference: %.2f%%\n\n'
                      'Please adjust the percentages in the sharing lines.') % 
                    (total, total - 100.0)
                )
    
    @api.constrains('apply_to', 'categ_id', 'product_id')
    def _check_application(self):
        """Validate rule application"""
        for rule in self:
            if rule.apply_to == 'category' and not rule.categ_id:
                raise ValidationError(_('Please select a product category!'))
            if rule.apply_to == 'product' and not rule.product_id:
                raise ValidationError(_('Please select a product!'))
    
    @api.constrains('date_from', 'date_to')
    def _check_date_range(self):
        """Validate date range"""
        for rule in self:
            if rule.date_from and rule.date_to and rule.date_from > rule.date_to:
                raise ValidationError(
                    _('Valid From date must be before Valid To date!')
                )
    
    def get_sharing_for_product(self, product, operating_unit=None, date=None):
        """
        Get revenue sharing rule for a product with OU and date filtering
        
        Args:
            product: product.product record
            operating_unit: operating.unit record (optional)
            date: date to check validity (optional, defaults to today)
        
        Returns:
            revenue.sharing.rule record or False
        """
        if date is None:
            date = fields.Date.today()
        
        # Build domain for date validity
        date_domain = [
            '|', ('date_from', '=', False), ('date_from', '<=', date),
            '|', ('date_to', '=', False), ('date_to', '>=', date),
        ]
        
        # Priority 1: Specific OU + Specific Product
        if operating_unit:
            rule = self.search([
                ('apply_to', '=', 'product'),
                ('product_id', '=', product.id),
                ('operating_unit_id', '=', operating_unit.id),
                ('active', '=', True),
            ] + date_domain, order='sequence, id', limit=1)
            
            if rule:
                return rule
        
        # Priority 2: Any OU + Specific Product
        rule = self.search([
            ('apply_to', '=', 'product'),
            ('product_id', '=', product.id),
            ('operating_unit_id', '=', False),
            ('active', '=', True),
        ] + date_domain, order='sequence, id', limit=1)
        
        if rule:
            return rule
        
        # Priority 3: Specific OU + Category
        if operating_unit:
            rule = self.search([
                ('apply_to', '=', 'category'),
                ('categ_id', '=', product.categ_id.id),
                ('operating_unit_id', '=', operating_unit.id),
                ('active', '=', True),
            ] + date_domain, order='sequence, id', limit=1)
            
            if rule:
                return rule
        
        # Priority 4: Any OU + Category
        rule = self.search([
            ('apply_to', '=', 'category'),
            ('categ_id', '=', product.categ_id.id),
            ('operating_unit_id', '=', False),
            ('active', '=', True),
        ] + date_domain, order='sequence, id', limit=1)
        
        if rule:
            return rule
        
        # Priority 5: Specific OU + All Products
        if operating_unit:
            rule = self.search([
                ('apply_to', '=', 'all'),
                ('operating_unit_id', '=', operating_unit.id),
                ('active', '=', True),
            ] + date_domain, order='sequence, id', limit=1)
            
            if rule:
                return rule
        
        # Priority 6: Any OU + All Products (Default)
        rule = self.search([
            ('apply_to', '=', 'all'),
            ('operating_unit_id', '=', False),
            ('active', '=', True),
        ] + date_domain, order='sequence, id', limit=1)
        
        return rule


class RevenueSharingRuleLine(models.Model):
    """Revenue Sharing Rule Lines (Percentage per OU Type)"""
    _name = 'revenue.sharing.rule.line'
    _description = 'Revenue Sharing Rule Line'
    _order = 'sequence, ou_type_id'

    rule_id = fields.Many2one(
        'revenue.sharing.rule',
        string='Revenue Sharing Rule',
        required=True,
        ondelete='cascade'
    )
    sequence = fields.Integer(
        string='Sequence',
        default=10
    )
    ou_type_id = fields.Many2one(
        'operating.unit.type',
        string='Operating Unit Type',
        required=True,
        help='Type of operating unit (HO, DC, Store)'
    )
    percentage = fields.Float(
        string='Revenue Share (%)',
        required=True,
        default=0.0,
        help='Percentage of revenue for this OU type'
    )
    description = fields.Text(
        string='Description',
        help='Additional notes'
    )
    
    _sql_constraints = [
        ('percentage_positive', 'CHECK(percentage >= 0)', 'Percentage must be positive!'),
        ('percentage_max', 'CHECK(percentage <= 100)', 'Percentage cannot exceed 100%!'),
    ]
