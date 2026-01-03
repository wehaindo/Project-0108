# -*- coding: utf-8 -*-

from odoo import models, fields


class PosConfig(models.Model):
    _inherit = 'pos.config'
    
    require_pin_delete_orderline = fields.Boolean(
        string='Require PIN to Delete Order Line',
        default=True,
        help='Require advanced employee PIN to delete order lines'
    )
    
    require_pin_clear_order = fields.Boolean(
        string='Require PIN to Clear Order',
        default=True,
        help='Require advanced employee PIN to clear all order lines'
    )
    
    require_pin_refund = fields.Boolean(
        string='Require PIN for Refund',
        default=True,
        help='Require advanced employee PIN for refund operations'
    )
