# -*- coding: utf-8 -*-
# Copyright 2026 Weha
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl-3.0).

from odoo import api, fields, models, _
from odoo.exceptions import UserError
import logging

_logger = logging.getLogger(__name__)


class FixOperatingUnitWizard(models.TransientModel):
    """Wizard to identify and fix Operating Unit configuration issues"""
    _name = 'fix.operating.unit.wizard'
    _description = 'Fix Operating Unit Configuration Issues'

    issue_ids = fields.One2many(
        'fix.operating.unit.issue',
        'wizard_id',
        string='Issues Found'
    )
    issue_count = fields.Integer(
        string='Issues Count',
        compute='_compute_issue_count'
    )
    replenishment_rule_count = fields.Integer(
        string='Replenishment Rules',
        compute='_compute_issue_count'
    )
    orderpoint_count = fields.Integer(
        string='Warehouse Orderpoints',
        compute='_compute_issue_count'
    )
    location_count = fields.Integer(
        string='Location Issues',
        compute='_compute_issue_count'
    )

    @api.depends('issue_ids')
    def _compute_issue_count(self):
        for wizard in self:
            wizard.issue_count = len(wizard.issue_ids)
            wizard.replenishment_rule_count = len(wizard.issue_ids.filtered(
                lambda i: i.issue_type == 'replenishment_rule'
            ))
            wizard.orderpoint_count = len(wizard.issue_ids.filtered(
                lambda i: i.issue_type == 'orderpoint'
            ))
            wizard.location_count = len(wizard.issue_ids.filtered(
                lambda i: i.issue_type == 'location'
            ))

    @api.model
    def default_get(self, fields_list):
        """Scan for issues when wizard opens"""
        res = super().default_get(fields_list)
        issues = self._scan_for_issues()
        res['issue_ids'] = [(0, 0, issue) for issue in issues]
        return res

    def _scan_for_issues(self):
        """Scan database for operating unit configuration issues"""
        issues = []

        # 1. Check replenishment rules
        _logger.info('Scanning replenishment rules for OU issues...')
        rules = self.env['stock.replenishment.rule'].search([])
        for rule in rules:
            # Check warehouse OU matches rule OU
            if rule.warehouse_id and rule.operating_unit_id:
                if rule.warehouse_id.operating_unit_id != rule.operating_unit_id:
                    issues.append({
                        'issue_type': 'replenishment_rule',
                        'record_id': rule.id,
                        'record_name': rule.name,
                        'description': 'Warehouse "%s" (OU: %s) does not match Rule OU: %s' % (
                            rule.warehouse_id.name,
                            rule.warehouse_id.operating_unit_id.name if rule.warehouse_id.operating_unit_id else 'None',
                            rule.operating_unit_id.name
                        ),
                        'warehouse_id': rule.warehouse_id.id,
                        'warehouse_ou_id': rule.warehouse_id.operating_unit_id.id if rule.warehouse_id.operating_unit_id else False,
                        'location_id': rule.location_id.id if rule.location_id else False,
                        'location_ou_id': rule.location_id.operating_unit_id.id if rule.location_id and rule.location_id.operating_unit_id else False,
                        'expected_ou_id': rule.operating_unit_id.id,
                    })
            
            # Check location OU matches warehouse OU
            if rule.warehouse_id and rule.location_id:
                if (rule.warehouse_id.operating_unit_id and 
                    rule.location_id.operating_unit_id and
                    rule.warehouse_id.operating_unit_id != rule.location_id.operating_unit_id):
                    issues.append({
                        'issue_type': 'replenishment_rule',
                        'record_id': rule.id,
                        'record_name': rule.name,
                        'description': 'Location "%s" (OU: %s) does not match Warehouse "%s" (OU: %s)' % (
                            rule.location_id.complete_name,
                            rule.location_id.operating_unit_id.name,
                            rule.warehouse_id.name,
                            rule.warehouse_id.operating_unit_id.name
                        ),
                        'warehouse_id': rule.warehouse_id.id,
                        'warehouse_ou_id': rule.warehouse_id.operating_unit_id.id,
                        'location_id': rule.location_id.id,
                        'location_ou_id': rule.location_id.operating_unit_id.id,
                        'expected_ou_id': rule.warehouse_id.operating_unit_id.id,
                    })

        # 2. Check warehouse orderpoints (reorder rules)
        _logger.info('Scanning warehouse orderpoints for OU issues...')
        if 'stock.warehouse.orderpoint' in self.env:
            orderpoints = self.env['stock.warehouse.orderpoint'].search([])
            for op in orderpoints:
                if (op.warehouse_id.operating_unit_id and 
                    op.location_id and op.location_id.operating_unit_id and
                    op.warehouse_id.operating_unit_id != op.location_id.operating_unit_id):
                    issues.append({
                        'issue_type': 'orderpoint',
                        'record_id': op.id,
                        'record_name': op.display_name,
                        'description': 'Warehouse "%s" (OU: %s) does not match Location "%s" (OU: %s)' % (
                            op.warehouse_id.name,
                            op.warehouse_id.operating_unit_id.name,
                            op.location_id.complete_name,
                            op.location_id.operating_unit_id.name
                        ),
                        'warehouse_id': op.warehouse_id.id,
                        'warehouse_ou_id': op.warehouse_id.operating_unit_id.id,
                        'location_id': op.location_id.id,
                        'location_ou_id': op.location_id.operating_unit_id.id,
                        'expected_ou_id': op.warehouse_id.operating_unit_id.id,
                    })

        # 3. Check locations without operating units but in warehouses with OUs
        _logger.info('Scanning locations for missing OU assignments...')
        warehouses = self.env['stock.warehouse'].search([
            ('operating_unit_id', '!=', False)
        ])
        for warehouse in warehouses:
            locations = self.env['stock.location'].search([
                ('warehouse_id', '=', warehouse.id),
                ('operating_unit_id', '=', False),
                ('usage', '=', 'internal')
            ])
            for loc in locations:
                issues.append({
                    'issue_type': 'location',
                    'record_id': loc.id,
                    'record_name': loc.complete_name,
                    'description': 'Location in Warehouse "%s" (OU: %s) has no Operating Unit assigned' % (
                        warehouse.name,
                        warehouse.operating_unit_id.name
                    ),
                    'warehouse_id': warehouse.id,
                    'warehouse_ou_id': warehouse.operating_unit_id.id,
                    'location_id': loc.id,
                    'location_ou_id': False,
                    'expected_ou_id': warehouse.operating_unit_id.id,
                })

        _logger.info('Found %d operating unit configuration issues', len(issues))
        return issues

    def action_fix_all(self):
        """Fix all issues automatically"""
        self.ensure_one()
        
        fixed_count = 0
        error_count = 0
        
        for issue in self.issue_ids:
            try:
                issue.action_fix()
                fixed_count += 1
            except Exception as e:
                error_count += 1
                _logger.error('Failed to fix issue %s: %s', issue.record_name, str(e))
        
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': _('Fix Complete'),
                'message': _('Fixed %d issues. %d errors.') % (fixed_count, error_count),
                'type': 'success' if error_count == 0 else 'warning',
                'sticky': False,
            }
        }

    def action_view_issues(self):
        """View issues in detail"""
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'fix.operating.unit.issue',
            'view_mode': 'tree,form',
            'domain': [('id', 'in', self.issue_ids.ids)],
            'context': {'default_wizard_id': self.id},
            'name': _('Operating Unit Configuration Issues'),
        }


