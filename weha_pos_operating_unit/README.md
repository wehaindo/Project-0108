# POS Operating Unit

## Overview
This module integrates Odoo 18 Point of Sale with OCA's Operating Unit modules. It automatically assigns operating units to all journal entries created from POS transactions.

**Note**: This module requires OCA's operating_unit and account_operating_unit modules to be installed first.

## Features

### Core Functionality
- **POS Configuration**: Assign operating unit to each POS configuration
- **Automatic Assignment**: All journal entries from POS are automatically assigned to the operating unit:
  - POS Session closing entries
  - POS Order invoices
  - POS Payment entries
  - Reversal/refund entries

### Integration Points
- **POS Config**: Operating unit field (required)
- **POS Session**: Inherits operating unit from configuration
- **POS Order**: Inherits operating unit from session
- **POS Payment**: Inherits operating unit from order
- Uses OCA's account_operating_unit for journal entry operating unit fields

## Installation

### Prerequisites
This module requires OCA's Operating Unit modules:
- **operating_unit**: Base operating unit module
- **account_operating_unit**: Operating unit for accounting

Install these modules first before installing this module.

### Installation Steps
1. Install OCA's operating_unit module
2. Install OCA's account_operating_unit module
3. Copy this module to your Odoo addons directory
4. Update the app list: Apps → Update Apps List
5. Search for "POS Operating Unit"
6. Click Install

## Configuration

### 1. Create Operating Units (OCA Module)
**Settings → Users & Companies → Operating Units**

- Create your operating units using OCA's module
- Set up code, name, company, and partner for each unit

### 2. Assign Operating Unit to POS
**Point of Sale → Configuration → Point of Sale**

- Open your POS configuration
- Select the Operating Unit field
- The operating unit is required for all POS configurations

### 3. Use POS
- All orders created in POS will automatically inherit the operating unit
- All journal entries (session closing, invoices, payments) will have the operating unit assigned

## Technical Details

### Models Extended
- `pos.config`: Added operating_unit_id field (required, from OCA's operating.unit)
- `pos.session`: Added operating_unit_id field (related from config)
- `pos.order`: Added operating_unit_id field (related from session)
- `pos.payment`: Added operating_unit_id field (related from order)

### Methods Overridden
- `pos.session._create_account_move()`: Assigns operating unit to session closing entry
- `pos.order._create_invoice()`: Assigns operating unit to invoice
- `pos.order._create_misc_reversal_move()`: Assigns operating unit to reversal entries
- `pos.payment._create_payment_moves()`: Assigns operating unit to payment moves

### Views Added
- Extended POS Config, Session, Order views to show operating unit field

### Dependencies on OCA Modules
- **operating_unit**: Provides the base operating.unit model
- **account_operating_unit**: Provides operating_unit_id fields on account.move and account.move.line

## Usage Scenarios

### Scenario 1: Multi-Store Operations
- Create operating units for each store
- Assign each POS to its store's operating unit
- All journal entries are automatically tagged with the store
- Generate reports by operating unit to see per-store performance

### Scenario 2: Department-based Accounting
- Create operating units for departments (Food, Beverage, Retail)
- Assign POS to department operating units
- Track income and expenses by department

### Scenario 3: Multi-Company with Branches
- Create operating units for each branch
- Assign POS configurations to branch operating units
- Maintain separate accounting per branch while using shared master data

## Security

Access rights defined for:
- POS Users: Read access to operating units
- POS Managers: Full access to operating units
Uses OCA's operating unit security model.

## Dependencies
- point_of_sale
- account
- operating_unit (OCA)
- account_operating_unit (OCA)rsion: 18.0
- Module Version: 1.0.0

## Author
Weha
https://weha-id.com

## License
LGPL-3

## Support
For support, please contact your Odoo implementation partner.

## Changelog

### Version 1.0.0
- Initial release
- Operating unit master data
- POS integration
- Automatic journal entry assignment
- Views and security rules
Integration with OCA's operating_unit and account_operating_unit modules
- POS integration with operating unit
- Automatic journal entry assignment
- Views for POS model