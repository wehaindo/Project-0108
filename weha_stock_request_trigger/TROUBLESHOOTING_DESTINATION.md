# Troubleshooting: Stock Request Destination Issues

## Problem: Transfer shows DC → DC instead of DC → Store

### Symptoms
When creating a stock request from Store:
- ❌ Transfer created: DC/Stock → DC/Stock
- ✅ Expected: DC/Stock → Store/Stock

### Root Causes

#### Cause 1: Wrong Warehouse Selected (Most Common)

**Problem:** When creating replenishment rule for Store A, you selected DC warehouse instead of Store warehouse.

**Configuration Error:**
```
Replenishment Rule for Store A:
- Operating Unit: Store A ✅
- Warehouse: DC East Warehouse ❌ (WRONG!)
- Location: DC East/Stock ❌ (WRONG!)
```

**Correct Configuration:**
```
Replenishment Rule for Store A:
- Operating Unit: Store A ✅
- Warehouse: Store A Warehouse ✅
- Location: Store A/Stock ✅
```

**How to Fix:**
1. Open the replenishment rule
2. Change Warehouse from "DC East Warehouse" to "Store A Warehouse"
3. Change Location to "Store A/Stock"
4. Save

Now the warehouse_id domain will help prevent this:
- Warehouse dropdown will only show warehouses belonging to selected OU
- Location dropdown will only show locations in selected warehouse

---

#### Cause 2: Route Configuration Error

**Problem:** Route's pull rule has wrong source or destination configured.

**Check Route Configuration:**
```
Inventory > Configuration > Routes > [Your Route]

Example: "DC East → Store A"

Rule should be:
- Action: Pull From
- Source Location: DC East/Stock ✅
- Destination Location: Store A/Stock ✅
- Picking Type: Store A: Internal Transfers ✅
```

**Common Mistakes:**
```
❌ Source: DC East/Stock, Destination: DC East/Stock (both same!)
❌ Picking Type: DC East: Internal Transfers (should be Store's)
❌ Action: Push To (should be Pull From for stock requests)
```

**How to Fix:**
1. Navigate to Inventory > Configuration > Routes
2. Find your route (e.g., "DC East → Store A")
3. Click on the route
4. Check the Rules tab
5. Edit the rule:
   - Source Location: DC East warehouse location
   - Destination Location: Store A warehouse location
   - Picking Type: Store A's internal transfer type
6. Save

---

#### Cause 3: No Route Configured

**Problem:** Replenishment rule has no route selected.

**Result:** Stock request created but uses default behavior, which might pick wrong locations.

**How to Fix:**
1. Open replenishment rule
2. Scroll to "Source (from Hierarchy)" section
3. Select appropriate Route (e.g., "DC East → Store A")
4. Save

---

## Understanding the Flow

### Correct Setup Example

**Operating Units:**
```
HO (Head Office)
└── DC East (Distribution Center)
    └── Store A (Retail Store)
```

**Warehouses:**
```
HO Warehouse
- Location: HO/Stock

DC East Warehouse  
- Location: DCE/Stock

Store A Warehouse
- Location: STA/Stock
```

**Replenishment Rule for Store A:**
```
Operating Unit: Store A
Warehouse: Store A Warehouse
Location: STA/Stock
Product: Product X
Minimum: 10
Maximum: 50
Route: DC East → Store A
Source OU: DC East
```

**Route: "DC East → Store A"**
```
Pull Rule:
- Source: DCE/Stock
- Destination: STA/Stock
- Picking Type: Store A: Internal Transfers
```

### What Happens When Stock Low

**Step 1: Stock Request Created**
```
Stock Request:
- Product: Product X
- Quantity: 45 units
- Operating Unit: Store A
- Warehouse: Store A Warehouse
- Location: STA/Stock (DESTINATION)
- Route: DC East → Store A
```

**Step 2: Route Determines Source**
```
Route "DC East → Store A" says:
- Pull from: DCE/Stock (SOURCE)
- Deliver to: STA/Stock (DESTINATION)
```

**Step 3: Transfer Created**
```
Internal Transfer:
- From: DCE/Stock ✅
- To: STA/Stock ✅
- Picking Type: Store A: Internal Transfers
```

---

## Quick Diagnosis Checklist

When you see DC → DC transfer:

### ✅ Check 1: Replenishment Rule Warehouse
```
Open: Replenishment Rule
Check: Warehouse field
Expected: Store's warehouse (e.g., "Store A Warehouse")
If wrong: Change to correct warehouse
```

### ✅ Check 2: Replenishment Rule Location
```
Open: Replenishment Rule
Check: Location field
Expected: Store's stock location (e.g., "STA/Stock")
If wrong: Change to correct location
```

### ✅ Check 3: Route Selected
```
Open: Replenishment Rule
Check: Route field in "Source" section
Expected: Route name like "DC East → Store A"
If empty: Select appropriate route
```

### ✅ Check 4: Route Configuration
```
Open: Inventory > Configuration > Routes > [Route]
Check: Rules tab
Verify:
- Source Location = DC location
- Destination Location = Store location
- Picking Type = Store's internal transfer type
```

### ✅ Check 5: Stock Request Details
```
Open: Created Stock Request
Check:
- Warehouse = Store warehouse ✅
- Location = Store location ✅
- Route = Correct route ✅
```

---

## Prevention: Updated Field Constraints

The module now has domain constraints to prevent mistakes:

