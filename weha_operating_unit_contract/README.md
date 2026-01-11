# Operating Unit Revenue Sharing Contract

## Overview

This module manages revenue sharing contracts and calculations for multi-level operating unit hierarchies (HO → DC → Store).

## Features

### 1. Revenue Sharing Rules

- **Product-based Rules**: Define sharing percentages by product or product category
- **OU Type Percentages**: Configure different percentages for each OU type (HO, DC, Store)
- **Multiple Rules**: Support different rules for different products
- **Validation**: Ensures total percentages equal 100%

### 2. Revenue Sharing Periods

- **Monthly Periods**: Automatically created based on POS order dates
- **Calculation**: Calculate revenue sharing from POS orders
- **States**: Draft → Calculated → Validated → Posted → Closed
- **Accounting Integration**: Generate journal entries for inter-OU transfers

### 3. Revenue Sharing Entries

- **Detailed Tracking**: Individual entries per order line and receiving OU
- **Source & Target**: Track which OU sold and which OU receives
- **Amounts**: Total revenue, share percentage, and share amount
- **Reporting**: Analyze revenue distribution across OUs

## Configuration

### Step 1: Create Revenue Sharing Rules

1. Go to **Revenue Sharing > Configuration > Sharing Rules**
2. Create a new rule
3. Set:
   - **Name**: e.g., "Default Product Sharing"
   - **Apply To**: All Products / Category / Specific Product
   - **Sharing Lines**: Add lines for each OU type with percentages

Example:
```
Rule: Default Product Sharing
- Store: 70%
- DC: 20%
- HO: 10%
Total: 100%
```

### Step 2: Enable Auto Revenue Sharing

1. Go to **Operating Units > Configuration > Operating Units**
2. Edit each OU
3. Enable **Auto Share Revenue** checkbox
4. This enables automatic revenue sharing for POS orders

### Step 3: Process Revenue Sharing

1. Go to **Revenue Sharing > Operations > Sharing Periods**
2. System automatically creates monthly periods
3. Click **Calculate Revenue Sharing** button
4. Review entries
5. Click **Validate** → **Post Accounting** → **Close Period**

## Business Flow

### Example: Store Sells Product

**Sale:**
- Store A sells Product X for 1,000,000
- POS Order is created and paid

**Revenue Sharing:**
```
Total Revenue: 1,000,000
├─ Store A (70%): 700,000
├─ DC East (20%): 200,000
└─ HO (10%): 100,000
```

**Entries Created:**
1. Store A → Store A: 700,000 (70%)
2. Store A → DC East: 200,000 (20%)
3. Store A → HO: 100,000 (10%)

### Monthly Workflow

1. **POS Sales** happen throughout the month
2. **Period Auto-Created** at end of month
3. **Calculate** revenue sharing entries
4. **Review** entries for accuracy
5. **Validate** entries
6. **Post** accounting entries (inter-OU transfers)
7. **Close** period

## Reports & Analytics

### Revenue by Operating Unit

View revenue distribution:
- Total revenue per OU
- Revenue as selling OU
- Revenue as receiving OU
- Revenue sharing percentage

### Period Analysis

- Compare periods
- Track revenue trends
- Analyze sharing effectiveness

## Technical Details

### Models

- **revenue.sharing.rule**: Revenue sharing rules configuration
- **revenue.sharing.rule.line**: Percentage per OU type
- **revenue.sharing.period**: Monthly calculation periods
- **revenue.sharing.entry**: Individual revenue sharing entries

### Dependencies

- `operating_unit` (OCA)
- `account_operating_unit` (OCA)
- `point_of_sale`
- `weha_operating_unit_hierarchy`
- `weha_pos_operating_unit`

### Auto-Installation

This module must be manually installed after `weha_operating_unit_hierarchy`.

## Support

For issues or questions:
- Create an issue in the project repository
- Contact: support@weha-id.com

## License

LGPL-3.0

## Credits

- **Author**: Weha
- **Maintainer**: Weha
- **Version**: 18.0.1.0.0
