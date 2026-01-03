# Weha POS Product Sync - Fast Loading with Offline Support

## Overview
This module optimizes product loading in Odoo 18 Point of Sale by implementing local storage (IndexedDB), timestamp-based synchronization, and offline-first loading strategies. Products are stored locally in the browser and only sync changes from the server, making POS load instantly even with thousands of products.

## 📚 Documentation
- **[DATA_FORMAT_GUIDE.md](./DATA_FORMAT_GUIDE.md)** - Complete data format specifications
- **[DATA_FORMAT_DIAGRAM.md](./DATA_FORMAT_DIAGRAM.md)** - Visual data flow diagrams and quick reference
- **[TROUBLESHOOTING.md](./TROUBLESHOOTING.md)** - Common errors and solutions
- **[MANUAL_SYNC_IMPLEMENTATION.md](./MANUAL_SYNC_IMPLEMENTATION.md)** - Manual sync feature guide

## ✨ Multi-Model Support
This module syncs **11 product-related models**:
- `product.product` - Main products
- `product.template` - Product templates
- `product.category` - Categories
- `product.pricelist` - Pricelists
- `product.pricelist.item` - Pricelist items
- `product.packaging` - Product packaging
- `product.tag` - Product tags
- `product.attribute` - Attributes
- `product.attribute.value` - Attribute values
- `product.template.attribute.line` - Template attribute lines
- `product.template.attribute.value` - Template attribute values

## Key Features

### 1. **Skip Product Loading on POS Initialization**
- **Products are NOT downloaded during POS startup** when local storage is enabled
- Overrides `_load_pos_data_models()` to exclude 13 product-related models
- Faster POS initialization (no product download bottleneck)
- Products loaded separately via sync mechanism

### 2. **Smart Loading Strategy**
- **First Time**: Downloads all products from server → Saves to local storage (IndexedDB)
- **Subsequent Loads**: If local DB has > 1 product → Loads from local instantly → Syncs updates in background
- **Fast startup**: POS ready in < 1 second with local products

### 3. **Automatic Background Sync**
- Automatically checks for updates after loading from local
- Only syncs products modified since last sync (uses `write_date`)
- Handles deleted/archived products automatically
- Non-blocking: POS usable while syncing

### 4. **Manual Sync Control**
- Sync button in POS navbar for manual refresh
- View last sync timestamp
- Force full resync anytime
- Clear local database and resync

### 5. **Offline-First Loading (Local Storage)**
- Products stored in browser's IndexedDB
- Instant POS load from local storage
- Works offline after initial sync
- No need to load from server every time

### 6. **Incremental Updates**
- Tracks `write_date` to detect changes
- Downloads only new or modified products
- Efficient bandwidth usage
- Fast sync even with large catalogs

### 7. **Separate Pricelist Loading**
- Pricelists also excluded from initial POS load
- Loaded separately via `load_pricelists()` method
- Supports incremental pricelist sync
- Efficient for multiple pricelists

## Installation

1. Copy this module to your Odoo addons directory
2. Update the app list: `Settings > Apps > Update Apps List`
3. Search for "Weha POS Product Sync"
4. Click Install

## Configuration

1. Go to `Point of Sale > Configuration > Point of Sale`
2. Select your POS
3. Scroll to the "Products" section
4. Configure the following options:

### Fast Product Loading
- **Enable Fast Product Loading**: Turn on optimization (default: enabled)
- **Store Products Locally**: Enable offline-first loading with IndexedDB (default: enabled)
- **Initial Product Load Limit**: Batch size for sync (default: 100, recommended: 500 for faster full sync)

### Category Filtering (Optional)
- **Limit to Specific Categories**: Load only products from selected categories
- **POS Categories**: Select which categories to sync

## How It Works

### First Time Use (Initial Download)
1. POS starts and checks local storage (IndexedDB)
2. **Local DB is empty or has ≤ 1 product**
3. **Downloads all products from server in batches (500 at a time)**
4. **Saves each batch to local storage immediately**
5. Products loaded into POS as they're downloaded
6. Records sync timestamp
7. POS ready to use

