# -*- coding: utf-8 -*-

from odoo import api, models
from odoo.fields import SQL


class ResPartnerBank(models.Model):
    _inherit = 'res.partner.bank'

    @api.depends('acc_number')
    def _compute_duplicate_bank_partner_ids(self):
        """
        Override to fix potential errors in duplicate_bank_partner_ids computation.
        This method handles edge cases that might cause the original computation to fail.
        """
        if not self.ids:
            # Handle empty recordset
            for bank in self:
                bank.duplicate_bank_partner_ids = False
            return

        try:
            # Execute the SQL query with proper error handling
            id2duplicates = dict(self.env.execute_query(SQL(
                """
                    SELECT this.id,
                           ARRAY_AGG(other.partner_id)
                      FROM res_partner_bank this
                 LEFT JOIN res_partner_bank other ON this.acc_number = other.acc_number
                                                 AND this.id != other.id
                                                 AND other.active = TRUE
                     WHERE this.id = ANY(%(ids)s)
                       AND other.partner_id IS NOT NULL
                       AND this.active = TRUE
                       AND (
                            ((this.company_id = other.company_id) OR (this.company_id IS NULL AND other.company_id IS NULL))
                            OR
                            other.company_id IS NULL
                        )
                  GROUP BY this.id
                """,
                ids=self.ids,
            )))
            
            # Assign the computed values
            for bank in self:
                # Use _origin.id to handle new records properly
                partner_ids = id2duplicates.get(bank._origin.id)
                if partner_ids:
                    # Filter out None values from the array and browse
                    valid_partner_ids = [pid for pid in partner_ids if pid is not None]
                    bank.duplicate_bank_partner_ids = self.env['res.partner'].browse(valid_partner_ids)
                else:
                    bank.duplicate_bank_partner_ids = False
                    
        except Exception as e:
            # Log the error and set empty values to prevent crashes
            import logging
            _logger = logging.getLogger(__name__)
            _logger.warning(
                'Error computing duplicate_bank_partner_ids for res.partner.bank records %s: %s',
                self.ids,
                str(e)
            )
            # Set all records to empty to prevent UI errors
            for bank in self:
                bank.duplicate_bank_partner_ids = False
