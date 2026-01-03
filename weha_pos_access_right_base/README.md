# POS Access Right Base

## Overview
This module provides PIN-based authorization for sensitive POS operations. It integrates with the `pos_hr` module to use advanced employees for authorization.

## Features
- **Delete Order Line Protection**: Require advanced employee PIN to delete order lines
- **Clear Order Protection**: Require advanced employee PIN to clear all order lines
- **Refund Authorization**: Require advanced employee PIN for refund operations
- **Integration with pos_hr**: Uses the "Employees with manager access" field from pos_hr module

## Dependencies
- `point_of_sale`
- `pos_hr`

## Configuration

### Setup
1. Install the module from Apps menu
2. Make sure `pos_hr` module is installed
3. Go to **Point of Sale → Configuration → Point of Sale**
4. Select a POS configuration
5. Configure "Employees with manager access" in the HR section (from pos_hr module)
6. Enable authorization options in the new settings section:
   - **Require PIN to Delete Order Line**: Enable to require PIN when deleting order lines
   - **Require PIN to Clear Order**: Enable to require PIN when clearing all order lines
   - **Require PIN for Refund**: Enable to require PIN for refund operations

### Setting up Advanced Employees
1. Go to POS Configuration
2. In the "Employees with manager access" field (provided by pos_hr)
3. Add employees who should have authorization rights
4. Make sure these employees have PIN codes set

## Usage

### Delete Order Line
- When enabled, attempting to delete an order line will show a PIN popup
- Enter the PIN of any employee from "Employees with manager access"
- Order line will be deleted only if PIN is correct

### Clear Order
- When enabled, attempting to clear all order lines will show a PIN popup
- Enter the PIN of any advanced employee
- All order lines will be cleared only if PIN is correct

### Refund Operations
- When enabled, processing a refund (negative order total) will require PIN
- Enter the PIN of any advanced employee at payment validation
- Refund will be processed only if PIN is correct

## Technical Details
- **Odoo Version**: 18.0
- **Dependencies**: point_of_sale, pos_hr
- **License**: LGPL-3

## Module Structure
```
weha_pos_access_right_base/
├── __init__.py
├── __manifest__.py
├── models/
│   ├── __init__.py
│   └── pos_config.py
├── security/
│   └── ir.model.access.csv
├── static/
│   └── src/
│       ├── js/
│       │   ├── pin_popup.js
│       │   └── pos_access_control.js
│       └── xml/
│           └── pin_popup.xml
├── views/
│   └── pos_config_views.xml
└── README.md
```

## How It Works

1. **PIN Popup Component**: Custom popup that validates employee PIN
2. **Access Control Patches**: JavaScript patches that intercept POS operations
3. **Employee Validation**: Uses pos_hr's advanced_employee_ids field
4. **Operation Blocking**: Operations are blocked if PIN is incorrect or cancelled

## Author
Your Company

## Support
For issues or questions, please contact your system administrator.
