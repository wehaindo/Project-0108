# POS Order Backup Module

## Features

- **Automatic Backup**: Validated orders are automatically backed up to IndexedDB
- **Server Sync**: Backups sync to server and saved in `pos.data.log` table
- **Restore Missing Orders**: Import orders from backup if missing on server
- **Data Safety**: Prevents data loss due to network issues

## How It Works

1. **Order Validation**: When cashier validates an order, it's saved to:
   - Server (normal flow)
   - IndexedDB (backup database)

2. **Background Sync**: Backup orders automatically sync to server every few seconds

3. **Missing Order Detection**: System can check for missing orders and restore from backup

4. **Manual Import**: From backend, can manually import backed up orders

## Usage

### For Cashiers
- Orders are automatically backed up (no action needed)
- Backup happens transparently in background

### For Managers
- View backups: Point of Sale → Order Backups
- Check missing orders
- Import missing orders manually if needed

## Technical Details

- **IndexedDB Database**: `pos_order_backup_{config_id}`
- **Server Table**: `pos.data.log`
- **Backup Data**: Full order JSON (order, lines, payments)
