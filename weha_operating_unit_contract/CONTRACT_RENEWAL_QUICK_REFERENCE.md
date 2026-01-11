# Revenue Sharing Contract Renewal - Quick Reference

## 🎯 New Features Overview

```
┌─────────────────────────────────────────────────────────────────┐
│  Revenue Sharing Rule (v18.0.2.0.0)                            │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  📍 Operating Unit Field (NEW)                                 │
│     ├─ Empty = Global rule (applies to all OUs)               │
│     └─ Selected = OU-specific rule (only for that store)      │
│                                                                 │
│  📅 Effective Date Range (NEW)                                 │
│     ├─ Valid From: Contract start date                         │
│     ├─ Valid To: Contract end date                            │
│     └─ Empty = Always valid                                    │
│                                                                 │
│  📦 Product Scope                                               │
│     ├─ All Products                                            │
│     ├─ Product Category                                        │
│     └─ Specific Product                                        │
│                                                                 │
│  💰 Sharing Lines (must total 100%)                           │
│     ├─ Store Type: X%                                          │
│     ├─ DC Type: Y%                                             │
│     └─ HO Type: Z%                                             │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

---

## 🔍 Rule Selection Priority

When processing a POS order, the system searches for rules in this order:

```
Priority 1 (Highest) ⭐⭐⭐⭐⭐⭐
┌──────────────────────────────────────────────────┐
│ Specific OU + Specific Product + Valid Date     │
│ Example: Store A + iPhone 15 + 2026 Contract    │
└──────────────────────────────────────────────────┘
                    ↓ (not found)
                    
Priority 2 ⭐⭐⭐⭐⭐
┌──────────────────────────────────────────────────┐
│ Any OU + Specific Product + Valid Date          │
│ Example: All Stores + iPhone 15 + 2026 Contract │
└──────────────────────────────────────────────────┘
                    ↓ (not found)
                    
Priority 3 ⭐⭐⭐⭐
┌──────────────────────────────────────────────────┐
│ Specific OU + Product Category + Valid Date     │
│ Example: Store A + Electronics + 2026 Contract  │
└──────────────────────────────────────────────────┘
                    ↓ (not found)
                    
Priority 4 ⭐⭐⭐
┌──────────────────────────────────────────────────┐
│ Any OU + Product Category + Valid Date          │
│ Example: All Stores + Electronics + 2026        │
└──────────────────────────────────────────────────┘
                    ↓ (not found)
                    
Priority 5 ⭐⭐
┌──────────────────────────────────────────────────┐
│ Specific OU + All Products + Valid Date         │
│ Example: Store A + All Products + 2026 Contract │
└──────────────────────────────────────────────────┘
                    ↓ (not found)
                    
Priority 6 (Default) ⭐
┌──────────────────────────────────────────────────┐
│ Any OU + All Products + Valid Date              │
│ Example: Global Default Rule (Fallback)         │
└──────────────────────────────────────────────────┘
```

---

## 📅 Contract Renewal Timeline Example

```
Timeline: Store A Revenue Sharing Contracts
─────────────────────────────────────────────────────────────────

2025                                    2026
│                                       │
├───────────────────────────────────────┼───────────────────────►
│                                       │
│   2025 Contract                       │   2026 Contract
│   ┌──────────────────────────────┐   │   ┌─────────────────►
│   │ Valid: 2025-01-01 to         │   │   │ Valid: 2026-01-01
│   │        2025-12-31            │   │   │        to 2026-12-31
│   │                              │   │   │
│   │ Store A: 30%                 │   │   │ Store A: 35%
│   │ DC:      40%                 │   │   │ DC:      35%
│   │ HO:      30%                 │   │   │ HO:      30%
│   └──────────────────────────────┘   │   │
│                                       │   │
│                                       │   │
└───────────────────────────────────────┴───┴──────────────────►
        Orders use 2025 rule          Transition!
                                       Orders use 2026 rule


✨ Automatic Switch:
   - Before 2026-01-01: Uses 2025 percentages
   - On/After 2026-01-01: Uses 2026 percentages
   - No manual intervention required!
