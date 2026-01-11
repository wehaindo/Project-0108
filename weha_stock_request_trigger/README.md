# Stock Request Trigger - Automatic Replenishment

## Overview

This module provides automatic stock replenishment functionality integrated with Operating Units and Stock Request system. It monitors stock levels per operating unit and automatically creates stock requests when products fall below minimum levels.

## Key Features

### 1. Replenishment Rules
- Configure min/max stock levels per product per operating unit
- Define reorder points and quantities
- Automatic source determination from OU hierarchy
- Support for multiple locations and warehouses

### 2. Automatic Replenishment
- Scheduled action runs hourly to check stock levels
- Auto-creates stock requests when below minimum
- Uses OU hierarchy to determine source (Store → DC → HO)
- Tracks trigger dates and history

### 3. Manual Replenishment
- Wizard to manually trigger replenishment
- Preview and adjust quantities before creation
- Batch create requests for multiple products
- Filter by operating unit

### 4. Stock Request Integration
- Links replenishment rules to stock requests
- Tracks auto-generated vs manual requests
- Extended views show replenishment information
- Filter and search by auto-generation status

## Installation

1. Install dependencies:
   - `stock`
   - `stock_request` (OCA)
   - `stock_operating_unit` (OCA)
   - `operating_unit` (OCA)
   - `weha_operating_unit_hierarchy`
   - `weha_stock_request_operating_unit`

2. Install `weha_stock_request_trigger`

3. Update apps list and install the module

## Configuration

### 1. Setup Replenishment Rules

Navigate to: **Inventory > Replenishment > Replenishment Rules**

For each product/location/OU combination:
- Select Operating Unit
- Select Warehouse and Location
- Select Product
- Set Minimum Quantity (reorder point)
- Set Maximum Quantity (target stock)
- **Select Route** (DC → Store transfer route)
- Enable Auto Trigger (optional)

### 2. Configure Routes (IMPORTANT!)

**Stock requests need routes to generate transfers!**

See **[ROUTE_CONFIGURATION_GUIDE.md](ROUTE_CONFIGURATION_GUIDE.md)** for complete setup.

Quick setup:
```
Inventory > Configuration > Routes > Create

Name: DC East → Store A
Add Rule:
- Action: Pull From
- Source: DC East/Stock
- Destination: Store A/Stock
- Picking Type: Store A: Internal Transfers
```

Then link route to replenishment rule.

### 3. Configure Scheduled Action

Navigate to: **Settings > Technical > Automation > Scheduled Actions**

Find: **Check Stock Replenishment Rules**
- Default: Runs every 1 hour
- Adjust interval as needed
- Ensure it's active

### 3. Setup OU Hierarchy

Ensure Operating Unit hierarchy is configured in `weha_operating_unit_hierarchy`:
- HO (Head Office) at top level
- DC (Distribution Centers) as children of HO
- Stores as children of DCs

Each Store should have `default_source_ou_id` pointing to its parent DC.

## Usage

### Automatic Replenishment

1. **System monitors stock levels** (hourly by default)
2. **When stock < minimum:**
   - System checks replenishment rule
   - Determines source OU from hierarchy
   - Creates stock request automatically
   - Updates trigger date
3. **Stock request flows** through standard workflow

### Manual Replenishment

1. Navigate to: **Inventory > Replenishment > Manual Replenishment**
2. Select Operating Unit
3. System shows all products below minimum
4. Review and adjust quantities
5. Click "Create Stock Requests"
6. Review created requests

### View Replenishment Status

**Replenishment Rules:**
- Red rows = Below minimum stock
- Filter by "Below Minimum"
- Group by Operating Unit, Product, or Location

**Stock Requests:**
- Badge shows "Auto Generated"
- Filter by "Auto Generated"
- View linked replenishment rule

## Technical Details

### Models

#### stock.replenishment.rule
- Main model for replenishment configuration
- Fields:
  - `operating_unit_id`: Target OU
  - `product_id`: Product to replenish
  - `location_id`: Stock location
  - `minimum_qty`: Reorder point
  - `maximum_qty`: Target quantity
  - `current_qty`: Computed current stock
  - `reorder_qty`: Computed order quantity
  - `auto_trigger`: Enable auto-creation
  - `source_ou_id`: Computed from hierarchy

