# POS Order Limit

## Overview
This module allows you to hide/show the "Add Order" button and limit the number of orders that can be created in Odoo 18 Point of Sale.

## Features
- **Hide Add Order Button**: Option to completely hide the "Add Order" button from POS interface
- **Enable Order Limit**: Set a maximum number of orders that can be created in a single POS session
- **Configurable per POS**: Each POS configuration can have its own settings

## Configuration

### Setup
1. Install the module from Apps menu
2. Go to **Point of Sale → Configuration → Point of Sale**
3. Select a POS configuration
4. In the **Order Management** section, you'll find:
   - **Hide Add Order Button**: Check this to hide the button
   - **Enable Order Limit**: Check this to enable order limitation
   - **Maximum Orders**: Set the maximum number of orders (only visible when order limit is enabled)

### Usage
- When **Hide Add Order Button** is enabled, users won't see the "Add Order" button in POS
- When **Enable Order Limit** is enabled with a maximum value (e.g., 10):
  - Users can create orders up to the limit
  - Once the limit is reached, the "Add Order" button becomes hidden automatically
  - A warning notification appears if users try to exceed the limit
  - The button reappears when orders are removed and count is below the limit

## Technical Details
- **Odoo Version**: 18.0
- **Dependencies**: point_of_sale
- **License**: LGPL-3

## Module Structure
```
weha_pos_order_limit/
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
│       │   └── pos_order_limit.js
│       └── xml/
│           └── pos_order_limit.xml
├── views/
│   └── pos_config_views.xml
└── README.md
```

## Author
Your Company

## Support
For issues or questions, please contact your system administrator.
