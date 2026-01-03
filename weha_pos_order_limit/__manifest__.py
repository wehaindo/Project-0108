# -*- coding: utf-8 -*-
{
    'name': 'POS Order Limit',
    'version': '18.0.1.0.0',
    'category': 'Point of Sale',
    'summary': 'Hide/Show Add Order Button and Limit Order Creation in POS',
    'description': """
        POS Order Limit
        ===============
        
        Features:
        ---------
        * Hide or show the "Add Order" button in POS interface
        * Set maximum number of orders that can be created
        * Configure settings per POS session
    """,
    'author': 'Your Company',
    'website': 'https://www.yourcompany.com',
    'depends': ['point_of_sale'],
    'data': [
        'security/ir.model.access.csv',
        'views/pos_config_views.xml',
    ],
    'assets': {
        'point_of_sale._assets_pos': [
            'weha_pos_order_limit/static/src/js/pos_order_limit.js',
            'weha_pos_order_limit/static/src/xml/pos_order_limit.xml',
        ],
    },
    'installable': True,
    'application': False,
    'auto_install': False,
    'license': 'LGPL-3',
}
