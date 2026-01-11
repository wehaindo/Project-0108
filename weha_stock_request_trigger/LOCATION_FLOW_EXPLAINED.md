# Understanding Stock Request Location Flow

## How Stock Requests Work

### Key Concept: location_id = DESTINATION

In Odoo stock requests:
- `location_id` = **WHERE** you want the stock to arrive (DESTINATION)
- `route_id` = **HOW** to get the stock there (determines SOURCE)

### Example Flow

#### Setup:
```
Operating Units:
- DC East (Distribution Center)
- Store A (Retail Store)

Warehouses:
- DC East Warehouse (DCE)
  - Location: DCE/Stock
- Store A Warehouse (STA)
  - Location: STA/Stock

Route: "DC East → Store A"
- Pull Rule:
  - Source: DCE/Stock
  - Destination: STA/Stock
```

#### Replenishment Rule Configuration:
```python
Stock Replenishment Rule for Store A:
- operating_unit_id: Store A
- warehouse_id: Store A Warehouse  ← DESTINATION warehouse
- location_id: STA/Stock           ← DESTINATION location
- route_id: "DC East → Store A"    ← HOW to get stock
- source_ou_id: DC East (computed) ← WHERE stock comes from
```

#### Stock Request Creation:
```python
Stock Request:
- product_id: Product X
- product_uom_qty: 45 units
- operating_unit_id: Store A
- warehouse_id: Store A Warehouse  ← DESTINATION
- location_id: STA/Stock           ← DESTINATION
- route_id: "DC East → Store A"    ← Determines SOURCE
```

### What Happens During Confirmation

#### Step 1: Stock Request Created
```python
stock_request = env['stock.request'].create({
    'location_id': STA/Stock,  # DESTINATION
    'route_id': route_dc_to_store,
    ...
})
```

#### Step 2: Procurement Launched
```python
# In _action_launch_procurement_rule()
procurement = Procurement(
    product_id,
    qty,
    uom,
    location_id,  # STA/Stock (DESTINATION)
    name,
    origin,
    company,
    values  # Contains route_id
)
```

#### Step 3: Route Determines Source
```python
# Route "DC East → Store A" has pull rule:
rule = {
    'action': 'pull',
    'location_src_id': DCE/Stock,    # SOURCE
    'location_dest_id': STA/Stock,   # DESTINATION
    'picking_type_id': store_internal_transfer
}
```

#### Step 4: Transfer Created
```python
Stock Picking:
- picking_type_id: Store A: Internal Transfers
- location_id: DCE/Stock       ← SOURCE (from route rule)
- location_dest_id: STA/Stock  ← DESTINATION (from stock request)
- move_ids:
  - location_id: DCE/Stock
  - location_dest_id: STA/Stock
```

## Common Mistakes

### ❌ Mistake 1: Using DC Location in Stock Request

**Wrong Configuration:**
```python
Stock Request:
- location_id: DCE/Stock  # DC location (WRONG!)
- route_id: "DC East → Store A"
```

**Result:**
```
Transfer: DCE/Stock → DCE/Stock (Both same!)
```

**Why Wrong:**
- Stock request thinks destination is DC
- Route rule says: "When destination is STA/Stock, pull from DCE/Stock"
- But destination is DCE/Stock, so rule doesn't apply
- Falls back to default: same location → same location

### ✅ Correct Configuration:

```python
Stock Request:
- location_id: STA/Stock  # Store location (CORRECT!)
- route_id: "DC East → Store A"
```

**Result:**
```
Transfer: DCE/Stock → STA/Stock (Correct!)
```

**Why Correct:**
- Stock request destination is STA/Stock
- Route rule matches: "When destination is STA/Stock, pull from DCE/Stock"
- Transfer created: DCE/Stock → STA/Stock

---

### ❌ Mistake 2: Wrong Warehouse in Replenishment Rule

**Wrong Configuration:**
```python
Replenishment Rule:
- operating_unit_id: Store A
- warehouse_id: DC East Warehouse  # WRONG!
- location_id: DCE/Stock
```

**What Happens:**
```python
# Stock request created with:
location_id = DCE/Stock  # DC location instead of Store location

# Transfer becomes:
DCE/Stock → DCE/Stock  # Both same!
```

### ✅ Correct Configuration:

```python
Replenishment Rule:
- operating_unit_id: Store A
- warehouse_id: Store A Warehouse  # CORRECT!
- location_id: STA/Stock
```

**What Happens:**
```python
# Stock request created with:
location_id = STA/Stock  # Store location (destination)

# Transfer becomes:
DCE/Stock → STA/Stock  # Correct!
```

---

## Code Flow in Detail

