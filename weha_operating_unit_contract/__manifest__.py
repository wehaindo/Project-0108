# -*- coding: utf-8 -*-
# Copyright 2026 Weha
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl-3.0).

{
    'name': 'Operating Unit Revenue Sharing Contract',
    'version': '18.0.3.0.0',
    'category': 'Accounting',
    'summary': 'Revenue Sharing with OU-Specific Rules, Effective Dates, and Optimized Aggregation',
    'description': """
        Operating Unit Revenue Sharing Contract
        ========================================
        
        This module manages revenue sharing contracts and calculations for 
        multi-level operating unit hierarchies.
        
        Key Features:
        ------------
        
        **1. Revenue Sharing Configuration**
        - Product category-based sharing rules
        - Product-specific sharing rules
        - Operating unit type-based rules
        - Configurable revenue sharing percentages per level
        - Support for multiple revenue sharing rules
        - **NEW v2.0:** Operating Unit-specific rules (global or location-specific)
        - **NEW v2.0:** Effective date ranges (contract start/end dates)
        - **NEW v2.0:** Contract renewal support (multiple rules with different dates)
        
        **2. Revenue Sharing from POS Orders**
        - Automatic revenue distribution across hierarchy levels
        - Monthly revenue sharing periods
        - Automatic calculation and validation
        - Smart rule selection based on OU, date, and product
        - **NEW v3.0:** Optimized aggregated entries (reduces data by 95%+)
        
        **3. Performance Optimization**
        - Entries aggregated by: Period + Source OU + Target OU + Rule
        - Eliminates per-order-line entries
        - Typical reduction: 10,000+ entries → 10-50 entries per month
        - Maintains accurate totals and statistics
        - Store → DC → HO revenue flow tracking
        
        **3. Accounting Integration**
        - Automatic journal entries for revenue sharing
        - Inter-OU accounting entries
        - Revenue tracking per operating unit
        
        **4. Reporting & Analytics**
        - Revenue sharing reports by OU
        - Parent-child revenue tracking
        - Commission calculations
        - Period-based analytics
        
        Business Flow Example:
        ---------------------
        
        Store sells product → Revenue = 1,000,000
        - Store keeps: 70% (700,000)
        - DC gets: 20% (200,000)
        - HO gets: 10% (100,000)
        
        Configuration:
        - Create Revenue Sharing Rules with percentages per OU type
        - System automatically creates monthly periods
        - POS orders are linked to periods
        - Calculate and validate revenue sharing per period
        - Post accounting entries
        
        Dependencies:
        ------------
        - operating_unit (OCA)
        - account_operating_unit (OCA)
        - point_of_sale
        - weha_operating_unit_hierarchy
        - weha_pos_operating_unit
    """,
    'author': 'Weha',
    'website': 'https://weha-id.com',
    'depends': [
        'operating_unit',
        'account_operating_unit',
        'point_of_sale',
        'weha_operating_unit_hierarchy',
        'weha_pos_operating_unit',
    ],
    'data': [
        'security/revenue_sharing_security.xml',
        'security/ir.model.access.csv',
        'wizard/revenue_sharing_diagnostic_views.xml',
        'views/revenue_sharing_rule_views.xml',
        'views/revenue_sharing_period_views.xml',
        'views/revenue_sharing_entry_views.xml',
        'views/menu_views.xml',
    ],
    'demo': [],
    'installable': True,
    'auto_install': False,
    'application': False,
    'license': 'LGPL-3',
}
