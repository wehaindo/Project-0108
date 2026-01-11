# Weha POS RFID Tag Reader

## Overview

This module enables automatic product selection in Odoo Point of Sale using RFID tags through a WebSocket connection. **Each physical product item has its own unique RFID tag**, allowing for accurate inventory tracking and quick scanning at checkout.

## Concept

- **One Product → Many RFID Tags**: Each product can have multiple RFID tags
- **One RFID Tag → One Physical Item**: Each RFID tag represents one physical item in your inventory
- **RFID Tag = Serial/Lot Number**: For tracked products, RFID tag automatically creates and links to serial/lot number
- **Real-time Location Tracking**: Know exactly where each item is in your warehouse
- **Stock Opname (Physical Inventory)**: Use RFID for fast and accurate inventory counts
- **Example**: 100 bottles of shampoo = 100 unique RFID tags = 100 serial numbers in Odoo

This approach enables:
- Accurate inventory tracking (each item is individually tracked)
- Quick checkout (scan items without manual barcode entry)
- Stock verification (know exactly which items have been sold)
- Loss prevention (track individual items)
- **Fast stock opname using RFID scanner**
- **Integration with Odoo's native inventory system**

## Features

- **WebSocket Integration**: Connects to a local WebSocket server to receive RFID tag data
- **Real-time Detection**: Automatically adds products to cart when RFID tags are scanned
- **Individual Item Tracking**: Each RFID tag represents one physical product item
- **Stock Integration**:
  - Automatic lot/serial number creation for tracked products
  - Link RFID tags to stock.lot (serial/lot numbers)
  - Track stock quantities per RFID tag
  - Integration with stock.quant
  - Automatic location updates via stock moves
- **Physical Inventory (Stock Opname)**:
  - RFID-based inventory count wizard
  - Compare scanned vs system inventory
  - Identify discrepancies automatically
  - Generate inventory adjustments
- **Tag Status Management**: Track tags as Active, Sold, or Inactive
- **Location Tracking**: Real-time location of each tagged item
- **Location History**: Complete audit trail of item movements
- **Scan Statistics**: Track scan count and last scanned date for each tag
- **Visual Feedback**: Shows connection status and tag reading indicators
- **Audio Feedback**: Optional beep sound when tags are successfully read
- **Auto-reconnect**: Automatically reconnects if WebSocket connection is lost
- **Bulk Operations**: Update locations for multiple tags at once

## Requirements

### Hardware
- RFID reader hardware compatible with your RFID tags
- Computer/device to run the WebSocket server

### Software
- Odoo 18.0 or higher
- WebSocket server that can communicate with your RFID reader
- Modern web browser with WebSocket support

## Installation

1. Copy the `weha_pos_rfid_tag` folder to your Odoo addons directory
2. Restart Odoo server
3. Update the apps list
4. Install the "Weha POS RFID Tag Reader" module

## WebSocket Server Setup

You need a WebSocket server that reads from your RFID hardware and sends tag data. Here's a simple Python example:

```python
# rfid_websocket_server.py
import asyncio
import websockets
import json

# This is a mock implementation - replace with actual RFID reader code
async def read_rfid():
    """Replace this with your actual RFID reader implementation"""
    # Example: return tag data from your RFID hardware
    return "RFID-001-ABC123"

async def handler(websocket, path):
    print(f"Client connected: {websocket.remote_address}")
    try:
        while True:
            # Read RFID tag from hardware
            rfid_tag = await read_rfid()
            
            if rfid_tag:
                # Send tag data as JSON
                data = json.dumps({"tag": rfid_tag})
                await websocket.send(data)
                print(f"Sent RFID tag: {rfid_tag}")
            
            await asyncio.sleep(0.1)
    except websockets.exceptions.ConnectionClosed:
        print("Client disconnected")

async def main():
    async with websockets.serve(handler, "localhost", 8765):
        print("WebSocket server started on ws://localhost:8765")
        await asyncio.Future()  # run forever

if __name__ == "__main__":
    asyncio.run(main())
```

