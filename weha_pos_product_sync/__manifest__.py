{
    'name': 'Weha POS Product Sync - Fast Loading',
    'version': '18.0.1.0.0',
    'category': 'Point of Sale',
    'summary': 'Optimize POS product loading with pagination and caching',
    'description': """
        Fast POS Product Loading
        ========================
        This module optimizes product loading in Odoo 18 POS by:
        * Implementing pagination for large product catalogs
        * Reducing data payload by loading only essential fields
        * Caching product data to minimize database queries
        * Loading products on-demand when needed
        * Improving initial POS load time significantly
    """,
    'author': 'Weha',
    'website': 'https://weha-id.com',
    'license': 'LGPL-3',
    'depends': ['point_of_sale', 'product'],
    'data': [
        'security/ir.model.access.csv',
        'views/res_config_settings_views.xml',
        'wizard/product_generator_wizard_views.xml',
    ],
    'assets': {
        'point_of_sale._assets_pos': [
            'weha_pos_product_sync/static/src/app/product_storage.js',
            'weha_pos_product_sync/static/src/app/models.js',
            # 'weha_pos_product_sync/static/src/app/product_screen.js',
            'weha_pos_product_sync/static/src/app/sync_button.js',
            'weha_pos_product_sync/static/src/app/sync_button.xml',
            'weha_pos_product_sync/static/src/app/sync_button.scss',
            'weha_pos_product_sync/static/src/app/navbar_patch.js',
            'weha_pos_product_sync/static/src/app/navbar_patch.xml',
        ],
    },
    'installable': True,
    'auto_install': False,
    'application': False,
}
