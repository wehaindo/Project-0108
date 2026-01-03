from odoo import models, fields, api
from odoo.exceptions import UserError
import random


class ProductGeneratorWizard(models.TransientModel):
    _name = 'product.generator.wizard'
    _description = 'Generate Test Products for POS'

    product_count = fields.Integer(
        string='Number of Products',
        default=3000,
        required=True,
        help='Number of test products to generate'
    )
    
    prefix = fields.Char(
        string='Product Name Prefix',
        default='Test Product',
        required=True
    )
    
    price_min = fields.Float(
        string='Minimum Price',
        default=10.0,
        required=True
    )
    
    price_max = fields.Float(
        string='Maximum Price',
        default=1000.0,
        required=True
    )
    
    generate_barcodes = fields.Boolean(
        string='Generate Barcodes',
        default=True
    )
    
    generate_images = fields.Boolean(
        string='Generate Images',
        default=False,
        help='Generate placeholder images (slower)'
    )
    
    available_in_pos = fields.Boolean(
        string='Available in POS',
        default=True
    )
    
    category_id = fields.Many2one(
        'product.category',
        string='Product Category',
        help='Category for generated products'
    )

    @api.model
    def _generate_barcode(self, sequence):
        """Generate a valid EAN13 barcode"""
        # Simple barcode generation: 200 + 9-digit sequence + checksum
        base = f"200{sequence:09d}"
        # Calculate EAN13 checksum
        odd_sum = sum(int(base[i]) for i in range(0, 12, 2))
        even_sum = sum(int(base[i]) for i in range(1, 12, 2))
        checksum = (10 - ((odd_sum + even_sum * 3) % 10)) % 10
        return base + str(checksum)

    def action_generate_products(self):
        """Generate test products"""
        self.ensure_one()
        
        if self.product_count <= 0 or self.product_count > 10000:
            raise UserError('Please enter a number between 1 and 10000')
        
        if self.price_min >= self.price_max:
            raise UserError('Minimum price must be less than maximum price')
        
        # Get or create category
        if not self.category_id:
            category = self.env['product.category'].search([('name', '=', 'Test Products')], limit=1)
            if not category:
                category = self.env['product.category'].create({
                    'name': 'Test Products',
                })
            self.category_id = category
        
        # Get or create POS category
        pos_category = self.env['pos.category'].search([('name', '=', 'Test Products')], limit=1)
        if not pos_category:
            pos_category = self.env['pos.category'].create({
                'name': 'Test Products',
            })
        
        products_to_create = []
        batch_size = 100
        
        for i in range(self.product_count):
            # Generate random price
            price = round(random.uniform(self.price_min, self.price_max), 2)
            
            product_vals = {
                'name': f'{self.prefix} {i+1:05d}',
                'default_code': f'TEST{i+1:05d}',
                'categ_id': self.category_id.id,
                'pos_categ_ids': [(6, 0, [pos_category.id])],
                'list_price': price,
                'standard_price': round(price * 0.6, 2),  # 40% margin
                'available_in_pos': self.available_in_pos,
                'sale_ok': True,
            }
            
            if self.generate_barcodes:
                product_vals['barcode'] = self._generate_barcode(i + 1)
            
            products_to_create.append(product_vals)
            
            # Create in batches for better performance
            if len(products_to_create) >= batch_size or i == self.product_count - 1:
                self.env['product.product'].create(products_to_create)
                products_to_create = []
        
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': 'Success',
                'message': f'{self.product_count} test products generated successfully!',
                'type': 'success',
                'sticky': False,
            }
        }
    
    def action_delete_test_products(self):
        """Delete all test products"""
        self.ensure_one()
        
        # Find products with the test prefix
        products = self.env['product.product'].search([
            ('default_code', '=like', 'TEST%')
        ])
        
        count = len(products)
        
        if count > 0:
            products.unlink()
            message = f'{count} test products deleted successfully!'
        else:
            message = 'No test products found to delete.'
        
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': 'Success',
                'message': message,
                'type': 'success',
                'sticky': False,
            }
        }
