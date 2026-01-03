# -*- coding: utf-8 -*-

from odoo import api, fields, models


class ResPartner(models.Model):
    _inherit = 'res.partner'

    @api.depends('bank_ids.acc_number')
    def _compute_duplicate_bank_partner_ids(self):
        """
        Compute partners that share bank accounts with this partner.
        This aggregates all duplicate partners from all bank accounts.
        """
        for partner in self:
            duplicate_partners = self.env['res.partner']
            for bank in partner.bank_ids:
                duplicate_partners |= bank.duplicate_bank_partner_ids
            partner.duplicate_bank_partner_ids = duplicate_partners

    duplicate_bank_partner_ids = fields.Many2many(
        'res.partner',
        compute='_compute_duplicate_bank_partner_ids',
        string='Partners with Duplicate Bank Accounts',
        help='Partners that share the same bank account numbers'
    )