class FixOperatingUnitIssue(models.TransientModel):
    """Individual issue found"""
    _name = 'fix.operating.unit.issue'
    _description = 'Operating Unit Configuration Issue'
    _order = 'issue_type, record_name'

    wizard_id = fields.Many2one(
        'fix.operating.unit.wizard',
        string='Wizard',
        required=True,
        ondelete='cascade'
    )
    issue_type = fields.Selection([
        ('replenishment_rule', 'Replenishment Rule'),
        ('orderpoint', 'Warehouse Orderpoint'),
        ('location', 'Location Missing OU'),
    ], string='Issue Type', required=True)
    
    record_id = fields.Integer(string='Record ID', required=True)
    record_name = fields.Char(string='Record Name', required=True)
    description = fields.Text(string='Issue Description', required=True)
    
    warehouse_id = fields.Many2one('stock.warehouse', string='Warehouse')
    warehouse_ou_id = fields.Many2one('operating.unit', string='Warehouse OU')
    location_id = fields.Many2one('stock.location', string='Location')
    location_ou_id = fields.Many2one('operating.unit', string='Location OU')
    expected_ou_id = fields.Many2one('operating.unit', string='Expected OU')
    
    fix_action = fields.Selection([
        ('update_location_ou', 'Update Location Operating Unit'),
        ('update_warehouse_ou', 'Update Warehouse Operating Unit'),
        ('manual', 'Manual Fix Required'),
    ], string='Fix Action', compute='_compute_fix_action')
    
    is_fixed = fields.Boolean(string='Fixed', default=False)

    @api.depends('issue_type', 'location_ou_id', 'warehouse_ou_id', 'expected_ou_id')
    def _compute_fix_action(self):
        for issue in self:
            if issue.issue_type == 'location':
                issue.fix_action = 'update_location_ou'
            elif issue.issue_type in ('replenishment_rule', 'orderpoint'):
                if not issue.location_ou_id or issue.location_ou_id != issue.expected_ou_id:
                    issue.fix_action = 'update_location_ou'
                elif issue.warehouse_ou_id != issue.expected_ou_id:
                    issue.fix_action = 'update_warehouse_ou'
                else:
                    issue.fix_action = 'manual'
            else:
                issue.fix_action = 'manual'

    def action_fix(self):
        """Fix this specific issue"""
        self.ensure_one()
        
        if self.fix_action == 'update_location_ou':
            if self.location_id and self.expected_ou_id:
                self.location_id.write({'operating_unit_id': self.expected_ou_id.id})
                self.is_fixed = True
                _logger.info('Fixed location %s: Set OU to %s', 
                           self.location_id.complete_name, self.expected_ou_id.name)
        
        elif self.fix_action == 'update_warehouse_ou':
            if self.warehouse_id and self.expected_ou_id:
                self.warehouse_id.write({'operating_unit_id': self.expected_ou_id.id})
                self.is_fixed = True
                _logger.info('Fixed warehouse %s: Set OU to %s',
                           self.warehouse_id.name, self.expected_ou_id.name)
        
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': _('Fixed'),
                'message': _('Issue has been resolved'),
                'type': 'success',
                'sticky': False,
            }
        }

    def action_open_record(self):
        """Open the problematic record"""
        self.ensure_one()
        
        if self.issue_type == 'replenishment_rule':
            model = 'stock.replenishment.rule'
            view_mode = 'form'
        elif self.issue_type == 'orderpoint':
            model = 'stock.warehouse.orderpoint'
            view_mode = 'form'
        elif self.issue_type == 'location':
            model = 'stock.location'
            view_mode = 'form'
        else:
            return {}
        
        return {
            'type': 'ir.actions.act_window',
            'res_model': model,
            'res_id': self.record_id,
            'view_mode': view_mode,
            'target': 'current',
        }
