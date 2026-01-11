# Quick Installation & Setup Guide

## Stock Request Operating Unit Module

### Prerequisites Installation Order

#### Step 1: Install OCA Operating Unit Modules
```bash
# 1. operating_unit (Base OU module)
# Go to Apps → Search "Operating Unit" → Install

# 2. stock_operating_unit (Stock OU integration)
# Go to Apps → Search "Stock Operating Unit" → Install

# 3. stock_request (Base stock request)
# Go to Apps → Search "Stock Request" → Install
```

#### Step 2: Install This Module
```bash
# 4. weha_stock_request_operating_unit
# Go to Apps → Update Apps List → Search "Stock Request Operating Unit" → Install
```

---

## Configuration Steps

### 1. Create Operating Units
**Path**: Settings → Users & Companies → Operating Units

```
Example Setup:
- Code: DC01
  Name: Distribution Center
  Company: Your Company
  Partner: Create or select partner
  
- Code: STORE01
  Name: Store Jakarta
  Company: Your Company
  Partner: Create or select partner
  
- Code: STORE02
  Name: Store Surabaya
  Company: Your Company
  Partner: Create or select partner
```

### 2. Configure Users
**Path**: Settings → Users & Companies → Users

For each user:
1. Open user form
2. Go to "Operating Units" tab
3. Add allowed operating units
4. Set "Default Operating Unit"

```
Example:
Store Manager Jakarta:
- Allowed OUs: [DC01, STORE01]
- Default OU: STORE01

Store Manager Surabaya:
- Allowed OUs: [DC01, STORE02]
- Default OU: STORE02

DC Manager:
- Allowed OUs: [DC01, STORE01, STORE02]
- Default OU: DC01
```

### 3. Configure Warehouses (Optional)
**Path**: Inventory → Configuration → Warehouses

Assign operating units to warehouses if using stock_warehouse_operating_unit module.

---

## Usage Examples

### Example 1: Create Stock Request from Store

**Scenario**: Store Jakarta needs to request stock from DC

1. Go to **Inventory → Operations → Stock Requests**
2. Click **Create**
3. Fill in:
   - **Product**: Select product
   - **Quantity**: 100
   - **Warehouse**: Your warehouse
   - **Operating Unit**: STORE01 (Jakarta) ← Auto-filled from user default
   - **Expected Date**: Select date
4. Click **Save**
5. Click **Confirm**

**Result**: 
- Stock request created with OU = STORE01
- Stock move created with OU = STORE01
- Stock picking created with OU = STORE01
- DC can see this request if they have access to STORE01 OU

---

### Example 2: Create Stock Request Order (Multiple Products)

**Scenario**: Store Surabaya needs multiple products

1. Go to **Inventory → Operations → Stock Request Orders**
2. Click **Create**
3. Fill in:
   - **Warehouse**: Your warehouse
   - **Operating Unit**: STORE02 (Surabaya)
4. Click **Add a line** for each product:
   - Product A: 50 units
   - Product B: 100 units
   - Product C: 75 units
5. Click **Save**
6. Click **Confirm**

**Result**:
- 3 stock requests created, all with OU = STORE02
- All stock moves have OU = STORE02
- All pickings have OU = STORE02

---

### Example 3: View Stock Requests from Picking

1. Go to **Inventory → Operations → Transfers**
2. Open any picking created from stock request
3. Look for smart button "**Stock Requests**" at the top
4. Click the button to see related stock requests

---

## Testing Your Setup

### Test 1: Default Operating Unit
```
1. Login as Store Manager Jakarta
2. Create new stock request
3. Verify "Operating Unit" field is pre-filled with STORE01
✓ Pass if default OU appears
```

### Test 2: Operating Unit on Moves
```
1. Create stock request with STORE01
2. Confirm the request
3. Open stock move (Technical menu)
4. Verify operating_unit_id = STORE01
✓ Pass if move has correct OU
```

### Test 3: Security Rules
```
1. Login as Store Manager Jakarta (has access to STORE01 only)
2. Go to Stock Requests
3. Create request for STORE02
4. Should show error or not allow creation
✓ Pass if user cannot create request for unauthorized OU
```

### Test 4: Filter by Operating Unit
```
1. Go to Stock Requests list view
2. Click on "Group By" → "Operating Unit"
3. Verify requests are grouped by OU
✓ Pass if grouping works correctly
```

---

## Troubleshooting

### Issue: "Operating Unit field not visible"
**Solution**: 
- Ensure all dependencies are installed
- Update module list
- Upgrade the module

### Issue: "Operating unit required error"
**Solution**:
- Assign default operating unit to user
- Settings → Users → Your User → Operating Units tab

### Issue: "User cannot see stock requests"
**Solution**:
- Check user's allowed operating units
- Ensure stock request has OU assigned
- User must have access to that specific OU

### Issue: "Stock move doesn't have operating unit"
**Solution**:
- Ensure stock_operating_unit module is installed
- Check if stock request has OU before confirmation
- Re-confirm the stock request

---

## Quick Reference

### Key Shortcuts
- **Stock Requests**: Inventory → Operations → Stock Requests
- **Stock Request Orders**: Inventory → Operations → Stock Request Orders
- **Operating Units**: Settings → Users & Companies → Operating Units
- **User Configuration**: Settings → Users & Companies → Users

### Important Fields
- `operating_unit_id`: Required on stock.request and stock.request.order
- Auto-propagates from order to requests
- Auto-propagates from request to moves
- Auto-propagates from moves to pickings (via stock_operating_unit)

### Smart Buttons
- On **Stock Picking**: "Stock Requests" button
- Shows all stock requests that generated moves in this picking

---

## Your Store → DC → Supplier Flow

### Complete Workflow Example

#### Scenario Setup
```
Operating Units:
- DC01: Distribution Center (has inventory)
- STORE01: Store Jakarta (needs stock)

Products:
- Product A: 500 units in DC01
- Product B: 0 units in DC01 (need to purchase)
```

#### Flow 1: DC Has Stock (Product A)
```
1. Store Creates Request:
   - Store Manager creates stock request
   - Product A, Qty: 100
   - Operating Unit: STORE01
   - Source: DC01
   
2. DC Checks Stock:
   - DC has 500 units
   - Create internal transfer (DC01 → STORE01)
   - Transfer has both OUs tracked
   
3. Store Receives:
   - Picking delivered to STORE01
   - Stock updated with OU = STORE01
```

#### Flow 2: DC Needs to Purchase (Product B)
```
1. Store Creates Request:
   - Store Manager creates stock request
   - Product B, Qty: 100
   - Operating Unit: STORE01
   - Source: DC01
   
2. DC Checks Stock:
   - DC has 0 units
   - DC creates Purchase Order
   - PO operating unit: DC01
   
3. DC Receives from Supplier:
   - Goods received at DC01
   - Stock updated with OU = DC01
   
4. DC Transfers to Store:
   - Internal transfer (DC01 → STORE01)
   - Store receives goods
   - Stock updated with OU = STORE01
```

---

## Support & Documentation

- **Full Documentation**: See README.md
- **Module Structure**: See MODULE_STRUCTURE.md
- **Technical Details**: See models/*.py files
- **Author**: Weha (https://weha-id.com)
- **License**: LGPL-3

---

**Installation Date**: January 11, 2026  
**Module Version**: 18.0.1.0.0  
**Odoo Version**: 18.0
