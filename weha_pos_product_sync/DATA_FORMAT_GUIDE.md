# POS Product Sync - Data Format Guide

## Overview
This guide explains the data format differences between server (Odoo backend) and POS (frontend) to ensure IndexedDB stores data in a format that POS can read correctly.

## Server Data Format (from Odoo)

### Method: `search_read()`
Odoo's `search_read()` returns data in this format:

```python
# Example: product.product
products = self.env['product.product'].search_read(
    [('available_in_pos', '=', True)],
    ['id', 'name', 'barcode', 'categ_id', 'product_tag_ids']
)

# Returns list of dictionaries:
[
    {
        'id': 123,
        'name': 'Product Name',
        'barcode': '1234567890',
        'categ_id': [5, 'Category Name'],      # Many2one: [id, display_name]
        'product_tag_ids': [1, 2, 3]           # Many2many: [id1, id2, ...]
    }
]
```

### Key Format Rules for Server Data:

1. **Many2one fields** (e.g., `categ_id`, `product_tmpl_id`):
   - Format: `[id, display_name]`
   - Example: `[5, 'Food / Beverages']`
   - Can also be `false` if not set

2. **Many2many fields** (e.g., `product_tag_ids`, `taxes_id`):
   - Format: `[id1, id2, id3, ...]`
   - Example: `[1, 2, 3]`
   - Empty: `[]`

3. **One2many fields** (e.g., `packaging_ids`, `seller_ids`):
   - Format: `[id1, id2, id3, ...]`
   - Example: `[10, 11, 12]`
   - Empty: `[]`

4. **Simple fields** (e.g., `name`, `barcode`, `price`):
   - String: `"Product Name"`
   - Float: `99.99`
   - Boolean: `true` or `false`
   - Integer: `123`

## POS Expected Format

### Two Methods for Loading Data into POS:

#### Method 1: Data Service (`this.data.create()`)
This is the **PREFERRED** method for Odoo 18:

```javascript
// POS expects the SAME format as server
this.data.create('product.product', {
    id: 123,
    name: 'Product Name',
    barcode: '1234567890',
    categ_id: [5, 'Category Name'],      // Many2one as [id, name]
    product_tag_ids: [1, 2, 3]           // Many2many as array of IDs
});
```

#### Method 2: Direct Model Create (`this.models['product.product'].create()`)
Fallback method when data service fails:

```javascript
// Accepts either format:
// 1. Server format (preferred):
this.models['product.product'].create({
    id: 123,
    categ_id: [5, 'Category Name'],
    product_tag_ids: [1, 2, 3]
});

// 2. Numeric ID format (also works):
this.models['product.product'].create({
    id: 123,
    categ_id: 5,                         // Numeric ID
    product_tag_ids: [1, 2, 3]
});
```

## IndexedDB Storage Format

### What to Store:
**Store data in the EXACT format received from server (`search_read()`).**

```javascript
// Save directly from server without transformation
const serverData = await odoo.call('pos.session', 'get_all_product_models_for_sync');

// serverData.models['product.product'] contains:
[
    {
        id: 123,
        name: 'Product Name',
        categ_id: [5, 'Category Name'],      // Keep as-is
        product_tag_ids: [1, 2, 3],          // Keep as-is
        product_tmpl_id: [45, 'Template'],   // Keep as-is
        write_date: '2026-01-03 10:30:00'
    }
]

// Save to IndexedDB without modification
await productStorage.saveRecords('product.product', serverData.models['product.product']);
```

## Data Transformation (when loading from IndexedDB)

### Current Implementation in `models.js`:

```javascript
_transformRecordDataForCreate(modelName, recordData) {
    const data = { ...recordData };
    
    // 1. Ensure Many2many/One2many fields are arrays
    const relationFields = {
        'product.product': [
            'product_tag_ids', 'taxes_id', 'supplier_taxes_id', 
            'pos_categ_ids', 'packaging_ids'
        ],
        'product.template': [
            'product_tag_ids', 'taxes_id', 'pos_categ_ids',
            'attribute_line_ids', 'product_variant_ids'
        ]
    };
    
    for (const field of relationFields[modelName] || []) {
        if (data[field] !== undefined && data[field] !== null) {
            if (!Array.isArray(data[field])) {
                // Convert non-array to array
                data[field] = data[field] ? [data[field]] : [];
            }
        } else {
            data[field] = [];
        }
    }
    
    // 2. Many2one fields - NO transformation needed
    // Server format [id, name] or numeric id both work
    
    return data;
}
```

## Model-Specific Field Mappings

