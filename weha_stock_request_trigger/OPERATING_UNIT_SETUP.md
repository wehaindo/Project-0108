# Operating Unit Setup for Stock Replenishment

## The Problem

When creating stock requests from Store (requesting OU) to DC (source OU), you get this error:

```
Configuration error. The Stock moves must be related to a location 
(source or destination) that belongs to the requesting Operating Unit.
```

## Understanding the Constraint

The `stock_operating_unit` module has this constraint on stock moves:

```python
ou_pick = picking.operating_unit_id      # Picking's OU
ou_src = source_location.operating_unit_id   # Source location's OU
ou_dest = dest_location.operating_unit_id    # Destination location's OU

# Error if BOTH source AND destination don't match picking's OU
if ou_src and ou_pick and (ou_src != ou_pick) and (ou_dest != ou_pick):
    raise UserError("Configuration error...")
```

**Rule**: At least ONE of (source or destination) must belong to the picking's OU.

## The Root Cause

### Scenario: Store requests stock from DC

1. **Stock Request Setup**:
   - `operating_unit_id` = Store OU
   - `warehouse_id` = Store Warehouse
   - `location_id` = Store/Stock (destination)

2. **Route Rule Setup** (THIS IS CRITICAL!):
   - Route Name: "DC → Store A"
   - Pull Rule Source: DC/Stock
   - Pull Rule Destination: Store A/Stock
   - **Route's Warehouse**: ??? ← THIS DETERMINES PICKING'S OU!

3. **What Happens**:
   - Procurement creates picking using route's warehouse
   - Picking's OU = Route's warehouse OU
   - If route's warehouse = DC Warehouse → Picking OU = DC OU ❌
   - Move: DC/Stock (DC OU) → Store/Stock (Store OU)
   - Constraint fails: NEITHER location belongs to picking's OU (DC)

## The Solution

### Option 1: Route Warehouse Must Be DESTINATION (Recommended)

**Configure the route to use the DESTINATION warehouse (Store)**:

1. Go to **Inventory > Configuration > Routes**
2. Find/Create route "DC → Store A"
3. Set **Warehouse** = Store A Warehouse (not DC!)
4. Pull Rule:
   - **Action**: Pull From
   - **Source Location**: DC/Stock
   - **Destination Location**: Store A/Stock

**Why this works**:
- Picking's OU = Store OU (from route's warehouse)
- Destination = Store/Stock (belongs to Store OU) ✅
- Constraint passes!

### Option 2: Use Stock Request's Warehouse (Automatic)

Our module now overrides `_prepare_procurement_values()` to **force** the warehouse:

```python
def _prepare_procurement_values(self, group_id=False):
    vals = super()._prepare_procurement_values(group_id=group_id)
    # FORCE warehouse to be stock request's warehouse (Store)
    if self.warehouse_id:
        vals['warehouse_id'] = self.warehouse_id
    return vals
```

This ensures pickings use Store's warehouse, giving picking OU = Store OU.

### Option 3: Multi-Step Routes (Advanced)

For inter-OU transfers, use a 2-step approach:

**Step 1**: DC → Transit Location (belongs to DC OU)
- Picking 1: DC OU
- Source: DC/Stock (DC OU) ✓
- Dest: Transit (DC OU) ✓

**Step 2**: Transit → Store (belongs to Store OU)
- Picking 2: Store OU
- Source: Transit (Store OU) ✓
- Dest: Store/Stock (Store OU) ✓

## Verification Checklist

### 1. Check Stock Request Configuration

```python
# In Odoo debug mode or log output
Stock Request: SR0001
- operating_unit_id: Store A (ID: 3)
- warehouse_id: Store A Warehouse (OU: Store A)
- location_id: Store A/Stock (OU: Store A)
```

### 2. Check Route Configuration

```sql
-- In Odoo shell or database
SELECT r.name, w.name as warehouse, ou.name as ou
FROM stock_route r
LEFT JOIN stock_warehouse w ON r.warehouse_ids::text LIKE '%'||w.id||'%'
LEFT JOIN operating_unit ou ON w.operating_unit_id = ou.id
WHERE r.name LIKE '%DC%Store%';
```

### 3. Check Pull Rule Configuration

```python
# In route form view
Route: DC → Store A
Pull Rules:
  Rule 1:
    - Action: Pull From
    - Source Location: DC/Stock (OU: DC)
    - Destination Location: Store A/Stock (OU: Store A)
    - Warehouse: Store A Warehouse (OU: Store A) ← CRITICAL!
```

### 4. Check Move/Picking After Creation

