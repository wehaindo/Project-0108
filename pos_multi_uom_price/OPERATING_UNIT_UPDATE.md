# Operating Unit Integration Update

## Overview
This document describes the integration of Operating Unit functionality into the `pos_multi_uom_price` module, allowing different prices per UOM per Operating Unit.

## Changes Made

### 1. Dependencies Added
**File**: `__manifest__.py`

Added dependencies:
- `operating_unit` - OCA Operating Unit base module
- `weha_pos_operating_unit` - POS Operating Unit integration

### 2. Model Updates

#### ProductTmplMultiUom (`product.tmpl.multi.uom.price`)
**File**: `models/product_multi_uom_price.py`

**New Field**:
```python
operating_unit_id = fields.Many2one(
    'operating.unit',
    string='Operating Unit',
    required=False,
    ondelete="cascade",
    help='Leave empty to apply this price to all operating units. '
         'Set to apply this price only for specific operating unit.'
)
```

**Updated Constraint**:
- Changed from: `UNIQUE(product_tmpl_id, uom_id)`
- Changed to: `UNIQUE(product_tmpl_id, uom_id, operating_unit_id)`
- Ensures unique price per template, UOM, and operating unit combination

**Updated Logic**:
- `_sync_price_to_variants()` now includes operating unit in sync logic
- Handles both global prices (no OU) and OU-specific prices

#### ProductMultiUom (`product.multi.uom.price`)
**File**: `models/product_multi_uom_price.py`

**New Field**:
```python
operating_unit_id = fields.Many2one(
    'operating.unit',
    string='Operating Unit',
    required=False,
    ondelete="cascade",
    help='Leave empty to apply this price to all operating units. '
         'Set to apply this price only for specific operating unit.'
)
```

**Updated Constraint**:
- Changed from: `UNIQUE(product_id, uom_id)`
- Changed to: `UNIQUE(product_id, uom_id, operating_unit_id)`
- Ensures unique price per variant, UOM, and operating unit combination

**POS Data Loading**:
- `_load_pos_self_data_fields()`: Added `'operating_unit_id'` to loaded fields
- `_load_pos_self_data_domain()`: Filters prices based on POS operating unit
  - Loads prices for current POS operating unit OR global prices (no OU set)
  - If POS has no operating unit, only loads global prices

### 3. View Updates
**File**: `views/product_view.xml`

Both product template and product variant views updated:
- Added `category_id` field (invisible, for domain filtering)
- Added `operating_unit_id` field (visible, optional column)
- Better structured list view for price management

**Template View**:
```xml
<list editable="bottom">
    <field name="category_id" column_invisible="1"/>
    <field name="uom_id"/>
    <field name="operating_unit_id" optional="show"/>
    <field name="price"/>
</list>
```

**Variant View**: Same structure as template view

### 4. Code Quality Improvements
- Fixed class naming to follow CamelCase convention
- Added proper docstrings to all methods
- Added price validation to prevent negative prices
- Improved POS domain filtering logic
- Added `expression` import for proper domain handling

## Usage

### Setting Up Prices

#### Global Prices (All Operating Units)
1. Go to Product > Product Template
2. Open POS tab
3. In UOM Price section, add UOM prices
4. Leave "Operating Unit" field empty
5. Price applies to all operating units

#### Operating Unit Specific Prices
1. Go to Product > Product Template
2. Open POS tab
3. In UOM Price section, add UOM prices
4. Select specific Operating Unit
5. Price applies only to selected operating unit

### Price Priority Logic
When a POS session loads prices:
1. If POS has an operating unit configured:
   - Loads prices for that specific operating unit
   - Also loads global prices (no OU set)
2. If POS has no operating unit:
   - Only loads global prices

**Example**:
- Product A, 1 Unit: $10 (no OU) - Global price
- Product A, 1 Unit: $12 (OU: Store 1) - Store 1 specific
- Product A, 1 Dozen: $100 (no OU) - Global price

When Store 1 POS loads:
- Gets $12 for 1 Unit (OU specific takes precedence)
- Gets $100 for 1 Dozen (uses global price)

### Database Migration Notes

**Important**: After updating the module, you need to:

1. **Update the module** in Odoo:
   ```bash
   ./odoo-bin -u pos_multi_uom_price -d your_database
   ```

2. **Existing data**: 
   - All existing UOM prices will have `operating_unit_id = NULL` (global prices)
   - They will work for all operating units
   - You can edit them to make them OU-specific if needed

3. **No data loss**: Existing prices are preserved

## Technical Details

### SQL Constraints
Both models use a unique constraint including operating unit:
```sql
UNIQUE(product_tmpl_id/product_id, uom_id, operating_unit_id)
```

This allows:
- Product A, 1 Unit, No OU: $10
- Product A, 1 Unit, Store 1: $12
- Product A, 1 Unit, Store 2: $15

But prevents:
- Product A, 1 Unit, Store 1: $12 (duplicate)

### POS Data Loading
The `_load_pos_self_data_domain()` method implements smart filtering:

```python
if config.get('operating_unit_id'):
    domain = expression.AND([
        domain,
        ['|',
            ('operating_unit_id', '=', config['operating_unit_id']),
            ('operating_unit_id', '=', False)
        ]
    ])
```

This ensures minimal data transfer to POS frontend while maintaining flexibility.

## Testing Checklist

- [ ] Create global price (no OU)
- [ ] Create OU-specific price
- [ ] Verify both prices can coexist for same product/UOM
- [ ] Open POS with OU configured
- [ ] Verify correct prices loaded in POS
- [ ] Test product selection with different UOMs
- [ ] Verify price calculation in POS
- [ ] Test with POS without OU configured
- [ ] Verify template price syncs to variants
- [ ] Test constraint: duplicate product/UOM/OU should fail

## Compatibility

- **Odoo Version**: 18.0
- **Required Modules**:
  - `point_of_sale`
  - `operating_unit` (OCA)
  - `weha_pos_operating_unit`
- **Optional Modules**:
  - `account_operating_unit` (for full OU integration)

## Future Enhancements

Potential improvements:
1. Add import/export templates for bulk price management
2. Add price history tracking per OU
3. Add price comparison view across OUs
4. Add automatic price replication wizard across OUs
5. Add OU-based pricing rules/formulas
