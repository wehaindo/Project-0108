# -*- coding: utf-8 -*-
{
    'name': 'POS Access Right Base',
    'version': '18.0.1.0.0',
    'category': 'Point of Sale',
    'summary': 'PIN Authorization for POS Operations - Delete Line, Clear Order, Refund',
    'description': """
        POS Access Right Base
        =====================
        
        Features:
        ---------
        * PIN authorization for deleting order lines
        * PIN authorization for clearing all orders
        * PIN authorization for refund operations
        * Configure advance user per POS with PIN access
        * Security control for sensitive POS operations
    """,
    'author': 'Your Company',
    'website': 'https://www.yourcompany.com',
    'depends': ['point_of_sale', 'pos_hr'],
    'data': [
        'security/ir.model.access.csv',
        'views/pos_config_views.xml',
    ],
    'assets': {
        'point_of_sale._assets_pos': [
            'weha_pos_access_right_base/static/src/js/pin_popup.js',
            'weha_pos_access_right_base/static/src/js/pos_access_control.js',
            'weha_pos_access_right_base/static/src/js/ui_patches.js',
            'weha_pos_access_right_base/static/src/xml/pin_popup.xml',
            'weha_pos_access_right_base/static/src/xml/ui_patches.xml',
            'weha_pos_access_right_base/static/src/css/pos_access_right.css',
        ],
    },
    'installable': True,
    'application': False,
    'auto_install': False,
    'license': 'LGPL-3',
}