```python
# From log output or Odoo debug
Move: SR0001-1
- Picking: WH/IN/00123
- Picking OU: Store A ← MUST match destination's OU
- Source: DC/Stock (OU: DC)
- Destination: Store A/Stock (OU: Store A) ← Matches picking OU ✓
```

## Troubleshooting Steps

### Step 1: Enable Logging

The module now logs detailed information. Check Odoo logs for:

```
Stock Request SR0001: OU=Store A, Warehouse=Store A Warehouse, Location=Store A/Stock
  Move SR0001-1: Picking OU=DC, Source=DC/Stock (OU=DC), Dest=Store A/Stock (OU=Store A)
```

If "Picking OU=DC" → **PROBLEM**: Route is using DC warehouse!

### Step 2: Check Route Warehouse

```python
# In Odoo shell
route = env['stock.route'].search([('name', '=', 'DC → Store A')])
print(f"Route: {route.name}")
print(f"Warehouse: {route.warehouse_ids.mapped('name')}")
print(f"Warehouse OU: {route.warehouse_ids.mapped('operating_unit_id.name')}")
```

**Expected**: Warehouse OU should be **Store A** (destination), not DC (source).

### Step 3: Check Location Operating Units

```python
# In Odoo shell
dc_loc = env['stock.location'].search([('complete_name', '=', 'DC/Stock')])
store_loc = env['stock.location'].search([('complete_name', '=', 'Store A/Stock')])

print(f"DC Location OU: {dc_loc.operating_unit_id.name}")  # Should be: DC
print(f"Store Location OU: {store_loc.operating_unit_id.name}")  # Should be: Store A
```

### Step 4: Manually Fix Picking OU (Temporary)

If the picking is created with wrong OU, you can manually fix it:

```python
# In Odoo shell (temporary fix only!)
picking = env['stock.picking'].browse(123)  # Replace with actual ID
picking.write({'operating_unit_id': picking.move_ids[0].location_dest_id.operating_unit_id.id})
```

But this is NOT a permanent solution! Fix the route configuration instead.

## Common Mistakes

### ❌ Mistake 1: Route Warehouse = Source (DC)

```
Route: DC → Store A
Warehouse: DC Warehouse ← WRONG!
```

**Result**: Picking OU = DC, but destination = Store A → Constraint fails!

### ❌ Mistake 2: No Warehouse on Route

```
Route: DC → Store A
Warehouse: (empty) ← WRONG!
```

**Result**: Odoo picks first warehouse, might be wrong OU.

### ❌ Mistake 3: Location Belongs to Wrong OU

```
Stock Request:
- warehouse_id: Store A Warehouse (OU: Store A)
- location_id: Store A/Stock (OU: DC) ← WRONG!
```

**Result**: Location doesn't belong to warehouse's OU.

## Recommended Setup

### 1. Configure Locations

```
Operating Unit: DC
└─ Warehouse: DC Warehouse
   └─ Location: DC/Stock (internal)

Operating Unit: Store A
└─ Warehouse: Store A Warehouse
   └─ Location: Store A/Stock (internal)
```

### 2. Configure Routes (Per Store)

```
Route: DC → Store A
- Applicability: Can be selected on products
- Warehouse: Store A Warehouse ← Use DESTINATION warehouse!
- Pull Rules:
  └─ Pull From Another Location
     - Source Location: DC/Stock
     - Destination Location: Store A/Stock
```

### 3. Configure Replenishment Rule

```
Replenishment Rule: Store A - Product X
- Operating Unit: Store A
- Warehouse: Store A Warehouse
- Location: Store A/Stock
- Route: DC → Store A
- Min: 10
- Max: 50
```

### 4. Test the Flow

1. **Create Stock Request** (manually or via cron)
2. **Confirm Stock Request**
3. **Check Picking**:
   - Picking OU should be: Store A ✓
   - Source: DC/Stock (DC OU)
   - Destination: Store A/Stock (Store A OU) ✓
   - Constraint passes because destination matches picking OU ✓

## Advanced: Multi-Company/Multi-OU Setup

If you have multiple stores, create a route for each:

```
Route: DC → Store A (Warehouse: Store A)
Route: DC → Store B (Warehouse: Store B)
Route: DC → Store C (Warehouse: Store C)
```

Or use a single generic route with dynamic warehouse selection (requires custom development).

## Support

If you still encounter issues after following this guide:

1. **Check logs** for detailed OU information
2. **Verify route configuration** matches recommended setup
3. **Check location OU assignments** are correct
4. **Review picking OU** matches destination location's OU

The constraint is designed to prevent invalid inter-OU transfers. The solution is to ensure pickings are created with the **requesting OU** (destination), not the source OU.
