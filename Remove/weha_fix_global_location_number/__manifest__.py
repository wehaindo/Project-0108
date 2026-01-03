# -*- coding: utf-8 -*-
{
    'name': 'Fix Global Location Number',
    'version': '18.0.1.0.0',
    'category': 'Accounting',
    'summary': 'Fix global_location_number field error in res.partner',
    'description': """
        This module fixes errors related to the global_location_number field
        in res.partner model by ensuring it exists even when account_add_gln
        module is not installed or has issues.
    """,
    'author': 'Your Company',
    'website': 'https://www.yourcompany.com',
    'depends': ['base'],
    'data': [],
    'installable': True,
    'application': False,
    'auto_install': False,
    'license': 'LGPL-3',
}
