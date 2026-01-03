# -*- coding: utf-8 -*-
{
    'name': 'Fix Duplicate Bank Partner IDs',
    'version': '18.0.1.0.0',
    'category': 'Accounting',
    'summary': 'Fix duplicate_bank_partner_ids computation error in res.partner.bank',
    'description': """
        This module fixes the duplicate_bank_partner_ids computation error
        in res.partner.bank model by properly handling edge cases in the SQL query.
    """,
    'author': 'Your Company',
    'website': 'https://www.yourcompany.com',
    'depends': ['account'],
    'data': [],
    'installable': True,
    'application': False,
    'auto_install': False,
    'license': 'LGPL-3',
}
