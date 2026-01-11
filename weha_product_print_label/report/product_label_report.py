# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from collections import defaultdict
from odoo import _, models
from odoo.exceptions import UserError
import base64
import io

try:
    import barcode
    from barcode.writer import ImageWriter
except ImportError:
    barcode = None


def generate_barcode_base64(barcode_value, width=2, height=50):
    """Generate barcode as base64 encoded image"""
    if not barcode or not barcode_value:
        return None
    
    try:
        # Create barcode
        code128 = barcode.get('code128', barcode_value, writer=ImageWriter())
        
        # Generate image in memory
        buffer = io.BytesIO()
        code128.write(buffer, options={
            'module_width': 0.2,
            'module_height': height / 3,
            'quiet_zone': 2,
            'text_distance': 2,
            'font_size': 0,
        })
        
        # Convert to base64
        buffer.seek(0)
        barcode_base64 = base64.b64encode(buffer.read()).decode('utf-8')
        return f'data:image/png;base64,{barcode_base64}'
    except Exception:
        return None


def _prepare_data(env, docids, data):
    """
    Prepare data for product label reports
    Change product ids by actual product objects to get access to fields in xml template
    """
    layout_wizard = env['product.label.layout'].browse(data.get('layout_wizard'))
    
    if data.get('active_model') == 'product.template':
        Product = env['product.template'].with_context(display_default_code=False)
    elif data.get('active_model') == 'product.product':
        Product = env['product.product'].with_context(display_default_code=False)
    else:
        raise UserError(_('Product model not defined, Please contact your administrator.'))

    if not layout_wizard:
        return {}

    total = 0
    qty_by_product_in = data.get('quantity_by_product')
    # Search for products all at once, ordered by name desc since popitem() used in xml  
    # is LIFO, which results in ordering by product name in the report
    products = Product.search([('id', 'in', [int(p) for p in qty_by_product_in.keys()])], order='name desc')
    quantity_by_product = defaultdict(list)
    
    for product in products:
        q = qty_by_product_in[str(product.id)]
        quantity_by_product[product].append((product.barcode, q))
        total += q
    
    if data.get('custom_barcodes'):
        # We expect custom barcodes format as: {product: [(barcode, qty_of_barcode)]}
        for product, barcodes_qtys in data.get('custom_barcodes').items():
            quantity_by_product[product] = barcodes_qtys
            total += sum(qty for _, qty in barcodes_qtys)

    return {
        'quantity': quantity_by_product,
        'page_numbers': -(-total // (layout_wizard.rows * layout_wizard.columns)),  # Ceiling division
        'pricelist': layout_wizard.pricelist_id,
        'extra_html': layout_wizard.extra_html,
        'generate_barcode': generate_barcode_base64,
    }


class ReportProductLabel2x7(models.AbstractModel):
    _name = 'report.weha_product_print_label.label_2x7'
    _description = 'Product Label Report 2x7'

    def _get_report_values(self, docids, data):
        return _prepare_data(self.env, docids, data)


class ReportProductLabel3x7(models.AbstractModel):
    _name = 'report.weha_product_print_label.label_3x7'
    _description = 'Product Label Report 3x7'

    def _get_report_values(self, docids, data):
        return _prepare_data(self.env, docids, data)


class ReportProductLabel4x7(models.AbstractModel):
    _name = 'report.weha_product_print_label.label_4x7'
    _description = 'Product Label Report 4x7'

    def _get_report_values(self, docids, data):
        return _prepare_data(self.env, docids, data)


class ReportProductLabel4x12(models.AbstractModel):
    _name = 'report.weha_product_print_label.label_4x12'
    _description = 'Product Label Report 4x12'

    def _get_report_values(self, docids, data):
        return _prepare_data(self.env, docids, data)


class ReportProductLabel2x7Logo(models.AbstractModel):
    _name = 'report.weha_product_print_label.label_2x7_logo'
    _description = 'Product Label Report 2x7 with Logo'

    def _get_report_values(self, docids, data):
        return _prepare_data(self.env, docids, data)


class ReportProductLabel3x7Logo(models.AbstractModel):
    _name = 'report.weha_product_print_label.label_3x7_logo'
    _description = 'Product Label Report 3x7 with Logo'

    def _get_report_values(self, docids, data):
        return _prepare_data(self.env, docids, data)


class ReportProductLabel4x7Logo(models.AbstractModel):
    _name = 'report.weha_product_print_label.label_4x7_logo'
    _description = 'Product Label Report 4x7 with Logo'

    def _get_report_values(self, docids, data):
        return _prepare_data(self.env, docids, data)


class ReportProductLabel4x12Logo(models.AbstractModel):
    _name = 'report.weha_product_print_label.label_4x12_logo'
    _description = 'Product Label Report 4x12 with Logo'

    def _get_report_values(self, docids, data):
        return _prepare_data(self.env, docids, data)
