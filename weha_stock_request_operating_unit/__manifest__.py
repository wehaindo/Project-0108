# -*- coding: utf-8 -*-
# Copyright 2026 Weha
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl-3.0).

{
    'name': 'Stock Request Operating Unit',
    'version': '18.0.1.0.0',
    'category': 'Warehouse Management',
    'summary': 'Add Operating Unit support for Stock Request',
    'description': """
        Stock Request Operating Unit
        =============================
        This module adds operating unit functionality to Stock Request.
        All stock moves and pickings created from stock requests will be assigned to the operating unit.
        
        Features:
        ---------
        * Add operating unit field to Stock Request
        * Add operating unit field to Stock Request Order
        * Automatically assign operating unit to stock moves
        * Automatically assign operating unit to stock pickings
        * Operating unit based access control
        * Filter stock requests by operating unit
        
        Dependencies:
        ------------
        This module requires OCA's Operating Unit modules:
        - operating_unit: Base operating unit module
        - stock_operating_unit: Operating unit for stock
        
        Install these modules first before installing this module.
    """,
    'author': 'Weha',
    'website': 'https://weha-id.com',
    'depends': [
        'stock_request',  # OCA Stock Request module
        'operating_unit',  # OCA Operating Unit module
        'stock_operating_unit',  # OCA Stock Operating Unit module
    ],
    'data': [
        'security/stock_request_security.xml',
        'views/stock_request_views.xml',
        'views/stock_request_order_views.xml',
    ],
    'installable': True,
    'auto_install': False,
    'license': 'LGPL-3',
}
