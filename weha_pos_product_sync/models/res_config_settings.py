from odoo import fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    pos_fast_product_loading = fields.Boolean(
        related='pos_config_id.fast_product_loading',
        readonly=False,
        string='Fast Product Loading'
    )
    
    pos_enable_local_product_storage = fields.Boolean(
        related='pos_config_id.enable_local_product_storage',
        readonly=False,
        string='Enable Local Product Storage'
    )
    
    pos_product_load_limit = fields.Integer(
        related='pos_config_id.product_load_limit',
        readonly=False,
        string='Initial Product Load Limit'
    )
    
    pos_limit_product_categories = fields.Boolean(
        related='pos_config_id.limit_product_categories',
        readonly=False,
        string='Limit to Specific Categories'
    )
    
    pos_category_ids = fields.Many2many(
        related='pos_config_id.pos_category_ids',
        readonly=False,
        string='POS Categories'
    )
