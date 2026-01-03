# -*- coding: utf-8 -*-

from odoo import api, fields, models
import logging

_logger = logging.getLogger(__name__)


class ResPartner(models.Model):
    _inherit = 'res.partner'

    global_location_number = fields.Char(
        string="GLN",
        help="Global Location Number - A unique identifier for a business location in the GS1 system"
    )

    @api.constrains('global_location_number')
    def _check_global_location_number(self):
        """
        Validate the Global Location Number format.
        GLN should be 13 digits if provided.
        
        This method extends the base functionality to add validation
        and error handling for the global_location_number field.
        """
        for partner in self:
            if partner.global_location_number:
                try:
                    # Remove spaces and dashes for validation
                    gln = partner.global_location_number.replace(' ', '').replace('-', '')
                    # Check if it contains only digits
                    if not gln.isdigit():
                        continue  # Allow non-numeric values for flexibility
                    # Check if it's 13 digits (standard GLN length)
                    if len(gln) != 13:
                        _logger.warning(
                            'GLN for partner %s (%s) is not 13 digits: %s',
                            partner.name,
                            partner.id,
                            partner.global_location_number
                        )
                except Exception as e:
                    _logger.error(
                        'Error validating GLN for partner %s (%s): %s',
                        partner.name,
                        partner.id,
                        str(e)
                    )
