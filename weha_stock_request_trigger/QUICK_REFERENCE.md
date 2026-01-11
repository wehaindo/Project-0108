# Quick Reference Guide - Stock Request Trigger

## Quick Start (5 minutes)

### 1. Create Replenishment Rule
```
Inventory > Replenishment > Replenishment Rules > Create

Fields:
- Operating Unit: Store A
- Warehouse: Main Warehouse
- Location: WH/Stock
- Product: Your Product
- Minimum Quantity: 10
- Maximum Quantity: 50
- Auto Trigger: ✓ (checked)
```

### 2. View Current Status
```
Inventory > Replenishment > Replenishment Rules

Look for RED rows = Below minimum stock
```

### 3. Manual Replenishment
```
Inventory > Replenishment > Manual Replenishment

Select: Operating Unit
System shows: All products below minimum
Click: Create Stock Requests
```

## Common Tasks

### Check Which Products Need Replenishment
```
Inventory > Replenishment > Replenishment Rules
Filter: Below Minimum
```

### View Auto-Generated Stock Requests
```
Inventory > Stock Requests
Filter: Auto Generated
```

### Disable Auto Replenishment for a Product
```
Open replenishment rule
Uncheck: Auto Trigger
or
Click: Archive (in top-right)
```

### Change Reorder Frequency
```
Settings > Technical > Automation > Scheduled Actions
Search: "Check Stock Replenishment"
Edit: Interval Number (default: 1 hour)
```

## Key Concepts

### Minimum Quantity (Reorder Point)
- Stock level that triggers replenishment
- Example: Min = 10 units
- When stock < 10, system creates request

### Maximum Quantity (Target Stock)
- Desired stock level after replenishment
- Example: Max = 50 units
- System orders: Max - Current = 50 - 5 = 45 units

### Reorder Quantity
- Automatically calculated: Maximum - Current Stock
- Only positive values trigger requests
- Updates when stock changes

### Auto Trigger
- When enabled: Scheduled action creates requests automatically
- When disabled: Manual trigger only
- Can be changed anytime

### Source Operating Unit
- Where stock comes from (determined by hierarchy)
- Store → DC (parent)
- DC → HO (parent)
- Uses `default_source_ou_id` if set

## Workflow Examples

### Example 1: Store Low Stock (Auto)
```
Current State:
- Store A: Product X = 5 units
- Rule: Min=10, Max=50, Auto=True

Hourly Check (Automatic):
1. System detects: 5 < 10 (below minimum)
2. Calculates: 50 - 5 = 45 units
3. Creates stock request: DC → Store A, 45 units
4. Updates trigger date

Result:
- Stock request created automatically
- No manual intervention needed
```

### Example 2: Manual Replenishment (Multiple Products)
```
Current State:
- Store B has 3 products below minimum

Manual Process:
1. Open: Manual Replenishment wizard
2. Select: Store B
3. System shows:
   - Product A: Current=2, Min=10, Order=48
   - Product B: Current=5, Min=20, Order=95
   - Product C: Current=1, Min=5, Order=29
4. Adjust quantities if needed
5. Click: Create Stock Requests

Result:
- 3 stock requests created at once
- All requests linked to rules
```

### Example 3: DC Requests from HO
```
Store Request:
- Store A requests 45 units from DC East

DC Check:
- DC East stock: 20 units (not enough)
- DC East has own rule: Min=50, Max=200
- DC becomes below minimum

DC Auto-Request:
- DC creates request to HO
- HO fulfills DC request
- DC fulfills Store request

Result:
- Cascading replenishment through hierarchy
```

## Troubleshooting Quick Fix

### Problem: No automatic requests created
**Check 1:** Rule active?
```
Replenishment Rules > Check Active badge
```

**Check 2:** Auto Trigger enabled?
```
Open rule > Check Auto Trigger field
```

**Check 3:** Scheduled action running?
```
Settings > Technical > Scheduled Actions
Search: "Check Stock Replenishment"
Check: Active = True
```