#### stock.request (extended)
- Added fields:
  - `replenishment_rule_id`: Link to rule
  - `is_auto_generated`: Auto vs manual flag

### Methods

#### _cron_check_replenishment()
- Scheduled action method
- Finds all active rules with auto_trigger
- Checks stock levels
- Creates stock requests for items below minimum

#### action_create_stock_request()
- Manual trigger from rule form
- Creates single stock request
- Opens created request

#### _compute_source_ou()
- Determines source OU from hierarchy
- Uses `default_source_ou_id` if set
- Falls back to `parent_id`

## Workflow Example

### Store A needs product replenishment:

1. **Initial State:**
   - Store A: Product X stock = 5 units
   - Minimum = 10 units
   - Maximum = 50 units
   - Source = DC East

2. **Automatic Trigger:**
   - Scheduled action runs
   - Detects: 5 < 10 (below minimum)
   - Calculates: 50 - 5 = 45 units needed
   - Creates stock request:
     - From: DC East
     - To: Store A
     - Product: X
     - Qty: 45 units

3. **Request Processing:**
   - DC East receives request
   - Checks own stock
   - If available: Transfers to Store A
   - If not available: Creates request to HO

4. **Result:**
   - Store A receives 45 units
   - New stock = 50 units (maximum)
   - Ready for next sales cycle

## Customization

### Adjust Reorder Logic

Override `_compute_reorder_qty()` in `stock.replenishment.rule`:

```python
@api.depends('current_qty', 'maximum_qty', 'minimum_qty')
def _compute_reorder_qty(self):
    for rule in self:
        # Custom logic: Order to maximum + safety stock
        safety_stock = 10.0
        if rule.current_qty < rule.minimum_qty:
            rule.reorder_qty = rule.maximum_qty - rule.current_qty + safety_stock
        else:
            rule.reorder_qty = 0.0
```

### Change Scheduled Frequency

Modify `ir_cron_data.xml`:

```xml
<field name="interval_number">30</field>  <!-- Every 30 minutes -->
<field name="interval_type">minutes</field>
```

### Add Email Notifications

Extend `_cron_check_replenishment()`:

```python
# After creating request
if stock_request:
    template = self.env.ref('your_module.email_template_low_stock')
    template.send_mail(stock_request.id, force_send=True)
```

## Security

### Access Rights

- **Stock User:** Read, Write, Create replenishment rules
- **Stock Manager:** All rights including Delete

### Record Rules

Rules respect operating unit access rights from `operating_unit` module.

## Troubleshooting

### Stock requests not created automatically

1. Check scheduled action is active
2. Verify replenishment rule:
   - Active = True
   - Auto Trigger = True
   - Below minimum = True
3. Check source OU is configured
4. Review logs in **Settings > Technical > Logging**

### Wrong quantities calculated

1. Verify current stock in location
2. Check minimum/maximum values
3. Review reorder quantity computation
4. Ensure correct UoM

### Source OU not found

1. Check OU hierarchy in `weha_operating_unit_hierarchy`
2. Verify `default_source_ou_id` is set
3. Ensure parent_id is configured for fallback

## Module Structure

```
weha_stock_request_trigger/
├── __init__.py
├── __manifest__.py
├── README.md
├── models/
│   ├── __init__.py
│   ├── stock_replenishment_rule.py  # Main replenishment logic
│   └── stock_request.py              # Stock request extension
├── wizard/
│   ├── __init__.py
│   ├── stock_replenishment_wizard.py # Manual replenishment
│   └── stock_replenishment_wizard_views.xml
├── views/
│   ├── stock_replenishment_rule_views.xml
│   └── stock_request_views.xml
├── data/
│   ├── ir_cron_data.xml              # Scheduled action
│   └── demo_data.xml                 # Demo rules
└── security/
    └── ir.model.access.csv           # Access rights
```

## Dependencies

- Odoo 18.0
- stock (core)
- stock_request (OCA)
- stock_operating_unit (OCA)
- operating_unit (OCA)
- weha_operating_unit_hierarchy (custom)
- weha_stock_request_operating_unit (custom)

## Support

For issues or questions:
1. Check logs: **Settings > Technical > Logging**
2. Review demo data for examples
3. Test with manual replenishment first
4. Verify OU hierarchy configuration

## License

LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl-3.0)

## Author

Weha (2026)