### 1. product.product
```javascript
{
    // Many2one fields
    'categ_id': [5, 'Food'],
    'product_tmpl_id': [10, 'Product Template'],
    'uom_id': [1, 'Unit'],
    'pos_categ_id': [2, 'POS Category'],
    
    // Many2many fields
    'product_tag_ids': [1, 2, 3],
    'taxes_id': [5, 6],
    'pos_categ_ids': [1, 2],
    
    // One2many fields
    'packaging_ids': [10, 11],
    'seller_ids': [20, 21]
}
```

### 2. product.template
```javascript
{
    // Many2one fields
    'categ_id': [5, 'Food'],
    'uom_id': [1, 'Unit'],
    'pos_categ_id': [2, 'POS Category'],
    
    // Many2many fields
    'product_tag_ids': [1, 2, 3],
    'taxes_id': [5, 6],
    'pos_categ_ids': [1, 2],
    
    // One2many fields
    'attribute_line_ids': [30, 31],
    'product_variant_ids': [100, 101]
}
```

### 3. product.pricelist
```javascript
{
    // Many2one fields
    'company_id': [1, 'My Company'],
    'currency_id': [2, 'USD'],
    
    // One2many fields
    'item_ids': [50, 51, 52],
    
    // Many2many fields
    'country_group_ids': [1, 2]
}
```

### 4. product.pricelist.item
```javascript
{
    // Many2one fields
    'pricelist_id': [1, 'Public Pricelist'],
    'product_tmpl_id': [10, 'Product Template'],
    'product_id': [100, 'Product Variant'],
    'categ_id': [5, 'Food'],
    'company_id': [1, 'My Company']
}
```

### 5. product.category
```javascript
{
    // Many2one fields
    'parent_id': [1, 'Parent Category'],
    
    // Computed fields
    'parent_path': '1/5/'
}
```

### 6. product.template.attribute.line
```javascript
{
    // Many2one fields
    'product_tmpl_id': [10, 'Product Template'],
    'attribute_id': [3, 'Size'],
    
    // Many2many fields
    'value_ids': [10, 11, 12],
    'product_template_value_ids': [20, 21]
}
```

## Common Issues and Solutions

### Issue 1: "Cannot convert object to primitive value"
**Cause**: Relational field is not an array
```javascript
// ❌ Wrong
data.product_tag_ids = { id: 1, name: 'Tag' }

// ✅ Correct
data.product_tag_ids = [1, 2, 3]
```

### Issue 2: Many2one field rejected
**Cause**: Many2one field sent as string instead of array or number
```javascript
// ❌ Wrong
data.categ_id = 'Food'

// ✅ Correct (either format works)
data.categ_id = [5, 'Food']  // or
data.categ_id = 5
```

### Issue 3: "Model create failed"
**Cause**: Missing required fields or wrong data type

**Solution**: Use dual create approach:
```javascript
try {
    this.data.create(modelName, transformedData);  // Try data service first
} catch (error) {
    this.models[modelName].create(transformedData);  // Fallback to direct create
}
```

## Backend Sync Methods

### `get_all_product_models_for_sync(config_id)`
Returns all models in proper format:
```python
{
    'success': True,
    'models': {
        'product.product': [...],      # List of records
        'product.category': [...],
        'product.pricelist': [...],
        # ... all 11 models
    }
}
```

### `sync_all_product_models_since(last_sync_date, config_id)`
Returns incremental updates:
```python
{
    'success': True,
    'sync_date': '2026-01-03 10:30:00',
    'models': {
        'product.product': {
            'records': [...],          # Updated/new records
            'deleted_ids': [1, 2, 3]   # Deleted record IDs
        },
        # ... other models
    }
}
```

## Best Practices

1. **Store server format directly in IndexedDB**
   - No transformation on save
   - Keep original Many2one format `[id, name]`
   - Keep original Many2many format `[id1, id2, ...]`

2. **Transform only when loading into POS**
   - Ensure arrays are arrays
   - Keep Many2one as-is (both formats work)
   - Use `_transformRecordDataForCreate()`

3. **Use dual create approach**
   ```javascript
   try {
       this.data.create(modelName, data);  // Preferred
   } catch (error) {
       this.models[modelName].create(data);  // Fallback
   }
   ```

4. **Log errors with full record data**
   ```javascript
   catch (error) {
       console.error(`Failed to create ${modelName}:`, error);
       console.error('Record data:', recordData);
   }
   ```

5. **Validate data before create**
   ```javascript
   if (!recordData.id) {
       console.warn('Skipping record without ID');
       return;
   }
   ```

## Summary

| Aspect | Format |
|--------|--------|
| **Server Output** | Odoo `search_read()` format |
| **IndexedDB Storage** | Same as server (no transform) |
| **POS Loading** | Transform arrays only |
| **Many2one** | `[id, name]` or `id` both work |
| **Many2many** | Must be array `[id1, id2, ...]` |
| **One2many** | Must be array `[id1, id2, ...]` |
| **Create Method** | Try `data.create()` then `model.create()` |
