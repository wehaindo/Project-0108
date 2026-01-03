# -*- coding: utf-8 -*-
{
    'name': 'POS Order Backup',
    'version': '18.0.1.0.0',
    'category': 'Point of Sale',
    'summary': 'Backup POS orders to IndexedDB and sync to server',
    'description': """
        POS Order Backup System
        =======================
        - Automatically backup validated orders to IndexedDB
        - Sync backup data to server (pos.data.log table)
        - Import missing orders from backup if needed
        - Prevent data loss in case of network issues
    """,
    'author': 'Weha',
    'website': 'https://weha-id.com',
    'license': 'LGPL-3',
    'depends': ['point_of_sale'],
    'data': [
        'security/ir.model.access.csv',
        'views/pos_data_log_views.xml',
    ],
    'assets': {
        'point_of_sale._assets_pos': [
            'weha_pos_order_backup/static/src/app/order_backup_storage.js',
            'weha_pos_order_backup/static/src/app/models.js',
        ],
    },
    'installable': True,
    'auto_install': False,
    'application': False,
}
