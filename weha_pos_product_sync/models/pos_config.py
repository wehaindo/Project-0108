from odoo import models, fields


class PosConfig(models.Model):
    _inherit = 'pos.config'

    fast_product_loading = fields.Boolean(
        string='Fast Product Loading',
        default=True,
        help='Enable optimized product loading with pagination and reduced data payload'
    )
    
    enable_local_product_storage = fields.Boolean(
        string='Enable Local Product Storage',
        default=True,
        help='Store products locally in browser for offline-first loading'
    )
    
    product_load_limit = fields.Integer(
        string='Initial Product Load Limit',
        default=100,
        help='Number of products to load initially (more products load on-demand)'
    )
    
    limit_product_categories = fields.Boolean(
        string='Limit to Specific Categories',
        default=False,
        help='Load only products from selected POS categories'
    )
    
    pos_category_ids = fields.Many2many(
        'pos.category',
        'pos_config_category_sync_rel',
        'pos_config_id',
        'pos_category_id',
        string='POS Categories',
        help='Products from these categories will be loaded initially'
    )

