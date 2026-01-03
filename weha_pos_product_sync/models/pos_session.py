from odoo import models, api, fields
from odoo.osv.expression import AND

import logging

_logger = logging.getLogger(__name__)


class PosSession(models.Model):
    _inherit = 'pos.session'

    def _transform_record_for_pos(self, record):
        """Transform a record from search_read format to POS format
        
        Transforms:
        - Many2one fields from [id, 'Name'] to just numeric id
        - Many2many fields stay as arrays (already correct)
        - False values stay as false
        
        Example:
            Input:  {'categ_id': [7, 'Food'], 'taxes_id': [1, 2]}
            Output: {'categ_id': 7, 'taxes_id': [1, 2]}
        """
        transformed = {}
        for field, value in record.items():
            # Check if this is a Many2one field (tuple/list with 2 elements: [id, name])
            if isinstance(value, (list, tuple)) and len(value) == 2 and isinstance(value[0], int):
                # Convert Many2one from [id, name] to just id
                transformed[field] = value[0]
            else:
                # Keep everything else as-is (Many2many arrays, primitives, false, etc.)
                transformed[field] = value
        return transformed

    @api.model
    def _load_pos_data_models(self, config_id):
        """Keep all models in list but return empty data for products"""
        models = super()._load_pos_data_models(config_id)
        
        # Get config to check if local storage is enabled
        config = self.env['pos.config'].browse(config_id)
        
        if config.enable_local_product_storage:
            _logger.info(
                'POS Session: Local storage enabled - models will be created but product data will be empty'
            )
        
        # Return all models - they will be created but with empty data
        return models
    
    def _load_product_product(self):
        """Return empty product data when local storage is enabled"""
        config = self.config_id
        
        # If local storage is enabled, return empty data with proper structure
        if config.enable_local_product_storage:
            _logger.info('Product loading skipped - Local storage enabled for config %s', config.id)
            fields = self.env['product.product']._load_pos_data_fields(config.id)
            return {'data': [], 'fields': fields}  # Empty data but proper structure
        
        # Normal loading if disabled  
        if not config.fast_product_loading:
            return super()._load_product_product()
        
        # Load products in batches
        domain = self._load_pos_data_domain('product.product')
        field_list = self._load_pos_data_fields('product.product')
        
        limit = config.product_load_limit or 100
        
        products = self.env['product.product'].search_read(
            domain,
            field_list,
            limit=limit,
            order='name'
        )
        
        return products

    def _load_product_pricelist(self):
        """Return empty pricelist data when local storage is enabled"""
        config = self.config_id
        
        if config.enable_local_product_storage:
            _logger.info('Pricelist loading skipped - Local storage enabled')
            fields = self.env['product.pricelist']._load_pos_data_fields(config.id)
            return {'data': [], 'fields': fields}
        
        return super()._load_product_pricelist()
    
    def _load_product_pricelist_item(self):
        """Return empty pricelist item data when local storage is enabled"""
        config = self.config_id
        
        if config.enable_local_product_storage:
            _logger.info('Pricelist item loading skipped - Local storage enabled')
            fields = self.env['product.pricelist.item']._load_pos_data_fields(config.id)
            return {'data': [], 'fields': fields}
        
        return super()._load_product_pricelist_item()
    
    def _load_product_template(self):
        """Return empty product template data when local storage is enabled"""
        config = self.config_id
        
        if config.enable_local_product_storage:
            _logger.info('Product template loading skipped - Local storage enabled')
            fields = self.env['product.template']._load_pos_data_fields(config.id)
            return {'data': [], 'fields': fields}
        
        return super()._load_product_template()
    
    def _load_product_category(self):
        """Return empty product category data when local storage is enabled"""
        config = self.config_id
        
        if config.enable_local_product_storage:
            _logger.info('Product category loading skipped - Local storage enabled')
            fields = self.env['product.category']._load_pos_data_fields(config.id)
            return {'data': [], 'fields': fields}
        
        return super()._load_product_category()
    
    def _load_product_packaging(self):
        """Return empty product packaging data when local storage is enabled"""
        config = self.config_id
        
        if config.enable_local_product_storage:
            _logger.info('Product packaging loading skipped - Local storage enabled')
            fields = self.env['product.packaging']._load_pos_data_fields(config.id)
            return {'data': [], 'fields': fields}
        
        return super()._load_product_packaging()

    def get_pos_ui_product_pricelist_item_by_product(self, product_tmpl_ids, product_ids, config_id):
        """Override to handle empty products when local storage is enabled"""
        config = self.env['pos.config'].browse(config_id)
        
        if config.enable_local_product_storage:
            # Return empty structure when local storage is enabled
            _logger.info('Pricelist item loading skipped - Local storage enabled')
            return {'product.pricelist.item': []}
        
        # Normal loading if disabled
        return super().get_pos_ui_product_pricelist_item_by_product(product_tmpl_ids, product_ids, config_id)

    @api.model
    def load_more_products(self, offset=0, limit=100, search_term=''):
        """Load additional products on demand"""
        domain = [('available_in_pos', '=', True)]
        
        if search_term:
            domain = AND([
                domain,
                ['|', '|', '|',
                 ('name', 'ilike', search_term),
                 ('default_code', 'ilike', search_term),
                 ('barcode', 'ilike', search_term),
                 ('categ_id.name', 'ilike', search_term)]
            ])
        
        field_list = [
            'id', 'display_name', 'name', 'default_code', 'barcode',
            'categ_id', 'pos_categ_ids', 'product_tmpl_id',
            'uom_id', 'standard_price', 'lst_price', 'list_price',
            'available_in_pos', 'to_weight', 'tracking',
            'taxes_id', 'image_128', 'write_date'
        ]
        
        products = self.env['product.product'].search_read(
            domain,
            field_list,
            offset=offset,
            limit=limit,
            order='name'
        )
        
        total_count = self.env['product.product'].search_count(domain)
        
        return {
            'products': products,
            'offset': offset,
            'limit': limit,
            'total_count': total_count,
            'has_more': (offset + limit) < total_count
        }

    @api.model
    def search_products(self, search_term, limit=50):
        """Quick product search with minimal fields"""
        domain = [
            ('available_in_pos', '=', True),
            '|', '|', '|',
            ('name', 'ilike', search_term),
            ('default_code', 'ilike', search_term),
            ('barcode', '=', search_term),
            ('categ_id.name', 'ilike', search_term)
        ]
        
        products = self.env['product.product'].search_read(
            domain,
            ['id', 'display_name', 'name', 'default_code', 'barcode', 
             'lst_price', 'list_price', 'image_128'],
            limit=limit,
            order='name'
        )
        
        return products

    @api.model
    def sync_products_since(self, last_sync_date, limit=1000):
        """Sync products modified since last sync date"""
        domain = [('available_in_pos', '=', True)]
        
        if last_sync_date:
            # Check for both NEW products (create_date) and UPDATED products (write_date)
            domain.append('|')
            domain.append(('create_date', '>', last_sync_date))
            domain.append(('write_date', '>', last_sync_date))
        
        field_list = [
            'id', 'display_name', 'name', 'default_code', 'barcode',
            'categ_id', 'pos_categ_ids', 'product_tmpl_id',
            'uom_id', 'standard_price', 'lst_price', 'list_price',
            'available_in_pos', 'to_weight', 'tracking',
            'taxes_id', 'image_128', 'write_date', 'create_date'
        ]
        
        products = self.env['product.product'].search_read(
            domain,
            field_list,
            limit=limit,
            order='write_date DESC'
        )
        
        _logger.info(
            'Background Sync: Found %s products (new/modified since %s)',
            len(products), last_sync_date
        )
        
        # Get deleted products (archived or no longer available in POS)
        deleted_domain = [
            '|',
            ('available_in_pos', '=', False),
            ('active', '=', False)
        ]
        if last_sync_date:
            deleted_domain.append(('write_date', '>', last_sync_date))
        
        deleted_products = self.env['product.product'].search_read(
            deleted_domain,
            ['id', 'write_date'],
            limit=limit
        )
        
        _logger.info(
            'Background Sync: Found %s deleted products',
            len(deleted_products)
        )
        
        return {
            'products': products,
            'deleted_products': [p['id'] for p in deleted_products],
            'sync_date': fields.Datetime.now().isoformat(),
            'has_more': len(products) >= limit
        }

    @api.model
    def get_all_products_for_sync(self, offset=0, limit=500):
        """Get all products for initial sync with pagination"""
        domain = [('available_in_pos', '=', True)]
        
        field_list = [
            'id', 'display_name', 'name', 'default_code', 'barcode',
            'categ_id', 'pos_categ_ids', 'product_tmpl_id',
            'uom_id', 'standard_price', 'lst_price', 'list_price',
            'available_in_pos', 'to_weight', 'tracking',
            'taxes_id', 'image_128', 'write_date', 'create_date'
        ]
        
        products = self.env['product.product'].search_read(
            domain,
            field_list,
            offset=offset,
            limit=limit,
            order='id'
        )
        
        total_count = self.env['product.product'].search_count(domain)
        has_more = (offset + len(products)) < total_count
        
        _logger.info(
            'Product Sync: Downloaded batch offset=%s, count=%s, has_more=%s, total=%s',
            offset, len(products), has_more, total_count
        )
        
        return {
            'products': products,
            'offset': offset,
            'limit': limit,
            'total_count': total_count,
            'has_more': has_more,
            'sync_date': fields.Datetime.now().isoformat()
        }

    @api.model
    def get_all_product_models_for_sync(self, config_id):
        """Get all product-related models for initial sync
        
        DATA FORMAT OUTPUT:
        ==================
        Returns data in Odoo search_read format:
        {
            'success': True,
            'models': {
                'product.product': [
                    {
                        'id': 123,
                        'name': 'Product Name',
                        'categ_id': [5, 'Food'],          # Many2one: [id, display_name]
                        'product_tag_ids': [1, 2, 3],     # Many2many: [id1, id2, ...]
                        'packaging_ids': [10, 11],        # One2many: [id1, id2, ...]
                        'write_date': '2026-01-03 10:30:00'
                    }
                ],
                'product.category': [...],
                # ... all 11 models
            }
        }
        
        IMPORTANT: Frontend should store this data in IndexedDB WITHOUT transformation.
        The POS can read this format directly.
        """
        config = self.env['pos.config'].browse(config_id)
        
        if not config.enable_local_product_storage:
            return {'success': False, 'error': 'Local storage not enabled'}
        
        _logger.info('Fetching all product models for initial sync...')
        
        result = {
            'success': True,
            'models': {}
        }
        
        # 1. Product Categories
        categories = self.env['product.category'].search_read(
            [],
            ['id', 'name', 'parent_id', 'write_date']
        )
        result['models']['product.category'] = [self._transform_record_for_pos(c) for c in categories]
        _logger.info('Loaded %s product categories', len(categories))
        
        # 2. Product Tags
        tags = self.env['product.tag'].search_read(
            [],
            ['id', 'name', 'color', 'write_date']
        )
        result['models']['product.tag'] = [self._transform_record_for_pos(t) for t in tags]
        _logger.info('Loaded %s product tags', len(tags))
        
        # 3. Product Attributes
        attributes = self.env['product.attribute'].search_read(
            [],
            ['id', 'name', 'display_type', 'create_variant', 'write_date']
        )
        result['models']['product.attribute'] = [self._transform_record_for_pos(a) for a in attributes]
        _logger.info('Loaded %s product attributes', len(attributes))
        
        # 4. Product Attribute Values
        attr_values = self.env['product.attribute.value'].search_read(
            [],
            ['id', 'name', 'attribute_id', 'is_custom', 'html_color', 'write_date']
        )
        result['models']['product.attribute.value'] = [self._transform_record_for_pos(v) for v in attr_values]
        _logger.info('Loaded %s product attribute values', len(attr_values))
        
        # 5. Product Templates (basic info)
        templates = self.env['product.template'].search_read(
            [('available_in_pos', '=', True)],
            ['id', 'name', 'categ_id', 'list_price', 'standard_price', 'uom_id', 
             'uom_po_id', 'pos_categ_ids', 'product_tag_ids', 'write_date']
        )
        result['models']['product.template'] = [self._transform_record_for_pos(t) for t in templates]
        _logger.info('Loaded %s product templates', len(templates))
        
        # 6. Product Template Attribute Lines
        tmpl_attr_lines = self.env['product.template.attribute.line'].search_read(
            [('product_tmpl_id.available_in_pos', '=', True)],
            ['id', 'product_tmpl_id', 'attribute_id', 'value_ids', 'write_date']
        )
        result['models']['product.template.attribute.line'] = [self._transform_record_for_pos(l) for l in tmpl_attr_lines]
        _logger.info('Loaded %s template attribute lines', len(tmpl_attr_lines))
        
        # 7. Product Template Attribute Values
        tmpl_attr_values = self.env['product.template.attribute.value'].search_read(
            [('product_tmpl_id.available_in_pos', '=', True)],
            ['id', 'product_tmpl_id', 'attribute_id', 'product_attribute_value_id', 
             'price_extra', 'write_date']
        )
        result['models']['product.template.attribute.value'] = [self._transform_record_for_pos(v) for v in tmpl_attr_values]
        _logger.info('Loaded %s template attribute values', len(tmpl_attr_values))
        
        # 8. Product Packaging
        packaging = self.env['product.packaging'].search_read(
            [('product_id.available_in_pos', '=', True)],
            ['id', 'name', 'product_id', 'qty', 'barcode', 'write_date']
        )
        result['models']['product.packaging'] = [self._transform_record_for_pos(p) for p in packaging]
        _logger.info('Loaded %s product packaging', len(packaging))
        
        # 9. Pricelists
        pricelists = self.env['product.pricelist'].search_read(
            [('id', 'in', config._get_available_pricelists().ids)],
            ['id', 'name', 'currency_id', 'company_id', 'active', 'write_date']
        )
        result['models']['product.pricelist'] = [self._transform_record_for_pos(p) for p in pricelists]
        _logger.info('Loaded %s pricelists', len(pricelists))
        
        # 10. Pricelist Items
        if pricelists:
            pricelist_ids = [p['id'] for p in pricelists]
            pricelist_items = self.env['product.pricelist.item'].search_read(
                [('pricelist_id', 'in', pricelist_ids)],
                ['id', 'pricelist_id', 'product_tmpl_id', 'product_id', 'categ_id',
                 'min_quantity', 'fixed_price', 'percent_price', 'price_discount',
                 'base', 'compute_price', 'write_date']
            )
            result['models']['product.pricelist.item'] = [self._transform_record_for_pos(i) for i in pricelist_items]
            _logger.info('Loaded %s pricelist items', len(pricelist_items))
        
        # 11. Products (main)
        products = self.env['product.product'].search_read(
            [('available_in_pos', '=', True)],
            ['id', 'display_name', 'name', 'default_code', 'barcode', 'type',
             'categ_id', 'pos_categ_ids', 'product_tmpl_id', 'product_template_variant_value_ids',
             'uom_id', 'uom_po_id', 'standard_price', 'lst_price', 'list_price',
             'available_in_pos', 'active', 'to_weight', 'tracking', 'product_tag_ids',
             'all_product_tag_ids', 'taxes_id', 'supplier_taxes_id', 'image_128',
             'attribute_line_ids', 'optional_product_ids', 'combo_ids',
             'is_storable', 'service_tracking', 'color', 'invoice_policy',
             'description', 'description_sale', 'write_date', 'create_date']
        )
        result['models']['product.product'] = [self._transform_record_for_pos(p) for p in products]
        _logger.info('Loaded %s products', len(products))
        
        _logger.info('All models loaded successfully for config %s', config_id)
        return result

    @api.model
    def sync_all_product_models_since(self, last_sync_date, config_id):
        """Sync all product-related models modified since last sync date
        
        DATA FORMAT OUTPUT:
        ==================
        Returns incremental updates in search_read format:
        {
            'success': True,
            'sync_date': '2026-01-03 10:30:00',
            'models': {
                'product.product': {
                    'records': [
                        {
                            'id': 123,
                            'name': 'Updated Product',
                            'categ_id': [5, 'Food'],      # Many2one format preserved
                            'product_tag_ids': [1, 2],    # Many2many format preserved
                            'write_date': '2026-01-03 09:00:00'
                        }
                    ],
                    'deleted_ids': [456, 789]             # IDs of deleted records
                },
                # ... other models
            }
        }
        
        IMPORTANT: 
        - Frontend merges 'records' into IndexedDB (upsert)
        - Frontend removes 'deleted_ids' from IndexedDB
        - No transformation needed on either side
        """
        config = self.env['pos.config'].browse(config_id)
        
        if not config.enable_local_product_storage:
            return {'success': False, 'error': 'Local storage not enabled'}
        
        _logger.info('Syncing all models since %s', last_sync_date)
        
        result = {
            'success': True,
            'models': {},
            'sync_date': fields.Datetime.now().isoformat()
        }
        
        # Helper to get updated records
        def get_updated_records(model_name, domain, fields_list):
            base_domain = domain.copy() if domain else []
            if last_sync_date:
                base_domain.append('|')
                base_domain.append(('create_date', '>', last_sync_date))
                base_domain.append(('write_date', '>', last_sync_date))
            
            records = self.env[model_name].search_read(
                base_domain,
                fields_list,
                order='write_date DESC'
            )
            
            # Transform records to POS format
            records = [self._transform_record_for_pos(r) for r in records]
            
            # Get deleted (archived or inactive) records
            # Check which fields exist on this model
            model = self.env[model_name]
            has_active = 'active' in model._fields
            has_available_in_pos = 'available_in_pos' in model._fields
            
            deleted_ids = []
            if has_active or has_available_in_pos:
                deleted_domain = domain.copy() if domain else []
                
                # Build OR condition only for fields that exist
                if has_active and has_available_in_pos:
                    deleted_domain.append('|')
                    deleted_domain.append(('active', '=', False))
                    deleted_domain.append(('available_in_pos', '=', False))
                elif has_active:
                    deleted_domain.append(('active', '=', False))
                elif has_available_in_pos:
                    deleted_domain.append(('available_in_pos', '=', False))
                
                if last_sync_date:
                    deleted_domain.append(('write_date', '>', last_sync_date))
                
                deleted = model.search_read(
                    deleted_domain,
                    ['id', 'write_date']
                )
                deleted_ids = [r['id'] for r in deleted]
            
            return {
                'records': records,
                'deleted_ids': deleted_ids
            }
        
        # Sync each model
        result['models']['product.category'] = get_updated_records(
            'product.category', [], 
            ['id', 'name', 'parent_id', 'write_date']
        )
        
        result['models']['product.tag'] = get_updated_records(
            'product.tag', [],
            ['id', 'name', 'color', 'write_date']
        )
        
        result['models']['product.attribute'] = get_updated_records(
            'product.attribute', [],
            ['id', 'name', 'display_type', 'create_variant', 'write_date']
        )
        
        result['models']['product.attribute.value'] = get_updated_records(
            'product.attribute.value', [],
            ['id', 'name', 'attribute_id', 'is_custom', 'html_color', 'write_date']
        )
        
        result['models']['product.template'] = get_updated_records(
            'product.template', [('available_in_pos', '=', True)],
            ['id', 'name', 'categ_id', 'list_price', 'standard_price', 'uom_id',
             'uom_po_id', 'pos_categ_ids', 'product_tag_ids', 'write_date']
        )
        
        result['models']['product.template.attribute.line'] = get_updated_records(
            'product.template.attribute.line', [('product_tmpl_id.available_in_pos', '=', True)],
            ['id', 'product_tmpl_id', 'attribute_id', 'value_ids', 'write_date']
        )
        
        result['models']['product.template.attribute.value'] = get_updated_records(
            'product.template.attribute.value', [('product_tmpl_id.available_in_pos', '=', True)],
            ['id', 'product_tmpl_id', 'attribute_id', 'product_attribute_value_id',
             'price_extra', 'write_date']
        )
        
        result['models']['product.packaging'] = get_updated_records(
            'product.packaging', [('product_id.available_in_pos', '=', True)],
            ['id', 'name', 'product_id', 'qty', 'barcode', 'write_date']
        )
        
        # Pricelists and items
        pricelist_ids = config._get_available_pricelists().ids
        result['models']['product.pricelist'] = get_updated_records(
            'product.pricelist', [('id', 'in', pricelist_ids)],
            ['id', 'name', 'currency_id', 'company_id', 'active', 'write_date']
        )
        
        result['models']['product.pricelist.item'] = get_updated_records(
            'product.pricelist.item', [('pricelist_id', 'in', pricelist_ids)],
            ['id', 'pricelist_id', 'product_tmpl_id', 'product_id', 'categ_id',
             'min_quantity', 'fixed_price', 'percent_price', 'price_discount',
             'base', 'compute_price', 'write_date']
        )
        
        # Products
        result['models']['product.product'] = get_updated_records(
            'product.product', [('available_in_pos', '=', True)],
            ['id', 'display_name', 'name', 'default_code', 'barcode', 'type',
             'categ_id', 'pos_categ_ids', 'product_tmpl_id', 'product_template_variant_value_ids',
             'uom_id', 'uom_po_id', 'standard_price', 'lst_price', 'list_price',
             'available_in_pos', 'active', 'to_weight', 'tracking', 'product_tag_ids',
             'all_product_tag_ids', 'taxes_id', 'supplier_taxes_id', 'image_128',
             'attribute_line_ids', 'optional_product_ids', 'combo_ids',
             'is_storable', 'service_tracking', 'color', 'invoice_policy',
             'description', 'description_sale', 'write_date', 'create_date']
        )
        
        # Log summary
        for model_name, model_data in result['models'].items():
            _logger.info(
                'Sync: %s - %s updated, %s deleted',
                model_name, len(model_data['records']), len(model_data['deleted_ids'])
            )
        
        return result

    @api.model
    def manual_sync_products(self, config_id, last_sync_date=None, batch_size=500):
        """
        Manual product sync with full control
        Returns sync status and products in batches
        """
        config = self.env['pos.config'].browse(config_id)
        
        if not config.enable_local_product_storage:
            return {
                'success': False,
                'error': 'Local product storage is not enabled for this POS'
            }
        
        # Get sync statistics
        total_count = self.env['product.product'].search_count([
            ('available_in_pos', '=', True)
        ])
        
        if last_sync_date:
            # Incremental sync
            modified_count = self.env['product.product'].search_count([
                ('available_in_pos', '=', True),
                ('write_date', '>', last_sync_date)
            ])
            
            return {
                'success': True,
                'sync_type': 'incremental',
                'total_products': total_count,
                'modified_products': modified_count,
                'batch_size': batch_size,
                'batches_needed': (modified_count + batch_size - 1) // batch_size if batch_size else 0
            }
        else:
            # Full sync
            return {
                'success': True,
                'sync_type': 'full',
                'total_products': total_count,
                'batch_size': batch_size,
                'batches_needed': (total_count + batch_size - 1) // batch_size if batch_size else 0
            }

    @api.model
    def get_sync_batch(self, batch_number=0, batch_size=500, last_sync_date=None):
        """
        Get a specific batch of products for sync
        batch_number: 0-indexed batch number
        """
        offset = batch_number * batch_size
        
        domain = [('available_in_pos', '=', True)]
        if last_sync_date:
            domain.append(('write_date', '>', last_sync_date))
        
        field_list = [
            'id', 'display_name', 'name', 'default_code', 'barcode',
            'categ_id', 'pos_categ_ids', 'product_tmpl_id',
            'uom_id', 'standard_price', 'lst_price', 'list_price',
            'available_in_pos', 'to_weight', 'tracking',
            'taxes_id', 'image_128', 'write_date', 'create_date'
        ]
        
        products = self.env['product.product'].search_read(
            domain,
            field_list,
            offset=offset,
            limit=batch_size,
            order='id' if not last_sync_date else 'write_date DESC'
        )
        
        total_count = self.env['product.product'].search_count(domain)
        
        return {
            'success': True,
            'batch_number': batch_number,
            'batch_size': batch_size,
            'products': products,
            'products_in_batch': len(products),
            'offset': offset,
            'total_count': total_count,
            'has_more': (offset + batch_size) < total_count,
            'sync_date': fields.Datetime.now().isoformat()
        }

    @api.model
    def start_manual_sync(self, config_id):
        """
        Initialize manual sync process
        Returns sync configuration and initial status
        """
        config = self.env['pos.config'].browse(config_id)
        
        if not config.enable_local_product_storage:
            return {
                'success': False,
                'error': 'Local product storage is not enabled'
            }
        
        # Get all categories for sync
        categories = self.env['pos.category'].search_read(
            [],
            ['id', 'name', 'parent_id', 'sequence', 'write_date']
        )
        
        product_categories = self.env['product.category'].search_read(
            [],
            ['id', 'name', 'parent_id', 'write_date']
        )
        
        # Get taxes
        taxes = self.env['account.tax'].search_read(
            [('active', '=', True)],
            ['id', 'name', 'amount', 'amount_type', 'price_include', 'write_date']
        )
        
        # Get UoM
        uoms = self.env['uom.uom'].search_read(
            [],
            ['id', 'name', 'category_id', 'factor', 'rounding', 'write_date']
        )
        
        # Product count
        product_count = self.env['product.product'].search_count([
            ('available_in_pos', '=', True)
        ])
        
        return {
            'success': True,
            'config': {
                'id': config.id,
                'name': config.name,
                'enable_local_product_storage': config.enable_local_product_storage,
            },
            'metadata': {
                'pos_categories': categories,
                'product_categories': product_categories,
                'taxes': taxes,
                'uoms': uoms,
            },
            'sync_info': {
                'total_products': product_count,
                'recommended_batch_size': 500,
                'sync_date': fields.Datetime.now().isoformat()
            }
        }

    @api.model
    def complete_manual_sync(self, config_id, synced_count, sync_start_date):
        """
        Finalize manual sync and update config
        """
        config = self.env['pos.config'].browse(config_id)
        
        return {
            'success': True,
            'synced_count': synced_count,
            'sync_start_date': sync_start_date,
            'sync_end_date': fields.Datetime.now().isoformat(),
            'message': f'Successfully synced {synced_count} products'
        }

    @api.model
    def check_sync_required(self, config_id, last_sync_date):
        """
        Check if sync is required based on product modifications
        """
        if not last_sync_date:
            return {
                'sync_required': True,
                'reason': 'No previous sync found',
                'modified_count': None
            }
        
        modified_count = self.env['product.product'].search_count([
            ('available_in_pos', '=', True),
            ('write_date', '>', last_sync_date)
        ])
        
        deleted_count = self.env['product.product'].search_count([
            '|',
            ('available_in_pos', '=', False),
            ('active', '=', False),
            ('write_date', '>', last_sync_date)
        ])
        
        return {
            'sync_required': (modified_count > 0 or deleted_count > 0),
            'modified_count': modified_count,
            'deleted_count': deleted_count,
            'last_sync_date': last_sync_date,
            'current_date': fields.Datetime.now().isoformat()
        }

    @api.model
    def load_pricelists(self, config_id):
        """
        Load pricelists and pricelist items for current POS session
        This is called separately when local storage is enabled
        """
        config = self.env['pos.config'].browse(config_id)
        
        if not config:
            return {
                'success': False,
                'error': 'Invalid POS configuration'
            }
        
        # Get available pricelists for this POS config
        pricelists = config.available_pricelist_ids
        
        if not pricelists:
            pricelists = self.env['product.pricelist'].search([])
        
        # Get pricelist items for these pricelists
        pricelist_items = self.env['product.pricelist.item'].search([
            ('pricelist_id', 'in', pricelists.ids)
        ])
        
        # Read pricelist data
        pricelist_data = pricelists.read([
            'id', 'name', 'currency_id', 'company_id', 
            'active', 'sequence', 'write_date'
        ])
        
        # Read pricelist items data
        pricelist_item_data = pricelist_items.read([
            'id', 'pricelist_id', 'product_tmpl_id', 'product_id',
            'categ_id', 'min_quantity', 'applied_on', 
            'compute_price', 'fixed_price', 'percent_price',
            'price_discount', 'price_surcharge', 'price_round',
            'price_min_margin', 'price_max_margin',
            'date_start', 'date_end', 'write_date'
        ])
        
        _logger.info(
            'Pricelist Sync: Loaded %s pricelists and %s pricelist items for config %s',
            len(pricelist_data), len(pricelist_item_data), config.name
        )
        
        return {
            'success': True,
            'pricelists': pricelist_data,
            'pricelist_items': pricelist_item_data,
            'sync_date': fields.Datetime.now().isoformat()
        }

    @api.model
    def sync_pricelists_since(self, config_id, last_sync_date):
        """
        Sync pricelists modified since last sync date
        """
        config = self.env['pos.config'].browse(config_id)
        
        if not config:
            return {
                'success': False,
                'error': 'Invalid POS configuration'
            }
        
        # Get available pricelists for this POS config
        pricelists = config.available_pricelist_ids
        
        if not pricelists:
            pricelists = self.env['product.pricelist'].search([])
        
        # Filter modified pricelists
        domain = [('id', 'in', pricelists.ids)]
        if last_sync_date:
            domain.append(('write_date', '>', last_sync_date))
        
        modified_pricelists = self.env['product.pricelist'].search_read(
            domain,
            ['id', 'name', 'currency_id', 'company_id', 
             'active', 'sequence', 'write_date']
        )
        
        # Get modified pricelist items
        item_domain = [('pricelist_id', 'in', pricelists.ids)]
        if last_sync_date:
            item_domain.append(('write_date', '>', last_sync_date))
        
        modified_items = self.env['product.pricelist.item'].search_read(
            item_domain,
            ['id', 'pricelist_id', 'product_tmpl_id', 'product_id',
             'categ_id', 'min_quantity', 'applied_on', 
             'compute_price', 'fixed_price', 'percent_price',
             'price_discount', 'price_surcharge', 'price_round',
             'price_min_margin', 'price_max_margin',
             'date_start', 'date_end', 'write_date']
        )
        
        _logger.info(
            'Pricelist Sync: Found %s modified pricelists and %s modified items since %s',
            len(modified_pricelists), len(modified_items), last_sync_date
        )
        
        return {
            'success': True,
            'pricelists': modified_pricelists,
            'pricelist_items': modified_items,
            'sync_date': fields.Datetime.now().isoformat()
        }