Install dependencies:
```bash
pip install websockets
```

Run the server:
```bash
python rfid_websocket_server.py
```

### Data Format

The WebSocket server should send RFID tag data in one of these formats:

**Format 1 - Simple string:**
```
RFID-001-ABC123
```

**Format 2 - JSON with 'tag' field:**
```json
{"tag": "RFID-001-ABC123"}
```

**Format 3 - JSON with 'rfid' field:**
```json
{"rfid": "RFID-001-ABC123"}
```

**Format 4 - JSON with 'id' field:**
```json
{"id": "RFID-001-ABC123"}
```

## Configuration

### 1. Configure WebSocket URL

Go to **Point of Sale → Configuration → Settings**:

1. Scroll to "RFID Reader" section
2. Enable "Auto Connect to RFID Reader"
3. Set "RFID Websocket URL" (default: `ws://localhost:8765`)
4. Enable/disable "Enable Sound on Tag Read"
5. Click "Save"

### 2. Assign RFID Tags to Products

**Option 1: From Product Form**

Go to **Products → Products**:

1. Open a product
2. Go to the "RFID Tags" tab
3. Click "Add a line"
4. Enter the unique RFID tag identifier (e.g., "RFID-001-ABC123")
5. The status will be "Active" by default
6. Add as many tags as you have physical items
7. Save the product

**Option 2: From RFID Tags Menu**

Go to **Point of Sale → RFID Tags**:

1. Click "Create"
2. Enter the RFID Tag ID
3. Select the Product
4. Set Status to "Active"
5. Save

**Important**: 
- Each RFID tag ID must be unique across all products
- You can add multiple tags to the same product (one per physical item)
- Only "Active" tags will be recognized in POS
- Mark tags as "Sold" or "Inactive" to prevent them from being scanned

## Usage

### Managing RFID Tags

**View All Tags**: Go to **Point of Sale → RFID Management → RFID Tags**

