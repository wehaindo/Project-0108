# Module Separation: Revenue Sharing to weha_operating_unit_contract

## Overview

The revenue sharing functionality has been separated from `weha_operating_unit_hierarchy` into a new module: `weha_operating_unit_contract`.

## What Changed

### Old Structure (Before)
```
weha_operating_unit_hierarchy/
├── models/
│   ├── operating_unit_type.py
│   ├── operating_unit.py
│   ├── revenue_sharing_rule.py ← Moved
│   ├── revenue_sharing_period.py ← Moved
│   ├── revenue_sharing_entry.py ← Moved
│   └── pos_order.py ← Moved
├── views/
│   ├── operating_unit_type_views.xml
│   ├── operating_unit_views.xml
│   ├── revenue_sharing_rule_views.xml ← Moved
│   ├── revenue_sharing_period_views.xml ← Moved
│   └── revenue_sharing_entry_views.xml ← Moved
└── security/
    ├── ir.model.access.csv (includes revenue sharing)
    └── revenue_sharing_security.xml ← Moved
```

### New Structure (After)
```
weha_operating_unit_hierarchy/
├── models/
│   ├── operating_unit_type.py
│   └── operating_unit.py
├── views/
│   ├── operating_unit_type_views.xml
│   └── operating_unit_views.xml
└── security/
    └── ir.model.access.csv (OU types only)

weha_operating_unit_contract/ (NEW MODULE)
├── models/
│   ├── revenue_sharing_rule.py
│   ├── revenue_sharing_period.py
│   ├── revenue_sharing_entry.py
│   └── pos_order.py
├── views/
│   ├── revenue_sharing_rule_views.xml
│   ├── revenue_sharing_period_views.xml
│   ├── revenue_sharing_entry_views.xml
│   └── menu_views.xml
└── security/
    ├── ir.model.access.csv
    └── revenue_sharing_security.xml
```

## Why Separate?

### Benefits:
1. **Modularity**: Core hierarchy management separate from revenue sharing
2. **Optional Feature**: Can use hierarchy without revenue sharing
3. **Easier Maintenance**: Each module has clear responsibility
4. **Better Dependencies**: Clear dependency chain
5. **Scalability**: Can add more contract types in the future

### Use Cases:
- **Use only hierarchy**: Install only `weha_operating_unit_hierarchy`
- **Use hierarchy + revenue sharing**: Install both modules

## Migration Steps

### For New Installations

1. **Install base module**:
   ```
   Apps → Search "Operating Unit Hierarchy"
   → Install weha_operating_unit_hierarchy
   ```

2. **Install revenue sharing** (if needed):
   ```
   Apps → Search "Operating Unit Revenue Sharing"
   → Install weha_operating_unit_contract
   ```

### For Existing Installations (Upgrade)

⚠️ **IMPORTANT**: Follow these steps carefully to avoid data loss!

#### Step 1: Backup Your Database
```bash
# Create database backup before upgrade
pg_dump your_database > backup_before_revenue_separation.sql
```

#### Step 2: Uninstall Old Module
```
1. Go to Apps
2. Search "weha_operating_unit_hierarchy"
3. Click "Uninstall"
   - This will mark the module for removal
   - Data will be preserved in database
```

#### Step 3: Update Module List
```
Apps → Update Apps List
```

#### Step 4: Install New Modules
```
1. Install weha_operating_unit_hierarchy (new version)
   - This installs only hierarchy management
   
2. Install weha_operating_unit_contract (new module)
   - This installs revenue sharing functionality
   - All revenue sharing data will be preserved
```

#### Step 5: Verify Data

Check that data is intact:

1. **Operating Unit Types**:
   ```
   Operating Units → Configuration → Operating Unit Types
   ```

2. **Operating Units**:
   ```
   Operating Units → Operating Units
   ```

3. **Revenue Sharing Rules**:
   ```
   Revenue Sharing → Configuration → Sharing Rules
   ```

4. **Revenue Sharing Periods**:
   ```
   Revenue Sharing → Operations → Sharing Periods
   ```

5. **Revenue Sharing Entries**:
   ```
   Revenue Sharing → Operations → Sharing Entries
   ```

## Dependencies

### weha_operating_unit_hierarchy
```python
depends = [
    'operating_unit',
    'stock_request',
    'weha_stock_request_operating_unit',
]
```

### weha_operating_unit_contract
```python
depends = [
    'operating_unit',
    'account_operating_unit',
    'point_of_sale',
    'weha_operating_unit_hierarchy',  # Must install base first
    'weha_pos_operating_unit',
]
```

## Module Comparison

| Feature | Base Module | Contract Module |
|---------|-------------|-----------------|
| OU Hierarchy | ✅ | ➖ |
| OU Types | ✅ | ➖ |
| Parent-Child Relations | ✅ | ➖ |
| Default Source OU | ✅ | ➖ |
| Revenue Sharing Rules | ➖ | ✅ |
| Revenue Sharing Periods | ➖ | ✅ |
| Revenue Sharing Entries | ➖ | ✅ |
| POS Integration | ➖ | ✅ |
| Accounting Integration | ➖ | ✅ |

## Menu Structure

### Base Module (weha_operating_unit_hierarchy)
```
Operating Units (from OCA module)
├── Configuration
│   └── Operating Unit Types
└── Operating Units
```

### Contract Module (weha_operating_unit_contract)
```
Revenue Sharing (NEW)
├── Configuration
│   └── Sharing Rules
└── Operations
    ├── Sharing Periods
    └── Sharing Entries
```

## Troubleshooting

### Issue: "Module not found" after upgrade

**Solution**:
1. Update apps list: `Apps → Update Apps List`
2. Search for the module again
3. If still not found, restart Odoo server

### Issue: Revenue sharing data disappeared

**Solution**:
1. Check if `weha_operating_unit_contract` is installed
2. If not, install it: `Apps → Search "Operating Unit Revenue Sharing"`
3. Data is preserved in database, just need to install the module

### Issue: Dependency errors

**Solution**:
Install modules in this order:
1. `weha_operating_unit_hierarchy` (base)
2. `weha_operating_unit_contract` (depends on base)

### Issue: Menu items missing

**Solution**:
1. Clear browser cache: `Ctrl+Shift+Del`
2. Refresh page: `F5`
3. If still missing, check module is installed and active

## Testing Checklist

After migration, test these features:

### Base Module ✓
- [ ] Create Operating Unit Type
- [ ] Create Operating Unit
- [ ] Set parent-child relationships
- [ ] Set default source OU
- [ ] View hierarchy tree

### Contract Module ✓
- [ ] Create Revenue Sharing Rule
- [ ] Configure percentages per OU type
- [ ] Create/view Revenue Sharing Period
- [ ] Calculate revenue sharing
- [ ] Validate entries
- [ ] Post accounting entries
- [ ] View revenue sharing entries

### Integration ✓
- [ ] POS orders link to periods
- [ ] Revenue sharing calculated from POS
- [ ] Hierarchy used in revenue distribution
- [ ] Reports show correct data

## Support

For issues during migration:
1. Check this guide first
2. Review Odoo logs: `/var/log/odoo/odoo-server.log`
3. Contact support: support@weha-id.com

## Version Compatibility

- **Odoo Version**: 18.0
- **Base Module**: weha_operating_unit_hierarchy v18.0.1.0.0
- **Contract Module**: weha_operating_unit_contract v18.0.1.0.0

Both modules must be same version for compatibility.