### Problem: Wrong quantity calculated
**Check 1:** Current stock correct?
```
Open rule > Check Current Qty field
Compare with: Inventory > Products > Stock
```

**Check 2:** Min/Max values correct?
```
Open rule > Verify Minimum and Maximum Qty
```

### Problem: No source OU found
**Check:** Hierarchy configured?
```
Inventory > Configuration > Operating Units
Check: Parent ID or Default Source OU
```

## Field Reference

### Replenishment Rule Form

| Field | Description | Example |
|-------|-------------|---------|
| Operating Unit | Where to replenish | Store A |
| Warehouse | Warehouse for stock | Main WH |
| Location | Specific location | WH/Stock |
| Product | Product to monitor | Product X |
| Current Qty | Real-time stock | 5.0 (computed) |
| Minimum Qty | Reorder point | 10.0 |
| Maximum Qty | Target stock | 50.0 |
| Reorder Qty | Amount to order | 45.0 (computed) |
| Auto Trigger | Enable auto-creation | ✓ |
| Trigger Date | Last request date | 2026-01-15 10:30 |
| Source OU | Where stock comes from | DC East (computed) |

### Stock Request Form (Extended)

| New Field | Description | Example |
|-----------|-------------|---------|
| Auto Generated | Created by system | ✓ (badge) |
| Replenishment Rule | Link to rule | Store A - Product X |

## Filters and Views

### Replenishment Rules Filters
- **Below Minimum:** Shows products needing replenishment
- **Auto Trigger:** Shows rules with auto-creation enabled
- **Active:** Shows active rules only
- **Archived:** Shows archived rules

### Group By Options
- **Operating Unit:** See all products per OU
- **Product:** See all OUs for a product
- **Location:** See all products per location

### Stock Request Filters
- **Auto Generated:** Shows system-created requests
- **Not Done:** Shows pending requests
- **Operating Unit:** Filter by OU

## Tips and Best Practices

### Setting Min/Max Quantities
```
Consider:
- Average daily sales
- Delivery lead time
- Safety stock

Example (daily sales = 5 units, lead time = 3 days):
- Minimum = 15 (3 days × 5)
- Maximum = 50 (10 days × 5)
```

### Scheduled Action Frequency
```
High-volume stores: Every 30 minutes
Normal stores: Every 1 hour (default)
Low-volume stores: Every 4 hours
```

### Monitoring
```
Daily: Check "Below Minimum" filter
Weekly: Review trigger dates
Monthly: Analyze replenishment patterns
```

### Testing New Rules
```
1. Create rule with Auto Trigger = False
2. Test with Manual Replenishment
3. Verify quantities correct
4. Enable Auto Trigger
5. Monitor for 1 week
```

## Module Integration

### With Operating Unit Hierarchy
- Uses parent-child relationships
- Respects default source OU settings
- Supports multi-level requests (Store→DC→HO)

### With Stock Request
- Creates standard stock requests
- Follows normal approval workflow
- Links back to replenishment rule

### With Stock Operating Unit
- Respects OU access rights
- Uses OU-specific warehouses/locations
- Maintains OU security

## Quick Commands

### Python Code to Check Rules
```python
# Find rules below minimum
rules = env['stock.replenishment.rule'].search([
    ('active', '=', True),
    ('below_minimum', '=', True),
])

for rule in rules:
    print(f"{rule.name}: {rule.current_qty}/{rule.minimum_qty}")
```

### SQL to View Statistics
```sql
-- Count rules by status
SELECT 
    operating_unit_id,
    COUNT(*) as total_rules,
    SUM(CASE WHEN current_qty < minimum_qty THEN 1 ELSE 0 END) as below_min
FROM stock_replenishment_rule
WHERE active = true
GROUP BY operating_unit_id;
```

## Support Resources

- **Full Documentation:** README.md
- **Module Structure:** See module files
- **Demo Data:** Install with demo data enabled
- **Logs:** Settings > Technical > Logging (filter: stock.replenishment)

## Version

- Module Version: 18.0.1.0.0
- Odoo Version: 18.0
- Last Updated: 2026
