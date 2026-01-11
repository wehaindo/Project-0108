# POS Order Backup - Quick Reference

## 🚀 Quick Start

### For Cashiers
✅ Nothing to do! Orders backup automatically.

### For Managers - Daily Tasks

1. **Check Backup Status**
   ```
   POS → Order Backups → Backup Dashboard
   ```

2. **Import Missing Orders**
   ```
   POS → Order Backups → Filter: "Missing on Server" → Select All → Action → Batch Import
   ```

3. **Weekly Cleanup**
   ```
   POS → Order Backups → Cleanup Old Backups → Set 30 days → Delete
   ```

## 📊 States Quick Reference

| Icon | State | Meaning | Action |
|------|-------|---------|--------|
| 🔵 | Backup | Local only | Wait for sync |
| 🟡 | Synced | On server backup table | Verify |
| 🟢 | Verified | Found on POS orders | ✓ OK |
| ✅ | Imported | Restored from backup | ✓ Done |
| ⚫ | Duplicate | Already exists | Skip |
| 🔴 | Error | Import failed | Check error |

## 🔍 Essential Filters

| Filter | Use Case |
|--------|----------|
| Missing on Server | Find orders to restore |
| Ready to Import | Safe to import now |
| Last 7 Days | Recent activity |
| Errors | Troubleshoot issues |
| By Session | Session reconciliation |

## ⚡ Quick Actions

### Import Single Order
```
Open backup → Import Order button
```

### Batch Import
```
Select multiple → Action menu → Batch Import Orders
```

### Verify Orders
```
Select backups → Action → Verify on Server
```

### Mark Duplicate
```
Select backups → Action → Mark as Duplicate
```

## 📈 Dashboard Metrics

- **Total Backups**: All backup records
- **Verified**: Orders confirmed on server  
- **Missing**: Orders not found on server
- **Success Rate**: Verified / Total

## 🛠️ Troubleshooting Fast

| Problem | Quick Fix |
|---------|-----------|
| Not syncing | Check network, wait 30 sec |
| Import fails | Check session exists |
| Duplicate error | Already imported, mark as duplicate |
| Missing orders | Use batch import wizard |

## 💾 Storage Locations

- **Local**: Browser IndexedDB (per device)
- **Server**: `pos.order.backup` table (PostgreSQL)
- **Final**: `pos.order` table (after import)

## ⏰ Automatic Tasks

- **Sync**: Every 30 seconds
- **Verify**: Every 6 hours  
- **Cleanup**: Every day (30+ day old backups)

## 🔐 Security

- **POS User**: View, create backups
- **POS Manager**: Full access, import, cleanup

## 📱 Mobile Support

✅ Works on all devices with modern browsers
✅ IndexedDB supported on mobile
✅ Sync works on any connection

## 🎯 Best Practices

1. ✅ Check dashboard daily
2. ✅ Import missing orders immediately
3. ✅ Run cleanup weekly
4. ✅ Monitor error states
5. ✅ Verify before closing session

## 📞 Emergency Recovery

**Lost Orders?**

1. Go to Order Backups
2. Filter: Missing on Server  
3. Verify session is correct
4. Batch Import → Select All
5. Confirm import

**That's it!** Orders restored in seconds.

## 🔗 Related Menus

```
Point of Sale
├── Order Backups (main)
│   ├── Backup Dashboard
│   └── Cleanup Old Backups
├── Sessions
└── Orders
```

## 📋 Daily Checklist

- [ ] Open Backup Dashboard
- [ ] Check for missing orders
- [ ] Import any missing orders
- [ ] Review error states
- [ ] Verify sync is working

## 💡 Pro Tips

- Use keyboard shortcuts in list view
- Bulk select with Shift+Click
- Export data for analysis
- Set up email alerts (custom)
- Monitor by session before closing

## 🆘 Need Help?

1. Check browser console (F12)
2. Review server logs  
3. Check this guide
4. Read full README.md
5. Contact: support@weha-id.com

---

**Remember**: Backups happen automatically. You only need to act when orders are missing!
