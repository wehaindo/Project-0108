# Revenue Sharing Calculation Debugging Guide

## Issue: 0 Data with December 2025 POS Orders

### Common Causes & Solutions

#### 1. **Date Range Mismatch**

**Problem**: Period dates don't match POS order dates

**Check**:
```python
# In Odoo Python console or debug mode
period = env['revenue.sharing.period'].browse(PERIOD_ID)
print(f"Period: {period.name}")
print(f"Date From: {period.date_from}")
print(f"Date To: {period.date_to}")

# Check POS orders in that range
pos_orders = env['pos.order'].search([
    ('date_order', '>=', period.date_from),
    ('date_order', '<=', period.date_to),
    ('state', 'in', ['paid', 'done', 'invoiced']),
])
print(f"Found {len(pos_orders)} POS orders")
for order in pos_orders[:5]:
    print(f"  - {order.name}: {order.date_order}, OU: {order.operating_unit_id.name}")
```

**Solution**: Ensure period covers December 2025:
- Date From: 2025-12-01
- Date To: 2025-12-31

---

#### 2. **Date Field Type Issue**

**Problem**: `date_order` might be datetime, period uses date

**Check**:
```python
order = env['pos.order'].search([('state', 'in', ['paid', 'done'])], limit=1)
print(f"date_order type: {type(order.date_order)}")
print(f"date_order value: {order.date_order}")

# If datetime, convert to date
from datetime import datetime
if isinstance(order.date_order, datetime):
    order_date = order.date_order.date()
else:
    order_date = order.date_order
print(f"Converted: {order_date}")
```

**Solution**: Update calculation to handle datetime:
```python
# In revenue_sharing_period.py
pos_orders = self.env['pos.order'].search([
    ('date_order', '>=', fields.Datetime.to_datetime(self.date_from)),
    ('date_order', '<=', fields.Datetime.to_datetime(self.date_to) + relativedelta(days=1)),
    # ... rest of domain
])
```

---

#### 3. **Operating Unit Not Set**

**Problem**: POS orders missing `operating_unit_id`

**Check**:
```python
# Count orders without OU
no_ou = env['pos.order'].search_count([
    ('date_order', '>=', '2025-12-01'),
    ('date_order', '<=', '2025-12-31'),
    ('state', 'in', ['paid', 'done', 'invoiced']),
    ('operating_unit_id', '=', False),
])
print(f"Orders without OU: {no_ou}")

# Count orders with OU
with_ou = env['pos.order'].search_count([
    ('date_order', '>=', '2025-12-01'),
    ('date_order', '<=', '2025-12-31'),
    ('state', 'in', ['paid', 'done', 'invoiced']),
    ('operating_unit_id', '!=', False),
])
print(f"Orders with OU: {with_ou}")
```

**Solution**: Set OU on POS orders or configure default OU per session

---

#### 4. **Auto Share Revenue Disabled**

**Problem**: `auto_share_revenue` is False on Operating Units

**Check**:
```python
# Check OU settings
ous = env['operating.unit'].search([])
for ou in ous:
    print(f"{ou.name}: auto_share_revenue = {ou.auto_share_revenue}")
```

**Solution**: Enable auto share revenue:
```python
# Enable for all OUs
env['operating.unit'].search([]).write({'auto_share_revenue': True})
```

---

#### 5. **No Revenue Sharing Rules**

**Problem**: No rules defined for products

**Check**:
```python
# Check rules
rules = env['revenue.sharing.rule'].search([])
print(f"Total rules: {len(rules)}")
for rule in rules:
    print(f"  - {rule.name}")
    print(f"    Categories: {rule.product_categ_ids.mapped('name')}")
    print(f"    Products: {rule.product_ids.mapped('name')}")
    print(f"    Lines: {len(rule.line_ids)}")
```

**Solution**: Create revenue sharing rules for your products/categories

---

#### 6. **No Parent OUs**

**Problem**: OUs don't have parent relationships set

**Check**:
```python
# Check OU hierarchy
ous = env['operating.unit'].search([])
for ou in ous:
    parents = ou.get_all_parents()
    print(f"{ou.name}: {len(parents)} parents - {[p.name for p in parents]}")
```

**Solution**: Set parent_id on Operating Units to create hierarchy

---

#### 7. **POS Order State**

**Problem**: Orders not in correct state

**Check**:
```python
# Count by state
for state in ['draft', 'paid', 'done', 'invoiced', 'cancel']:
    count = env['pos.order'].search_count([
        ('date_order', '>=', '2025-12-01'),
        ('date_order', '<=', '2025-12-31'),
        ('state', '=', state),
    ])
    print(f"{state}: {count}")
```

**Solution**: Ensure orders are in 'paid', 'done', or 'invoiced' state

---

## Quick Diagnostic Script

Run this in Odoo shell to diagnose the issue:

