# -*- coding: utf-8 -*-
{
    'name': 'POS Operating Unit',
    'version': '18.0.1.0.0',
    'category': 'Point of Sale',
    'summary': 'Add Operating Unit support for Point of Sale',
    'description': """
        POS Operating Unit
        ==================
        This module adds operating unit functionality to Point of Sale.
        All journal entries created from POS orders will be assigned to the operating unit.
        
        Features:
        ---------
        * Add operating unit field to POS Config
        * Add operating unit field to POS Session
        * Automatically assign operating unit to all journal entries from POS
        * Operating unit based access control
    """,
    'author': 'Weha',
    'website': 'https://weha-id.com',
    'depends': [
        'point_of_sale',
        'account',
        'operating_unit',  # OCA Operating Unit module
        'account_operating_unit',  # OCA Account Operating Unit module
    ],
    'data': [
        'security/pos_security.xml',
        'views/pos_config_views.xml',
        'views/pos_session_views.xml',
        'views/pos_order_views.xml',
        'views/res_config_settings_views.xml',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
    'license': 'LGPL-3',
}
