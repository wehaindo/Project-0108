# -*- coding: utf-8 -*-
{
    'name': 'POS Session Date Reminder',
    'version': '18.0.1.0.0',
    'category': 'Point of Sale',
    'summary': 'Warn users when POS session date is not current date',
    'description': """
        POS Session Date Reminder
        =========================
        
        This module shows a warning when opening POS if the session date 
        is not the same as the current date. Users will be reminded to 
        close the current session before continuing.
        
        Features:
        ---------
        * Checks session date vs current date on login screen
        * Shows warning dialog if dates don't match
        * Reminds users to close old sessions
    """,
    'author': 'Your Company',
    'website': 'https://www.yourcompany.com',
    'depends': [
        'pos_hr',
        'point_of_sale',
    ],
    'data': [
    ],
    'assets': {
        'point_of_sale._assets_pos': [
            'weha_pos_session_reminder/static/src/app/session_warning/session_warning.js',
            'weha_pos_session_reminder/static/src/app/session_warning/session_warning.xml',
            'weha_pos_session_reminder/static/src/app/session_warning/session_warning.scss',
        ],
    },
    'installable': True,
    'auto_install': False,
    'application': False,
    'license': 'LGPL-3',
}
