# Quick Start Guide

## Installation

### 1. Prerequisites Check

Make sure these modules are installed:
```
✅ operating_unit (OCA)
✅ account_operating_unit (OCA)
✅ point_of_sale (Odoo Core)
✅ weha_pos_operating_unit (Custom)
```

Optional for stock features:
```
⭕ stock_request (OCA)
⭕ weha_stock_request_operating_unit (Custom)
```

### 2. Install Module

1. Module is already in: `d:\OdooProject\Project-0108\weha_operating_unit_hierarchy`
2. Restart Odoo server
3. Update Apps List
4. Search: "Operating Unit Hierarchy"
5. Click **Install**
6. ✅ Install demo data (recommended for first time)

---

## First Time Setup (5 minutes)

### Step 1: Verify OU Types
Navigate: **Operating Units → Configuration → Operating Unit Types**

You should see:
- ✅ Head Office (HO) - Level 0
- ✅ Distribution Center (DC) - Level 1
- ✅ Store (STORE) - Level 2

### Step 2: Check OU Hierarchy
Navigate: **Operating Units → Configuration → OU Hierarchy**

Demo structure:
```
🏛️ Head Office Jakarta
    ├── 📦 DC Jakarta
    │       ├── 🏪 Store Jakarta 01
    │       └── 🏪 Store Jakarta 02
    └── 📦 DC Surabaya
            └── 🏪 Store Surabaya 01
```

### Step 3: Review Revenue Sharing Rule
Navigate: **Point of Sale → Revenue Sharing → Revenue Sharing Rules**

Default rule: **70-20-10**
- Store: 70%
- DC: 20%
- HO: 10%
- Total: 100% ✅

---

## Test the System (10 minutes)

### Test 1: Create POS Orders

1. Go to **Point of Sale**
2. Open session for **Store Jakarta 01**
3. Create 2-3 orders with different products
4. Pay and close orders
5. Repeat for **Store Jakarta 02**

### Test 2: Process Revenue Sharing

1. Navigate: **Point of Sale → Revenue Sharing → Revenue Sharing Periods**
2. You should see current month period (e.g., "January 2026")
3. Open the period
4. Click **Calculate Revenue Sharing** button
5. Wait for notification: "Created X revenue sharing entries"
6. Click the **Entries** smart button

### Test 3: View Results

**Tree View:**
- See all entries with amounts
- Check source OU (Store) and target OU (Store/DC/HO)
- Verify percentages (70%, 20%, 10%)

**Pivot View:**
- Click "Pivot" view
- Rows: Target OU
- Columns: Period
- Measures: Share Amount
- See revenue distribution by OU

**Graph View:**
- Click "Graph" view
- Bar chart showing revenue by OU
- Should see Store gets most, then DC, then HO

### Test 4: Validate and Close

1. Back to the period form
2. Click **Validate** button
3. Review: Period state → "Validated"
4. Click **Close Period** button
5. Period state → "Closed"

---

## Common Use Cases

### Case 1: Add New Store

1. **Create OU:**
   - Navigate: Operating Units → Configuration → OU Hierarchy
   - Click Create
   - Name: "Store Jakarta 03"
   - Code: "STORE-JKT-03"
   - OU Type: Store
   - Parent: DC Jakarta
   - Revenue Share %: 70.0
   - Auto Share Revenue: ✅ Yes
   - Default Source OU: DC Jakarta

2. **Configure POS:**
   - Go to Point of Sale → Configuration → Point of Sale
   - Create/edit POS config for new store
   - Set Operating Unit: Store Jakarta 03

3. **Test:**
   - Make POS sales in new store
   - Process revenue sharing period
   - Verify entries created for new store

### Case 2: Different Revenue Split for Electronics

1. **Create Product Category Rule:**
   - Navigate: Point of Sale → Revenue Sharing → Rules
   - Click Create
   - Name: "Electronics Revenue Sharing (60-25-15)"
   - Sequence: 10 (higher priority than default)
   - Apply To: Product Category
   - Category: Electronics
   
2. **Add Lines:**
   - Store: 60%
   - DC: 25%
   - HO: 15%
   - Total: 100% ✅

3. **Test:**
   - Make POS sale with electronic product
   - Process period
   - Verify electronics get different split

### Case 3: Monthly Closing Process

**Every Month End:**

1. **Review Period:**
   - Check all POS orders are in "paid" state
   - Verify no pending orders

2. **Calculate:**
   - Open revenue sharing period
   - Click "Calculate Revenue Sharing"
   - Review notification for entry count

