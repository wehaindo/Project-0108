# Operating Unit Hierarchy

Multi-level operating unit hierarchy with automated monthly revenue sharing for Odoo 18.0.

## Overview

This module manages operating unit hierarchy for multi-level business structures:
**Head Office (HO) → Distribution Center (DC) → Store**

## Key Features

### 1. Operating Unit Hierarchy
- Define parent-child relationships between operating units
- Support multi-level hierarchy (HO → DC → Store)
- Automatic hierarchy validation (prevents circular references)
- Visual hierarchy tree view
- Operating unit types with configurable levels

### 2. Monthly Revenue Sharing from POS Orders
- **Monthly batch processing** instead of per-order calculation
- Automatic revenue distribution across hierarchy levels
- Configurable revenue sharing percentages per level
- Support for multiple revenue sharing rules (by product category, product, or all products)
- Revenue sharing periods with workflow: Draft → Calculated → Validated → Posted → Closed
- Detailed revenue sharing entries for tracking and auditing

### 3. Revenue Sharing Configuration
- **Revenue Sharing Rules**: Define how revenue is split
  - Apply to: All Products, Product Category, or Specific Product
  - Multiple rule lines per OU type (Store, DC, HO)
  - Total percentage must equal 100%
  
- **Revenue Sharing Periods**: Monthly calculation periods
  - Auto-created from POS orders
  - Manual calculation trigger
  - Validation workflow
  - Accounting integration ready

### 4. Stock Request Integration (Future)
- Store requests from DC
- DC requests from HO or purchases from supplier
- Automatic routing based on hierarchy
- Stock availability checking at parent level

## Business Flow

### Revenue Sharing Example:

```
Store Jakarta 01 sells product → Total Revenue = Rp 1,000,000

Revenue Sharing (70-20-10 rule):
├── Store Jakarta 01 keeps: 70% → Rp 700,000
├── DC Jakarta gets: 20% → Rp 200,000
└── Head Office gets: 10% → Rp 100,000
```

### Monthly Processing Workflow:

1. **Throughout the month**: Stores make POS sales
2. **End of month**: Accountant opens "Revenue Sharing Period"
3. **Calculate**: Click "Calculate Revenue Sharing" button
   - System processes ALL POS orders for the month
   - Creates revenue sharing entries for each order line
4. **Review**: Verify entries are correct
5. **Validate**: Lock calculations
6. **Post Accounting**: Generate journal entries (future)
7. **Close Period**: Finalize the period

## Installation

### Prerequisites

Required OCA modules:
- `operating_unit`
- `account_operating_unit`
- `stock_request` (optional, for stock flow)

Required custom modules:
- `weha_pos_operating_unit`
- `weha_stock_request_operating_unit` (optional)

### Install Steps

1. Copy this module to your addons directory
2. Update app list
3. Install "Operating Unit Hierarchy"
4. Install demo data to see example structure

## Configuration

### 1. Create Operating Unit Types

Navigate to: **Operating Units → Configuration → Operating Unit Types**

Create three types:
- **HO** (Head Office): Level 0, can have children
- **DC** (Distribution Center): Level 1, can have parent and children
- **STORE** (Store): Level 2, can have parent

### 2. Create Operating Unit Hierarchy

Navigate to: **Operating Units → Configuration → OU Hierarchy**

Example structure:
```
Head Office Jakarta (HO)
├── DC Jakarta (DC)
│   ├── Store Jakarta 01 (STORE)
│   └── Store Jakarta 02 (STORE)
└── DC Surabaya (DC)
    └── Store Surabaya 01 (STORE)
```

For each OU, configure:
- **OU Type**: Select appropriate type
- **Parent OU**: Select parent (if applicable)
- **Revenue Share %**: Percentage this OU receives (e.g., Store: 70%, DC: 20%, HO: 10%)
- **Auto Share Revenue**: Enable automatic revenue sharing
- **Default Source OU**: For stock requests (stores → DC)