### 1. Warehouse Domain
```python
warehouse_id = fields.Many2one(
    domain="[('operating_unit_id', '=', operating_unit_id)]"
)
```

**Effect:** Only warehouses belonging to the selected Operating Unit appear in dropdown.

**Example:**
- Select "Store A" as Operating Unit
- Warehouse dropdown shows only "Store A Warehouse"
- DC warehouses won't appear

### 2. Location Domain
```python
location_id = fields.Many2one(
    domain="[('usage', '=', 'internal'), ('warehouse_id', '=', warehouse_id)]"
)
```

**Effect:** Only locations in the selected warehouse appear.

**Example:**
- Select "Store A Warehouse"
- Location dropdown shows only locations in Store A warehouse
- DC locations won't appear

### 3. Enhanced Help Text

All fields now have clearer descriptions:

```
Operating Unit: "...the DESTINATION (e.g., Store requesting stock)"
Warehouse: "...must belong to the requesting OU (Store warehouse)"
Location: "...destination location in Store warehouse"
Source OU: "...where stock will come FROM"
Route: "...REQUIRED for automatic transfers!"
```

---

## Testing Your Configuration

### Test 1: Manual Creation
```
1. Create replenishment rule for Store A
2. Set stock below minimum
3. Click "Create Stock Request" button
4. Check created stock request:
   - Warehouse = Store A Warehouse ✅
   - Location = STA/Stock ✅
5. Confirm stock request
6. Check transfer:
   - From = DCE/Stock ✅
   - To = STA/Stock ✅
```

### Test 2: Check Route Separately
```
1. Inventory > Configuration > Routes
2. Open route: "DC East → Store A"
3. Go to Rules tab
4. Verify:
   - Source Location contains "DC"
   - Destination Location contains "Store"
   - Picking Type belongs to Store
```

### Test 3: Validate Warehouse Assignment
```
1. Inventory > Configuration > Warehouses
2. For each warehouse, check:
   - HO Warehouse: Operating Unit = Head Office
   - DC East Warehouse: Operating Unit = DC East
   - Store A Warehouse: Operating Unit = Store A
```

---

## Common Scenarios & Solutions

### Scenario 1: "I can't see my Store warehouse"

**Cause:** Warehouse not assigned to Operating Unit

**Solution:**
```
1. Inventory > Configuration > Warehouses
2. Open Store A Warehouse
3. Set Operating Unit = Store A
4. Save
```

### Scenario 2: "Route field is empty"

**Cause:** No route created yet

**Solution:** See [ROUTE_CONFIGURATION_GUIDE.md](ROUTE_CONFIGURATION_GUIDE.md)

Quick create:
```
1. Inventory > Configuration > Routes > Create
2. Name: "DC East → Store A"
3. Add Rule:
   - Action: Pull From
   - Source: DCE/Stock
   - Destination: STA/Stock
4. Save
```

### Scenario 3: "Transfer created but wrong direction"

**Cause:** Route rule has reversed source/destination

**Solution:**
```
1. Open Route
2. Edit Rule
3. Swap Source and Destination if needed
4. Or check Picking Type matches destination
```

### Scenario 4: "Multiple transfers created"

**Cause:** Multiple rules or complex route configuration

**Solution:**
```
1. Check only one replenishment rule per product/OU/location
2. Verify route has single pull rule
3. Check no conflicting routes on warehouse
```

---

## Summary

**Key Points:**

1. **Warehouse = Destination** (Store warehouse, not DC)
2. **Location = Destination** (Store location, not DC)
3. **Route determines source** (pulls from DC to Store)
4. **Domain constraints prevent errors** (only shows valid options)

**Golden Rule:**
> Replenishment rule should be configured from the perspective of the **requestor** (Store), not the **supplier** (DC)!

**When in doubt:**
- Operating Unit = Who needs stock? → Store
- Warehouse = Where does stock go? → Store warehouse
- Location = Final destination? → Store location
- Route = How to get there? → DC → Store
- Source OU = Where from? → DC (computed)

---

## Still Not Working?

### Debug Steps:

1. **Check warehouse.operating_unit_id:**
```python
# In Odoo shell or debug
warehouse = env['stock.warehouse'].browse(WAREHOUSE_ID)
print(f"Warehouse: {warehouse.name}")
print(f"Operating Unit: {warehouse.operating_unit_id.name}")
```

2. **Check location.warehouse_id:**
```python
location = env['stock.location'].browse(LOCATION_ID)
print(f"Location: {location.complete_name}")
print(f"Warehouse: {location.warehouse_id.name}")
```

3. **Check route rules:**
```python
route = env['stock.route'].browse(ROUTE_ID)
for rule in route.rule_ids:
    print(f"Rule: {rule.name}")
    print(f"Source: {rule.location_src_id.complete_name}")
    print(f"Dest: {rule.location_dest_id.complete_name}")
```

4. **Check stock request:**
```python
request = env['stock.request'].browse(REQUEST_ID)
print(f"Warehouse: {request.warehouse_id.name} (OU: {request.operating_unit_id.name})")
print(f"Location: {request.location_id.complete_name}")
print(f"Route: {request.route_id.name if request.route_id else 'NONE'}")
```

### Get Help:

- Review module README.md
- Check ROUTE_CONFIGURATION_GUIDE.md
- Verify demo data configuration
- Check Odoo logs for errors

---

## Version

- Module: weha_stock_request_trigger
- Version: 18.0.1.0.0
- Updated: January 11, 2026
