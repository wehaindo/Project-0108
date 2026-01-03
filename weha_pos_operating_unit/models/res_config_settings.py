# -*- coding: utf-8 -*-

from odoo import api, fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    pos_operating_unit_id = fields.Many2one(
        'operating.unit',
        related='pos_config_id.operating_unit_id',
        string='Operating Unit',
        readonly=False,
        help='Operating Unit for this Point of Sale'
    )
