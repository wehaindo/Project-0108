from odoo import models, api
import logging

_logger = logging.getLogger(__name__)


class ProductProduct(models.Model):
    _inherit = 'product.product'

    @api.model
    def _load_pos_data(self, data):
        """Override to return empty data when local storage is enabled"""
        # Get the session from context or response data
        session_data = data.get('pos.session', {}).get('data', [{}])[0]
        config_id = session_data.get('config_id')
        
        if config_id:
            config = self.env['pos.config'].browse(config_id[0] if isinstance(config_id, (list, tuple)) else config_id)
            if config.enable_local_product_storage:
                _logger.info('ProductProduct: Skipping data load - Local storage enabled')
                return {
                    'data': [],
                    'fields': self._load_pos_data_fields(config.id)
                }
        
        return super()._load_pos_data(data)


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    @api.model
    def _load_pos_data(self, data):
        """Override to return empty data when local storage is enabled"""
        session_data = data.get('pos.session', {}).get('data', [{}])[0]
        config_id = session_data.get('config_id')
        
        if config_id:
            config = self.env['pos.config'].browse(config_id[0] if isinstance(config_id, (list, tuple)) else config_id)
            if config.enable_local_product_storage:
                _logger.info('ProductTemplate: Skipping data load - Local storage enabled')
                return {
                    'data': [],
                    'fields': self._load_pos_data_fields(config.id)
                }
        
        return super()._load_pos_data(data)


class ProductPricelist(models.Model):
    _inherit = 'product.pricelist'

    @api.model
    def _load_pos_data(self, data):
        """Override to return empty data when local storage is enabled"""
        session_data = data.get('pos.session', {}).get('data', [{}])[0]
        config_id = session_data.get('config_id')
        
        if config_id:
            config = self.env['pos.config'].browse(config_id[0] if isinstance(config_id, (list, tuple)) else config_id)
            if config.enable_local_product_storage:
                _logger.info('ProductPricelist: Skipping data load - Local storage enabled')
                return {
                    'data': [],
                    'fields': self._load_pos_data_fields(config.id)
                }
        
        return super()._load_pos_data(data)


class ProductPricelistItem(models.Model):
    _inherit = 'product.pricelist.item'

    @api.model
    def _load_pos_data(self, data):
        """Override to return empty data when local storage is enabled"""
        session_data = data.get('pos.session', {}).get('data', [{}])[0]
        config_id = session_data.get('config_id')
        
        if config_id:
            config = self.env['pos.config'].browse(config_id[0] if isinstance(config_id, (list, tuple)) else config_id)
            if config.enable_local_product_storage:
                _logger.info('ProductPricelistItem: Skipping data load - Local storage enabled')
                return {
                    'data': [],
                    'fields': self._load_pos_data_fields(config.id)
                }
        
        return super()._load_pos_data(data)


class ProductCategory(models.Model):
    _inherit = 'product.category'

    @api.model
    def _load_pos_data(self, data):
        """Override to return empty data when local storage is enabled"""
        session_data = data.get('pos.session', {}).get('data', [{}])[0]
        config_id = session_data.get('config_id')
        
        if config_id:
            config = self.env['pos.config'].browse(config_id[0] if isinstance(config_id, (list, tuple)) else config_id)
            if config.enable_local_product_storage:
                _logger.info('ProductCategory: Skipping data load - Local storage enabled')
                return {
                    'data': [],
                    'fields': self._load_pos_data_fields(config.id)
                }
        
        return super()._load_pos_data(data)


class ProductPackaging(models.Model):
    _inherit = 'product.packaging'

    @api.model
    def _load_pos_data(self, data):
        """Override to return empty data when local storage is enabled"""
        session_data = data.get('pos.session', {}).get('data', [{}])[0]
        config_id = session_data.get('config_id')
        
        if config_id:
            config = self.env['pos.config'].browse(config_id[0] if isinstance(config_id, (list, tuple)) else config_id)
            if config.enable_local_product_storage:
                _logger.info('ProductPackaging: Skipping data load - Local storage enabled')
                return {
                    'data': [],
                    'fields': self._load_pos_data_fields(config.id)
                }
        
        return super()._load_pos_data(data)
