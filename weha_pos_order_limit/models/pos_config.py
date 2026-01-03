# -*- coding: utf-8 -*-

from odoo import models, fields


class PosConfig(models.Model):
    _inherit = 'pos.config'

    hide_add_order_button = fields.Boolean(
        string='Hide Add Order Button',
        default=False,
        help='Hide the Add Order button in the POS interface'
    )
    
    enable_order_limit = fields.Boolean(
        string='Enable Order Limit',
        default=False,
        help='Enable limitation on number of orders that can be created'
    )
    
    max_orders = fields.Integer(
        string='Maximum Orders',
        default=10,
        help='Maximum number of orders that can be created in a single session'
    )