3. **Analyze:**
   - Click "Entries" smart button
   - Use Pivot view to analyze by:
     - Store performance
     - Product categories
     - DC performance
   - Export to Excel if needed

4. **Validate:**
   - Click "Validate" button
   - Lock calculations

5. **Accounting (Future):**
   - Click "Post Accounting"
   - Generate journal entries

6. **Close:**
   - Click "Close Period"
   - Period is now locked

---

## Troubleshooting

### Issue: No revenue sharing entries created

**Check:**
1. ✅ POS orders have operating_unit_id?
2. ✅ POS orders in "paid/done/invoiced" state?
3. ✅ Operating unit has auto_share_revenue enabled?
4. ✅ Revenue sharing rule exists?
5. ✅ Order date within period range?

**Fix:**
- Review POS order details
- Check OU configuration
- Verify rule exists (at least "all products" rule)

### Issue: Total percentage not 100%

**Fix:**
1. Open revenue sharing rule
2. Check all lines
3. Adjust percentages to total 100%
4. Save

### Issue: Wrong amounts calculated

**Fix:**
1. Open period
2. Click "Reset to Draft"
3. Fix any issues (rules, OU settings)
4. Click "Calculate Revenue Sharing" again

### Issue: Can't find period

**Check:**
- Period auto-created from POS orders
- If no POS orders, no period created

**Fix:**
- Make at least one POS order
- Period will be created automatically

---

## Next Steps

### Customize for Your Business

1. **Modify Revenue Sharing Rules:**
   - Create rules for specific products
   - Different splits for categories
   - Seasonal promotions with different splits

2. **Add More Stores:**
   - Create new store OUs
   - Link to appropriate DC
   - Configure POS for each store

3. **Expand Hierarchy:**
   - Add more DCs
   - Add regional offices (if needed)
   - Adjust hierarchy levels

4. **Accounting Integration (Coming Soon):**
   - Configure journal accounts
   - Set up inter-company transfer accounts
   - Automate journal entry creation

---

## Tips & Best Practices

### ✅ Do's

- ✅ Process revenue sharing monthly
- ✅ Review entries before validating
- ✅ Use pivot tables for analysis
- ✅ Keep backup of period data
- ✅ Document any custom rules
- ✅ Test with demo data first

### ❌ Don'ts

- ❌ Don't skip validation step
- ❌ Don't modify closed periods
- ❌ Don't create rules with total ≠ 100%
- ❌ Don't disable auto_share_revenue without reason
- ❌ Don't forget to configure parent OUs

---

## Performance Tips

### For Large Volumes

If processing 10,000+ orders per month:

1. **Optimize Period Calculation:**
   - Run during off-peak hours
   - Close POS sessions before processing
   - Ensure good database performance

2. **Archive Old Periods:**
   - Keep last 12 months active
   - Archive older periods

3. **Index Recommendations:**
   ```sql
   -- Run in database if needed
   CREATE INDEX IF NOT EXISTS idx_pos_order_date_ou ON pos_order(date_order, operating_unit_id, state);
   CREATE INDEX IF NOT EXISTS idx_revenue_entry_period ON revenue_sharing_entry(period_id, target_ou_id);
   ```

---

## Support

### Documentation
- 📖 **README.md:** Complete user guide
- 🔧 **MODULE_STRUCTURE.md:** Technical details
- 📝 **CREATION_SUMMARY.md:** What was built

### Help Resources
- **Email:** support@weha-id.com
- **Website:** https://weha-id.com

### Report Issues
Include:
1. Odoo version
2. Module version
3. Error message/screenshot
4. Steps to reproduce

---

## Success Checklist

After installation, verify:

- [ ] Module installed successfully
- [ ] OU types visible (HO, DC, Store)
- [ ] OU hierarchy created
- [ ] Revenue sharing rule exists
- [ ] Demo data loaded (if selected)
- [ ] Can create POS orders
- [ ] Can process revenue sharing period
- [ ] Entries created correctly
- [ ] Pivot/graph views working
- [ ] Can validate and close period

---

## What's Next?

### Phase 2 Features (Coming Soon)
- 🏦 Automatic journal entry creation
- 📦 Stock request hierarchy routing
- 💵 Commission payment wizard
- 📧 Email notifications

### Get Started Now!
1. Install the module
2. Load demo data
3. Test with sample orders
4. Configure for your business
5. Start using monthly revenue sharing

---

**Ready to begin? Let's go!** 🚀
