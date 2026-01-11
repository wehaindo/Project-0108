# Installation & Testing Checklist

## Pre-Installation

- [ ] Backup database
- [ ] Note current module version
- [ ] Document any customizations
- [ ] Verify Odoo 18.0 compatibility

## Installation Steps

### 1. Update Module
```bash
# Option 1: Command line
odoo-bin -u weha_pos_order_backup -d your_database

# Option 2: From UI
Apps → Update Apps List → Find "POS Order Backup" → Upgrade
```

### 2. Verify Installation
- [ ] No upgrade errors in log
- [ ] All menus appear
- [ ] Security rules loaded
- [ ] Cron jobs created

## Post-Installation Testing

### Basic Functionality

#### Test 1: Order Backup Creation
- [ ] Open POS interface
- [ ] Create and validate an order
- [ ] Check browser console for backup messages
- [ ] Verify order appears in Order Backups menu
- [ ] Check state is 'synced'

#### Test 2: Data Structure
- [ ] Open a backup record
- [ ] Verify all fields populated:
  - [ ] pos_reference
  - [ ] access_token
  - [ ] backup_date
  - [ ] order_date
  - [ ] session_id
  - [ ] user_id
  - [ ] partner_id (if applicable)
  - [ ] amount_total
  - [ ] lines_count
  - [ ] payments_count
- [ ] Check JSON data is complete

#### Test 3: Verification
- [ ] Click "Verify on Server" button
- [ ] State changes to 'verified'
- [ ] imported_order_id field populated
- [ ] is_missing = False

### Advanced Functionality

#### Test 4: Missing Order Import
- [ ] Create backup for non-existent order (test scenario)
- [ ] Filter by "Missing on Server"
- [ ] Click "Import Order"
- [ ] Verify order created in pos.order
- [ ] Check state changed to 'imported'
- [ ] Verify import_date and import_user_id set

#### Test 5: Batch Import Wizard
- [ ] Select multiple backup records
- [ ] Click Action → Batch Import Orders
- [ ] Select "Selected Records" filter
- [ ] Check "Only Missing on Server"
- [ ] Click Preview
- [ ] Verify correct backups shown
- [ ] Click Import Orders
- [ ] Check results summary
- [ ] Verify successful imports

#### Test 6: Duplicate Detection
- [ ] Try to import already-imported order
- [ ] Verify error message about duplicate
- [ ] Check state marked as 'duplicate'
- [ ] Verify linked to existing order

#### Test 7: Dashboard
- [ ] Open Backup Dashboard
- [ ] Verify graph displays correctly
- [ ] Check pivot table works
- [ ] Verify filters apply
- [ ] Check data accuracy

### Filters & Search

#### Test 8: Quick Filters
- [ ] "Missing on Server" filter
- [ ] "Can Import" filter
- [ ] "Ready to Import" filter
- [ ] "Today" filter
- [ ] "Last 7 Days" filter
- [ ] "Last 30 Days" filter

#### Test 9: State Filters
- [ ] Filter by each state
- [ ] Verify counts accurate
- [ ] Check color coding

#### Test 10: Group By
- [ ] Group by Status
- [ ] Group by Session
- [ ] Group by POS Config
- [ ] Group by Backup Date
- [ ] Group by Order Date

### Cleanup & Maintenance

#### Test 11: Manual Cleanup
- [ ] Open Cleanup Wizard
- [ ] Set retention to 60 days
- [ ] Select states to clean
- [ ] Click Preview
- [ ] Verify correct records shown
- [ ] Execute cleanup
- [ ] Verify records deleted

#### Test 12: Cron Jobs
- [ ] Go to Scheduled Actions
- [ ] Find "POS: Cleanup Old Order Backups"
  - [ ] Verify active
  - [ ] Check interval (1 day)
- [ ] Find "POS: Verify Order Backups on Server"
  - [ ] Verify active
  - [ ] Check interval (6 hours)
- [ ] Manually run each cron
- [ ] Verify no errors

### Session Integration

#### Test 13: Session Stats
- [ ] Open a POS Session
- [ ] Click "View Backup Statistics"
- [ ] Verify backup count displayed
- [ ] Check missing order count
- [ ] Verify action opens filtered view

### UI/UX Testing

#### Test 14: Tree View
- [ ] Multi-select works
- [ ] Inline buttons work
- [ ] Decorations show correctly
- [ ] Columns sortable
- [ ] Optional columns toggle

#### Test 15: Form View
- [ ] All fields display correctly
- [ ] Buttons work as expected
- [ ] Ribbon badges show when appropriate
- [ ] Status bar transitions work
- [ ] Notebook tabs accessible

#### Test 16: Bulk Actions
- [ ] Select multiple records
- [ ] Action → Verify on Server
- [ ] Action → Mark as Duplicate
- [ ] Action → Batch Import
- [ ] All work correctly

