# Revenue Sharing Contract Renewal Guide

## Overview

The `weha_operating_unit_contract` module now supports **Operating Unit-specific revenue sharing rules** with **effective date ranges**. This allows you to:

- Create location-specific revenue sharing contracts
- Handle contract renewals with new sharing percentages
- Manage multiple contracts with different time periods
- Automatically apply the correct rule based on OU, date, and product

---

## New Features (v18.0.2.0.0)

### 1. Operating Unit-Specific Rules

You can now create revenue sharing rules that apply to:
- **All Operating Units** (global rules) - Leave "Operating Unit" field empty
- **Specific Operating Units** (location-specific contracts) - Select an OU

**Example Use Cases:**
- Different revenue sharing for Store A vs Store B
- Special contracts for flagship stores
- Regional variations in revenue distribution

---

### 2. Effective Date Ranges

Each rule can have:
- **Valid From** date (contract start date)
- **Valid To** date (contract end date)
- Leave either or both empty for no time restriction

**Example Use Cases:**
- Annual contract renewals
- Seasonal promotional sharing rules
- Trial period contracts
- Temporary special agreements

---

## Configuration Guide

### Creating a Basic Rule

1. Go to **Operating Unit → Configuration → Revenue Sharing Rules**
2. Click **Create**
3. Fill in basic information:
   - **Name:** Descriptive name (e.g., "Store A - 2026 Contract")
   - **Sequence:** Priority order (lower = higher priority)
   - **Operating Unit:** Select specific OU or leave empty for global
   - **Valid From:** Contract start date (optional)
   - **Valid To:** Contract end date (optional)
   - **Apply To:** Choose product scope (All/Category/Specific)

4. Add **Revenue Sharing Lines** (must total 100%):
   - Store Type: 30%
   - DC Type: 40%
   - HO Type: 30%

5. **Save**

---

## Contract Renewal Workflow

### Scenario: Renewing a Revenue Sharing Contract

**Current Contract (2025):**
- Valid: Jan 1, 2025 - Dec 31, 2025
- Store: 30%, DC: 40%, HO: 30%

**New Contract (2026):**
- Valid: Jan 1, 2026 - Dec 31, 2026
- Store: 35%, DC: 35%, HO: 30%

### Steps:

1. **Keep the old rule active:**
   - Name: "Store A - 2025 Contract"
   - Operating Unit: Store A
   - Valid From: 2025-01-01
   - Valid To: 2025-12-31
   - Lines: Store 30%, DC 40%, HO 30%

2. **Create the new rule:**
   - Name: "Store A - 2026 Contract"
   - Operating Unit: Store A
   - Valid From: 2026-01-01
   - Valid To: 2026-12-31
   - Lines: Store 35%, DC 35%, HO 30%

3. **Result:**
   - Orders from 2025 → Use 2025 contract percentages
   - Orders from 2026 → Use 2026 contract percentages
   - Automatic transition on Jan 1, 2026

---

## Rule Selection Priority

When calculating revenue sharing, the system selects rules in this order:

### Priority Levels (Highest to Lowest)

1. **Specific OU + Specific Product + Valid Date**
   - Most specific rule for a particular store and product
   
2. **Any OU + Specific Product + Valid Date**
   - Global rule for a specific product
   
3. **Specific OU + Product Category + Valid Date**
   - Store-specific rule for product category
   
4. **Any OU + Product Category + Valid Date**
   - Global rule for product category
   
5. **Specific OU + All Products + Valid Date**
   - Store-specific default rule
   
6. **Any OU + All Products + Valid Date**
   - Global default rule (fallback)

### Date Validation

For a rule to be selected:
- If **Valid From** is set: Order date must be >= Valid From
- If **Valid To** is set: Order date must be <= Valid To
- If both empty: Rule is always valid

---

## Common Use Cases

### Use Case 1: Global Default Rule

**Requirement:** Default 30/40/30 split for all stores and all products

**Configuration:**
```
Name: Global Default Revenue Sharing
Operating Unit: (empty)
Valid From: (empty)
Valid To: (empty)
Apply To: All Products
Lines: Store 30%, DC 40%, HO 30%
```

---

### Use Case 2: Store-Specific Contract

**Requirement:** Store A has special 35/35/30 split

**Configuration:**
```
Name: Store A Special Contract
Operating Unit: Store A
Valid From: (empty)
Valid To: (empty)
Apply To: All Products
Lines: Store 35%, DC 35%, HO 30%
```

**Result:** Store A uses 35/35/30, all other stores use global default

---

### Use Case 3: Annual Contract Renewal

**Requirement:** Store B renews contract yearly with new percentages

**2025 Contract:**
```
Name: Store B - 2025 Contract
Operating Unit: Store B
Valid From: 2025-01-01
Valid To: 2025-12-31
Apply To: All Products
Lines: Store 30%, DC 40%, HO 30%
```

**2026 Contract:**
```
Name: Store B - 2026 Contract
Operating Unit: Store B
Valid From: 2026-01-01
Valid To: 2026-12-31
Apply To: All Products
Lines: Store 32%, DC 38%, HO 30%
```

**Result:** Automatic percentage change on January 1, 2026

---

### Use Case 4: Product-Specific Contract

**Requirement:** Electronics category has different split (40/30/30) for Store C

