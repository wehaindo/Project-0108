# -*- coding: utf-8 -*-
# © 2025 ehuerta _at_ ixer.mx
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl-3.0.html).

from odoo import models, api


class ProductMultiUomCleanup(models.AbstractModel):
    """Cleanup utility for removing duplicate multi-UOM price records."""
    _name = 'product.multi.uom.price.cleanup'
    _description = 'Multi-UOM Price Cleanup Utility'

    @api.model
    def cleanup_duplicate_prices(self):
        """
        Remove duplicate product.multi.uom.price records.
        Keeps the record with the highest ID (most recent) for each unique combination.
        
        Can be called from:
        - Python code: self.env['product.multi.uom.price.cleanup'].cleanup_duplicate_prices()
        - XML-RPC or command line
        """
        ProductMultiUom = self.env['product.multi.uom.price']
        
        # Find all records
        all_prices = ProductMultiUom.search([])
        
        # Group by unique key
        seen_keys = {}
        duplicates_to_remove = []
        
        for price in all_prices:
            key = (
                price.product_id.id,
                price.uom_id.id,
                price.operating_unit_id.id if price.operating_unit_id else False
            )
            
            if key in seen_keys:
                # We have a duplicate - keep the one with higher ID (more recent)
                existing = seen_keys[key]
                if price.id > existing.id:
                    # Keep current, remove existing
                    duplicates_to_remove.append(existing.id)
                    seen_keys[key] = price
                else:
                    # Keep existing, remove current
                    duplicates_to_remove.append(price.id)
            else:
                seen_keys[key] = price
        
        if duplicates_to_remove:
            # Remove duplicates
            ProductMultiUom.browse(duplicates_to_remove).unlink()
            return {
                'removed': len(duplicates_to_remove),
                'message': f'Removed {len(duplicates_to_remove)} duplicate price records.'
            }
        else:
            return {
                'removed': 0,
                'message': 'No duplicate price records found.'
            }

    @api.model
    def cleanup_template_duplicate_prices(self):
        """
        Remove duplicate product.tmpl.multi.uom.price records.
        Keeps the record with the highest ID (most recent) for each unique combination.
        """
        ProductTmplMultiUom = self.env['product.tmpl.multi.uom.price']
        
        # Find all records
        all_prices = ProductTmplMultiUom.search([])
        
        # Group by unique key
        seen_keys = {}
        duplicates_to_remove = []
        
        for price in all_prices:
            key = (
                price.product_tmpl_id.id,
                price.uom_id.id,
                price.operating_unit_id.id if price.operating_unit_id else False
            )
            
            if key in seen_keys:
                # We have a duplicate - keep the one with higher ID (more recent)
                existing = seen_keys[key]
                if price.id > existing.id:
                    # Keep current, remove existing
                    duplicates_to_remove.append(existing.id)
                    seen_keys[key] = price
                else:
                    # Keep existing, remove current
                    duplicates_to_remove.append(price.id)
            else:
                seen_keys[key] = price
        
        if duplicates_to_remove:
            # Remove duplicates
            ProductTmplMultiUom.browse(duplicates_to_remove).unlink()
            return {
                'removed': len(duplicates_to_remove),
                'message': f'Removed {len(duplicates_to_remove)} duplicate template price records.'
            }
        else:
            return {
                'removed': 0,
                'message': 'No duplicate template price records found.'
            }
