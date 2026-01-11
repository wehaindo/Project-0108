# -*- coding: utf-8 -*-
# Copyright 2026 Weha
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl-3.0).

from odoo import api, fields, models, _
from odoo.exceptions import UserError


class StockReplenishmentWizard(models.TransientModel):
    """Wizard to manually trigger replenishment for multiple products"""
    _name = 'stock.replenishment.wizard'
    _description = 'Stock Replenishment Wizard'
    
    operating_unit_id = fields.Many2one(
        'operating.unit',
        string='Operating Unit',
        required=True,
        help='Operating unit to replenish'
    )
    line_ids = fields.One2many(
        'stock.replenishment.wizard.line',
        'wizard_id',
        string='Products to Replenish'
    )
    
    @api.model
    def default_get(self, fields_list):
        """Load rules below minimum"""
        res = super().default_get(fields_list)
        
        # Get active OU from context or use first available
        ou_id = self.env.context.get('default_operating_unit_id')
        if not ou_id:
            ou = self.env['operating.unit'].search([], limit=1)
            ou_id = ou.id if ou else False
        
        if ou_id:
            res['operating_unit_id'] = ou_id
            
            # Find rules below minimum for this OU
            rules = self.env['stock.replenishment.rule'].search([
                ('operating_unit_id', '=', ou_id),
                ('active', '=', True),
                ('below_minimum', '=', True),
            ])
            
            # Create wizard lines
            lines = []
            for rule in rules:
                if rule.reorder_qty > 0:
                    lines.append((0, 0, {
                        'rule_id': rule.id,
                        'product_id': rule.product_id.id,
                        'current_qty': rule.current_qty,
                        'minimum_qty': rule.minimum_qty,
                        'maximum_qty': rule.maximum_qty,
                        'reorder_qty': rule.reorder_qty,
                        'selected': True,
                    }))
            
            res['line_ids'] = lines
        
        return res
    
    def action_create_requests(self):
        """Create stock requests for selected lines"""
        self.ensure_one()
        
        selected_lines = self.line_ids.filtered(lambda l: l.selected and l.reorder_qty > 0)
        
        if not selected_lines:
            raise UserError(_('Please select at least one product to replenish!'))
        
        created_requests = self.env['stock.request']
        
        for line in selected_lines:
            rule = line.rule_id
            
            if not rule.source_ou_id:
                continue
            
            # Create stock request
            request = self.env['stock.request'].create({
                'product_id': line.product_id.id,
                'product_uom_id': line.product_id.uom_id.id,
                'product_uom_qty': line.reorder_qty,
                'operating_unit_id': self.operating_unit_id.id,
                'warehouse_id': rule.warehouse_id.id,
                'location_id': rule.location_id.id,
                'route_id': rule.route_id.id if rule.route_id else False,
                'expected_date': fields.Datetime.now(),
                'replenishment_rule_id': rule.id,
                'is_auto_generated': False,
            })
            
            created_requests |= request
            rule.trigger_date = fields.Datetime.now()
        
        # Return action to view created requests
        return {
            'name': _('Created Stock Requests'),
            'type': 'ir.actions.act_window',
            'res_model': 'stock.request',
            'view_mode': 'list,form',
            'domain': [('id', 'in', created_requests.ids)],
            'target': 'current',
        }


class StockReplenishmentWizardLine(models.TransientModel):
    """Wizard line for each product to replenish"""
    _name = 'stock.replenishment.wizard.line'
    _description = 'Stock Replenishment Wizard Line'
    
    wizard_id = fields.Many2one(
        'stock.replenishment.wizard',
        string='Wizard',
        required=True,
        ondelete='cascade'
    )
    rule_id = fields.Many2one(
        'stock.replenishment.rule',
        string='Rule',
        required=True,
        readonly=True
    )
    selected = fields.Boolean(
        string='Select',
        default=True
    )
    product_id = fields.Many2one(
        'product.product',
        string='Product',
        required=True,
        readonly=True
    )
    current_qty = fields.Float(
        string='Current Qty',
        readonly=True
    )
    minimum_qty = fields.Float(
        string='Minimum Qty',
        readonly=True
    )
    maximum_qty = fields.Float(
        string='Maximum Qty',
        readonly=True
    )
    reorder_qty = fields.Float(
        string='Qty to Order',
        required=True
    )
