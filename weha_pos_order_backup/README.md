# POS Order Backup Module

## Overview

Advanced POS order backup system that automatically backs up orders locally and syncs to a dedicated server table. Features batch import, automatic duplicate detection, analytics dashboard, and data retention management.

## Key Features

### 🔒 **Automatic Backup**
- Orders automatically backed up to IndexedDB when validated
- Background sync to server every 30 seconds
- Separate `pos.order.backup` table (not pos.order)

### 📊 **Structured Data Storage**
- Dedicated backup table with structured fields
- Easy searching and filtering by:
  - Order reference, date, session
  - Customer, amount, status
  - Config, user, state
- Better query performance than JSON-only storage

### 🔄 **Batch Import**
- Import multiple orders at once
- Filter by session, date range, or selection
- Preview before importing
- Detailed import results with error tracking

### ✅ **Smart Duplicate Detection**
- Automatic detection of existing orders
- Prevents duplicate imports
- Mark orders as verified when found on server

### 📈 **Analytics Dashboard**
- Visual statistics with graphs and pivot tables
- Track backup success rate
- Monitor missing orders by session
- View trends over time

### 🧹 **Data Retention**
- Configurable cleanup wizard
- Auto-delete old backups (verified/imported/duplicates)
- Retention policy settings
- Preview before cleanup

### 🎯 **Enhanced UI**
- Smart filters: "Missing on Server", "Ready to Import", "Last 7 Days"
- Bulk actions from tree view
- Color-coded states
- Status badges and ribbons

## How It Works

### 1. Order Validation
When a cashier validates an order in POS:
- Order saved to server (normal flow)
- Order backed up to IndexedDB (local storage)
- Backup includes full order data (lines, payments, etc.)

### 2. Background Sync
- Every 30 seconds, unsynced backups sync to server
- Saved in `pos.order.backup` table (separate from pos.order)
- Structured fields extracted for easy querying

### 3. Order Verification
- System checks if order exists on server
- Updates backup state: backup → synced → verified
- Identifies missing orders automatically

### 4. Import Process
When order is missing on server:
- Manager can import from backup
- Uses standard POS order creation method
- Tracks import user, date, and results
- Prevents duplicates

## Usage Guide

### For Cashiers
Orders are automatically backed up - no action needed!

### For Managers

#### View Backups
**Point of Sale → Order Backups**
- See all backed up orders
- Filter by status, date, session
- View backup statistics

#### Find Missing Orders
Use filters:
- **"Missing on Server"** - Orders not found on server
- **"Ready to Import"** - Orders that can be imported
- **"Can Import"** - Safe to import now

#### Batch Import Orders

**Method 1: From Tree View**
1. Select multiple backup records
2. Click "Action" → "Batch Import Orders"
3. Choose options (only missing, etc.)
4. Preview then Import

**Method 2: From Wizard**
1. Go to Order Backups
2. Click "Action" → "Batch Import Orders"
3. Select filter type:
   - All Missing Orders
   - By Session
   - By Date Range
   - Selected Records
4. Preview and confirm

#### View Dashboard
**Point of Sale → Order Backups → Backup Dashboard**
- View graphs and statistics
- Analyze backup trends
- Track success rates
- Monitor by session/config

#### Cleanup Old Backups
**Point of Sale → Order Backups → Cleanup Old Backups**
1. Set retention days (default: 30)
2. Choose states to clean (verified, imported, duplicates)
3. Preview records to delete
4. Confirm cleanup

## Backup States

| State | Description |
|-------|-------------|
| **Backup** | Saved locally, not yet synced to server |
| **Synced** | Successfully synced to server backup table |
| **Verified** | Confirmed to exist on server as pos.order |
| **Imported** | Imported from backup to pos.order table |
| **Duplicate** | Order already exists, no import needed |
| **Error** | Import failed, check error message |

## Technical Details

### Models

**pos.order.backup**
- Main backup model with structured fields
- Stores complete order data as JSON
- Automatic verification and duplicate detection
- Import tracking and error handling

**pos.order.backup.import.wizard**
- Batch import multiple orders
- Flexible filtering options
- Preview and results display

**pos.order.backup.cleanup.wizard**
- Data retention management
- Configurable cleanup rules
- Safety checks (min 7 days)

### Storage

**Local: IndexedDB**
- Database: `pos_order_backup_{config_id}`
- Key: `access_token`
- Indexes: pos_reference, date_order, backup_date, synced

**Server: PostgreSQL**
- Table: `pos_order_backup`
- Structured columns for fast queries
- JSON field for complete data
- Indexes on key fields

### API Methods

```python
# Save backup from POS
pos.order.backup.save_order_backup(order_data)

# Import single order
backup.action_import_order()

# Verify on server
backup.action_verify_on_server()

# Get statistics
pos.order.backup.get_backup_statistics(session_id)

# Cleanup old backups
pos.order.backup.cleanup_old_backups(days=30)
```

## Configuration

### Automatic Sync Interval
Default: 30 seconds (configurable in JS)

### Retention Period
Default: 30 days (configurable per cleanup)

### Permissions
- **POS User**: Read, Create backups
- **POS Manager**: Full access, Import, Cleanup

## Troubleshooting

### Backup Not Syncing
- Check network connection
- View browser console for errors
- Check Server logs for sync failures

### Import Fails
- Verify session still exists
- Check order doesn't already exist
- Review error message in backup form
- Check server logs

### Missing Orders
1. Go to Order Backups
2. Filter: "Missing on Server"
3. Verify they're actually missing
4. Use batch import to restore

## Benefits

✅ **Data Safety** - Never lose orders due to network issues
✅ **Easy Recovery** - Restore missing orders in clicks
✅ **Batch Operations** - Import multiple orders efficiently  
✅ **Smart Detection** - Automatic duplicate prevention
✅ **Clean Data** - Structured fields for better management
✅ **Analytics** - Track and monitor backup health
✅ **Maintenance** - Automatic cleanup of old data

## Migration from Old Version

If upgrading from pos.data.log:
1. Old backups remain in pos.data.log
2. New backups use pos.order.backup
3. Both models coexist
4. Manually import old backups if needed

## Support

For issues or questions:
- Check server logs: Odoo log file
- Check browser console: F12 → Console tab
- Review backup state and error messages
- Contact: support@weha-id.com
