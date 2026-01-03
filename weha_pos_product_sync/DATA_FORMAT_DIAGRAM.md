# Data Format Quick Reference

## Data Flow Diagram

```
┌─────────────────────────────────────────────────────────────────────┐
│                         DATA FORMAT FLOW                            │
└─────────────────────────────────────────────────────────────────────┘

┌──────────────┐         ┌──────────────┐         ┌──────────────┐
│   SERVER     │         │  IndexedDB   │         │     POS      │
│   (Odoo)     │────────▶│   Storage    │────────▶│   Models     │
└──────────────┘         └──────────────┘         └──────────────┘
     search_read()       save as-is           transform + create()


┌─────────────────────────────────────────────────────────────────────┐
│ STEP 1: Server → IndexedDB (NO TRANSFORMATION)                      │
└─────────────────────────────────────────────────────────────────────┘

Server Output (search_read):
{
    id: 123,
    name: "Product Name",
    categ_id: [5, "Food"],              ← Many2one: [id, display_name]
    product_tag_ids: [1, 2, 3],         ← Many2many: array of IDs
    packaging_ids: [10, 11],            ← One2many: array of IDs
    write_date: "2026-01-03 10:30:00"
}
                    ↓ (store directly)
IndexedDB:
{
    id: 123,
    name: "Product Name",
    categ_id: [5, "Food"],              ← SAME FORMAT
    product_tag_ids: [1, 2, 3],         ← SAME FORMAT
    packaging_ids: [10, 11],            ← SAME FORMAT
    write_date: "2026-01-03 10:30:00"
}


┌─────────────────────────────────────────────────────────────────────┐
│ STEP 2: IndexedDB → POS (MINIMAL TRANSFORMATION)                    │
└─────────────────────────────────────────────────────────────────────┘

IndexedDB Data:
{
    id: 123,
    categ_id: [5, "Food"],
    product_tag_ids: [1, 2, 3]
}
                    ↓ (_transformRecordDataForCreate)
Transformed:
{
    id: 123,
    categ_id: [5, "Food"],              ← Keep as-is (both formats work)
    product_tag_ids: [1, 2, 3]          ← Ensure it's an array ✓
}
                    ↓ (dual create approach)
POS Models:
Try: this.data.create('product.product', data)         ← Preferred
Catch: this.models['product.product'].create(data)     ← Fallback


┌─────────────────────────────────────────────────────────────────────┐
│ FIELD TYPE FORMATS                                                  │
└─────────────────────────────────────────────────────────────────────┘

┌──────────────┬─────────────────────┬────────────────────┬───────────┐
│ Field Type   │ Server Format       │ IndexedDB          │ POS       │
├──────────────┼─────────────────────┼────────────────────┼───────────┤
│ Many2one     │ [id, 'Name']        │ [id, 'Name']       │ Same ✓    │
│              │ or false            │ or false           │           │
│              │ Example:            │ Example:           │           │
│              │ [5, 'Food']         │ [5, 'Food']        │ Both work:│
│              │                     │                    │ [5,'Food']│
│              │                     │                    │ or 5      │
├──────────────┼─────────────────────┼────────────────────┼───────────┤
│ Many2many    │ [id1, id2, id3]     │ [id1, id2, id3]    │ Must be   │
│              │ Example:            │ Example:           │ array ✓   │
│              │ [1, 2, 3]           │ [1, 2, 3]          │ [1, 2, 3] │
├──────────────┼─────────────────────┼────────────────────┼───────────┤
│ One2many     │ [id1, id2, id3]     │ [id1, id2, id3]    │ Must be   │
│              │ Example:            │ Example:           │ array ✓   │
│              │ [10, 11, 12]        │ [10, 11, 12]       │ [10,11,12]│
├──────────────┼─────────────────────┼────────────────────┼───────────┤
│ String       │ "Product Name"      │ "Product Name"     │ Same ✓    │
├──────────────┼─────────────────────┼────────────────────┼───────────┤
│ Float        │ 99.99               │ 99.99              │ Same ✓    │
├──────────────┼─────────────────────┼────────────────────┼───────────┤
│ Integer      │ 123                 │ 123                │ Same ✓    │
├──────────────┼─────────────────────┼────────────────────┼───────────┤
│ Boolean      │ true/false          │ true/false         │ Same ✓    │
├──────────────┼─────────────────────┼────────────────────┼───────────┤
│ Date/DateTime│ "2026-01-03 10:30"  │ "2026-01-03 10:30" │ Same ✓    │
└──────────────┴─────────────────────┴────────────────────┴───────────┘


┌─────────────────────────────────────────────────────────────────────┐
│ TRANSFORMATION RULES                                                │
└─────────────────────────────────────────────────────────────────────┘

✅ DO:
  - Store server data in IndexedDB WITHOUT modification
  - Ensure Many2many/One2many are arrays when loading to POS
  - Use dual create: data.create() → model.create()
  - Log errors with full record data for debugging

❌ DON'T:
  - Transform Many2one from [id, name] to just id (keep original)
  - Convert arrays to objects or other structures
  - Modify field names or add custom fields
  - Skip validation of required fields


┌─────────────────────────────────────────────────────────────────────┐
│ COMMON ERRORS & SOLUTIONS                                           │
└─────────────────────────────────────────────────────────────────────┘

ERROR: "Cannot convert object to primitive value"
├─ Cause: Relational field is not an array
├─ Wrong: product_tag_ids: {id: 1, name: 'Tag'}
└─ Fix:   product_tag_ids: [1, 2, 3]

ERROR: "Model create failed"
├─ Cause: Missing required fields or wrong format
└─ Fix:   Use dual create approach with error logging

ERROR: Many2one field rejected
├─ Cause: Field sent as string instead of array/number
├─ Wrong: categ_id: 'Food'
└─ Fix:   categ_id: [5, 'Food'] or categ_id: 5


┌─────────────────────────────────────────────────────────────────────┐
│ CODE SNIPPETS                                                       │
└─────────────────────────────────────────────────────────────────────┘

Server (Python):
────────────────
products = self.env['product.product'].search_read(
    [('available_in_pos', '=', True)],
    ['id', 'name', 'categ_id', 'product_tag_ids']
)
# Returns: [{'id': 1, 'categ_id': [5, 'Food'], 'product_tag_ids': [1,2,3]}]

Storage (JavaScript):
─────────────────────
// Save directly without transformation
await productStorage.saveRecords('product.product', serverData);

Loading (JavaScript):
─────────────────────
const records = await productStorage.getAllRecords('product.product');
for (const recordData of records) {
    const data = this._transformRecordDataForCreate(modelName, recordData);
    try {
        this.data.create(modelName, data);  // Try data service
    } catch (error) {
        this.models[modelName].create(data);  // Fallback
    }
}


┌─────────────────────────────────────────────────────────────────────┐
│ SUPPORTED MODELS (11 total)                                         │
└─────────────────────────────────────────────────────────────────────┘

1. product.product              ← Main products
2. product.template             ← Product templates
3. product.category             ← Categories
4. product.pricelist            ← Pricelists
5. product.pricelist.item       ← Pricelist items
6. product.packaging            ← Product packaging
7. product.tag                  ← Product tags
8. product.attribute            ← Attributes
9. product.attribute.value      ← Attribute values
10. product.template.attribute.line
11. product.template.attribute.value
```
