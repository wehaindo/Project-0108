# -*- coding: utf-8 -*-
from odoo import fields, models, api, _


class PosConfig(models.Model):
    _inherit = 'pos.config'

    operating_unit_id = fields.Many2one(
        'operating.unit',
        string='Operating Unit',
        required=True,
        domain="[('company_id', '=', company_id)]",
        help='Operating unit for this POS. All journal entries will be assigned to this operating unit.'
    )
    
    @api.onchange('company_id')
    def _onchange_company_id_operating_unit(self):
        """Reset operating unit when company changes"""
        if self.operating_unit_id and self.operating_unit_id.company_id != self.company_id:
            self.operating_unit_id = False
