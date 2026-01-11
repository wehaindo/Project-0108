# -*- coding: utf-8 -*-
{
    'name': 'Weha Product Print Label - Enhanced',
    'version': '18.0.1.0.0',
    'category': 'Product',
    'summary': 'Enhanced product label printing with improved PDF generation performance',
    'description': """
        Enhanced Product Label Printing
        ================================
        
        This module extends the standard Odoo product label printing functionality with:
        * Optimized PDF generation for faster performance
        * Batch processing to reduce memory usage
        * Improved rendering efficiency
        * Caching mechanisms for repeated prints
        
        Performance Improvements:
        * Reduced database queries through prefetching
        * Optimized report data preparation
        * Efficient batch processing
        * Minimized redundant calculations
    """,
    'author': 'Weha',
    'depends': ['product', 'stock', 'barcodes'],
    'data': [
        'security/ir.model.access.csv',
        'wizard/product_label_layout_views.xml',
        'report/product_label_reports.xml',
        'report/product_label_templates.xml',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
    'license': 'LGPL-3',
}
