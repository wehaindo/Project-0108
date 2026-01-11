# -*- coding: utf-8 -*-
{
    'name': 'POS Log Base',
    'version': '17.0.1.0.0',
    'category': 'Point of Sale',
    'summary': 'Base logging system for POS operations with local storage and server sync',
    'description': """
POS Log Base Module
===================
This module provides a comprehensive logging system for Point of Sale operations.

Features:
---------
* Log cashier login/logout events
* Log POS session events
* Extensible event types for custom logging
* Local storage with server synchronization
* Track sync status of each log entry
* JSON data field for flexible event details
* Search and filter logs by user, session, date, event type
* Base module that can be inherited by other modules

Use Cases:
----------
* Audit trail for cashier activities
* Session management tracking
* Compliance and reporting
* Troubleshooting POS operations
* Performance monitoring

Technical:
----------
* Stores logs in pos.log model
* Automatic timestamp recording
* Sync status tracking (synced/pending)
* Extendable event types via selection field
* JSON field for flexible data storage
    """,
    'author': 'Weha',
    'website': '',
    'depends': [
        'point_of_sale',
        'base',
    ],
    'data': [
        'security/ir.model.access.csv',
        'views/pos_log_views.xml',
    ],
    'assets': {
        'point_of_sale._assets_pos': [
            'weha_pos_log/static/src/js/pos_log.js',
        ],
    },
    'installable': True,
    'application': False,
    'auto_install': False,
    'license': 'LGPL-3',
}