### 1. Replenishment Rule Creates Stock Request

```python
# In stock_replenishment_rule.py
def action_create_stock_request(self):
    stock_request = self.env['stock.request'].create({
        'product_id': self.product_id.id,
        'operating_unit_id': self.operating_unit_id.id,
        'warehouse_id': self.warehouse_id.id,      # Store warehouse
        'location_id': self.location_id.id,        # Store location (DESTINATION)
        'route_id': self.route_id.id,              # DC → Store route
        ...
    })
```

### 2. Stock Request Prepares Procurement Values

```python
# In stock_request.py (overridden in our module)
def _prepare_procurement_values(self, group_id=False):
    vals = super()._prepare_procurement_values(group_id=group_id)
    
    # Ensure route from replenishment rule is used
    if self.replenishment_rule_id and self.replenishment_rule_id.route_id:
        vals['route_ids'] = self.replenishment_rule_id.route_id
    
    return vals
    # Returns:
    # {
    #     'warehouse_id': Store A Warehouse,
    #     'route_ids': Route "DC East → Store A",
    #     'stock_request_id': self.id,
    #     ...
    # }
```

### 3. Procurement System Runs

```python
# In _action_launch_procurement_rule()
procurement = self.env["procurement.group"].Procurement(
    request.product_id,
    request.product_uom_qty,
    request.product_uom_id,
    request.location_id,        # STA/Stock (DESTINATION)
    request.name,
    request.name,
    request.company_id,
    values                      # Contains route_id
)

# Procurement system looks for matching rule:
# Route: "DC East → Store A"
# Rule: Pull from DCE/Stock to STA/Stock
# Match: destination = STA/Stock ✓
```

### 4. Pull Rule Creates Transfer

```python
# Route rule creates stock.picking
picking = env['stock.picking'].create({
    'picking_type_id': store_a_internal_transfer,
    'location_id': DCE/Stock,        # SOURCE (from rule)
    'location_dest_id': STA/Stock,   # DESTINATION (from procurement)
    ...
})

# And stock.move
move = env['stock.move'].create({
    'product_id': product_x,
    'location_id': DCE/Stock,        # SOURCE
    'location_dest_id': STA/Stock,   # DESTINATION
    'picking_id': picking.id,
    ...
})
```

---

## Debugging Location Issues

### Check 1: Replenishment Rule Configuration
```python
rule = env['stock.replenishment.rule'].browse(RULE_ID)

print("Operating Unit:", rule.operating_unit_id.name)
print("Warehouse:", rule.warehouse_id.name)
print("Warehouse OU:", rule.warehouse_id.operating_unit_id.name)
print("Location:", rule.location_id.complete_name)
print("Route:", rule.route_id.name if rule.route_id else "NONE")

# Expected:
# Operating Unit: Store A
# Warehouse: Store A Warehouse
# Warehouse OU: Store A
# Location: STA/Stock
# Route: DC East → Store A
```

### Check 2: Stock Request Configuration
```python
request = env['stock.request'].browse(REQUEST_ID)

print("Location (dest):", request.location_id.complete_name)
print("Warehouse:", request.warehouse_id.name)
print("Route:", request.route_id.name if request.route_id else "NONE")

# Expected:
# Location (dest): STA/Stock
# Warehouse: Store A Warehouse
# Route: DC East → Store A
```

### Check 3: Route Pull Rule
```python
route = env['stock.route'].browse(ROUTE_ID)

for rule in route.rule_ids:
    print("Rule:", rule.name)
    print("Action:", rule.action)
    print("Source:", rule.location_src_id.complete_name)
    print("Destination:", rule.location_dest_id.complete_name)
    print("Picking Type:", rule.picking_type_id.name)

# Expected:
# Rule: Store A: Pull from DC East
# Action: pull
# Source: DCE/Stock
# Destination: STA/Stock
# Picking Type: Store A: Internal Transfers
```

### Check 4: Created Transfer
```python
request = env['stock.request'].browse(REQUEST_ID)
pickings = request.picking_ids

for picking in pickings:
    print("Picking:", picking.name)
    print("Type:", picking.picking_type_id.name)
    print("From:", picking.location_id.complete_name)
    print("To:", picking.location_dest_id.complete_name)
    
# Expected:
# Picking: STA/INT/00123
# Type: Store A: Internal Transfers
# From: DCE/Stock
# To: STA/Stock
```

---

## Visual Flow Diagram