**Configuration:**
```
Name: Store C - Electronics Premium
Operating Unit: Store C
Valid From: 2026-01-01
Valid To: 2026-12-31
Apply To: Product Category
Category: Electronics
Lines: Store 40%, DC 30%, HO 30%
```

**Result:** Store C gets 40/30/30 for electronics, default for other products

---

### Use Case 5: Seasonal Promotional Rule

**Requirement:** Q4 2026 special sharing for all stores

**Configuration:**
```
Name: Q4 2026 Holiday Special
Operating Unit: (empty)
Valid From: 2026-10-01
Valid To: 2026-12-31
Apply To: All Products
Lines: Store 35%, DC 35%, HO 30%
```

**Result:** All stores use special sharing only during Q4 2026

---

## Search and Filter Features

### Available Filters

**Status Filters:**
- **Currently Valid:** Shows rules valid today
- **Future Rules:** Rules that start in the future
- **Expired Rules:** Rules that have ended

**Scope Filters:**
- **Global Rules:** Rules for all OUs
- **OU-Specific Rules:** Location-specific rules

**Product Filters:**
- **All Products**
- **By Category**
- **Specific Product**

### Group By Options

- **Operating Unit:** See rules by store
- **Apply To:** Group by product scope
- **Product Category:** Group by category
- **Valid From Month:** Group by contract start month

---

## Best Practices

### 1. Contract Organization

✅ **DO:**
- Use descriptive names (e.g., "Store A - 2026 Annual Contract")
- Set sequence numbers for priority control
- Document contract terms in rule description
- Keep old contracts active for historical accuracy

❌ **DON'T:**
- Delete old rules (needed for historical calculations)
- Create overlapping date ranges without clear priority
- Mix global and OU-specific rules with same priority

---

### 2. Date Management

✅ **DO:**
- Use clear start/end dates for annual contracts
- Leave dates empty for permanent rules
- Plan renewals with continuous date coverage
- Test date ranges before activation

❌ **DON'T:**
- Create gaps between contract periods
- Overlap dates without considering priority
- Use future dates without testing

---

### 3. Testing New Rules

Before activating a new contract:

1. **Create the rule** with appropriate dates
2. **Test with diagnostic wizard** (Action → Revenue Sharing Diagnostic)
3. **Verify rule selection** in test period
4. **Activate the rule** when ready

---

## Troubleshooting

### Issue: Wrong rule applied

**Check:**
1. Rule priority and sequence numbers
2. Date ranges overlap
3. OU and product scope settings
4. Active status of rules

**Solution:** Use search filters to see which rules match your criteria

---

### Issue: No rule found

**Check:**
1. Date range covers order date
2. OU or product matches rule scope
3. Rule is active
4. At least one global fallback rule exists

**Solution:** Create appropriate rule or adjust date ranges

---

### Issue: Contract transition not smooth

**Check:**
1. Old contract end date = New contract start date - 1 day
2. No gaps in date coverage
3. Both rules active

**Solution:** Adjust dates for continuous coverage

---

## Revenue Sharing Period Calculation

When you run **Calculate Revenue Sharing** on a period:

1. System processes each POS order in date range
2. For each order line:
   - Gets order date
   - Gets selling OU
   - Gets product
   - **Finds best matching rule** using priority system + date validation
   - Applies sharing percentages from selected rule
3. Creates revenue sharing entries

---

## API / Technical Details

### Method Signature

```python
def get_sharing_for_product(self, product, operating_unit=None, date=None):
    """
    Get revenue sharing rule for a product with OU and date filtering
    
    Args:
        product: product.product record
        operating_unit: operating.unit record (optional)
        date: date to check validity (optional, defaults to today)
    
    Returns:
        revenue.sharing.rule record or False
    """
```

### Example Usage

```python
# Get rule for specific product, OU, and date
product = self.env['product.product'].browse(123)
ou = self.env['operating.unit'].browse(456)
order_date = fields.Date.from_string('2026-03-15')

rule = self.env['revenue.sharing.rule'].get_sharing_for_product(
    product,
    operating_unit=ou,
    date=order_date
)

if rule:
    for line in rule.line_ids:
        print(f"{line.ou_type_id.name}: {line.percentage}%")
```

---

## Upgrade Notes

### From v18.0.1.0.0 to v18.0.2.0.0

**New Fields:**
- `operating_unit_id` (Many2one to operating.unit)
- `date_from` (Date)
- `date_to` (Date)

**Changed Methods:**
- `get_sharing_for_product()` now accepts `operating_unit` and `date` parameters

**Migration:**
- Existing rules automatically become global (operating_unit_id = False)
- Existing rules have no date restrictions (dates = False)
- Old calculations continue to work (backward compatible)

**Action Required:**
- Review existing rules
- Add OU and dates as needed for new contracts
- Test with diagnostic wizard

---

## Support

For issues or questions about revenue sharing contract management:

1. Check this documentation
2. Use **Revenue Sharing Diagnostic** wizard (Action menu in Period)
3. Review **REVENUE_SHARING_DEBUG.md** for troubleshooting
4. Contact system administrator

---

## Version History

**v18.0.2.0.0** (January 2026)
- Added Operating Unit-specific rules
- Added effective date ranges (Valid From/To)
- Enhanced rule selection with priority system
- Added contract renewal support
- Improved UI with contract information tab
- Added search filters for date ranges and OUs

**v18.0.1.0.0** (Initial Release)
- Basic revenue sharing rules
- Product/Category/All scope
- OU type-based percentages
- Monthly calculation periods
