# -*- coding: utf-8 -*-
# Copyright 2026 Weha
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl-3.0).

from odoo import api, fields, models, _
from odoo.exceptions import ValidationError


class OperatingUnit(models.Model):
    """Extended Operating Unit with Hierarchy Support"""
    _inherit = 'operating.unit'

    # Hierarchy Fields
    ou_type_id = fields.Many2one(
        'operating.unit.type',
        string='Operating Unit Type',
        required=True,
        help='Type of operating unit (HO, DC, Store)'
    )
    parent_id = fields.Many2one(
        'operating.unit',
        string='Parent Operating Unit',
        domain="[('company_id', '=', company_id), ('id', '!=', id)]",
        index=True,
        help='Parent operating unit in hierarchy (e.g., DC for Store, HO for DC)'
    )
    child_ids = fields.One2many(
        'operating.unit',
        'parent_id',
        string='Child Operating Units',
        help='Child operating units (e.g., Stores under DC, DCs under HO)'
    )
    parent_path = fields.Char(
        string='Parent Path',
        index=True,
        compute='_compute_parent_path',
        store=True,
        help='Path showing hierarchy from HO to this OU'
    )
    level = fields.Integer(
        string='Hierarchy Level',
        compute='_compute_level',
        store=True,
        help='Level in hierarchy (0=HO, 1=DC, 2=Store)'
    )
    
    # Revenue Sharing Fields
    revenue_share_percentage = fields.Float(
        string='Revenue Share (%)',
        default=0.0,
        help='Percentage of revenue this OU receives from child OUs sales'
    )
    auto_share_revenue = fields.Boolean(
        string='Auto Share Revenue',
        default=True,
        help='Automatically share revenue with parent when orders are posted'
    )
    
    # Stock Request Fields
    default_source_ou_id = fields.Many2one(
        'operating.unit',
        string='Default Source OU',
        domain="[('company_id', '=', company_id)]",
        help='Default source operating unit for stock requests (usually parent DC)'
    )
    auto_request_from_parent = fields.Boolean(
        string='Auto Request from Parent',
        default=True,
        help='Automatically request stock from parent OU when low'
    )
    
    # Statistics
    child_count = fields.Integer(
        string='Children Count',
        compute='_compute_child_count',
        help='Number of direct child operating units'
    )
    
    @api.depends('parent_id')
    def _compute_parent_path(self):
        """Compute full parent path"""
        for ou in self:
            if ou.parent_id:
                path = []
                current = ou
                while current:
                    path.insert(0, current.name)
                    current = current.parent_id
                ou.parent_path = ' / '.join(path)
            else:
                ou.parent_path = ou.name or ''
    
    @api.depends('parent_id', 'ou_type_id')
    def _compute_level(self):
        """Compute hierarchy level"""
        for ou in self:
            if ou.ou_type_id:
                ou.level = ou.ou_type_id.level
            else:
                # Calculate based on parent chain
                level = 0
                current = ou.parent_id
                while current:
                    level += 1
                    current = current.parent_id
                ou.level = level
    
    @api.depends('child_ids')
    def _compute_child_count(self):
        """Count direct children"""
        for ou in self:
            ou.child_count = len(ou.child_ids)
    
    @api.constrains('parent_id')
    def _check_hierarchy_loop(self):
        """Prevent circular hierarchy"""
        for ou in self:
            if not ou._check_recursion():
                raise ValidationError(
                    _('Error! You cannot create recursive operating unit hierarchy.')
                )
    
    @api.constrains('parent_id', 'ou_type_id')
    def _check_hierarchy_type(self):
        """Validate hierarchy type rules"""
        for ou in self:
            if ou.parent_id and ou.ou_type_id:
                # Check if this type can have parent
                if not ou.ou_type_id.can_have_parent:
                    raise ValidationError(
                        _('Operating unit type "%s" cannot have a parent!') % ou.ou_type_id.name
                    )
                
                # Check if parent type can have children
                if not ou.parent_id.ou_type_id.can_have_children:
                    raise ValidationError(
                        _('Parent operating unit type "%s" cannot have children!') 
                        % ou.parent_id.ou_type_id.name
                    )
    
    @api.onchange('ou_type_id')
    def _onchange_ou_type_id(self):
        """Auto-set revenue share percentage from type"""
        if self.ou_type_id:
            self.revenue_share_percentage = self.ou_type_id.default_revenue_share
            
            # Set default source to parent if exists
            if self.parent_id:
                self.default_source_ou_id = self.parent_id
    
    @api.onchange('parent_id')
    def _onchange_parent_id(self):
        """Auto-set default source to parent"""
        if self.parent_id:
            self.default_source_ou_id = self.parent_id
    
    def action_view_children(self):
        """View child operating units"""
        self.ensure_one()
        return {
            'name': _('Child Operating Units'),
            'type': 'ir.actions.act_window',
            'res_model': 'operating.unit',
            'view_mode': 'tree,form',
            'domain': [('parent_id', '=', self.id)],
            'context': {
                'default_parent_id': self.id,
                'default_company_id': self.company_id.id,
            }
        }
    
    def get_all_parents(self):
        """Get all parent operating units up to HO"""
        self.ensure_one()
        parents = []
        current = self.parent_id
        while current:
            parents.append(current)
            current = current.parent_id
        return self.env['operating.unit'].browse([p.id for p in parents])
    
    def get_all_children(self, include_self=False):
        """Get all child operating units recursively"""
        self.ensure_one()
        children = self if include_self else self.env['operating.unit']
        
        for child in self.child_ids:
            children |= child
            children |= child.get_all_children()
        
        return children