```
┌─────────────────────────────────────────────────────────────┐
│ REPLENISHMENT RULE (Store A - Product X)                    │
├─────────────────────────────────────────────────────────────┤
│ Operating Unit: Store A                                     │
│ Warehouse: Store A Warehouse ← DESTINATION WAREHOUSE        │
│ Location: STA/Stock          ← DESTINATION LOCATION         │
│ Route: DC East → Store A     ← DETERMINES SOURCE            │
│ Source OU: DC East           ← COMPUTED FROM HIERARCHY      │
└────────────────────┬────────────────────────────────────────┘
                     │
                     │ Creates Stock Request
                     ▼
┌─────────────────────────────────────────────────────────────┐
│ STOCK REQUEST                                               │
├─────────────────────────────────────────────────────────────┤
│ Product: Product X                                          │
│ Quantity: 45 units                                          │
│ Location: STA/Stock          ← DESTINATION                  │
│ Warehouse: Store A Warehouse                                │
│ Route: DC East → Store A                                    │
└────────────────────┬────────────────────────────────────────┘
                     │
                     │ Confirms → Launches Procurement
                     ▼
┌─────────────────────────────────────────────────────────────┐
│ PROCUREMENT                                                 │
├─────────────────────────────────────────────────────────────┤
│ Product: Product X                                          │
│ Quantity: 45 units                                          │
│ Location: STA/Stock          ← DESTINATION (where needed)   │
│ Route: DC East → Store A     ← Find matching rule          │
└────────────────────┬────────────────────────────────────────┘
                     │
                     │ Route finds matching pull rule
                     ▼
┌─────────────────────────────────────────────────────────────┐
│ ROUTE PULL RULE (DC East → Store A)                        │
├─────────────────────────────────────────────────────────────┤
│ Action: Pull                                                │
│ Source: DCE/Stock            ← SOURCE (where to get from)   │
│ Destination: STA/Stock       ← DESTINATION (matches!)       │
│ Picking Type: Store A: Internal Transfers                   │
└────────────────────┬────────────────────────────────────────┘
                     │
                     │ Creates Transfer
                     ▼
┌─────────────────────────────────────────────────────────────┐
│ STOCK PICKING / TRANSFER                                    │
├─────────────────────────────────────────────────────────────┤
│ Type: Internal Transfer                                     │
│ From: DCE/Stock              ← SOURCE                       │
│ To: STA/Stock                ← DESTINATION                  │
│ Moves:                                                      │
│   - Product X: 45 units                                     │
│     DCE/Stock → STA/Stock                                   │
└─────────────────────────────────────────────────────────────┘
```

---

## Summary

### Golden Rules:

1. **location_id = DESTINATION**
   - Always the location WHERE you want stock to arrive
   - For Store replenishment: Store location
   - NOT the source location

2. **route_id = HOW to get there**
   - Route determines SOURCE location
   - Pull rules match destination and provide source
   - Route name should indicate direction: "Source → Destination"

3. **Warehouse must match Operating Unit**
   - Store A replenishment → Store A Warehouse
   - DC East replenishment → DC East Warehouse
   - Never cross-assign

4. **Route must have correct pull rule**
   - Source: Supplier location (DC)
   - Destination: Requester location (Store)
   - Picking Type: Requester's internal transfer

### Quick Validation:

```python
# Correct configuration checklist:
rule.operating_unit_id.name == "Store A"                    ✓
rule.warehouse_id.operating_unit_id.name == "Store A"       ✓
rule.location_id.warehouse_id == rule.warehouse_id          ✓
rule.location_id.complete_name.startswith("STA/")          ✓
rule.route_id.name == "DC East → Store A"                   ✓
rule.source_ou_id.name == "DC East"                         ✓
```

### When You See DC → DC:

**Root cause:** Replenishment rule configured with DC warehouse/location instead of Store warehouse/location.

**Fix:** Change warehouse and location to Store's warehouse/location.

**Prevention:** Use domain constraints (already added in module).

---

## Module Implementation

Our `weha_stock_request_trigger` module ensures proper configuration through:

1. **Domain Constraints:**
   ```python
   warehouse_id = fields.Many2one(
       domain="[('operating_unit_id', '=', operating_unit_id)]"
   )
   location_id = fields.Many2one(
       domain="[('usage', '=', 'internal'), ('warehouse_id', '=', warehouse_id)]"
   )
   ```

2. **Route Enforcement:**
   ```python
   def _prepare_procurement_values(self, group_id=False):
       vals = super()._prepare_procurement_values(group_id=group_id)
       if self.replenishment_rule_id and self.replenishment_rule_id.route_id:
           vals['route_ids'] = self.replenishment_rule_id.route_id
       return vals
   ```

3. **Clear Documentation:**
   - Help text on all fields
   - TROUBLESHOOTING_DESTINATION.md
   - ROUTE_CONFIGURATION_GUIDE.md

These ensure the destination is always correct! ✅
