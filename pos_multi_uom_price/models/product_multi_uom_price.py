# -*- coding: utf-8 -*-
# © 2025 ehuerta _at_ ixer.mx
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl-3.0.html).

import logging
from odoo import models, fields, api, _
from odoo.exceptions import ValidationError
from odoo.osv import expression

_logger = logging.getLogger(__name__)


class ProductTmplMultiUom(models.Model):
    _name = 'product.tmpl.multi.uom.price'
    _description = 'Product template multiple uom price'

    product_tmpl_id = fields.Many2one(
        'product.template',
        'Product Template',
        required=True,
        ondelete="cascade",
        readonly=True
    )
    operating_unit_id = fields.Many2one(
        'operating.unit',
        string='Operating Unit',
        required=False,
        ondelete="cascade",
        help='Leave empty to apply this price to all operating units. Set to apply this price only for specific operating unit.'
    )
    category_id = fields.Many2one(related='product_tmpl_id.uom_id.category_id', readonly=True)
    uom_id = fields.Many2one('uom.uom',
        string="Unit of Measure",
        domain="[('category_id', '=', category_id)]",
        required=True
    )
    price = fields.Float('Price',
        required=True,
        digits='Product Price'
    )

    @api.constrains('price')
    def _check_price(self):
        """Validate that price is not negative."""
        for rec in self:
            if rec.price < 0:
                raise ValidationError(_('Price cannot be negative.'))

    def _sync_price_to_variants(self):
        """Sync template UOM prices to all product variants."""
        ProductMultiUom = self.env['product.multi.uom.price']
        
        for rec in self:
            for variant in rec.product_tmpl_id.product_variant_ids:
                # Build domain to find existing price
                domain = [
                    ('product_id', '=', variant.id),
                    ('uom_id', '=', rec.uom_id.id),
                ]
                
                # Add operating unit to domain
                if rec.operating_unit_id:
                    domain.append(('operating_unit_id', '=', rec.operating_unit_id.id))
                else:
                    domain.append(('operating_unit_id', '=', False))
                
                # Search for existing price
                existing = ProductMultiUom.search(domain, limit=1)
                
                if existing:
                    # Update existing price if different
                    if existing.price != rec.price:
                        existing.price = rec.price
                else:
                    # Create new price record
                    vals = {
                        'product_id': variant.id,
                        'uom_id': rec.uom_id.id,
                        'price': rec.price,
                    }
                    # Only set operating_unit_id if it exists
                    if rec.operating_unit_id:
                        vals['operating_unit_id'] = rec.operating_unit_id.id
                    
                    ProductMultiUom.create(vals)

    @api.model_create_multi
    def create(self, vals_list):
        """Override create to clean operating_unit_id handling."""
        # Clean vals_list to handle operating_unit_id properly
        for vals in vals_list:
            if 'operating_unit_id' in vals and not vals['operating_unit_id']:
                # Remove the key if it's False to let it default to NULL
                vals.pop('operating_unit_id')
        
        records = super(ProductTmplMultiUom, self).create(vals_list)
        records._sync_price_to_variants()
        return records

    def write(self, vals):
        res = super().write(vals)
        self._sync_price_to_variants()
        return res

    _sql_constraints = [
        ('product_tmpl_uom_ou_uniq',
         'UNIQUE(product_tmpl_id, uom_id, operating_unit_id)',
         'Each Unit of Measure must be unique per product template and operating unit.')
    ]


