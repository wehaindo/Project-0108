# -*- coding: utf-8 -*-
# Copyright 2026 Weha
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl-3.0).

from odoo import api, fields, models, _
from datetime import datetime
from dateutil.relativedelta import relativedelta


class RevenueSharingDiagnostic(models.TransientModel):
    """Diagnostic wizard for revenue sharing calculation issues"""
    _name = 'revenue.sharing.diagnostic'
    _description = 'Revenue Sharing Diagnostic'

    period_id = fields.Many2one(
        'revenue.sharing.period',
        string='Period',
        required=True
    )
    
    # Diagnostic Results
    total_pos_orders = fields.Integer(string='Total POS Orders', readonly=True)
    orders_with_state = fields.Integer(string='Orders with Correct State', readonly=True)
    orders_with_ou = fields.Integer(string='Orders with Operating Unit', readonly=True)
    orders_matching = fields.Integer(string='Orders Matching All Criteria', readonly=True)
    
    # OU Check
    total_ous = fields.Integer(string='Total Operating Units', readonly=True)
    ous_with_auto_share = fields.Integer(string='OUs with Auto Share Enabled', readonly=True)
    ous_with_parents = fields.Integer(string='OUs with Parent Hierarchy', readonly=True)
    
    # Rules Check
    total_rules = fields.Integer(string='Total Revenue Sharing Rules', readonly=True)
    active_rules = fields.Integer(string='Active Rules', readonly=True)
    
    diagnostic_message = fields.Html(string='Diagnostic Report', readonly=True)
    
    @api.model
    def default_get(self, fields_list):
        """Set default period from context"""
        res = super().default_get(fields_list)
        if 'period_id' in fields_list and self._context.get('active_id'):
            res['period_id'] = self._context.get('active_id')
        return res
    
    def action_run_diagnostic(self):
        """Run diagnostic checks"""
        self.ensure_one()
        period = self.period_id
        
        # Convert dates to datetime
        date_from_dt = fields.Datetime.to_datetime(period.date_from)
        date_to_dt = fields.Datetime.to_datetime(period.date_to) + relativedelta(days=1)
        
        # Check POS Orders
        total_orders = self.env['pos.order'].search_count([
            ('date_order', '>=', date_from_dt),
            ('date_order', '<', date_to_dt),
        ])
        
        orders_with_state = self.env['pos.order'].search_count([
            ('date_order', '>=', date_from_dt),
            ('date_order', '<', date_to_dt),
            ('state', 'in', ['paid', 'done', 'invoiced']),
        ])
        
        orders_with_ou = self.env['pos.order'].search_count([
            ('date_order', '>=', date_from_dt),
            ('date_order', '<', date_to_dt),
            ('state', 'in', ['paid', 'done', 'invoiced']),
            ('operating_unit_id', '!=', False),
        ])
        
        orders_matching = self.env['pos.order'].search_count([
            ('date_order', '>=', date_from_dt),
            ('date_order', '<', date_to_dt),
            ('state', 'in', ['paid', 'done', 'invoiced']),
            ('operating_unit_id', '!=', False),
            ('company_id', '=', period.company_id.id),
        ])
        
        # Check Operating Units
        ous = self.env['operating.unit'].search([])
        total_ous = len(ous)
        ous_with_auto_share = len(ous.filtered(lambda o: o.auto_share_revenue))
        ous_with_parents = len(ous.filtered(lambda o: o.parent_id))
        
        # Check Rules
        rules = self.env['revenue.sharing.rule'].search([])
        total_rules = len(rules)
        active_rules = len(rules.filtered(lambda r: r.state == 'active'))
        
        # Update fields
        self.write({
            'total_pos_orders': total_orders,
            'orders_with_state': orders_with_state,
            'orders_with_ou': orders_with_ou,
            'orders_matching': orders_matching,
            'total_ous': total_ous,
            'ous_with_auto_share': ous_with_auto_share,
            'ous_with_parents': ous_with_parents,
            'total_rules': total_rules,
            'active_rules': active_rules,
        })
        
        # Generate HTML report
        html = self._generate_diagnostic_report(period, date_from_dt, date_to_dt)
        self.diagnostic_message = html
        
        return {
            'type': 'ir.actions.act_window',
            'res_model': self._name,
            'res_id': self.id,
            'view_mode': 'form',
            'target': 'new',
        }
    
    def _generate_diagnostic_report(self, period, date_from_dt, date_to_dt):
        """Generate HTML diagnostic report"""
        
        # Get sample orders
        sample_orders = self.env['pos.order'].search([
            ('date_order', '>=', date_from_dt),
            ('date_order', '<', date_to_dt),
            ('state', 'in', ['paid', 'done', 'invoiced']),
            ('operating_unit_id', '!=', False),
            ('company_id', '=', period.company_id.id),
        ], limit=5)
        
        issues = []
        solutions = []
        
        # Check for issues
        if self.total_pos_orders == 0:
            issues.append('❌ No POS orders found in this date range')
            solutions.append('Check if orders exist for December 2025. Verify date_order field.')
        elif self.orders_with_state == 0:
            issues.append('❌ No orders with correct state (paid/done/invoiced)')
            solutions.append('Validate or pay the POS orders.')
        elif self.orders_with_ou == 0:
            issues.append('❌ No orders have Operating Unit set')
            solutions.append('Set operating_unit_id on POS orders or configure default OU on POS config.')
        elif self.orders_matching == 0:
            issues.append('❌ No orders match all criteria (state + OU + company)')
            solutions.append('Check company_id on orders matches the period company.')
        
        if self.ous_with_auto_share == 0:
            issues.append('⚠️ No Operating Units have auto_share_revenue enabled')
            solutions.append('Enable "Auto Share Revenue" on Operating Units.')
        
        if self.ous_with_parents == 0:
            issues.append('⚠️ No Operating Units have parent hierarchy set')
            solutions.append('Set parent_id on Operating Units to create hierarchy (DC → HO, Store → DC).')
        
        if self.active_rules == 0:
            issues.append('⚠️ No active revenue sharing rules')
            solutions.append('Create and activate revenue sharing rules for your products/categories.')
        
        html = f'''
        <div style="padding: 15px;">
            <h3>🔍 Diagnostic Report for {period.name}</h3>
            
            <div style="margin: 20px 0;">
                <h4>📅 Period Information</h4>
                <table style="border-collapse: collapse; width: 100%;">
                    <tr><td style="padding: 5px;"><b>Date Range:</b></td><td>{period.date_from} to {period.date_to}</td></tr>
                    <tr><td style="padding: 5px;"><b>DateTime Range:</b></td><td>{date_from_dt} to {date_to_dt}</td></tr>
                    <tr><td style="padding: 5px;"><b>Company:</b></td><td>{period.company_id.name}</td></tr>
                    <tr><td style="padding: 5px;"><b>State:</b></td><td>{period.state}</td></tr>
                </table>
            </div>
            
            <div style="margin: 20px 0;">
                <h4>📊 POS Orders Check</h4>
                <table style="border-collapse: collapse; width: 100%;">
                    <tr style="background: #f0f0f0;">
                        <td style="padding: 5px; border: 1px solid #ddd;"><b>Check</b></td>
                        <td style="padding: 5px; border: 1px solid #ddd;"><b>Count</b></td>
                        <td style="padding: 5px; border: 1px solid #ddd;"><b>Status</b></td>
                    </tr>
                    <tr>
                        <td style="padding: 5px; border: 1px solid #ddd;">Orders in date range</td>
                        <td style="padding: 5px; border: 1px solid #ddd;">{self.total_pos_orders}</td>
                        <td style="padding: 5px; border: 1px solid #ddd;">{'✅' if self.total_pos_orders > 0 else '❌'}</td>
                    </tr>
                    <tr>
                        <td style="padding: 5px; border: 1px solid #ddd;">With correct state</td>
                        <td style="padding: 5px; border: 1px solid #ddd;">{self.orders_with_state}</td>
                        <td style="padding: 5px; border: 1px solid #ddd;">{'✅' if self.orders_with_state > 0 else '❌'}</td>
                    </tr>
                    <tr>
                        <td style="padding: 5px; border: 1px solid #ddd;">With Operating Unit</td>
                        <td style="padding: 5px; border: 1px solid #ddd;">{self.orders_with_ou}</td>
                        <td style="padding: 5px; border: 1px solid #ddd;">{'✅' if self.orders_with_ou > 0 else '❌'}</td>
                    </tr>
                    <tr style="background: #ffffcc;">
                        <td style="padding: 5px; border: 1px solid #ddd;"><b>Matching all criteria</b></td>
                        <td style="padding: 5px; border: 1px solid #ddd;"><b>{self.orders_matching}</b></td>
                        <td style="padding: 5px; border: 1px solid #ddd;"><b>{'✅' if self.orders_matching > 0 else '❌'}</b></td>
                    </tr>
                </table>
            </div>
            
            <div style="margin: 20px 0;">
                <h4>🏢 Operating Units Check</h4>
                <table style="border-collapse: collapse; width: 100%;">
                    <tr style="background: #f0f0f0;">
                        <td style="padding: 5px; border: 1px solid #ddd;"><b>Check</b></td>
                        <td style="padding: 5px; border: 1px solid #ddd;"><b>Count</b></td>
                        <td style="padding: 5px; border: 1px solid #ddd;"><b>Status</b></td>
                    </tr>
                    <tr>
                        <td style="padding: 5px; border: 1px solid #ddd;">Total Operating Units</td>
                        <td style="padding: 5px; border: 1px solid #ddd;">{self.total_ous}</td>
                        <td style="padding: 5px; border: 1px solid #ddd;">{'✅' if self.total_ous > 0 else '❌'}</td>
                    </tr>
                    <tr>
                        <td style="padding: 5px; border: 1px solid #ddd;">With Auto Share Revenue</td>
                        <td style="padding: 5px; border: 1px solid #ddd;">{self.ous_with_auto_share}</td>
                        <td style="padding: 5px; border: 1px solid #ddd;">{'✅' if self.ous_with_auto_share > 0 else '⚠️'}</td>
                    </tr>
                    <tr>
                        <td style="padding: 5px; border: 1px solid #ddd;">With Parent Hierarchy</td>
                        <td style="padding: 5px; border: 1px solid #ddd;">{self.ous_with_parents}</td>
                        <td style="padding: 5px; border: 1px solid #ddd;">{'✅' if self.ous_with_parents > 0 else '⚠️'}</td>
                    </tr>
                </table>
            </div>
            
            <div style="margin: 20px 0;">
                <h4>📋 Revenue Sharing Rules Check</h4>
                <table style="border-collapse: collapse; width: 100%;">
                    <tr style="background: #f0f0f0;">
                        <td style="padding: 5px; border: 1px solid #ddd;"><b>Check</b></td>
                        <td style="padding: 5px; border: 1px solid #ddd;"><b>Count</b></td>
                        <td style="padding: 5px; border: 1px solid #ddd;"><b>Status</b></td>
                    </tr>
                    <tr>
                        <td style="padding: 5px; border: 1px solid #ddd;">Total Rules</td>
                        <td style="padding: 5px; border: 1px solid #ddd;">{self.total_rules}</td>
                        <td style="padding: 5px; border: 1px solid #ddd;">{'✅' if self.total_rules > 0 else '❌'}</td>
                    </tr>
                    <tr>
                        <td style="padding: 5px; border: 1px solid #ddd;">Active Rules</td>
                        <td style="padding: 5px; border: 1px solid #ddd;">{self.active_rules}</td>
                        <td style="padding: 5px; border: 1px solid #ddd;">{'✅' if self.active_rules > 0 else '⚠️'}</td>
                    </tr>
                </table>
            </div>
        '''
        
        # Show sample orders
        if sample_orders:
            html += '''
            <div style="margin: 20px 0;">
                <h4>📝 Sample Orders (first 5)</h4>
                <table style="border-collapse: collapse; width: 100%;">
                    <tr style="background: #f0f0f0;">
                        <td style="padding: 5px; border: 1px solid #ddd;"><b>Order</b></td>
                        <td style="padding: 5px; border: 1px solid #ddd;"><b>Date</b></td>
                        <td style="padding: 5px; border: 1px solid #ddd;"><b>Operating Unit</b></td>
                        <td style="padding: 5px; border: 1px solid #ddd;"><b>Amount</b></td>
                    </tr>
            '''
            for order in sample_orders:
                html += f'''
                    <tr>
                        <td style="padding: 5px; border: 1px solid #ddd;">{order.name}</td>
                        <td style="padding: 5px; border: 1px solid #ddd;">{order.date_order}</td>
                        <td style="padding: 5px; border: 1px solid #ddd;">{order.operating_unit_id.name}</td>
                        <td style="padding: 5px; border: 1px solid #ddd;">{order.amount_total} {order.currency_id.symbol}</td>
                    </tr>
                '''
            html += '</table></div>'
        
        # Show issues
        if issues:
            html += '<div style="margin: 20px 0; padding: 15px; background: #ffe6e6; border-left: 4px solid #ff0000;">'
            html += '<h4>❌ Issues Found</h4><ul>'
            for issue in issues:
                html += f'<li>{issue}</li>'
            html += '</ul></div>'
        
        # Show solutions
        if solutions:
            html += '<div style="margin: 20px 0; padding: 15px; background: #e6f3ff; border-left: 4px solid #0066cc;">'
            html += '<h4>💡 Solutions</h4><ul>'
            for solution in solutions:
                html += f'<li>{solution}</li>'
            html += '</ul></div>'
        
        # Summary
        if not issues:
            html += '''
            <div style="margin: 20px 0; padding: 15px; background: #e6ffe6; border-left: 4px solid #00cc00;">
                <h4>✅ All Checks Passed!</h4>
                <p>Configuration looks good. You can proceed with revenue sharing calculation.</p>
            </div>
            '''
        
        html += '</div>'
        
        return html
