# Usage Examples

## Common Scenarios

### Scenario 1: Network Outage During Sales

**Problem**: Internet goes down, cashier validates orders

**What Happens**:
1. Orders saved to IndexedDB automatically
2. Normal POS flow may fail (network error)
3. When network restored, backups sync to server
4. Manager can import missing orders from backups

**Steps to Recover**:
1. Go to **POS → Order Backups**
2. Filter: **"Missing on Server"**
3. Select all missing orders
4. Click **Action → Batch Import Orders**
5. Confirm import

### Scenario 2: Daily Verification

**Task**: Check all orders were backed up properly

**Steps**:
1. Open **POS → Order Backups → Backup Dashboard**
2. View today's statistics
3. Check for any "Missing on Server"
4. Review error states
5. Import any missing orders

### Scenario 3: End of Day Cleanup

**Task**: Clean up old verified backups

**Steps**:
1. Go to **POS → Order Backups → Cleanup Old Backups**
2. Set retention: 30 days
3. Check: Verified ✓, Imported ✓, Duplicates ✓
4. Click **Preview** to see what will be deleted
5. Click **Delete Old Backups**

### Scenario 4: Session Reconciliation

**Task**: Verify all session orders are backed up

**Steps**:
1. Open POS Session
2. Click **View Backup Statistics**
3. Review backup count vs order count
4. Check for missing orders
5. Import if needed

### Scenario 5: Batch Import by Date

**Task**: Import all missing orders from last week

**Steps**:
1. Go to **POS → Order Backups**
2. Click **Action → Batch Import Orders**
3. Select filter: **By Date Range**
4. Set dates: Last 7 days
5. Check: **Only Missing on Server**
6. Click **Preview** to review
7. Click **Import Orders**

## Code Examples

### Python: Programmatic Import

```python
# Get missing orders for a session
session = env['pos.session'].browse(123)
backups = env['pos.order.backup'].search([
    ('session_id', '=', session.id),
    ('state', 'in', ['backup', 'synced']),
    ('is_missing', '=', True)
])

# Import them
for backup in backups:
    try:
        backup.action_import_order()
    except Exception as e:
        print(f"Failed to import {backup.pos_reference}: {e}")
```

### Python: Get Statistics

```python
# Get backup stats for session
stats = env['pos.order.backup'].get_backup_statistics(session_id=123)

print(f"Total backups: {stats['total']}")
print(f"Verified: {stats['verified']}")
print(f"Missing: {stats['missing']}")
print(f"Errors: {stats['error']}")
```

### Python: Manual Cleanup

```python
# Cleanup backups older than 60 days
count = env['pos.order.backup'].cleanup_old_backups(days=60)
print(f"Cleaned up {count} old backups")
```

### Python: Verify Backups

```python
# Verify recent backups on server
backups = env['pos.order.backup'].search([
    ('state', 'in', ['backup', 'synced']),
    ('backup_date', '>=', '2026-01-01')
])

backups.action_verify_on_server()
```

### JavaScript: Get Local Backup Count

```javascript
// In POS interface
const stats = await this.pos.getBackupStats();
console.log(`Total: ${stats.total}, Unsynced: ${stats.unsynced}`);
```

### JavaScript: Manual Sync

```javascript
// Manually trigger sync
await this.pos.syncOrderBackups();
```

## Scheduled Tasks

### Automatic Cleanup (Daily)

Runs every day at midnight:
- Deletes backups older than 30 days
- Only deletes verified/imported/duplicate states
- Keeps errors and unverified orders

**Configure**: Settings → Technical → Scheduled Actions → "POS: Cleanup Old Order Backups"

### Automatic Verification (Every 6 Hours)

Runs 4 times per day:
- Checks recent backups against server
- Updates state to 'verified' if found
- Only checks last 7 days

**Configure**: Settings → Technical → Scheduled Actions → "POS: Verify Order Backups on Server"

## Advanced Filters

### Find Orders Ready to Import

```
Domain: [('can_import', '=', True)]
```

