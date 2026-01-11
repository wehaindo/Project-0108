# -*- coding: utf-8 -*-
{
    'name': 'Weha POS RFID Tag Reader',
    'version': '18.0.1.0.0',
    'category': 'Point of Sale',
    'summary': 'Read RFID tags via websocket for automatic product selection in POS',
    'description': """
        POS RFID Tag Reader
        ===================
        This module enables reading RFID tags through a local websocket connection
        for automatic product selection in Point of Sale.
        
        Features:
        ---------
        * Connect to local websocket server for RFID reading
        * Each RFID tag uniquely identifies a physical product item
        * Automatically add products to cart when RFID is detected
        * Real-time RFID scanning in POS
        * Manage RFID tag assignments in backend
        * Support for multiple RFID tags per product
        * **Track location of each RFID-tagged item**
        * **Location history tracking**
        * **Automatic location updates via stock moves**
        * **Integration with inventory/warehouse management**
        * Visual feedback for successful/failed tag reads
        * Configurable websocket connection settings
        
        Requirements:
        -------------
        * Local websocket server running on ws://localhost:8765 (configurable)
        * RFID reader hardware connected to websocket server
        
        Configuration:
        --------------
        1. Install a websocket server that reads from your RFID hardware
        2. Configure the websocket URL in POS settings
        3. Assign RFID tags to products in Product form
        4. Open POS and tags will be automatically detected
    """,
    'author': 'Weha',
    'website': 'https://weha-id.com',
    'license': 'LGPL-3',
    'depends': ['point_of_sale', 'product', 'stock'],
    'data': [
        'security/ir.model.access.csv',
        'views/product_rfid_tag_views.xml',
        'views/rfid_tag_location_history_views.xml',
        'views/stock_quant_views.xml',
        'views/product_template_views.xml',
        'views/res_config_settings_views.xml',
        'wizard/rfid_tag_wizard_views.xml',
    ],
    'assets': {
        'point_of_sale._assets_pos': [
            'weha_pos_rfid_tag/static/src/app/rfid_service.js',
            'weha_pos_rfid_tag/static/src/app/rfid_reader.js',
            'weha_pos_rfid_tag/static/src/app/rfid_reader.xml',
            'weha_pos_rfid_tag/static/src/app/rfid_reader.scss',
            'weha_pos_rfid_tag/static/src/app/product_screen_patch.js',
        ],
    },
    'installable': True,
    'auto_install': False,
    'application': False,
}
