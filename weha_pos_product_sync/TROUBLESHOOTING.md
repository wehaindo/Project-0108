# Data Format Troubleshooting Guide

## Common Errors and Solutions

### Error 1: "Cannot convert object to primitive value"

**Full Error:**
```
TypeError: Cannot convert object to primitive value
    at Array.push (<anonymous>)
    at _transformRecordDataForCreate
```

**Cause:**
A Many2many or One2many field contains an object instead of an array.

**Example of Wrong Data:**
```javascript
{
    product_tag_ids: {id: 1, name: 'Tag'}  // ❌ Object
}
```

**Correct Format:**
```javascript
{
    product_tag_ids: [1, 2, 3]  // ✅ Array of IDs
}
```

**Solution:**
Check your `_transformRecordDataForCreate()` method ensures all relational fields are arrays:
```javascript
if (!Array.isArray(data[field])) {
    data[field] = data[field] ? [data[field]] : [];
}
```

---

### Error 2: "Model create failed" or "this.models[modelName].create is not a function"

**Full Error:**
```
Error: Model create failed
    at loadAllModelsFromIndexedDB
```

**Cause:**
Model doesn't exist in POS or data format is incorrect.

**Solutions:**

1. **Check model exists:**
```javascript
if (!this.models[modelName]) {
    console.log(`Model ${modelName} not available, skipping`);
    continue;
}
```

2. **Use dual create approach:**
```javascript
try {
    this.data.create(modelName, transformedData);  // Try data service
} catch (createError) {
    this.models[modelName].create(transformedData);  // Fallback
}
```

3. **Log the data to debug:**
```javascript
catch (error) {
    console.error(`Failed to create ${modelName}:`, error);
    console.error('Record data:', recordData);
}
```

---

### Error 3: Many2one field rejected

**Full Error:**
```
ValueError: Invalid field value for categ_id
```

**Cause:**
Many2one field sent as string or wrong format.

**Wrong Formats:**
```javascript
categ_id: 'Food'              // ❌ String
categ_id: {id: 5, name: 'Food'}  // ❌ Object
```

**Correct Formats:**
```javascript
categ_id: [5, 'Food']  // ✅ [id, display_name]
// or
categ_id: 5            // ✅ Just the ID
// or
categ_id: false        // ✅ No value
```

**Solution:**
Keep Many2one fields in server format - no transformation needed:
```javascript
// Don't transform Many2one fields
// Both [id, name] and numeric id work in POS
```

---

### Error 4: "Active field does not exist"

**Full Error:**
```
ValueError: Invalid field product.category.active in leaf
```

**Cause:**
Backend trying to filter by a field that doesn't exist on the model.

**Solution:**
Check field existence before using in domain:
```python
# In pos_session.py
has_active = 'active' in self.env[model_name]._fields
has_available = 'available_in_pos' in self.env[model_name]._fields

if has_active:
    domain.append(('active', '=', True))
if has_available:
    domain.append(('available_in_pos', '=', True))
```

---

### Error 5: IndexedDB transaction error

**Full Error:**
```
DOMException: Failed to execute 'transaction' on 'IDBDatabase': 
One of the specified object stores was not found.
```

**Cause:**
IndexedDB schema version mismatch or object store doesn't exist.

**Solution:**
1. Check version is correct:
```javascript
const DB_VERSION = 2;  // Must match current version
```

2. Ensure all stores are created in `onupgradeneeded`:
```javascript
onupgradeneeded: (event) => {
    const db = event.target.result;
    if (!db.objectStoreNames.contains('product.product')) {
        db.createObjectStore('product.product', { keyPath: 'id' });
    }
}
```

3. Clear old data and re-init:
```javascript
// In browser console
indexedDB.deleteDatabase('pos_products_1');
location.reload();
```

---

### Error 6: "sync_all_product_models_since does not exist"

**Full Error:**
```
AttributeError: The method 'pos.session.sync_all_product_models_since' does not exist.
```

**Cause:**
Backend method not found (module not upgraded or method name typo).

**Solution:**
1. Upgrade the module:
```bash
./odoo-bin -u weha_pos_product_sync -d your_database
```

2. Check method exists in `models/pos_session.py`:
```python
@api.model
def sync_all_product_models_since(self, last_sync_date, config_id):
    # ...implementation
```

3. Restart Odoo server after upgrade.

---

### Error 7: Empty data loaded but products exist

**Symptom:**
Console shows "Loaded 0 products" but database has thousands of products.

**Cause:**
Local storage disabled or data not saved to IndexedDB.

**Solution:**
1. Check config setting:
```python
# In POS config
config.enable_local_product_storage = True
```

