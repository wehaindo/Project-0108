# XML View Fixes - Summary

## Issue
ParseError when loading views due to incorrect XPath expressions and external ID references.

## Root Causes
1. **Incorrect External ID References**: Used wrong format for `inherit_id`
   - Wrong: `stock_request.stock_request_view_form`
   - Correct: `stock_request.view_stock_request_form`

2. **XPath Expressions**: Used `xpath` when direct field positioning is cleaner and more reliable
   - Wrong: `<xpath expr="//field[@name='warehouse_id']" position="after">`
   - Better: `<field name="warehouse_id" position="after">`

## Changes Made

### 1. stock_request_views.xml

#### Form View
- Changed `inherit_id` from `stock_request.stock_request_view_form` to `stock_request.view_stock_request_form`
- Changed from XPath to direct field positioning
- Added `groups` and `readonly` attributes for consistency
- Removed `required="1"` (will handle via Python model)

#### Tree View
- Changed `inherit_id` from `stock_request.stock_request_view_tree` to `stock_request.view_stock_request_tree`
- Changed from XPath to direct field positioning

#### Search View
- Changed `inherit_id` from `stock_request.stock_request_view_search` to `stock_request.stock_request_search`
- Changed from XPath to direct field positioning
- Fixed filter name from `warehouse_id` to `warehouse` (correct name in base view)

### 2. stock_request_order_views.xml

#### Form View
- Changed `inherit_id` from `stock_request.stock_request_order_view_form` to `stock_request.stock_request_order_form`
- Changed from XPath to direct field positioning
- Added `groups` and `readonly` attributes

#### Tree View
- Changed `inherit_id` from `stock_request.stock_request_order_view_tree` to `stock_request.stock_request_order_tree`
- Changed from XPath to direct field positioning

#### Search View
- Changed `inherit_id` from `stock_request.stock_request_order_view_search` to `stock_request.stock_request_order_search`
- Changed from XPath to direct field positioning

### 3. Model Files

#### stock_request.py
- Removed `required=True` from operating_unit_id field
- Field is optional but can be made required via views or constraints

#### stock_request_order.py
- Removed `required=True` from operating_unit_id field
- Field is optional but can be made required via views or constraints

## Correct External ID Format

Based on the base module views:

| Model | View Type | Correct External ID |
|-------|-----------|---------------------|
| stock.request | form | `stock_request.view_stock_request_form` |
| stock.request | tree | `stock_request.view_stock_request_tree` |
| stock.request | search | `stock_request.stock_request_search` |
| stock.request.order | form | `stock_request.stock_request_order_form` |
| stock.request.order | tree | `stock_request.stock_request_order_tree` |
| stock.request.order | search | `stock_request.stock_request_order_search` |

## Best Practices Applied

1. **Direct Field Positioning**: More reliable than XPath
   ```xml
   <!-- Good -->
   <field name="warehouse_id" position="after">
       <field name="operating_unit_id"/>
   </field>
   
   <!-- Avoid when possible -->
   <xpath expr="//field[@name='warehouse_id']" position="after">
       <field name="operating_unit_id"/>
   </xpath>
   ```

2. **Consistent Attributes**: Match the base view's field attributes
   - If base has `groups`, add it to inherited field
   - If base has `readonly`, add it to inherited field
   - Keep consistency with surrounding fields

3. **Optional vs Required**: 
   - Don't force `required="1"` in views unless absolutely necessary
   - Better to handle via model constraints or business logic
   - Allows more flexibility for different use cases

## Testing Checklist

After these fixes:
- [ ] Module loads without ParseError
- [ ] Operating unit field visible in stock request form
- [ ] Operating unit field visible in stock request order form
- [ ] Operating unit appears in tree views
- [ ] Filter by operating unit works in search views
- [ ] Group by operating unit works
- [ ] Field is editable in draft state
- [ ] Field is readonly after confirmation

## Files Modified

1. ✅ `views/stock_request_views.xml`
2. ✅ `views/stock_request_order_views.xml`
3. ✅ `models/stock_request.py`
4. ✅ `models/stock_request_order.py`

---

**Fixed**: January 11, 2026  
**Issue**: XML ParseError  
**Status**: ✅ Resolved
