# -*- coding: utf-8 -*-

from odoo import api, models, tools
from functools import lru_cache
import logging

_logger = logging.getLogger(__name__)


class ProductProduct(models.Model):
    _inherit = 'product.product'
    
    @api.model
    @tools.ormcache('product_id', 'pricelist_id')
    def _get_cached_product_price(self, product_id, pricelist_id=None):
        """
        Cache product prices to improve label printing performance
        """
        product = self.browse(product_id)
        if pricelist_id:
            pricelist = self.env['product.pricelist'].browse(pricelist_id)
            return pricelist._get_product_price(product, 1.0)
        return product.list_price
    
    def get_label_data_batch(self, product_ids):
        """
        Fetch label data for multiple products efficiently
        
        :param product_ids: List of product IDs
        :return: Dictionary with product data optimized for label printing
        """
        products = self.browse(product_ids)
        
        # Prefetch all necessary fields at once
        products.read([
            'id', 'name', 'default_code', 'barcode', 
            'list_price', 'currency_id', 'uom_id'
        ])
        
        result = {}
        for product in products:
            result[product.id] = {
                'name': product.name,
                'default_code': product.default_code or '',
                'barcode': product.barcode or '',
                'price': product.list_price,
                'currency': product.currency_id.symbol,
                'uom': product.uom_id.name,
            }
        
        return result


class ProductTemplate(models.Model):
    _inherit = 'product.template'
    
    @api.model
    @tools.ormcache('template_id', 'pricelist_id')
    def _get_cached_template_price(self, template_id, pricelist_id=None):
        """
        Cache product template prices to improve label printing performance
        """
        template = self.browse(template_id)
        if pricelist_id:
            pricelist = self.env['product.pricelist'].browse(pricelist_id)
            return pricelist._get_product_price(template.product_variant_id, 1.0)
        return template.list_price
    
    def get_label_data_batch(self, template_ids):
        """
        Fetch label data for multiple product templates efficiently
        
        :param template_ids: List of product template IDs
        :return: Dictionary with product template data optimized for label printing
        """
        templates = self.browse(template_ids)
        
        # Prefetch all necessary fields at once
        templates.read([
            'id', 'name', 'default_code', 'barcode',
            'list_price', 'currency_id', 'uom_id'
        ])
        
        result = {}
        for template in templates:
            result[template.id] = {
                'name': template.name,
                'default_code': template.default_code or '',
                'barcode': template.barcode or '',
                'price': template.list_price,
                'currency': template.currency_id.symbol,
                'uom': template.uom_id.name,
            }
        
        return result
