# Stock Request Operating Unit Module - Structure

## Module: weha_stock_request_operating_unit

### File Structure
```
weha_stock_request_operating_unit/
├── __init__.py
├── __manifest__.py
├── README.md
├── models/
│   ├── __init__.py
│   ├── stock_request.py
│   ├── stock_request_order.py
│   ├── stock_move.py
│   └── stock_picking.py
├── views/
│   ├── stock_request_views.xml
│   └── stock_request_order_views.xml
├── security/
│   └── stock_request_security.xml
└── static/
    └── description/
        └── index.html
```

## Module Components

### 1. Manifest (__manifest__.py)
- **Name**: Stock Request Operating Unit
- **Version**: 18.0.1.0.0
- **Category**: Warehouse Management
- **License**: LGPL-3
- **Dependencies**:
  - stock_request (OCA)
  - operating_unit (OCA)
  - stock_operating_unit (OCA)

### 2. Models

#### stock_request.py
**Purpose**: Extends stock.request model with operating unit functionality

**Fields Added**:
- `operating_unit_id`: Many2one to operating.unit (required)

**Methods Extended**:
- `_get_default_operating_unit()`: Get default OU from user
- `_onchange_company_id_operating_unit()`: Reset OU on company change
- `_prepare_procurement_group_values()`: Add OU to procurement group
- `_prepare_stock_move_values()`: Add OU to stock move
- `_action_confirm()`: Ensure OU is set on all moves

#### stock_request_order.py
**Purpose**: Extends stock.request.order model with operating unit functionality

**Fields Added**:
- `operating_unit_id`: Many2one to operating.unit (required)

**Methods Extended**:
- `_get_default_operating_unit()`: Get default OU from user
- `_onchange_company_id_operating_unit()`: Reset OU on company change
- `create()`: Propagate OU to child stock requests
- `write()`: Propagate OU changes to child stock requests

#### stock_move.py
**Purpose**: Links stock moves to stock requests

**Fields Added**:
- `stock_request_id`: Many2one to stock.request (computed)

**Methods Added**:
- `_compute_stock_request_id()`: Compute stock request from allocation

#### stock_picking.py
**Purpose**: Shows related stock requests on pickings

**Fields Added**:
- `stock_request_ids`: Many2many to stock.request (computed)
- `stock_request_count`: Integer (computed)

**Methods Added**:
- `_compute_stock_request_ids()`: Compute stock requests from moves
- `action_view_stock_requests()`: Smart button action to view requests

### 3. Views

#### stock_request_views.xml
**Modifications**:
- Form view: Added operating_unit_id field
- Tree view: Added operating_unit_id field (optional)
- Search view: Added OU filter and group by

#### stock_request_order_views.xml
**Modifications**:
- Form view: Added operating_unit_id field
- Tree view: Added operating_unit_id field (optional)
- Search view: Added OU filter and group by
- Picking form: Added smart button for stock requests

### 4. Security

#### stock_request_security.xml
**Security Groups**:
- `group_stock_request_operating_unit`: Stock Request OU Access

**Record Rules**:
- `stock_request_comp_rule`: Users see only their OU's stock requests
- `stock_request_order_comp_rule`: Users see only their OU's stock request orders

Domain: Users can access records where:
- operating_unit_id is False, OR
- operating_unit_id is in user's operating_unit_ids

## Integration Flow

### Stock Request Creation Flow
```
User Creates Stock Request
    ↓
Operating Unit = User's Default OU (or manually selected)
    ↓
Stock Request Confirmed
    ↓
Stock Move Created with OU
    ↓
Stock Picking Created with OU (via stock_operating_unit)
    ↓
Smart Button on Picking shows related Stock Requests
```

### Stock Request Order Flow
```
User Creates Stock Request Order
    ↓
Operating Unit = User's Default OU (or manually selected)
    ↓
Add Stock Request Lines
    ↓
Operating Unit propagated to all child Stock Requests
    ↓
Stock Requests Confirmed
    ↓
All Stock Moves and Pickings have OU assigned
```

## Key Features

### 1. Automatic Operating Unit Assignment
- Stock requests require operating unit
- Stock moves inherit OU from stock request
- Stock pickings inherit OU via stock_operating_unit module
- Procurement groups tagged with OU

### 2. Operating Unit Propagation
- Order OU → Request OU
- Request OU → Move OU
- Move OU → Picking OU
- Full traceability maintained

### 3. User Experience Enhancements
- Default OU from user settings
- Smart buttons for easy navigation
- Filters and group by options
- Required field validation

### 4. Security & Access Control
- Multi-OU record rules
- Users limited to their OUs
- Manager override capabilities
- OCA security framework compliance

## Usage Examples

### Example 1: Store Stock Request
```python
# Create stock request for Store 1
stock_request = self.env['stock.request'].create({
    'product_id': product.id,
    'product_uom_qty': 100,
    'warehouse_id': warehouse.id,
    'operating_unit_id': store1_ou.id,  # Required!
    'location_id': store1_location.id,
})

# Confirm request
stock_request.action_confirm()

# Stock moves automatically have operating_unit_id = store1_ou.id
assert stock_request.move_ids.operating_unit_id == store1_ou
```

### Example 2: Stock Request Order
```python
# Create stock request order for multiple products
order = self.env['stock.request.order'].create({
    'warehouse_id': warehouse.id,
    'operating_unit_id': store2_ou.id,  # Will propagate to all requests
})

# Add stock request lines
self.env['stock.request'].create({
    'order_id': order.id,
    'product_id': product1.id,
    'product_uom_qty': 50,
    # operating_unit_id automatically set to store2_ou.id
})

# All child requests inherit the order's OU
assert all(r.operating_unit_id == store2_ou for r in order.stock_request_ids)
```

### Example 3: View Stock Requests from Picking
```python
# Get picking created from stock request
picking = stock_request.picking_ids[0]

# Smart button shows related stock requests
action = picking.action_view_stock_requests()
# Opens form/tree view of related stock requests
```

## Testing Checklist

- [ ] Install module with dependencies
- [ ] Create operating units
- [ ] Assign OUs to users
- [ ] Create stock request with OU
- [ ] Verify move has OU assigned
- [ ] Verify picking has OU assigned
- [ ] Test stock request order OU propagation
- [ ] Test filters and group by
- [ ] Test smart button on picking
- [ ] Test security rules (users see only their OU)
- [ ] Test company change resets OU
- [ ] Test default OU from user

## Notes

1. **Required Dependencies**: Must install OCA modules first:
   - operating_unit
   - stock_operating_unit
   - stock_request

2. **Operating Unit Required**: All stock requests must have an operating unit assigned

3. **OCA Compliance**: Uses OCA's operating unit framework for full compatibility

4. **Multi-Location Support**: Perfect for multi-store, multi-branch scenarios

5. **Store → DC → Supplier Flow**: Ideal for your use case where stores request from DC

## Future Enhancements (Optional)

- [ ] Add OU to stock request allocation
- [ ] Add OU summary dashboard
- [ ] Add OU-based stock request templates
- [ ] Add automatic OU assignment based on location
- [ ] Add OU-based stock request approval workflow

---
Created: January 11, 2026
Module Version: 18.0.1.0.0
Author: Weha
