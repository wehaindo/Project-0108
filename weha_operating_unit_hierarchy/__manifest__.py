# -*- coding: utf-8 -*-
# Copyright 2026 Weha
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl-3.0).

{
    'name': 'Operating Unit Hierarchy',
    'version': '18.0.1.0.0',
    'category': 'Sales',
    'summary': 'Operating Unit Hierarchy Management (HO → DC → Store)',
    'description': """
        Operating Unit Hierarchy
        ========================
        
        This module manages operating unit hierarchy for multi-level business structures:
        - Head Office (HO) → Distribution Center (DC) → Store
        
        Key Features:
        ------------
        
        **1. Operating Unit Hierarchy**
        - Define parent-child relationships between operating units
        - Support multi-level hierarchy (HO → DC → Store)
        - Automatic hierarchy validation
        - Visual hierarchy tree view
        - Default source OU configuration
        
        **2. Operating Unit Types**
        - Pre-defined types: HO, DC, Store
        - Custom type creation
        - Type-based functionality
        
        **3. Stock Request Flow**
        - Store requests from DC
        - DC requests from HO or purchases from supplier
        - Automatic routing based on hierarchy
        - Stock availability checking at parent level
        - Purchase request generation when stock not available
        
        **4. Reporting & Analytics**
        - Hierarchy visualization
        - Stock request flow tracking
        - Parent-child relationship management
        
        Business Flow:
        -------------
        
        **Stock Request:**
        Store needs stock → Request to DC → DC checks stock:
        - If DC has stock → Transfer to Store
        - If DC no stock → DC requests from HO or purchases from supplier
        
        **Hierarchy Management:**
        - Define parent-child relationships
        - Configure default source OU for each OU
        - Automatic hierarchy validation
        - Get all parents/children methods
        
        Dependencies:
        ------------
        - operating_unit (OCA)
        - stock_request (OCA)
        - weha_stock_request_operating_unit
        
        Optional Modules:
        ----------------
        - weha_operating_unit_contract: Revenue sharing functionality
    """,
    'author': 'Weha',
    'website': 'https://weha-id.com',
    'depends': [
        'operating_unit',
        'stock_request',
        'weha_stock_request_operating_unit',
    ],
    'data': [
        'security/ir.model.access.csv',
        'views/operating_unit_type_views.xml',
        'views/operating_unit_views.xml',
        'views/hierarchy_tree_dashboard_action.xml',
    ],
    'assets': {
        'web.assets_backend': [
            'weha_operating_unit_hierarchy/static/src/components/hierarchy_tree/hierarchy_tree.js',
            'weha_operating_unit_hierarchy/static/src/components/hierarchy_tree/hierarchy_tree.xml',
            'weha_operating_unit_hierarchy/static/src/components/hierarchy_tree/hierarchy_tree.scss',
        ],
    },
    'demo': [
        'data/demo_data.xml',
    ],
    'installable': True,
    'auto_install': False,
    'application': True,
    'license': 'LGPL-3',
}