```python
# === REVENUE SHARING DIAGNOSTIC ===

from datetime import datetime, date
from dateutil.relativedelta import relativedelta

# 1. Check Period
period_id = 1  # Replace with your period ID
period = env['revenue.sharing.period'].browse(period_id)
print(f"\n=== PERIOD CHECK ===")
print(f"Period: {period.name}")
print(f"Date From: {period.date_from} (type: {type(period.date_from)})")
print(f"Date To: {period.date_to} (type: {type(period.date_to)})")
print(f"State: {period.state}")

# 2. Check POS Orders - Date Only
print(f"\n=== POS ORDERS (Date Range) ===")
pos_orders = env['pos.order'].search([
    ('date_order', '>=', period.date_from),
    ('date_order', '<=', period.date_to),
])
print(f"Total orders in date range: {len(pos_orders)}")

# 3. Check POS Orders - With State
pos_orders_state = env['pos.order'].search([
    ('date_order', '>=', period.date_from),
    ('date_order', '<=', period.date_to),
    ('state', 'in', ['paid', 'done', 'invoiced']),
])
print(f"Orders with correct state: {len(pos_orders_state)}")

# 4. Check POS Orders - With OU
pos_orders_ou = env['pos.order'].search([
    ('date_order', '>=', period.date_from),
    ('date_order', '<=', period.date_to),
    ('state', 'in', ['paid', 'done', 'invoiced']),
    ('operating_unit_id', '!=', False),
])
print(f"Orders with Operating Unit: {len(pos_orders_ou)}")

# 5. Check POS Orders - With Company
pos_orders_company = env['pos.order'].search([
    ('date_order', '>=', period.date_from),
    ('date_order', '<=', period.date_to),
    ('state', 'in', ['paid', 'done', 'invoiced']),
    ('operating_unit_id', '!=', False),
    ('company_id', '=', period.company_id.id),
])
print(f"Orders matching all criteria: {len(pos_orders_company)}")

# 6. Sample Order Details
if pos_orders_company:
    print(f"\n=== SAMPLE ORDERS ===")
    for order in pos_orders_company[:3]:
        print(f"\nOrder: {order.name}")
        print(f"  Date: {order.date_order}")
        print(f"  State: {order.state}")
        print(f"  OU: {order.operating_unit_id.name}")
        print(f"  Auto Share: {order.operating_unit_id.auto_share_revenue}")
        print(f"  Lines: {len(order.lines)}")
        print(f"  Amount: {order.amount_total}")

# 7. Check Operating Units
print(f"\n=== OPERATING UNITS ===")
ous = env['operating.unit'].search([])
for ou in ous:
    parents = ou.get_all_parents() if hasattr(ou, 'get_all_parents') else []
    print(f"{ou.name}:")
    print(f"  Auto Share: {ou.auto_share_revenue}")
    print(f"  Parents: {len(parents)} - {[p.name for p in parents]}")

# 8. Check Revenue Sharing Rules
print(f"\n=== REVENUE SHARING RULES ===")
rules = env['revenue.sharing.rule'].search([])
print(f"Total rules: {len(rules)}")
for rule in rules:
    print(f"\n{rule.name}:")
    print(f"  State: {rule.state}")
    print(f"  Categories: {len(rule.product_categ_ids)}")
    print(f"  Products: {len(rule.product_ids)}")
    print(f"  Lines: {len(rule.line_ids)}")
    if rule.line_ids:
        for line in rule.line_ids:
            print(f"    - {line.ou_type_id.name}: {line.percentage}%")

print(f"\n=== DIAGNOSTIC COMPLETE ===")
```

---

## Fix Script

If date_order is datetime type, use this fix:

```python
# Add to revenue_sharing_period.py

from odoo import fields as odoo_fields

def action_calculate_revenue_sharing(self):
    """Calculate revenue sharing for this period"""
    self.ensure_one()
    
    # ... existing code ...
    
    # FIX: Convert dates to datetime for comparison
    date_from_dt = odoo_fields.Datetime.to_datetime(self.date_from)
    date_to_dt = odoo_fields.Datetime.to_datetime(self.date_to) + relativedelta(days=1)
    
    # Get all POS orders in this period
    pos_orders = self.env['pos.order'].search([
        ('date_order', '>=', date_from_dt),
        ('date_order', '<', date_to_dt),  # Use < instead of <=
        ('state', 'in', ['paid', 'done', 'invoiced']),
        ('operating_unit_id', '!=', False),
        ('company_id', '=', self.company_id.id),
    ])
    
    # ... rest of existing code ...
```

---

## Next Steps

1. **Run diagnostic script** to identify exact issue
2. **Check results** - which check fails?
3. **Apply appropriate solution** from above
4. **Re-run calculation**
5. **Verify entries created**

## Common Solutions Summary

| Issue | Quick Fix |
|-------|-----------|
| Date type mismatch | Use `fields.Datetime.to_datetime()` |
| No OU on orders | Set default OU on POS config |
| Auto share disabled | Enable on all OUs |
| No rules | Create revenue sharing rules |
| No hierarchy | Set parent_id on OUs |
| Wrong state | Validate/pay orders |

