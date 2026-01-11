# Migration Guide

## Upgrading from Version 1.x to 2.x

### What's New in Version 2.0

Version 2.0 introduces a new structured backup model (`pos.order.backup`) replacing the generic `pos.data.log` approach.

### Key Changes

1. **New Model**: `pos.order.backup` with structured fields
2. **Better Performance**: Indexed fields for faster queries
3. **Enhanced Features**: Batch import, analytics, automatic cleanup
4. **Improved UI**: Filters, bulk actions, dashboard

### Migration Steps

#### Step 1: Install/Upgrade Module
```bash
# Update module list
odoo-bin -u weha_pos_order_backup -d your_database

# Or from UI
Apps → Update Apps List → Upgrade weha_pos_order_backup
```

#### Step 2: Check Existing Data

After upgrade, you'll have both:
- **pos.data.log** (old backups)
- **pos.order.backup** (new backups)

New orders will automatically use the new model.

#### Step 3: Migrate Old Backups (Optional)

If you want to migrate old backups to the new model:

```python
# Run from Odoo shell or create a migration script
old_backups = env['pos.data.log'].search([])

for old_backup in old_backups:
    try:
        order_data = json.loads(old_backup.pos_data)
        
        # Check if already migrated
        existing = env['pos.order.backup'].search([
            ('access_token', '=', order_data.get('access_token'))
        ], limit=1)
        
        if not existing:
            # Create new backup record
            env['pos.order.backup'].save_order_backup(order_data)
            print(f"Migrated: {order_data.get('pos_reference')}")
    except Exception as e:
        print(f"Error migrating {old_backup.id}: {e}")
```

#### Step 4: Verify Migration

1. Go to **Point of Sale → Order Backups**
2. Check that backups are showing correctly
3. Verify states are accurate
4. Test import functionality

#### Step 5: Cleanup (After Testing)

Once you're satisfied the new system works:

```python
# Optional: Delete old pos.data.log records
env['pos.data.log'].search([]).unlink()
```

### Backwards Compatibility

- Both models coexist peacefully
- No data loss during upgrade
- Can keep old backups indefinitely
- New orders automatically use new model

### Configuration Changes

#### Before (v1.x)
```xml
'data': [
    'security/ir.model.access.csv',
    'views/pos_data_log_views.xml',
]
```

#### After (v2.x)
```xml
'data': [
    'security/ir.model.access.csv',
    'views/pos_order_backup_views.xml',
    'views/pos_order_backup_dashboard.xml',
    'views/pos_data_log_views.xml',  # Still included
    'wizard/pos_order_backup_import_wizard_views.xml',
    'wizard/pos_order_backup_cleanup_wizard_views.xml',
    'data/ir_cron_data.xml',
]
```

### API Changes

#### Before (v1.x)
```python
# Save backup
env['pos.data.log'].save_order_backup(order_data)

# Get missing orders
env['pos.data.log'].get_missing_orders(session_id, order_uids)

# Import order
backup.action_import_order()
```

#### After (v2.x)
```python
# Save backup (compatible)
env['pos.order.backup'].save_order_backup(order_data)

# Get statistics
env['pos.order.backup'].get_backup_statistics(session_id)

# Import order (enhanced)
backup.action_import_order()

# Batch import
wizard = env['pos.order.backup.import.wizard'].create({...})
wizard.action_import_backups()

# Cleanup
env['pos.order.backup'].cleanup_old_backups(days=30)
```

### JavaScript Changes

No changes needed! The JavaScript layer is compatible with both versions.

### Database Schema

#### New Table: pos_order_backup
```sql
CREATE TABLE pos_order_backup (
    id SERIAL PRIMARY KEY,
    pos_reference VARCHAR,
    access_token VARCHAR UNIQUE,
    backup_date TIMESTAMP,
    order_date TIMESTAMP,
    session_id INTEGER REFERENCES pos_session,
    config_id INTEGER REFERENCES pos_config,
    user_id INTEGER REFERENCES res_users,
    partner_id INTEGER REFERENCES res_partner,
    amount_total NUMERIC,
    amount_tax NUMERIC,
    amount_paid NUMERIC,
    amount_return NUMERIC,
    state VARCHAR,
    order_data TEXT,
    imported_order_id INTEGER REFERENCES pos_order,
    import_date TIMESTAMP,
    import_user_id INTEGER REFERENCES res_users,
    error_message TEXT,
    lines_count INTEGER,
    payments_count INTEGER,
    -- ... other fields
);
```

### Testing Checklist

After migration, test these scenarios:

- [ ] Create new order in POS
- [ ] Verify it backs up to IndexedDB
- [ ] Check it syncs to server (pos.order.backup)
- [ ] View backup in Order Backups menu
- [ ] Test single order import
- [ ] Test batch import wizard
- [ ] Check dashboard displays correctly
- [ ] Test filters and search
- [ ] Run cleanup wizard
- [ ] Verify cron jobs are active

### Troubleshooting

#### Issue: Old backups not visible
**Solution**: They're in pos.data.log, not pos.order.backup. Migrate them or keep both.

#### Issue: Import fails
**Solution**: Check session exists, order not duplicate, review error message.

#### Issue: Sync not working
**Solution**: Clear browser cache, check console for errors, verify session active.

### Rollback

If you need to rollback:

1. Uninstall module
2. Reinstall version 1.x
3. Old pos.data.log data will still be there

### Support

For migration issues:
- Check Odoo logs
- Review browser console
- Contact support@weha-id.com

## Version Compatibility

| Module Version | Odoo Version | Migration Required |
|----------------|--------------|-------------------|
| 1.0.0 | 18.0 | No |
| 2.0.0 | 18.0 | Automatic |

Migration is seamless - new features available immediately!