### Performance Testing

#### Test 17: Large Dataset
- [ ] Create 100+ backup records
- [ ] Test search performance
- [ ] Test filter performance
- [ ] Test import performance
- [ ] Check dashboard loads quickly

#### Test 18: Sync Performance
- [ ] Create multiple orders quickly
- [ ] Verify sync completes within 30 sec
- [ ] Check no sync errors
- [ ] Verify all backups synced

### Security Testing

#### Test 19: POS User Permissions
- [ ] Login as POS User
- [ ] Can view backups
- [ ] Can create backups
- [ ] Cannot delete backups
- [ ] Cannot access cleanup wizard
- [ ] Cannot access import wizard

#### Test 20: POS Manager Permissions
- [ ] Login as POS Manager
- [ ] Full read access
- [ ] Can import backups
- [ ] Can delete backups
- [ ] Can access all wizards
- [ ] Can run cleanup

### Error Handling

#### Test 21: Network Issues
- [ ] Disable network
- [ ] Create order
- [ ] Verify local backup created
- [ ] Enable network
- [ ] Verify sync occurs
- [ ] Check order imported

#### Test 22: Import Errors
- [ ] Try importing with invalid session
- [ ] Verify error message clear
- [ ] Check state set to 'error'
- [ ] Check error_message field populated

### Documentation

#### Test 23: Documentation Access
- [ ] README.md readable
- [ ] MIGRATION.md clear
- [ ] USAGE_EXAMPLES.md helpful
- [ ] QUICK_REFERENCE.md concise
- [ ] IMPLEMENTATION_SUMMARY.md complete

### Browser Compatibility

#### Test 24: Different Browsers
- [ ] Chrome/Edge
- [ ] Firefox
- [ ] Safari (if applicable)
- [ ] Mobile browsers

### Integration Testing

#### Test 25: With Other Modules
- [ ] Test with accounting module
- [ ] Test with inventory
- [ ] Test with custom POS modules
- [ ] Verify no conflicts

## Regression Testing

### Test 26: Old Functionality Still Works
- [ ] pos.data.log still accessible (if exists)
- [ ] Old backups viewable
- [ ] Can import from old model
- [ ] No JavaScript errors
- [ ] POS works normally

## Load Testing

### Test 27: Stress Test
- [ ] Process 50 orders in quick succession
- [ ] All backup correctly
- [ ] All sync successfully
- [ ] Dashboard updates correctly
- [ ] No performance degradation

## Final Verification

### Test 28: End-to-End Scenario
1. [ ] Open POS
2. [ ] Create 5 orders
3. [ ] Close POS
4. [ ] Verify all 5 backed up
5. [ ] Verify all 5 synced
6. [ ] Check dashboard shows accurate stats
7. [ ] Filter for missing orders
8. [ ] Import any missing
9. [ ] Run cleanup for old records
10. [ ] Verify session stats accurate

## Sign-Off

### Completed By
- Name: _________________
- Date: _________________
- Signature: _________________

### Issues Found
| # | Issue | Severity | Status | Notes |
|---|-------|----------|--------|-------|
| 1 |       |          |        |       |
| 2 |       |          |        |       |
| 3 |       |          |        |       |

### Overall Status
- [ ] ✅ PASSED - Ready for production
- [ ] ⚠️ PASSED WITH MINOR ISSUES - Document issues
- [ ] ❌ FAILED - Address critical issues before deployment

### Recommendations
_____________________________________
_____________________________________
_____________________________________

### Next Steps
1. _____________________________________
2. _____________________________________
3. _____________________________________

---

## Quick Issue Resolution

### Common Issues & Fixes

**Issue**: Module won't upgrade
- Check Odoo version compatibility
- Review server logs for specific errors
- Verify all dependencies installed

**Issue**: Backups not appearing
- Check browser console for errors
- Verify IndexedDB not disabled
- Check network connectivity
- Verify POS session active

**Issue**: Import fails
- Verify session exists and not closed
- Check order doesn't already exist
- Review error message in backup record
- Check server logs for details

**Issue**: Dashboard not loading
- Clear browser cache
- Check for JavaScript errors
- Verify data exists
- Try different browser

**Issue**: Cron jobs not running
- Verify cron jobs active in Scheduled Actions
- Check last run date
- Manually trigger to test
- Review server logs

**Issue**: Permission errors
- Verify user has correct group
- Check ir.model.access.csv loaded
- Refresh security rules
- Re-login to refresh permissions

## Support Contacts

- Technical Support: support@weha-id.com
- Documentation: GitHub/GitLab repository
- Community: Odoo forums

---

**Note**: This checklist should be completed before deploying to production. Keep this document with your module documentation for future reference.