### Find Yesterday's Backups

```
Domain: [
    ('backup_date', '>=', '2026-01-06 00:00:00'),
    ('backup_date', '<', '2026-01-07 00:00:00')
]
```

### Find Backups with Errors

```
Domain: [('state', '=', 'error')]
```

### Find High-Value Orders

```
Domain: [('amount_total', '>', 1000)]
```

### Find Backups by Customer

```
Domain: [('partner_id', '=', 123)]
```

## Reports

### Backup Success Rate

```python
# Calculate success rate
all_backups = env['pos.order.backup'].search([])
verified = all_backups.filtered(lambda b: b.state == 'verified')
rate = (len(verified) / len(all_backups)) * 100 if all_backups else 0
print(f"Success rate: {rate:.2f}%")
```

### Orders by State

```python
# Group by state
from collections import Counter
backups = env['pos.order.backup'].search([])
states = Counter(backups.mapped('state'))

for state, count in states.items():
    print(f"{state}: {count}")
```

### Session Summary

```python
# Get session backup summary
session = env['pos.session'].browse(123)
backups = env['pos.order.backup'].search([('session_id', '=', session.id)])

print(f"Session: {session.name}")
print(f"Total backups: {len(backups)}")
print(f"Total amount: {sum(backups.mapped('amount_total'))}")
print(f"Missing: {len(backups.filtered(lambda b: b.is_missing))}")
```

## Tips & Best Practices

### 1. Regular Verification
Check backup dashboard daily to catch issues early.

### 2. Quick Import
Use "Ready to Import" filter for one-click access to missing orders.

### 3. Batch Operations
Always use batch import for multiple orders - it's faster and provides better error handling.

### 4. Retention Policy
Set retention based on your needs:
- High volume stores: 7-14 days
- Low volume stores: 30-60 days
- Compliance requirements: Adjust accordingly

### 5. Monitor Errors
Check error state regularly and investigate root causes.

### 6. Session Reconciliation
Before closing session, verify backup count matches order count.

### 7. Network Issues
If frequent network issues, increase sync interval and monitor closely.

### 8. Database Size
Run cleanup regularly to keep database size manageable.

## Troubleshooting Examples

### Problem: Sync Failing

**Check**: Browser console for errors
```javascript
// Open browser console (F12)
// Look for "[Order Backup]" messages
// Check for network errors
```

**Solution**: Clear IndexedDB and refresh
```javascript
// In browser console
indexedDB.deleteDatabase('pos_order_backup_1');
location.reload();
```

### Problem: Import Fails with "Session not found"

**Cause**: Session was deleted or archived

**Solution**: Cannot import - session required for POS orders

### Problem: Duplicate Detection Not Working

**Check**: Access token matching
```python
backup = env['pos.order.backup'].browse(123)
order = env['pos.order'].search([
    ('access_token', '=', backup.access_token)
])
print(f"Found: {order}")
```

## Integration Examples

### Email Alert for Missing Orders

```python
# Send email if missing orders detected
session = env['pos.session'].browse(123)
backups = env['pos.order.backup'].search([
    ('session_id', '=', session.id),
    ('is_missing', '=', True)
])

if backups:
    template = env.ref('weha_pos_order_backup.email_missing_orders')
    template.send_mail(session.id, force_send=True)
```

### Custom Dashboard Widget

```xml
<record id="view_pos_dashboard_inherit" model="ir.ui.view">
    <field name="name">pos.dashboard.backup.widget</field>
    <field name="model">pos.config</field>
    <field name="inherit_id" ref="point_of_sale.view_pos_dashboard"/>
    <field name="arch" type="xml">
        <xpath expr="//div[@class='o_pos_dashboard']" position="inside">
            <div class="col-lg-3">
                <div class="card">
                    <div class="card-body">
                        <h5>Backup Status</h5>
                        <field name="backup_count"/>
                    </div>
                </div>
            </div>
        </xpath>
    </field>
</record>
```

These examples cover most common use cases. Customize as needed for your specific requirements!
