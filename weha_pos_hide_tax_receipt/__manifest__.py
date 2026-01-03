# -*- coding: utf-8 -*-
{
    'name': 'POS Hide Tax on Receipt',
    'version': '18.0.1.0.0',
    'category': 'Point of Sale',
    'summary': 'Hide tax information on POS receipts',
    'description': """
        Hide Tax Information on POS Receipt
        ====================================
        
        This module hides tax information from POS receipts:
        - Hides tax lines
        - Hides tax details
        - Shows only total amount
    """,
    'author': 'Your Company',
    'website': 'https://www.yourcompany.com',
    'depends': ['point_of_sale'],
    'data': [
        'views/pos_receipt_template.xml',
    ],
    'assets': {
        'point_of_sale._assets_pos': [
            'weha_pos_hide_tax_receipt/static/src/**/*',
        ],
    },
    'installable': True,
    'auto_install': False,
    'application': False,
    'license': 'LGPL-3',
}
