# Manual Product Sync Implementation

## Overview
This implementation provides cashiers with the ability to manually synchronize products in the POS interface, with full control over the sync process including full sync, incremental sync, and local database management.

## Features

### Backend (Python)

#### POS Session Methods

1. **`start_manual_sync(config_id)`**
   - Initializes the manual sync process
   - Returns metadata: categories, taxes, UoMs
   - Provides sync configuration and statistics

2. **`manual_sync_products(config_id, last_sync_date, batch_size)`**
   - Determines sync type (full or incremental)
   - Returns sync statistics and batch information
   - Calculates number of batches needed

3. **`get_sync_batch(batch_number, batch_size, last_sync_date)`**
   - Fetches a specific batch of products
   - Supports both full and incremental sync
   - Returns batch progress information

4. **`check_sync_required(config_id, last_sync_date)`**
   - Checks if products were modified since last sync
   - Returns counts of modified and deleted products
   - Helps determine if sync is needed

5. **`complete_manual_sync(config_id, synced_count, sync_start_date)`**
   - Finalizes the sync process
   - Returns sync summary and statistics

6. **`_load_pos_data_models(config_id)`**
   - Overrides default model loading
   - Excludes `product.product` when local storage is enabled
   - Prevents automatic product loading on POS start

### Frontend (JavaScript)

#### Sync Button Component

**File**: `static/src/app/sync_button.js`

Features:
- Collapsible sync panel with status bar
- Real-time sync status display
- Product count and modification tracking
- Multiple sync options:
  - **Quick Sync**: Incremental sync (only changed products)
  - **Full Sync**: Complete reload of all products
  - **Clear DB**: Reset local database
  - **Check Status**: Verify sync requirements

**State Management**:
```javascript
{
  showDetails: false,      // Panel visibility
  syncRequired: null,      // Sync requirement info
  productCount: 0          // Local product count
}
```

#### POS Store Patch

**File**: `static/src/app/models.js`

Enhanced methods:
- `manualSync(forceFull)`: Batch-based sync with progress tracking
- `checkSyncRequired()`: Verify if sync is needed
- `saveMetadata()`: Store categories, taxes, UoMs locally

**Sync Flow**:
1. Initialize sync → Get metadata
2. Get sync info → Determine batches needed
3. Load batches → Process in chunks of 500
4. Complete sync → Update last sync date

#### Product Storage

**File**: `static/src/app/product_storage.js`

New methods:
- `saveMetadata(metadata)`: Store POS metadata
- `getMetadata(key)`: Retrieve stored metadata

### UI Design

**Status Bar**:
- Compact view showing sync status
- Color-coded icons (green = synced, yellow = updates available)
- Last sync timestamp
- Click to expand details

**Details Panel**:
- Statistics: local products, modified count, deleted count
- Action buttons: Quick Sync, Full Sync, Clear DB, Check Status
- Visual feedback during sync
- Gradient button styles with hover effects

**Styling**: `static/src/app/sync_button.scss`
- Modern card design with shadows
- Smooth animations and transitions
- Responsive grid layout for stats
- Color-coded status indicators

## Usage Flow

### For Cashiers

1. **Check Status**
   - Click the sync status bar to view details
   - See number of local products
   - View pending updates (if any)

2. **Quick Sync** (Recommended)
   - Click "Quick Sync" button
   - Only syncs changed products
   - Fast and efficient

3. **Full Sync**
   - Use when complete refresh needed
   - Reloads all products from server
   - Confirmation prompt to prevent accidental use

4. **Clear Database**
   - Emergency reset option
   - Clears all local product data
   - Requires POS reload after clearing

### Sync Process

```
1. User clicks sync button
   ↓
2. Initialize sync → Get metadata
   ↓
3. Determine sync type (full/incremental)
   ↓
4. Calculate batches (500 products per batch)
   ↓
5. Load each batch with 100ms delay
   ↓
6. Save to IndexedDB + Update POS models
   ↓
7. Complete sync → Update last sync date
   ↓
8. Show success notification
```

## Configuration

Enable manual sync in POS configuration:
- **Setting**: `enable_local_product_storage`
- **Location**: POS Config → Product Loading

When enabled:
- Products won't auto-load on POS start
- Sync button appears in POS interface
- Products loaded from IndexedDB
- Manual sync required for updates

## Technical Details

### Batch Processing
- **Batch size**: 500 products
- **Delay between batches**: 100ms
- **Prevents**: Server overload
- **Progress tracking**: Real-time updates

### Data Storage
- **Technology**: IndexedDB
- **Stores**: Products + Metadata
- **Indexes**: write_date, barcode, default_code
- **Persistence**: Survives browser restarts

### Error Handling
- Network errors → User notification
- Sync conflicts → Automatic retry
- Database errors → Graceful fallback
- All errors logged to console

## Benefits

1. **Control**: Cashiers decide when to sync
2. **Performance**: No blocking on POS start
3. **Offline-ready**: Products cached locally
4. **Transparency**: Clear sync status
5. **Efficiency**: Incremental sync saves bandwidth
6. **Reliability**: Batch processing prevents timeouts

## Future Enhancements

- [ ] Background sync scheduler
- [ ] Conflict resolution UI
- [ ] Sync queue for offline changes
- [ ] Product sync prioritization
- [ ] Detailed sync logs
- [ ] Sync progress bar
- [ ] Selective product sync (by category)
