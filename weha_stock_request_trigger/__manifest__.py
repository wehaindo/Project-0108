# -*- coding: utf-8 -*-
# Copyright 2026 Weha
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl-3.0).

{
    'name': 'Stock Request Trigger by Operating Unit',
    'version': '18.0.1.0.0',
    'category': 'Inventory',
    'summary': 'Auto-trigger stock requests based on minimum stock levels per OU',
    'description': """
        Stock Request Trigger by Operating Unit
        ========================================
        
        Automatically create stock requests when inventory reaches minimum levels,
        using operating unit hierarchy to determine source and destination.
        
        Key Features:
        ------------
        
        **1. Replenishment Rules per Operating Unit**
        - Define minimum and maximum stock levels per product per OU
        - Set reorder point and optimal quantity
        - Enable/disable auto-trigger per rule
        - Support multiple warehouses per OU
        
        **2. Automatic Stock Request Creation**
        - Monitor stock levels in real-time
        - Auto-create stock requests when below minimum
        - Use OU hierarchy to determine source (Store → DC → HO)
        - Batch processing for multiple products
        
        **3. Manual Replenishment Wizard**
        - Review products below minimum stock
        - Select products to replenish
        - Preview stock request before creation
        - Adjust quantities as needed
        
        **4. Replenishment Scheduler**
        - Scheduled action to check stock levels
        - Configurable frequency (hourly, daily, etc.)
        - Email notifications for low stock
        - Dashboard for replenishment status
        
        Business Flow:
        -------------
        
        **Automatic Trigger:**
        1. Store has 10 units of Product A (minimum: 50, max: 200)
        2. System detects stock below minimum
        3. Auto-creates stock request for 190 units (to reach max)
        4. Request sent to DC (parent OU in hierarchy)
        5. DC approves and transfers stock
        
        **Manual Trigger:**
        1. Store manager opens "Run Replenishment" wizard
        2. System shows all products below minimum
        3. Manager selects products to replenish
        4. System creates stock requests to parent OU
        
        Dependencies:
        ------------
        - stock_request (OCA)
        - stock_operating_unit (OCA)
        - operating_unit (OCA)
        - weha_operating_unit_hierarchy
        - weha_stock_request_operating_unit
    """,
    'author': 'Weha',
    'website': 'https://weha-id.com',
    'depends': [
        'stock',
        'stock_request',
        'stock_operating_unit',
        'operating_unit',
        'weha_operating_unit_hierarchy',
        'weha_stock_request_operating_unit',
    ],
    'data': [
        'security/ir.model.access.csv',
        'data/ir_cron_data.xml',
        'views/stock_replenishment_rule_views.xml',
        'views/stock_request_views.xml',
        'wizard/stock_replenishment_wizard_views.xml',
    ],
    'demo': [
        'data/demo_data.xml',
    ],
    'installable': True,
    'auto_install': False,
    'application': False,
    'license': 'LGPL-3',
}
