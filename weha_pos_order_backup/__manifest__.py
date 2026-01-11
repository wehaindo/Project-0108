# -*- coding: utf-8 -*-
{
    'name': 'POS Order Backup',
    'version': '18.0.2.0.0',
    'category': 'Point of Sale',
    'summary': 'Advanced backup system for POS orders with batch import and analytics',
    'description': """
        POS Order Backup System
        =======================
        - Automatically backup validated orders to IndexedDB and server
        - Separate backup table (pos.order.backup) for easy management
        - Structured fields for better searching and reporting
        - Batch import wizard for multiple orders
        - Automatic duplicate detection
        - Missing order detection and recovery
        - Dashboard with statistics and analytics
        - Data retention and cleanup tools
        - Enhanced UI with filters and bulk actions
        
        Features:
        ---------
        * Local backup to IndexedDB
        * Server sync to pos.order.backup table
        * Batch import missing orders
        * Smart duplicate detection
        * Visual dashboard with graphs and pivots
        * Advanced search filters
        * Automatic cleanup of old backups
        * Import tracking and error handling
    """,
    'author': 'Weha',
    'website': 'https://weha-id.com',
    'license': 'LGPL-3',
    'depends': ['point_of_sale'],
    'data': [
        'security/ir.model.access.csv',
        'data/ir_cron_data.xml',
        'views/pos_order_backup_views.xml',
        'views/pos_order_backup_dashboard.xml',
        # 'views/pos_data_log_views.xml',
        'wizard/pos_order_backup_import_wizard_views.xml',
        'wizard/pos_order_backup_cleanup_wizard_views.xml',
    ],
    'assets': {
        'point_of_sale._assets_pos': [
            'weha_pos_order_backup/static/src/app/order_backup_storage.js',
            'weha_pos_order_backup/static/src/app/receipt_utils.js',
            'weha_pos_order_backup/static/src/app/models.js',
        ],
    },
    'installable': True,
    'auto_install': False,
    'application': False,
}