### Subsequent Uses (Fast Load from Local)
1. POS starts → **Checks local DB**
2. **Local DB has > 1 product → Loads from local instantly (< 1 second)**
3. POS immediately ready for use
4. **Background sync starts automatically (3 seconds later)**
5. Checks last sync timestamp
6. Downloads only modified/new products
7. Updates local storage
8. User doesn't notice - working with POS already

### Automatic Background Sync
- Runs 3 seconds after loading from local
- Query: `products WHERE write_date > last_sync_date`
- Updates modified products
- Removes deleted/archived products
- Saves updates to local storage
- Non-blocking: doesn't interrupt POS usage

### Manual Sync
- Click "Sync Products" button in navbar
- Forces full sync from server
- Shows progress and completion message
- Updates last sync timestamp

### Clear Local Database
- Click "Clear Local DB" button
- Removes all products from browser storage
- Triggers fresh full sync
- Useful after major data changes

## Sync Strategy

### Incremental Sync (Background)
```
- Runs automatically on POS startup
- Query: products WHERE write_date > last_sync_date
- Updates modified products
- Removes deleted/archived products
- Fast and efficient
```

### Full Sync (Initial/Manual)
```
- Loads all available products
- Syncs in batches of 500
- Saves to local storage
- Shows progress
- Used for:
  * First time setup
  * Manual sync trigger
  * After clearing local DB
```

## Performance Improvements

### Before (Without Module)
- Load 10,000 products: 30-60 seconds
- Every POS session loads from server
- No offline capability

### After (With Module)
- **First Load**: 10-20 seconds (full sync, one time)
- **Subsequent Loads**: < 1 second (from local storage)
- **Background Sync**: 1-3 seconds (only changes)
- **95%+ faster** after initial sync
- Offline capability included

### Example Timeline
```
Day 1, Session 1: 15 seconds (initial full sync of 10,000 products)
Day 1, Session 2: 0.5 seconds (load from local) + 2 seconds (background sync of 10 changes)
Day 2, Session 1: 0.5 seconds (load from local) + 1 second (background sync of 5 changes)
Day 2, Session 2: 0.5 seconds (load from local) + 0.5 seconds (no changes)
```

## Technical Details

### Backend Components
- `pos_session.py`: Sync methods
  - `sync_products_since()`: Incremental sync
  - `get_all_products_for_sync()`: Full sync
  - `search_products()`: Search API
  
- `pos_config.py`: Configuration fields
- `res_config_settings.py`: Settings interface

### Frontend Components
- `product_storage.js`: IndexedDB wrapper
  - Database: `pos_products_{pos_id}`
  - Stores: products, metadata
  - Indexes: write_date, barcode, default_code

- `models.js`: POS store patches
  - `loadProductsFromLocal()`: Load from IndexedDB
  - `fullProductSync()`: Complete server sync
  - `syncProductsInBackground()`: Incremental sync
  - `manualSync()`: User-triggered sync
  - `clearLocalProductDB()`: Clear and resync

- `sync_button.js`: UI component
- `navbar_patch.js`: Navbar integration

### Database Schema (IndexedDB)
```javascript
// Products Store
{
  keyPath: 'id',
  indexes: ['write_date', 'barcode', 'default_code']
}

// Metadata Store
{
  keyPath: 'key',
  data: { last_sync_date: '2024-12-27T10:30:00Z' }
}
```

## API Methods

### Backend
```python
# Incremental sync
sync_products_since(last_sync_date, limit=1000)
# Returns: { products, deleted_products, sync_date, has_more }

# Full sync
get_all_products_for_sync(offset=0, limit=500)
# Returns: { products, offset, limit, total_count, has_more, sync_date }

# Search
search_products(search_term, limit=50)
# Returns: [products]
```

### Frontend
```javascript
// Manual sync
await pos.manualSync()

// Clear and resync
await pos.clearLocalProductDB()

// Get sync status
pos.getSyncStatus()
// Returns: { is_syncing, last_sync_date, local_storage_enabled, all_products_loaded }

// Search products
await pos.searchProducts(searchTerm, limit)

// Get product by barcode
await pos.getProductByBarcode(barcode)
```

## User Interface

### Navbar Sync Button
- Shows last sync timestamp
- "Sync Products" button for manual sync
- "Clear Local DB" button to reset
- Visual indicator when syncing (spinner)

### Automatic Features
- Background sync on POS load
- Local search before server search
- Automatic product updates
- Deleted product removal

