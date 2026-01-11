# -*- coding: utf-8 -*-
from odoo import models, fields, api


class ProductTemplate(models.Model):
    _inherit = 'product.template'
    
    rfid_tag_ids = fields.One2many(
        'product.rfid.tag',
        'product_tmpl_id',
        string='RFID Tags',
        help='RFID tags assigned to this product. Each physical item has its own unique tag.'
    )
    
    rfid_tag_count = fields.Integer(
        string='RFID Tags Count',
        compute='_compute_rfid_tag_count',
        store=True
    )
    
    @api.depends('rfid_tag_ids')
    def _compute_rfid_tag_count(self):
        for record in self:
            record.rfid_tag_count = len(record.rfid_tag_ids)


class ProductProduct(models.Model):
    _inherit = 'product.product'
    
    rfid_tag_ids = fields.One2many(
        'product.rfid.tag',
        'product_id',
        string='RFID Tags',
        help='RFID tags assigned to this product variant'
    )
    
    rfid_tag_count = fields.Integer(
        string='RFID Tags Count',
        compute='_compute_rfid_tag_count',
        store=True
    )
    
    @api.depends('rfid_tag_ids')
    def _compute_rfid_tag_count(self):
        for record in self:
            record.rfid_tag_count = len(record.rfid_tag_ids)
