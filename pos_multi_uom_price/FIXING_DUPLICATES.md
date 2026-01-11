# Fixing Duplicate Key Error in POS

## Problem
Error: `Got duplicate key in t-foreach: 2`

This occurs when there are duplicate `product.multi.uom.price` records with the same product, UOM, and operating unit combination.

## Root Cause
When `operating_unit_id` is `False`, it needs to be stored as `NULL` in the database for the SQL unique constraint to work properly. Previous code might have created duplicates.

## Solution Applied

### 1. Code Fixes
Updated the following methods to prevent duplicates:

**ProductTmplMultiUom.create()**
- Removes `operating_unit_id` from vals if it's False (lets it default to NULL)
- Prevents duplicate creation at template level

**ProductTmplMultiUom._sync_price_to_variants()**
- Improved logic to check for existing records properly
- Only sets `operating_unit_id` in vals if it exists (not False)
- Uses proper domain filtering for NULL values

**ProductMultiUom.create()**
- Checks for existing records before creating
- Updates existing record instead of creating duplicate
- Properly handles NULL vs False for operating_unit_id

### 2. Cleanup Existing Duplicates

Run the cleanup utility to remove existing duplicates:

#### Option A: From Odoo Shell
```bash
./odoo-bin shell -d your_database --no-http
```

Then in the shell:
```python
# Clean variant price duplicates
result = env['product.multi.uom.price.cleanup'].cleanup_duplicate_prices()
print(result)

# Clean template price duplicates
result = env['product.multi.uom.price.cleanup'].cleanup_template_duplicate_prices()
print(result)

# Commit changes
env.cr.commit()
```

#### Option B: From Python Code
```python
self.env['product.multi.uom.price.cleanup'].cleanup_duplicate_prices()
self.env['product.multi.uom.price.cleanup'].cleanup_template_duplicate_prices()
```

#### Option C: Quick SQL Query (Advanced)
```sql
-- Find duplicates in variant prices
SELECT product_id, uom_id, operating_unit_id, COUNT(*) as count
FROM product_multi_uom_price
GROUP BY product_id, uom_id, COALESCE(operating_unit_id, 0)
HAVING COUNT(*) > 1;

-- Find duplicates in template prices
SELECT product_tmpl_id, uom_id, operating_unit_id, COUNT(*) as count
FROM product_tmpl_multi_uom_price
GROUP BY product_tmpl_id, uom_id, COALESCE(operating_unit_id, 0)
HAVING COUNT(*) > 1;
```

### 3. Update the Module

After updating the code:

```bash
./odoo-bin -u pos_multi_uom_price -d your_database
```

### 4. Verify Fix

1. Check for duplicates:
```python
# In Odoo shell
prices = env['product.multi.uom.price'].search([])
keys = {}
for p in prices:
    key = (p.product_id.id, p.uom_id.id, p.operating_unit_id.id if p.operating_unit_id else False)
    if key in keys:
        print(f"Duplicate found: {key}")
    keys[key] = p.id
```

2. Test POS:
   - Open POS
   - Select a product with multiple UOMs
   - Click on UOM selection
   - Should not get "duplicate key" error

## Prevention

The updated code prevents duplicates by:

1. **Proper NULL Handling**: False values are removed from vals, letting database use NULL
2. **Duplicate Check**: Before creating, checks if record already exists
3. **Update Instead of Create**: If duplicate found, updates existing record
4. **SQL Constraint**: Enforces uniqueness at database level

## SQL Constraints

Both models have unique constraints:

```sql
-- Template prices
UNIQUE(product_tmpl_id, uom_id, operating_unit_id)

-- Variant prices
UNIQUE(product_id, uom_id, operating_unit_id)
```

These allow:
- Same product + UOM with different operating units
- Same product + UOM with NULL operating unit (global)

But prevent:
- Same product + UOM + operating unit twice

## Testing Checklist

After applying fixes:

- [ ] Run cleanup utility
- [ ] Update module
- [ ] Open POS
- [ ] Select product with multiple UOMs
- [ ] Click UOM selection popup
- [ ] Verify no duplicate key error
- [ ] Create new UOM price with no OU
- [ ] Create new UOM price with OU
- [ ] Verify both can coexist
- [ ] Try creating duplicate (should update, not error)

## If Issue Persists

1. Check server logs for actual duplicate IDs
2. Query database directly to find duplicates
3. Run cleanup utility again
4. Restart Odoo server
5. Clear browser cache
6. Test in incognito mode

## Related Files Modified

- `models/product_multi_uom_price.py` - Main model with fixes
- `models/product_multi_uom_price_cleanup.py` - Cleanup utility
- `models/__init__.py` - Import cleanup module