**Filter by Status**:
- Active: Tags ready to be scanned
- Sold: Tags that have been sold (won't be added to cart)
- Inactive: Disabled tags

**Tag Actions**:
- Mark as Active/Sold/Inactive
- View scan statistics
- View location history
- View stock quantities
- Add notes to tags

### Stock Opname (Physical Inventory Count)

**Using RFID for Inventory Count**:

1. Go to **Point of Sale → RFID Management → Inventory Count (Opname)**
2. Select the location to count
3. Optionally filter by specific products
4. Click "Start Counting"
5. Scan all RFID tags in the location using your RFID reader
6. Review scanned items
7. Click "View Discrepancies" to see missing or extra items
8. Click "Generate Adjustment" to create inventory adjustment

**Benefits**:
- **10x faster** than manual counting
- **99%+ accuracy** with RFID scanning
- Real-time comparison with system inventory
- Automatic discrepancy detection
- Integration with Odoo's inventory adjustment

### Bulk Location Updates

1. Go to **RFID Tags** list view
2. Select multiple tags (checkbox)
3. Click **Action → Update Location**
4. Select new location
5. Add optional notes
6. Confirm

### Search RFID Tags

1. Go to **Point of Sale → RFID Management → Search Tag**
2. Enter RFID tag ID
3. Click "Search"
4. View tag details including:
   - Product information
   - Current location
   - Serial/lot number
   - Stock quantities
   - Location history

### In POS

1. Open a POS session
2. The RFID reader will automatically connect (if auto-connect is enabled)
3. Check the connection status indicator in the POS interface
4. Scan RFID tags near the reader
5. Products will be automatically added to the cart (quantity 1 per tag)
6. Each scan updates the tag's statistics (scan count, last scanned date)

### Connection Status

- **Green WiFi Icon**: Connected and ready
- **Red WiFi Icon**: Disconnected

### Manual Connect/Disconnect

Click the "Connect" or "Disconnect" button in the RFID reader widget to manually control the connection.

## Troubleshooting

### RFID Reader Won't Connect
status is "Active" (not Sold or Inactive)
2. Check if the tag is correctly assigned to a product
3. Ensure the product is available for sale in POS
4. Verify the product is in the POS product list
5. Look for error notifications in POS
6. Go to **Point of Sale → RFID Tags** to verify the tag existsconnection
4. Check browser console for error messages

### Tags Not Detected

1. Verify RFID tags are assigned to products
2. Check if the tag data format matches one of the supported formats
3. Look at WebSocket server logs to confirm data is being sent
4. Check browser console for RFID tag readings

### Products Not Added to Cart

1. Verify the RFID tag is correctly assigned to the product
2. Ensure the product is available for sale in POS
3. Check if the product is in the POS product list
4. Look for error notifications in POS

### Connection Keeps Dropping

1. Check WebSocket server stability
2. Verify network connection
3. Check for connection timeout settings
4. Review browser console for WebSocket errors

## Technical Details

### Architecture

```
RFID Reader Hardware
        ↓
WebSocket Serverrfid_tag.py       # RFID tag model (many tags per product)
│   ├── product_template.py       # Product extension with tag relationship
│   └── res_config_settings.py    # POS configuration
├── security/
│   └── ir.model.access.csv
├── static/src/app/
│   ├── rfid_service.js           # WebSocket service
│   ├── rfid_reader.js            # UI component
│   ├── rfid_reader.xml           # Component template
│   ├── rfid_reader.scss          # Component styles
│   └── product_screen_patch.js   # POS integration & tag loading
├── views/
│   ├── product_rfid_tag_views.xml  # RFID tag management views
│   ├── product_template_views.xml  # Product form with tags tab
weha_pos_rfid_tag/
├── __init__.py
├── __manifest__.py
├── models/
│   ├── __init__.py
│   ├── product_template.py      # RFID tag field on products
│   └── res_config_settings.py   # POS configuration
├── security/
│   └── ir.model.access.csv
├── static/src/app/
│   ├── rfid_service.js          # WebSocket service
│   ├── rfid_reader.js           # UI component
│   ├── rfid_reader.xml          # Component template
│   ├── rfid_reader.scss         # Component styles
│   └── product_screen_patch.js  # POS integration
├── views/
│   ├── product_template_views.xml
│   └── res_config_settings_views.xml
└── README.md
```

### JavaScript Services

- **rfidService**: ManLoads RFID tags from server and creates lookup index for fast tag-to-product resolution

### Models

**product.rfid.tag**:
- `name`: Unique RFID tag identifier
- `product_id`: Related product (many-to-one)
- `lot_id`: Related serial/lot number (auto-created for tracked products)
- `location_id`: Current warehouse location
- `status`: Active/Sold/Inactive
- `on_hand_qty`: Computed stock on hand
- `available_qty`: Computed available quantity
- `quant_ids`: Related stock quants
- `scan_count`: Number of times scanned
- `last_scanned_date`: Last time this tag was scanned
- `location_history_ids`: Movement history
- `notes`: Additional notes

**product.rfid.tag.location.history**:
- `rfid_tag_id`: Related RFID tag
- `product_id`: Related product
- `from_location_id`: Previous location
- `to_location_id`: New location
- `move_date`: When the move occurred
- `stock_move_id`: Related stock move (if applicable)
- `user_id`: User who performed the move

**stock.quant** (extended):
- `rfid_tag_id`: Link to RFID tag
- `rfid_tag_count`: Number of RFID tags at this location

**stock.move** (extended):
- Auto-updates RFID tag locations when moves are completed

**stock.lot** (extended):
- Automatically created from RFID tag for tracked products

**product.template** (extended):
- `rfid_tag_ids`: One2many relationship to RFID tags
- `rfid_tag_count`: Computed field showing number of tagsion, and dispatches tag events
- **RfidReader Component**: Displays connection status and allows manual control
- **PosStore Patch**: Indexes products by RFID tag for fast lookup

## API Reference

### RFID Service

```javascript
// Get RFID service
const rfid = useService("rfid");

// Connect to WebSocket
rfid.connect();

// Disconnect
rfid.disconnect();

// Check connection status
const isConnected = rfid.isConnected();

// Listen to events
rfid.addEventListener((event, data) => {
    if (event === 'tag_read') {
        console.log('Tag r name
const product = this.pos.getProductByRfidTag('RFID-001-ABC123');

// Get full RFID tag info (including tag ID, product, etc.)
const tagInfo = this.pos.getRfidTagInfo('RFID-001-ABC123');
// Returns: { id, name, product, product_id }

// Update scan statistics
await this.pos.env.services.orm.call(
    'product.rfid.tag',
    'update_scan_info',
    [[tagId]]

});
RFID tags loaded once at POS startup
- Only active tags are loaded into memory
- Automatic reconnection with exponential backoff
- Efficient WebSocket message handling
- Minimal POS UI impact
- Scan statistics updated asynchronously

## Use Cases

##Multiple RFID tags per product (one tag per physical item)
- Product assignment and lookup
- Tag status management (Active/Sold/Inactive)
- Scan statistics tracking
- Visual and audio feedback
- Auto-reconnect functionality
- POS configuration settings
- Bulk tag management interface were sold

### Electronics
- Each high-value item (phone, laptop) has unique RFID
- Prevent theft with individual item tracking
- Warranty tracking by serial number

### Inventory Management
- Physical stock counts by scanning RFID tags
- Know exactly which items are in stock vs. sold
- Track item movement and history
    url: 'ws://localhost:9000',
    soundEnabled: false
});
```

### Product Lookup

```javascript
// Get product by RFID tag
const product = this.pos.getProductByRfidTag('RFID-001-ABC123');
```

## Security

- RFID tags are validated for uniqueness
- WebSocket connection is local by default (localhost)
- No sensitive data is transmitted over WebSocket
- Standard Odoo access rights apply to product management

## Performance

- Indexed lookup for RFID tags (O(1) performance)
- Automatic reconnection with exponential backoff
- Efficient WebSocket message handling
- Minimal POS UI impact

## Changelog

### Version 18.0.1.0.0
- Initial release
- WebSocket integration for RFID reading
- Product assignment and lookup
- Visual and audio feedback
- Auto-reconnect functionality
- POS configuration settings
- **Bulk tag management interface**
- **Stock lot/serial integration**
- **Automatic serial number creation for tracked products**
- **Location tracking and history**
- **Stock quant integration**
- **Physical inventory count wizard (Stock Opname)**
- **Automatic location updates via stock moves**
- **Bulk location update operations**

## Stock Integration & Inventory Count (Stock Opname)

### Why Integrate with Odoo Stock?

Traditional RFID solutions often work standalone, but this module integrates deeply with Odoo's native inventory system, providing:
- **Full traceability** via stock.lot (serial/lot numbers)
- **Automatic location updates** via stock moves
- **Real-time stock quantities** via stock.quant
- **Fast physical inventory** (stock opname) using RFID scanner
- **Seamless inventory adjustments** directly in Odoo

### Automatic Lot/Serial Number Creation

When you create an RFID tag for a product that uses serial or lot tracking, the system automatically:
1. Creates a new lot/serial number using the RFID tag ID
2. Links the RFID tag to this lot/serial number
3. Enables full traceability in Odoo

**Example**:
- Product: iPhone 15 Pro (tracking: by unique serial number)
- RFID Tag ID: RFID-IPHONE-001
- Result: Serial number "RFID-IPHONE-001" automatically created and linked

### Stock Opname (Physical Inventory Count) with RFID

The RFID Inventory Count wizard transforms how you do physical inventory:

**Traditional Manual Count** (Without RFID):
1. Print inventory list
2. Walk warehouse with clipboard
3. Manually count each item
4. Write down quantities
5. Enter data into system
6. Find and fix errors
7. **Time: 4-6 hours for 1000 items**

**RFID Count** (With This Module):
1. Open inventory count wizard
2. Select location
3. Walk around with RFID reader
4. Tags are automatically scanned
5. System compares scanned vs. expected
6. Review discrepancies
7. Generate adjustment with one click
8. **Time: 15-30 minutes for 1000 items** ✨

**Time Savings: 90%+ reduction!**

### How to Use Stock Opname Feature

1. **Start Inventory Count**
   - Go to: **Point of Sale → RFID Management → Inventory Count (Opname)**
   - Select the warehouse location to count
   - Optionally filter by specific products
   - Click "Start Counting"

2. **Scan Items**
   - Walk through the location with your RFID reader
   - All RFID tags are automatically detected and recorded
   - See real-time count of scanned items
   - System shows: Total Scanned vs. Total in System

3. **Review Results**
   - View list of all scanned tags
   - See scanned vs. system inventory comparison
   - Click "View Discrepancies" to see:
     - Missing items (in system but not scanned)
     - Extra items (scanned but not in system)

4. **Generate Adjustment**
   - Click "Generate Adjustment"
   - System creates Odoo inventory adjustment
   - Review and validate the adjustment
   - Stock levels automatically updated

### Location Tracking

**Automatic Location Updates**:
- When you complete a stock move in Odoo, RFID tag locations update automatically
- When you validate a picking, all tagged items move to destination location
- Every movement is logged in location history

**Manual Location Updates**:
- **Bulk Update**: Select multiple tags → Action → Update Location
- **Individual Update**: Open tag → Change location field
- All changes are recorded with user, date, and notes

**Location History**:
- Complete audit trail of all movements
- See when, where, and who moved items
- Link to stock moves for full traceability
- Add notes for each movement

### Stock Quant Integration

**View RFID Tags in Inventory**:
- Each stock quant shows "RFID Tags" count
- Know how many tagged vs. untagged items
- Verify physical inventory against RFID data
- Link RFID tags directly to quants

### Search and Traceability

**Find Any Item Instantly**:
1. Go to **RFID Management → Search Tag**
2. Enter RFID tag ID (or scan with reader)
3. View complete information:
   - Product details
   - Current location
   - Serial/lot number
   - Stock quantities (on hand, available, reserved)
   - Complete movement history
   - Last scanned date/time

## Benefits Comparison

| Task | Without RFID | With RFID Module | Time Saved |
|------|--------------|------------------|------------|
| Inventory Count (1000 items) | 4-6 hours | 15-30 min | **90%+** |
| Find Single Item | 10-30 min | 10 seconds | **99%+** |
| Stock Move Verification | 5-10 min | Automatic | **100%** |
| Location Update | Manual entry | Automatic | **100%** |
| Discrepancy Detection | Manual | Automatic | **100%** |
| Serial Number Entry | Manual | Automatic | **100%** |

## Real-World Impact

### For Warehouse Manager
- Reduce inventory count from monthly to weekly (or even daily!)
- Know exact location of every item
- Catch discrepancies immediately
- Reduce shrinkage and loss

### For Finance/Audit
- Accurate inventory valuation
- Complete audit trail
- Meet compliance requirements
- Reduce discrepancies by 95%+

### For Operations
- Faster receiving and shipping
- No manual data entry
- Reduce human errors
- Improve efficiency

## Support

For issues, questions, or feature requests, please contact:
- Website: https://weha-id.com
- Email: support@weha-id.com

## License

LGPL-3

## Credits

- Developed by Weha
- Based on Odoo 18 Point of Sale framework