2. Check console for IndexedDB errors:
```javascript
console.log('[POS Sync] IndexedDB status:', !!this.productStorage);
```

3. Force initial download:
```javascript
await this.downloadAndSaveAllModels();
```

---

### Error 8: Duplicate records in POS

**Symptom:**
Products appear multiple times in product list.

**Cause:**
Records created multiple times without checking existence.

**Solution:**
Always check before creating:
```javascript
const existingRecord = this.models[modelName].get(recordData.id);
if (!existingRecord) {
    this.data.create(modelName, transformedData);
} else {
    console.log(`Record ${recordData.id} already exists, skipping`);
}
```

---

### Error 9: Slow sync performance

**Symptom:**
Background sync takes > 10 seconds for small updates.

**Cause:**
Loading too many records or inefficient queries.

**Solutions:**
1. Use proper indexing on `write_date`:
```python
_sql_constraints = [
    ('write_date_index', 'CREATE INDEX IF NOT EXISTS idx_write_date ON product_product(write_date)', ''),
]
```

2. Limit batch size:
```python
records = model.search_read(
    domain,
    fields,
    limit=500,  # Don't load all at once
    order='write_date DESC'
)
```

3. Use field-specific queries:
```python
# Only load needed fields
fields = ['id', 'name', 'write_date']  # Not all fields
```

---

### Error 10: Data service vs Direct create confusion

**Symptom:**
`this.data.create()` works for some models but not others.

**Explanation:**
In Odoo 18, there are two ways to create records:

1. **Data Service (Preferred):**
```javascript
this.data.create('product.product', data);
```
- Proper Odoo 18 way
- Handles relations automatically
- Better error messages

2. **Direct Model Create (Fallback):**
```javascript
this.models['product.product'].create(data);
```
- Legacy method
- More forgiving with data format
- Use as fallback

**Solution:**
Always use dual approach:
```javascript
try {
    this.data.create(modelName, transformedData);
} catch (createError) {
    console.warn(`Data service failed for ${modelName}, using direct create`);
    this.models[modelName].create(transformedData);
}
```

---

## Debugging Checklist

When troubleshooting data format issues:

- [ ] Check console for error messages
- [ ] Verify data format matches server output
- [ ] Confirm IndexedDB has data (Application tab in DevTools)
- [ ] Check model exists in `this.models`
- [ ] Verify relational fields are arrays
- [ ] Check Many2one fields are [id, name] or numeric
- [ ] Ensure dual create approach is used
- [ ] Log full record data when errors occur
- [ ] Check module is upgraded in Odoo
- [ ] Verify config setting is enabled

---

## Useful Console Commands

### Check IndexedDB data:
```javascript
// Get all product counts
await pos.productStorage.getAllCounts()

// Get specific record
await pos.productStorage.getRecord('product.product', 123)

// Check last sync date
await pos.productStorage.getLastSyncDate()
```

### Check POS models:
```javascript
// List all models
Object.keys(pos.models)

// Get product count in POS
pos.models['product.product'].getAll().length

// Get specific product
pos.models['product.product'].get(123)
```

### Check sync status:
```javascript
pos.getSyncStatus()
```

### Force sync:
```javascript
await pos.syncAllModelsInBackground()
```

### Clear and resync:
```javascript
await pos.clearLocalProductDB()
location.reload()
```

---

## Data Format Validation Script

Add this to your code to validate data format:
```javascript
function validateRecordFormat(modelName, recordData) {
    const errors = [];
    
    // Check ID exists
    if (!recordData.id) {
        errors.push('Missing id field');
    }
    
    // Get relation fields for model
    const relationFields = {
        'product.product': ['product_tag_ids', 'taxes_id', 'pos_categ_ids'],
        'product.template': ['product_tag_ids', 'taxes_id', 'attribute_line_ids']
    };
    
    // Validate relation fields are arrays
    for (const field of relationFields[modelName] || []) {
        if (recordData[field] !== undefined && 
            recordData[field] !== null && 
            !Array.isArray(recordData[field])) {
            errors.push(`${field} must be an array, got ${typeof recordData[field]}`);
        }
    }
    
    if (errors.length > 0) {
        console.error(`Validation failed for ${modelName} ${recordData.id}:`, errors);
        return false;
    }
    
    return true;
}
```

Use it before creating records:
```javascript
if (validateRecordFormat(modelName, recordData)) {
    const data = this._transformRecordDataForCreate(modelName, recordData);
    this.data.create(modelName, data);
} else {
    console.warn(`Skipping invalid record ${recordData.id}`);
}
```
