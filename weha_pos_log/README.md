# POS Log Base Module

A comprehensive logging system for Odoo Point of Sale operations with local storage and server synchronization.

## Overview

This module provides a base logging infrastructure for tracking all POS activities including cashier logins/logouts, session management, orders, payments, and custom events. It stores logs locally in the POS client and automatically syncs them to the server.

## Features

### Core Functionality
- ✅ **Automatic Event Logging**: Tracks login, logout, session, order, and payment events
- ✅ **Local Storage**: Logs stored locally in browser for offline operation
- ✅ **Server Sync**: Automatic background sync every 5 minutes
- ✅ **Extensible**: Other modules can easily add custom event types
- ✅ **Audit Trail**: Complete history of POS activities
- ✅ **Search & Filter**: Powerful search with filters by user, session, date, event type

### Event Types
The module logs the following events out of the box:

| Event Type | Description |
|------------|-------------|
| `login` | Cashier login |
| `logout` | Cashier logout |
| `session_open` | POS session opened |
| `session_close` | POS session closed |
| `order_create` | New order created |
| `order_paid` | Order finalized/paid |
| `order_cancel` | Order cancelled |
| `payment` | Payment line added |
| `refund` | Refund processed |
| `cash_in` | Cash added to register |
| `cash_out` | Cash removed from register |
| `error` | Error occurred |
| `sync` | Data synchronization event |
| `other` | Custom events |

## Installation

1. Copy the `weha_pos_log` folder to your Odoo addons directory
2. Update the app list: Go to Apps → Update Apps List
3. Search for "POS Log Base"
4. Click Install

## Usage

### For End Users

#### Viewing Logs
1. Go to **Point of Sale → POS Logs → Activity Logs**
2. Use filters to find specific events:
   - **Not Synced**: View logs pending server sync
   - **Today**: Show today's logs
   - **Login Events**: Filter by login events
   - **Errors**: View error logs only
3. Group logs by event type, user, session, or date

#### Log Details
Click on any log entry to view:
- Event type and timestamp
- User who triggered the event
- Related POS session and configuration
- Order information (if applicable)
- Additional event data (JSON)
- Sync status

### For Developers

#### Creating Custom Logs

**From Python:**
```python
# Simple log
self.env['pos.log'].create_log(
    event_type='custom_event',
    description='Something happened',
)

# Detailed log with data
self.env['pos.log'].create_log(
    event_type='cash_in',
    user_id=self.env.user.id,
    session_id=session.id,
    config_id=config.id,
    description='Cash added to register',
    event_data={
        'amount': 1000.0,
        'reason': 'Starting cash',
        'currency': 'IDR'
    }
)
```

**From JavaScript (POS Client):**
```javascript
// Simple log
this.pos.createLog('custom_event', {
    description: 'Something happened'
});

// Detailed log
this.pos.createLog('product_search', {
    description: 'Product searched',
    search_term: 'coffee',
    results_count: 5,
    execution_time: 125
});
```

#### Extending Event Types

Create an inherited model to add custom event types:

```python
from odoo import models, fields

class PosLogExtended(models.Model):
    _inherit = 'pos.log'
    
    event_type = fields.Selection(
        selection_add=[
            ('inventory_check', 'Inventory Check'),
            ('price_override', 'Price Override'),
            ('discount_applied', 'Discount Applied'),
        ],
        ondelete={
            'inventory_check': 'set default',
            'price_override': 'set default',
            'discount_applied': 'set default',
        }
    )
```

#### Accessing Log Data Programmatically

```python
# Get unsynced logs
pending = self.env['pos.log'].get_pending_logs(limit=100)

# Filter logs
today_logs = self.env['pos.log'].search([
    ('create_date', '>=', fields.Date.today())
])

# Count login events
login_count = self.env['pos.log'].search_count([
    ('event_type', '=', 'login'),
    ('create_date', '>=', fields.Date.today())
])

# Get logs for specific user
user_logs = self.env['pos.log'].search([
    ('user_id', '=', user_id),
    ('create_date', '>=', date_from),
    ('create_date', '<=', date_to)
])
```

## Technical Details

### Data Model

**Model:** `pos.log`