class ProductMultiUom(models.Model):
    _name = 'product.multi.uom.price'
    _inherit = ['pos.load.mixin']
    _description = 'Product variant multiple uom price'

    product_id = fields.Many2one(
        'product.product',
        'Product variant',
        required=True,
        ondelete="cascade",
        readonly=True
    )
    operating_unit_id = fields.Many2one(
        'operating.unit',
        string='Operating Unit',
        required=False,
        ondelete="cascade",
        help='Leave empty to apply this price to all operating units. Set to apply this price only for specific operating unit.'
    )
    category_id = fields.Many2one(related='product_id.uom_id.category_id', readonly=True)
    uom_id = fields.Many2one('uom.uom',
        string="Unit of Measure",
        domain="[('category_id', '=', category_id)]",
        required=True
    )
    price = fields.Float('Price',
        required=True,
        digits='Product Price'
    )

    @api.constrains('price')
    def _check_price(self):
        """Validate that price is not negative."""
        for rec in self:
            if rec.price < 0:
                raise ValidationError(_('Price cannot be negative.'))

    @api.model_create_multi
    def create(self, vals_list):
        """Override create to prevent duplicates and clean operating_unit_id."""
        # Clean vals_list to handle operating_unit_id properly
        for vals in vals_list:
            if 'operating_unit_id' in vals and not vals['operating_unit_id']:
                # Remove the key if it's False to let it default to NULL
                vals.pop('operating_unit_id')
        
        # Check for existing records to prevent duplicates
        records_to_create = []
        existing_records = self.browse()
        
        for vals in vals_list:
            domain = [
                ('product_id', '=', vals['product_id']),
                ('uom_id', '=', vals['uom_id']),
            ]
            if vals.get('operating_unit_id'):
                domain.append(('operating_unit_id', '=', vals['operating_unit_id']))
            else:
                domain.append(('operating_unit_id', '=', False))
            
            existing = self.search(domain, limit=1)
            if existing:
                # Update existing record instead of creating duplicate
                existing.write({'price': vals.get('price', existing.price)})
                existing_records |= existing
            else:
                records_to_create.append(vals)
        
        new_records = self.browse()
        if records_to_create:
            new_records = super(ProductMultiUom, self).create(records_to_create)
        
        return new_records | existing_records

    @api.model
    def _load_pos_self_data_fields(self, config_id):
        """Define fields to load for POS."""
        return ['id', 'product_id', 'uom_id', 'price', 'operating_unit_id']

    @api.model
    def _load_pos_self_data_domain(self, data):
        """Filter multi-UOM prices for products available in POS configuration."""
        domain = self._load_pos_data_domain(data)
        config = data.get('pos.config', {}).get('data', [{}])[0]
        
        # Only load prices that match the POS operating unit exactly
        if config.get('operating_unit_id'):
            domain = expression.AND([
                domain,
                [('operating_unit_id', '=', config['operating_unit_id'])]
            ])
        else:
            # If no operating unit in config, don't load any prices
            domain = expression.AND([domain, [('id', '=', False)]])
        
        # Filter by available products in POS if applicable
        if config.get('limit_categories') and config.get('iface_available_categ_ids'):
            domain = expression.AND([domain, [('product_id.pos_categ_ids', 'in', config['iface_available_categ_ids'])]])
        
        return domain
    
    def _load_pos_data(self, data):
        """Load multi-UOM price data for POS."""
        domain = self._load_pos_self_data_domain(data)
        fields = self._load_pos_self_data_fields(data['pos.config']['data'][0]['id'])
        
        _logger.info("="*80)
        _logger.info("POS Multi-UOM Price Data Loading")
        _logger.info("="*80)
        _logger.info(f"Domain: {domain}")
        _logger.info(f"Fields: {fields}")
        
        result_data = self.search_read(domain, fields, load=False)
        
        _logger.info(f"Total records loaded: {len(result_data)}")
        
        # Check for duplicates
        seen_keys = {}
        duplicates = []
        for record in result_data:
            key = (record.get('product_id'), record.get('uom_id'), record.get('operating_unit_id'))
            if key in seen_keys:
                duplicates.append({
                    'id': record.get('id'),
                    'duplicate_of': seen_keys[key]['id'],
                    'product_id': record.get('product_id'),
                    'uom_id': record.get('uom_id'),
                    'operating_unit_id': record.get('operating_unit_id'),
                    'price': record.get('price'),
                })
                _logger.error(f"DUPLICATE FOUND: ID {record.get('id')} is duplicate of ID {seen_keys[key]['id']}")
                _logger.error(f"  Product: {record.get('product_id')}, UOM: {record.get('uom_id')}, OU: {record.get('operating_unit_id')}")
            else:
                seen_keys[key] = record
        
        if duplicates:
            _logger.error(f"TOTAL DUPLICATES FOUND: {len(duplicates)}")
            _logger.error("Duplicate details:")
            for dup in duplicates:
                _logger.error(f"  - ID: {dup['id']}, Duplicate of: {dup['duplicate_of']}, Product: {dup['product_id']}, UOM: {dup['uom_id']}, OU: {dup['operating_unit_id']}, Price: {dup['price']}")
        else:
            _logger.info("No duplicates found in loaded data")
        
        # Log sample data
        _logger.info("Sample records (first 5):")
        for i, record in enumerate(result_data[:5]):
            _logger.info(f"  {i+1}. ID: {record.get('id')}, Product: {record.get('product_id')}, UOM: {record.get('uom_id')}, OU: {record.get('operating_unit_id')}, Price: {record.get('price')}")
        
        _logger.info("="*80)
        
        return {
            'data': result_data,
            'fields': fields,
        }
    
    _sql_constraints = [
        ('product_variant_uom_ou_uniq',
         'UNIQUE(product_id, uom_id, operating_unit_id)',
         'Each Unit of Measure must be unique per product variant and operating unit.')
    ]