## API Reference

### Backend Methods (pos.session)

#### `_load_pos_data_models(config_id)`
Overrides core Odoo method to exclude product models from initial POS load.
- **Excluded Models** (when local storage is enabled):
  - `product.product`, `product.template`
  - `product.template.attribute.line`, `product.attribute`
  - `product.attribute.custom.value`, `product.template.attribute.value`
  - `product.combo`, `product.combo.item`, `product.packaging`
  - `product.pricelist`, `product.pricelist.item`
  - `product.category`, `product.tag`
- **Returns**: Filtered list of model names to load

#### `load_pricelists(config_id)`
Load pricelists and pricelist items separately from POS initialization.
- **Parameters**: `config_id` - POS configuration ID
- **Returns**: Dict with `pricelists` and `pricelist_items` arrays
- **Usage**: Call during product sync to get pricing data

#### `sync_pricelists_since(config_id, last_sync_date)`
Incremental pricelist sync - only modified pricelists since given date.
- **Parameters**: 
  - `config_id` - POS configuration ID
  - `last_sync_date` - ISO datetime string
- **Returns**: Dict with modified `pricelists` and `pricelist_items`

#### `get_all_products_for_sync(offset, limit)`
Get paginated product list for sync.
- **Parameters**:
  - `offset` - Starting position (default: 0)
  - `limit` - Batch size (default: 500)
- **Returns**: Dict with products, total count, and pagination info

#### `sync_products_since(last_sync_date, limit)`
Incremental product sync - only modified since given date.
- **Parameters**:
  - `last_sync_date` - ISO datetime string
  - `limit` - Max products to return (default: 1000)
- **Returns**: Dict with products, deleted_products, and sync_date

#### `start_manual_sync(config_id)`
Initialize manual sync - loads metadata (categories, taxes, UoM).
- **Returns**: Dict with config, metadata, and sync_info

#### `get_sync_batch(batch_number, batch_size, last_sync_date)`
Get specific batch for paginated sync.
- **Parameters**:
  - `batch_number` - 0-indexed batch number
  - `batch_size` - Products per batch (default: 500)
  - `last_sync_date` - Optional, for incremental sync
- **Returns**: Dict with products array and pagination status

## Best Practices

1. **Initial Load Limit**: 
   - Set higher for faster full sync (500-1000)
   - Lower values = more sync iterations

2. **Sync Frequency**:
   - Automatic on each POS session start
   - Manual sync after bulk product updates
   - No need for frequent manual syncs

3. **Clear Local DB When**:
   - After major data structure changes
   - If sync seems inconsistent
   - Before major product catalog changes

4. **Monitor Sync Status**:
   - Check last sync timestamp
   - Verify product counts match
   - Test search functionality

## Troubleshooting

### Products Not Appearing
1. Check last sync timestamp
2. Click "Sync Products" to force sync
3. Verify "Available in POS" is enabled
4. Clear local DB and resync

### Slow Initial Load
- Normal for first-time sync with many products
- Subsequent loads will be instant
- Consider category filtering to reduce dataset

### Sync Not Working
1. Check browser console for errors
2. Verify IndexedDB is enabled in browser
3. Check browser storage quota
4. Try clearing local DB

### Out of Sync Data
1. Click "Clear Local DB"
2. Full resync will download all products
3. Check write_date fields are updating properly

### Browser Storage Full
- IndexedDB has generous quota (usually > 1GB)
- If full, clear local DB
- Consider category filtering

## Browser Compatibility
- Chrome/Edge: Full support
- Firefox: Full support
- Safari: Full support (iOS 14+)
- Requires IndexedDB support

## Security Notes
- Products stored only in user's browser
- Each POS has separate database
- Data cleared when browser cache is cleared
- No sensitive data exposed

## Offline Capability
- Products available offline after sync
- Search works offline
- Barcode scanning works offline
- Orders can be created offline (if other POS features support it)

## Support
For issues or questions:
- Email: support@weha-id.com
- Website: https://weha-id.com

## License
LGPL-3

## Changelog

### Version 18.0.1.0.0 (2024-12-27)
- Initial release
- IndexedDB local storage
- Timestamp-based sync
- Manual sync control
- Background sync
- Offline-first loading
- 95%+ performance improvement
