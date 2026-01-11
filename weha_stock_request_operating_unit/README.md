# Stock Request Operating Unit

## Overview
This module integrates Odoo 18 Stock Request with OCA's Operating Unit modules. It automatically assigns operating units to all stock moves and pickings created from stock requests.

**Note**: This module requires OCA's operating_unit and stock_operating_unit modules to be installed first.

## Features

### Core Functionality
- **Stock Request**: Assign operating unit to each stock request
- **Stock Request Order**: Assign operating unit to stock request orders
- **Automatic Assignment**: All stock moves and pickings from stock requests are automatically assigned to the operating unit
- **Smart Buttons**: View related stock requests from pickings
- **Filtering**: Filter and group by operating unit in list views

### Integration Points
- **Stock Request**: Operating unit field (required)
- **Stock Request Order**: Operating unit field (required), propagates to child requests
- **Stock Move**: Links to stock request, inherits operating unit
- **Stock Picking**: Shows related stock requests via smart button
- Uses OCA's stock_operating_unit for stock move and picking operating unit fields

## Installation

### Prerequisites
This module requires OCA's Operating Unit modules:
- **operating_unit**: Base operating unit module
- **stock_operating_unit**: Operating unit for stock operations
- **stock_request**: OCA Stock Request module

Install these modules first before installing this module.

### Installation Steps
1. Install OCA's operating_unit module
2. Install OCA's stock_operating_unit module
3. Install OCA's stock_request module
4. Copy this module to your Odoo addons directory
5. Update the app list: Inventory → Configuration → Settings → Update Apps List
6. Search for "Stock Request Operating Unit"
7. Click Install

## Configuration

### 1. Create Operating Units (OCA Module)
**Settings → Users & Companies → Operating Units**

- Create your operating units using OCA's module
- Set up code, name, company, and partner for each unit

### 2. Assign Users to Operating Units
**Settings → Users & Companies → Users**

- Open user form
- Assign operating units to users
- Set default operating unit

### 3. Create Stock Requests
**Inventory → Operations → Stock Requests**

- Create stock request
- Select the Operating Unit field
- The operating unit is required for all stock requests
- All generated stock moves and pickings will inherit this operating unit

## Usage

### Creating Stock Requests

#### Individual Stock Request
1. Go to **Inventory → Operations → Stock Requests**
2. Click **Create**
3. Select **Operating Unit** (defaults to user's default OU)
4. Fill in product, quantity, and other details
5. Click **Confirm**
6. All generated stock moves will have the operating unit assigned

#### Stock Request Order
1. Go to **Inventory → Operations → Stock Request Orders**
2. Click **Create**
3. Select **Operating Unit** (will propagate to all child requests)
4. Add stock request lines
5. Click **Confirm**
6. All stock requests and their moves will have the operating unit assigned

### Viewing Stock Requests from Pickings
1. Open any stock picking
2. If created from stock request, a smart button "Stock Requests" will appear
3. Click the button to view related stock requests

### Filtering by Operating Unit
- In stock request list view, use **Group By → Operating Unit**
- Use search filters to find requests by operating unit
- Works for both Stock Requests and Stock Request Orders

## Technical Details

### Models Extended
- `stock.request`: Added operating_unit_id field (required, from OCA's operating.unit)
- `stock.request.order`: Added operating_unit_id field (required, propagates to requests)
- `stock.move`: Added stock_request_id field (computed from allocation)
- `stock.picking`: Added stock_request_ids and smart button

### Methods Overridden
- `stock.request._prepare_procurement_group_values()`: Assigns operating unit to procurement group
- `stock.request._prepare_stock_move_values()`: Assigns operating unit to stock move
- `stock.request._action_confirm()`: Ensures operating unit is set on all moves
- `stock.request.order.create()`: Propagates operating unit to child requests
- `stock.request.order.write()`: Propagates operating unit changes to child requests

### Views Added/Modified
- Extended Stock Request form, tree, and search views
- Extended Stock Request Order form, tree, and search views
- Added smart button to Stock Picking form view
- Added operating unit filters and group by options

### Security Rules
- Multi-operating unit access rules for stock.request
- Multi-operating unit access rules for stock.request.order
- Users can only see requests in their assigned operating units

### Dependencies on OCA Modules
- **operating_unit**: Provides the base operating.unit model
- **stock_operating_unit**: Provides operating_unit_id fields on stock.move and stock.picking
- **stock_request**: Base stock request functionality

## Usage Scenarios

### Scenario 1: Multi-Store Replenishment
- Create operating units for each store
- Store creates stock request with store's operating unit
- DC fulfills from inventory tagged with DC's operating unit
- Track inventory movements by operating unit

### Scenario 2: Department-based Stock Management
- Create operating units for departments (Kitchen, Bar, Retail)
- Each department creates stock requests with their operating unit
- Central warehouse tracks stock by department
- Generate reports by operating unit

### Scenario 3: Multi-Company with Shared Warehouse
- Create operating units for each company branch
- Stock requests are tagged by branch
- Shared warehouse fulfills requests
- Accounting and reporting separated by operating unit

## Security

Access rights defined for:
- Stock Request Users: Can create and view requests in their operating units
- Stock Request Managers: Can manage requests across operating units
- Uses OCA's operating unit security model for multi-OU access control

## Dependencies
- stock_request (OCA)
- operating_unit (OCA)
- stock_operating_unit (OCA)

## Compatibility
- Odoo Version: 18.0
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
- Operating unit field on stock requests
- Operating unit field on stock request orders
- Automatic operating unit assignment to stock moves
- Smart button on pickings to view related stock requests
- Security rules for multi-operating unit access
- Views and filters for operating unit
