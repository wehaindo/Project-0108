# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import _, api, fields, models
from odoo.exceptions import UserError
from collections import defaultdict
import logging

_logger = logging.getLogger(__name__)


class ProductLabelLayoutEnhanced(models.TransientModel):
    _inherit = 'product.label.layout'
    
    # Override print_format to add 3x7 option
    print_format = fields.Selection(
        selection_add=[
            ('3x7xprice', '3 x 7 with price'),
            ('2x7xprice_logo', '2 x 7 with price and logo'),
            ('3x7xprice_logo', '3 x 7 with price and logo'),
            ('4x7xprice_logo', '4 x 7 with price and logo'),
            ('4x12xprice_logo', '4 x 12 with price and logo'),
        ],
        ondelete={
            '3x7xprice': 'set default',
            '2x7xprice_logo': 'set default',
            '3x7xprice_logo': 'set default',
            '4x7xprice_logo': 'set default',
            '4x12xprice_logo': 'set default',
        }
    )
    
    # Additional fields for enhanced functionality
    use_batch_processing = fields.Boolean(
        string='Use Batch Processing',
        default=True,
        help='Enable batch processing for better performance with large datasets'
    )
    batch_size = fields.Integer(
        string='Batch Size',
        default=100,
        help='Number of labels to process in each batch'
    )
    enable_caching = fields.Boolean(
        string='Enable Caching',
        default=True,
        help='Cache frequently used data to improve performance'
    )
    
    def _prepare_report_data(self):
        """
        Override to optimize data preparation with:
        - Prefetching related fields
        - Batch processing
        - Efficient data structure
        """
        self.ensure_one()
        
        # Determine XML ID for the report format
        if self.print_format == 'dymo':
            xml_id = 'product.report_product_template_label_dymo'
        elif 'x' in self.print_format:
            # Extract dimensions from format (e.g., '3x7xprice' -> 3, 7)
            # Check if logo version
            if '_logo' in self.print_format:
                xml_id = 'weha_product_print_label.report_product_template_label_%sx%s_logo' % \
                         (self.columns, self.rows)
            else:
                xml_id = 'weha_product_print_label.report_product_template_label_%sx%s' % \
                         (self.columns, self.rows)
            if 'xprice' not in self.print_format:
                xml_id += '_noprice'
        else:
            xml_id = ''
        
        active_model = ''
        products = []
        
        # Optimize product retrieval with prefetching
        if self.product_tmpl_ids:
            # Prefetch related fields to minimize queries
            fields_to_read = ['name', 'barcode', 'default_code']
            if 'xprice' in self.print_format:
                fields_to_read.extend(['list_price', 'currency_id'])
            # Trigger prefetch by reading fields
            self.product_tmpl_ids.read(fields_to_read)
            products = self.product_tmpl_ids.ids
            active_model = 'product.template'
            
        elif self.product_ids:
            # Prefetch related fields
            fields_to_read = ['name', 'barcode', 'default_code']
            if 'xprice' in self.print_format:
                fields_to_read.extend(['list_price', 'currency_id'])
            # Trigger prefetch by reading fields
            self.product_ids.read(fields_to_read)
            products = self.product_ids.ids
            active_model = 'product.product'
        else:
            raise UserError(_(
                "No product to print, if the product is archived "
                "please unarchive it before printing its label."
            ))
        
        # Build optimized data structure
        data = {
            'active_model': active_model,
            'quantity_by_product': {p: self.custom_quantity for p in products},
            'layout_wizard': self.id,
            'price_included': 'xprice' in self.print_format,
            'use_batch_processing': self.use_batch_processing,
            'batch_size': self.batch_size,
            'enable_caching': self.enable_caching,
        }
        
        return xml_id, data
    
    def process(self):
        """
        Override to add performance monitoring and optimized processing
        """
        self.ensure_one()
        
        try:
            xml_id, data = self._prepare_report_data()
            
            if not xml_id:
                raise UserError(_(
                    'Unable to find report template for %s format',
                    self.print_format
                ))
            
            # Generate report - pass None as first param, products in data dict
            report_action = self.env.ref(xml_id).report_action(
                None, 
                data=data, 
                config=False
            )
            
            # Update action with enhanced settings
            report_action.update({
                'close_on_report_download': True,
            })
            
            _logger.info(
                'Product label report generated for %d products using format %s',
                len(data['quantity_by_product']),
                self.print_format
            )
            
            return report_action
            
        except Exception as e:
            _logger.error('Error generating product labels: %s', str(e))
            raise
    
    @api.model
    def _get_optimized_product_data(self, product_ids, model_name):
        """
        Helper method to fetch product data efficiently in batch
        
        :param product_ids: List of product IDs
        :param model_name: Model name ('product.product' or 'product.template')
        :return: Dictionary with optimized product data
        """
        Product = self.env[model_name]
        
        # Fetch all products in one query with prefetching
        products = Product.browse(product_ids)
        
        # Prefetch commonly used fields using read
        fields_to_read = ['name', 'barcode', 'default_code', 'list_price', 'currency_id']
        products.read(fields_to_read)
        
        # Build optimized data dictionary
        product_data = {}
        for product in products:
            product_data[product.id] = {
                'name': product.name,
                'barcode': product.barcode or '',
                'default_code': product.default_code or '',
                'list_price': product.list_price,
            }
        
        return product_data