### 3. Create Revenue Sharing Rules

Navigate to: **Point of Sale → Revenue Sharing → Revenue Sharing Rules**

Example rule:
- **Name**: Default Revenue Sharing (70-20-10)
- **Apply To**: All Products
- **Lines**:
  - Store: 70%
  - DC: 20%
  - HO: 10%

You can create specific rules for:
- Product categories (e.g., Electronics: different split)
- Individual products (e.g., High-margin items)

## Usage

### Monthly Revenue Sharing Process

1. **View Periods**
   - Navigate to: **Point of Sale → Revenue Sharing → Revenue Sharing Periods**
   - Periods are auto-created from POS orders

2. **Calculate Revenue Sharing**
   - Open the period (e.g., "January 2026")
   - Click **Calculate Revenue Sharing** button
   - System processes all POS orders and creates entries

3. **Review Entries**
   - Click the **Entries** smart button
   - Verify amounts and percentages
   - Use pivot/graph views for analysis

4. **Validate**
   - Click **Validate** button
   - Locks the calculations

5. **Post Accounting** (Future feature)
   - Click **Post Accounting** button
   - Generates journal entries for inter-OU transfers

6. **Close Period**
   - Click **Close Period** button
   - Period is now closed and locked

### View Revenue Sharing Entries

Navigate to: **Point of Sale → Revenue Sharing → Revenue Sharing Entries**

Views available:
- **Tree**: List of all entries
- **Pivot**: Analysis by OU, period, product
- **Graph**: Visual charts of revenue distribution

### Reset and Recalculate

If you need to recalculate:
1. Open the period
2. Click **Reset to Draft**
3. Click **Calculate Revenue Sharing** again

## Demo Data

Install demo data to see:
- 3 OU Types (HO, DC, Store)
- 6 Operating Units (1 HO, 2 DC, 3 Stores)
- Default revenue sharing rule (70-20-10)

Structure:
```
Head Office Jakarta
├── DC Jakarta
│   ├── Store Jakarta 01
│   └── Store Jakarta 02
└── DC Surabaya
    └── Store Surabaya 01
```

## Technical Details

### Models

| Model | Description |
|-------|-------------|
| `operating.unit.type` | OU types (HO, DC, Store) |
| `operating.unit` | Extended with hierarchy fields |
| `revenue.sharing.rule` | Revenue sharing rules |
| `revenue.sharing.rule.line` | Rule lines per OU type |
| `revenue.sharing.period` | Monthly calculation periods |
| `revenue.sharing.entry` | Individual revenue sharing entries |
| `pos.order` | Extended with period link |

### Workflow States

**Revenue Sharing Period:**
- Draft → Calculated → Validated → Posted → Closed

**Revenue Sharing Entry:**
- Draft → Validated → Posted

## Benefits

✅ **Better Performance**: Monthly batch processing instead of per-order  
✅ **Batch Review**: Review all entries before posting  
✅ **Corrections**: Reset to draft and recalculate if needed  
✅ **Reporting**: View totals by period, OU, product  
✅ **Accounting Ready**: Prepared for journal entry integration  
✅ **Audit Trail**: Complete tracking of revenue distribution  
✅ **Flexibility**: Multiple rules by product/category

## Future Enhancements

- [ ] Accounting integration (auto-create journal entries)
- [ ] Stock request hierarchy routing
- [ ] Commission payments to employees
- [ ] Advanced reporting (revenue sharing dashboard)
- [ ] Multi-currency support
- [ ] Email notifications for period processing

## Support

For issues or questions:
- Email: support@weha-id.com
- Website: https://weha-id.com

## Credits

**Author**: Weha  
**License**: LGPL-3  
**Version**: 18.0.1.0.0

## Changelog

### Version 18.0.1.0.0 (2026-01-11)
- Initial release
- Operating unit hierarchy
- Monthly revenue sharing from POS orders
- Revenue sharing rules and periods
- Demo data with example structure