**Key Fields:**
- `event_type`: Type of event (selection)
- `user_id`: User who triggered the event
- `session_id`: Related POS session
- `config_id`: POS configuration
- `order_id`: Related POS order
- `create_date`: Event timestamp
- `is_synced`: Sync status
- `sync_date`: When synced to server
- `event_data`: JSON data (flexible storage)
- `description`: Human-readable description

### JavaScript API

The module extends `PosStore` with the following methods:

```javascript
// Create log
this.pos.createLog(eventType, data)

// Sync logs to server
await this.pos.syncLogs()

// Get unsynced count
const count = this.pos.getUnsyncedLogsCount()

// Start/stop auto-sync
this.pos.startLogSync()
this.pos.stopLogSync()
```

### Sync Mechanism

1. **Local Storage**: Logs created in POS are stored in `this.pos.posLogs` array
2. **Auto-Sync**: Every 5 minutes, unsynced logs are sent to server
3. **Manual Sync**: Triggered when closing session or on demand
4. **Offline Support**: Logs queue locally if offline, sync when back online
5. **Cleanup**: Old synced logs are pruned (keeps last 1000)

## Use Cases

### Audit & Compliance
- Track all cashier activities for audit trails
- Monitor session open/close times
- Review payment and refund history
- Identify suspicious patterns

### Performance Monitoring
- Measure order processing times
- Track error frequency
- Monitor sync performance
- Analyze peak usage times

### Troubleshooting
- Debug POS issues with detailed logs
- Identify when errors occurred
- Review sequence of events leading to problems

### Reporting
- Generate cashier activity reports
- Session performance analytics
- Error rate analysis
- User productivity metrics

## Configuration

No special configuration required. The module works out of the box.

### Optional Settings (via code)

```javascript
// Change sync interval (default: 5 minutes)
// In pos_log.js, modify startLogSync():
this.syncInterval = setInterval(() => {
    if (this.isOnline) {
        this.syncLogs();
    }
}, 10 * 60 * 1000); // 10 minutes
```

## Security

### Access Rights
- **POS User**: Can create and read logs, cannot delete
- **POS Manager**: Full access except delete
- **System Admin**: Full access including delete

### Data Privacy
- Logs contain user activity data
- Event data stored in JSON format
- Can include sensitive information (amounts, products)
- Consider data retention policies for compliance

## Dependencies

- `point_of_sale`: Odoo Point of Sale module
- `base`: Odoo base module

## Compatibility

- **Odoo Version**: 17.0
- **Community/Enterprise**: Both
- **Browser Support**: Modern browsers with localStorage

## Extending This Module

Other modules can inherit and extend:

### Add Custom Event Types
```python
_inherit = 'pos.log'
event_type = fields.Selection(selection_add=[...])
```

### Add Custom Fields
```python
_inherit = 'pos.log'
custom_field = fields.Char('Custom Data')
```

### Hook Into Logging
```javascript
import { patch } from "@web/core/utils/patch";
import { PosStore } from "@point_of_sale/app/store/pos_store";

patch(PosStore.prototype, {
    myCustomAction() {
        this.createLog('custom_event', {
            description: 'Custom action performed',
            custom_data: 'value'
        });
        return super.myCustomAction(...arguments);
    }
});
```

## Troubleshooting

### Logs Not Appearing
- Check if module is installed and upgraded
- Verify browser console for JavaScript errors
- Ensure POS session is open
- Check internet connectivity for sync

### Sync Issues
- Check server logs for errors
- Verify user has write access to pos.log
- Check network connectivity
- Manually trigger sync from browser console: `odoo.__DEBUG__.services['point_of_sale.pos'].syncLogs()`

### Performance Issues
- Reduce sync interval if too frequent
- Clean up old logs: Delete synced logs older than X months
- Index database fields: `create_date`, `is_synced`, `user_id`, `session_id`

## Support

For issues, questions, or contributions:
- Check Odoo logs for errors
- Review browser console for JavaScript errors
- Verify module dependencies are installed
- Ensure Odoo version compatibility

## License

LGPL-3

## Author

Weha

## Changelog

### Version 17.0.1.0.0
- Initial release
- Basic logging for login/logout/session/orders
- Local storage with server sync
- Web interface for viewing logs
- Extensible event system