```

---

## 🎬 Quick Start: Contract Renewal in 5 Steps

```
Step 1: Create New Contract Rule
┌────────────────────────────────────────┐
│ Name: Store A - 2026 Annual Contract  │
│ Operating Unit: Store A               │
│ Valid From: 2026-01-01                │
│ Valid To: 2026-12-31                  │
│ Apply To: All Products                │
└────────────────────────────────────────┘
           ↓
           
Step 2: Add Sharing Lines
┌────────────────────────────────────────┐
│ OU Type          Percentage           │
│ ─────────────────────────────────────  │
│ Store            35%                   │
│ DC               35%                   │
│ HO               30%                   │
│ ─────────────────────────────────────  │
│ Total:           100% ✓                │
└────────────────────────────────────────┘
           ↓
           
Step 3: Save & Activate
┌────────────────────────────────────────┐
│ [✓] Active                             │
│ Status: Ready for 2026-01-01           │
└────────────────────────────────────────┘
           ↓
           
Step 4: Test with Diagnostic
┌────────────────────────────────────────┐
│ Action → Revenue Sharing Diagnostic    │
│ ✓ Rule found for Store A              │
│ ✓ Dates valid                          │
│ ✓ Percentages total 100%              │
└────────────────────────────────────────┘
           ↓
           
Step 5: Wait for Effective Date
┌────────────────────────────────────────┐
│ System automatically uses new rule     │
│ starting 2026-01-01                    │
│ Old contract remains for history       │
└────────────────────────────────────────┘
```

---

## 💡 Common Use Cases

### Use Case 1: Global Default
```
┌───────────────────────────────────────────────┐
│ Operating Unit:  (empty)                      │
│ Valid From:      (empty)                      │
│ Valid To:        (empty)                      │
│ Apply To:        All Products                 │
│                                               │
│ Result: Applies to all stores, all products, │
│         all dates (fallback rule)            │
└───────────────────────────────────────────────┘
```

### Use Case 2: Store-Specific Forever
```
┌───────────────────────────────────────────────┐
│ Operating Unit:  Store A                      │
│ Valid From:      (empty)                      │
│ Valid To:        (empty)                      │
│ Apply To:        All Products                 │
│                                               │
│ Result: Store A has special percentages,     │
│         all other stores use global default  │
└───────────────────────────────────────────────┘
```

### Use Case 3: Annual Contract
```
┌───────────────────────────────────────────────┐
│ Operating Unit:  Store B                      │
│ Valid From:      2026-01-01                   │
│ Valid To:        2026-12-31                   │
│ Apply To:        All Products                 │
│                                               │
│ Result: Store B uses these percentages only  │
│         during 2026                           │
└───────────────────────────────────────────────┘
```

### Use Case 4: Seasonal Promotion
```
┌───────────────────────────────────────────────┐
│ Operating Unit:  (empty)                      │
│ Valid From:      2026-12-01                   │
│ Valid To:        2026-12-31                   │
│ Apply To:        Product Category: Toys       │
│                                               │
│ Result: Special sharing for toys during      │
│         December holiday season               │
└───────────────────────────────────────────────┘
```

### Use Case 5: Product Launch
```
┌───────────────────────────────────────────────┐
│ Operating Unit:  Store C                      │
│ Valid From:      2026-03-01                   │
│ Valid To:        2026-03-31                   │
│ Apply To:        Specific Product: iPhone 16  │
│                                               │
│ Result: Special sharing for iPhone 16 at     │
│         Store C during launch month           │
└───────────────────────────────────────────────┘
```

---

## 🔧 Configuration Checklist

Before creating a new contract rule:

```
☐ Determine Operating Unit scope
  ├─ ☐ Global (all OUs) - leave empty
  └─ ☐ Specific OU - select from dropdown

☐ Set effective dates
  ├─ ☐ Permanent - leave both empty
  ├─ ☐ Start date only - set Valid From
  ├─ ☐ End date only - set Valid To
  └─ ☐ Date range - set both (contract period)

☐ Choose product scope
  ├─ ☐ All Products (most common)
  ├─ ☐ Product Category (e.g., Electronics)
  └─ ☐ Specific Product (e.g., iPhone 15)

