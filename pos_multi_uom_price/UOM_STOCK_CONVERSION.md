# UOM Stock Conversion in POS Multi UOM Price

## Problem Description

When selling products with different Units of Measure (UOM) in POS, stock movements must properly convert quantities from the sale UOM to the product's base/stock UOM.

### Example Scenario

**Without conversion:**
- Product: Bottled Water
- Stock UOM: Units (bottles)
- Sale UOM: Box (1 box = 12 bottles)
- Sale: 5 boxes
- **Wrong Result:** Stock reduces by 5 units instead of 60 units ❌

**With conversion:**
- Sale: 5 boxes
- **Correct Result:** Stock reduces by 60 units ✅

## Technical Implementation

### Key Points

1. **Sale UOM vs Stock UOM:**
   - `product_uom_id` on `pos.order.line` = UOM used for sale
   - `product_id.uom_id` on `product.product` = Base/stock UOM

2. **Conversion Formula:**
   ```python
   qty_in_stock_uom = sale_uom._compute_quantity(
       qty_in_sale_uom,
       product_uom,
       rounding_method='HALF-UP'
   )
   ```

3. **Stock Move Creation:**
   - Quantity must be in product's stock UOM
   - `product_uom_qty` field holds the converted quantity
   - `product_uom` field should reference the stock UOM

## Code Implementation

The fix is in `models/stock_picking.py`:

```python
def _prepare_stock_move_vals(self, first_line, order_lines):
    res = super()._prepare_stock_move_vals(first_line, order_lines)
    
    # Get the sale UOM from the POS order line
    sale_uom = first_line.product_uom_id
    # Get the product's stock/reference UOM
    product_uom = first_line.product_id.uom_id
    
    # Convert quantity from sale UOM to product's stock UOM
    if sale_uom and sale_uom != product_uom:
        qty_in_sale_uom = sum(order_lines.mapped('qty'))
        qty_in_stock_uom = sale_uom._compute_quantity(
            qty_in_sale_uom,
            product_uom,
            rounding_method='HALF-UP'
        )
        
        res.update({
            'product_uom_qty': qty_in_stock_uom,
            'product_uom': product_uom.id,
        })
    else:
        res.update({'product_uom': sale_uom.id})
    
    return res
```

## Testing Scenarios

### Test Case 1: Different UOM
- Product: Water Bottles (Stock UOM: Unit)
- Sale: 3 boxes @ 12 units/box
- Expected: Stock move of 36 units

### Test Case 2: Same UOM
- Product: Individual Bottles (Stock UOM: Unit)
- Sale: 10 units
- Expected: Stock move of 10 units

### Test Case 3: Decimal Quantities
- Product: Fabric (Stock UOM: Meter)
- Sale: 2.5 rolls @ 50 meters/roll
- Expected: Stock move of 125 meters

## Important Notes

1. **UOM Category:** Sale UOM and Stock UOM must be in the same category
2. **Rounding:** Uses 'HALF-UP' rounding method for consistency
3. **Logging:** Conversion details are logged for debugging
4. **Backward Compatibility:** Works with existing single-UOM products

## Related Files

- `models/stock_picking.py` - Stock move preparation
- `models/pos_order.py` - POS order line with UOM
- `models/product_multi_uom_price.py` - Multi-UOM price configuration

## Date
Updated: January 11, 2026
