# Quick Start: Module Separation Implementation

## What Was Done

✅ **Created new module**: `weha_operating_unit_contract`
✅ **Updated base module**: `weha_operating_unit_hierarchy`
✅ **Copied all revenue sharing files** to new module
✅ **Updated manifests and dependencies**
✅ **Created documentation** (README, Migration Guide, Summary)

## Implementation Steps

### Step 1: Update Odoo Apps List
```
1. Open Odoo
2. Go to Apps
3. Click "Update Apps List" (top-right menu)
4. Wait for completion
```

### Step 2: Install New Module
```
1. Go to Apps
2. Remove any filters (click X on search)
3. Search: "Operating Unit Revenue Sharing"
4. Click "Install" on weha_operating_unit_contract
5. Wait for installation
```

### Step 3: Verify Installation
```
1. Check new menu appears: "Revenue Sharing"
2. Navigate to: Revenue Sharing → Configuration → Sharing Rules
3. Verify existing rules still exist
4. Check: Revenue Sharing → Operations → Sharing Periods
5. Verify existing periods and entries are intact
```

### Step 4: Test Functionality

**Test Revenue Sharing:**
- [ ] Create a new revenue sharing rule
- [ ] View existing periods
- [ ] Create new period
- [ ] Calculate revenue sharing
- [ ] Validate entries

**Test Base Module:**
- [ ] Create operating unit type
- [ ] Create operating unit
- [ ] Set parent-child relationships
- [ ] Set default source OU

### Step 5: Cleanup Old Files (Optional)

⚠️ **Only after confirming everything works!**

**Option A: Use PowerShell Script**
```powershell
cd "d:\OdooProject\Project-0108\weha_operating_unit_contract"
.\cleanup_old_files.ps1
```

**Option B: Manual Cleanup**
```powershell
# Navigate to base module
cd "d:\OdooProject\Project-0108\weha_operating_unit_hierarchy"

# Remove model files
Remove-Item "models\revenue_sharing_rule.py"
Remove-Item "models\revenue_sharing_period.py"
Remove-Item "models\revenue_sharing_entry.py"
Remove-Item "models\pos_order.py"

# Remove view files
Remove-Item "views\revenue_sharing_rule_views.xml"
Remove-Item "views\revenue_sharing_period_views.xml"
Remove-Item "views\revenue_sharing_entry_views.xml"

# Remove security file
Remove-Item "security\revenue_sharing_security.xml"
```

### Step 6: Final Verification

After cleanup:
```
1. Restart Odoo server
2. Go to Apps → Update Apps List
3. Upgrade weha_operating_unit_hierarchy
4. Verify no errors
5. Test both modules again
```

## Module Structure

### Before (Single Module)
```
weha_operating_unit_hierarchy
├── Hierarchy Management
└── Revenue Sharing ← Mixed together
```

### After (Separated Modules)
```
weha_operating_unit_hierarchy
└── Hierarchy Management ONLY

weha_operating_unit_contract (NEW)
└── Revenue Sharing ONLY
```

## Dependencies

```
weha_operating_unit_hierarchy
├── operating_unit (OCA)
├── stock_request (OCA)
└── weha_stock_request_operating_unit

weha_operating_unit_contract (NEW)
├── weha_operating_unit_hierarchy ← Base module
├── operating_unit (OCA)
├── account_operating_unit (OCA)
├── point_of_sale
└── weha_pos_operating_unit
```

## Menu Changes

### New Menu Structure
```
Revenue Sharing (NEW TOP MENU)
├── Configuration
│   └── Sharing Rules
└── Operations
    ├── Sharing Periods
    └── Sharing Entries
```

### Old Menus (Unchanged)
```
Operating Units (from OCA)
├── Configuration
│   └── Operating Unit Types
└── Operating Units
```

## Files Created

### New Module Files
```
weha_operating_unit_contract/
├── __init__.py
├── __manifest__.py
├── README.md
├── MIGRATION_GUIDE.md
├── MODULE_SEPARATION_SUMMARY.md
├── QUICK_START.md (this file)
├── cleanup_old_files.ps1
│
├── models/
│   ├── __init__.py
│   ├── revenue_sharing_rule.py
│   ├── revenue_sharing_period.py
│   ├── revenue_sharing_entry.py
│   └── pos_order.py
│
├── views/
│   ├── revenue_sharing_rule_views.xml
│   ├── revenue_sharing_period_views.xml
│   ├── revenue_sharing_entry_views.xml
│   └── menu_views.xml
│
└── security/
    ├── ir.model.access.csv
    └── revenue_sharing_security.xml
```

### Modified Base Module Files
```
weha_operating_unit_hierarchy/
├── __manifest__.py ← Updated
├── models/
│   └── __init__.py ← Updated
└── security/
    └── ir.model.access.csv ← Updated
```

## Troubleshooting

### Issue: Module not found in Apps
**Solution**: 
```
1. Apps → Update Apps List
2. Refresh browser (F5)
3. Search again
```

### Issue: Installation fails with dependency error
**Solution**:
```
1. Install base module first: weha_operating_unit_hierarchy
2. Then install contract module: weha_operating_unit_contract
```

### Issue: Revenue sharing menus disappeared
**Solution**:
```
1. Install weha_operating_unit_contract
2. Clear browser cache (Ctrl+Shift+Del)
3. Refresh page (F5)
```

### Issue: Data missing after installation
**Solution**:
```
Data is preserved in database!
Just install weha_operating_unit_contract module
```

## Rollback Procedure

If you need to revert:

1. **Uninstall new module**:
   ```
   Apps → weha_operating_unit_contract → Uninstall
   ```

2. **Restore old files** (from git or backup):
   ```powershell
   cd "d:\OdooProject\Project-0108"
   git checkout weha_operating_unit_hierarchy/
   ```

3. **Upgrade base module**:
   ```
   Apps → weha_operating_unit_hierarchy → Upgrade
   ```

## Testing Checklist

### Critical Tests ✓
- [ ] Base module installs without errors
- [ ] Contract module installs without errors
- [ ] Existing revenue sharing data intact
- [ ] Can create new revenue sharing rules
- [ ] Can create new sharing periods
- [ ] Revenue calculation works
- [ ] POS orders link to periods correctly
- [ ] Hierarchy functionality unchanged

### Advanced Tests ✓
- [ ] Accounting entries generated correctly
- [ ] Reports show correct data
- [ ] Multi-company setup works
- [ ] Security rules enforced properly

## Success Criteria

✅ Both modules installed successfully
✅ No installation errors
✅ Revenue sharing functionality works
✅ Hierarchy functionality unchanged
✅ All data preserved
✅ Menus appear correctly
✅ Tests pass

## Documentation

- **README.md**: User guide for contract module
- **MIGRATION_GUIDE.md**: Detailed migration instructions
- **MODULE_SEPARATION_SUMMARY.md**: Complete technical summary
- **QUICK_START.md**: This file - Quick implementation guide

## Support

For help:
1. Check documentation files
2. Review Odoo logs: Settings → Technical → Logging
3. Contact: support@weha-id.com

## Timeline

- **Separation**: January 11, 2026
- **Odoo Version**: 18.0
- **Module Versions**: 18.0.1.0.0

## Status

✅ **READY FOR IMPLEMENTATION**

All files created, modules separated, documentation complete.
Ready to install and test in Odoo.