☐ Configure sharing percentages
  ├─ ☐ Add line for each OU Type
  ├─ ☐ Set percentage for each
  └─ ☐ Verify total = 100%

☐ Test before activation
  ├─ ☐ Save as draft
  ├─ ☐ Run diagnostic wizard
  └─ ☐ Activate when ready

☐ Plan for renewals
  ├─ ☐ Set end date for current contract
  ├─ ☐ Create next contract with new start date
  └─ ☐ Verify no gaps in coverage
```

---

## 🔎 Search Filters Quick Reference

```
Filter Name          Description
────────────────────────────────────────────────────────────
Currently Valid      Rules valid today (effective now)
Future Rules         Rules starting in the future
Expired Rules        Rules that have ended

Global Rules         Rules for all OUs
OU-Specific Rules    Location-specific rules

All Products         Rules applying to all products
By Category          Category-based rules
Specific Product     Product-specific rules

Group By:
  ├─ Operating Unit      See rules per store
  ├─ Apply To            Group by product scope
  ├─ Product Category    Group by category
  └─ Valid From Month    Group by contract month
```

---

## ⚠️ Important Notes

### Date Management
```
✅ DO:
  - Use continuous date ranges (no gaps)
  - Plan renewals in advance
  - Keep old contracts for history
  
❌ DON'T:
  - Delete old rules
  - Create overlapping dates carelessly
  - Leave gaps between contracts
```

### Percentage Validation
```
Total must equal exactly 100%
  ├─ System uses 0.01% tolerance
  ├─ Visual indicator: Green = OK, Red = Error
  └─ Warning shown if not 100%
```

### Rule Priority
```
More specific rules win:
  ├─ Specific OU > Global
  ├─ Specific Product > Category > All
  └─ Within same priority: Lower sequence wins
```

---

## 📊 Testing Your Configuration

### Manual Test Steps
```
1. Create test POS order
   ├─ Select Operating Unit
   ├─ Select Product
   └─ Use specific date

2. Open Revenue Sharing Period
   ├─ Set date range covering test order
   └─ Click "Calculate Revenue Sharing"

3. Verify result
   ├─ Check which rule was used
   ├─ Verify percentages correct
   └─ Review generated entries
```

### Using Diagnostic Wizard
```
1. Open Revenue Sharing Period
2. Action → Revenue Sharing Diagnostic
3. Click "Run Diagnostic"
4. Review report:
   ├─ POS orders found
   ├─ OUs configured
   ├─ Rules matched
   └─ Issues identified
```

---

## 🆘 Troubleshooting

### Problem: No rule found for order
```
Check:
  ☐ Rule is active
  ☐ Date range covers order date
  ☐ OU matches (or global rule exists)
  ☐ Product scope matches
  ☐ At least one fallback rule exists
```

### Problem: Wrong percentages used
```
Check:
  ☐ Multiple rules may match (higher priority wins)
  ☐ Date ranges may overlap
  ☐ Sequence numbers affect priority
  ☐ OU-specific rule overrides global
```

### Problem: Total not 100%
```
Solution:
  ☐ Add/edit sharing lines
  ☐ Ensure all percentages entered correctly
  ☐ System checks with 0.01% tolerance
  ☐ Green indicator = OK, Red = Error
```

---

## 📚 Documentation Files

```
REVENUE_SHARING_CONTRACT_RENEWAL.md
  └─ Complete guide with examples
  
REVENUE_SHARING_DEBUG.md
  └─ Troubleshooting DateTime issues
  
This file (Quick Reference)
  └─ Visual diagrams and checklists
```

---

## 🎓 Training Tips

### For Administrators
1. Start with global default rule
2. Add OU-specific rules as needed
3. Plan contract renewals quarterly
4. Use diagnostic wizard regularly
5. Keep documentation updated

### For Users
1. Understand rule priority system
2. Check effective dates before creating
3. Verify 100% total before saving
4. Test with diagnostic wizard
5. Report issues immediately

---

**Version:** 18.0.2.0.0  
**Last Updated:** January 2026  
**Module:** weha_operating_unit_contract
