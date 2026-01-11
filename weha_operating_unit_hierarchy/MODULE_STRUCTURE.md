# Module Structure

## File Organization

```
weha_operating_unit_hierarchy/
├── __init__.py                                 # Module initialization
├── __manifest__.py                             # Module manifest
├── README.md                                   # User documentation
├── MODULE_STRUCTURE.md                         # This file
│
├── models/                                     # Python models
│   ├── __init__.py
│   ├── operating_unit_type.py                 # OU types (HO, DC, Store)
│   ├── operating_unit.py                      # OU with hierarchy
│   ├── revenue_sharing_rule.py                # Revenue sharing rules
│   ├── revenue_sharing_period.py              # Monthly periods
│   ├── revenue_sharing_entry.py               # Individual entries
│   └── pos_order.py                           # POS order extension
│
├── views/                                      # XML views
│   ├── operating_unit_type_views.xml          # OU type views
│   ├── operating_unit_views.xml               # OU hierarchy views
│   ├── revenue_sharing_rule_views.xml         # Rule configuration
│   ├── revenue_sharing_period_views.xml       # Period management
│   └── revenue_sharing_entry_views.xml        # Entry views & reports
│
├── security/                                   # Security files
│   ├── ir.model.access.csv                    # Access rights
│   └── revenue_sharing_security.xml           # Record rules
│
├── data/                                       # Demo/initial data
│   └── demo_data.xml                          # Demo OU hierarchy
│
└── static/                                     # Static assets
    └── description/
        └── icon.png                            # Module icon
```

## Model Details

### 1. operating.unit.type
**Purpose**: Define types of operating units (HO, DC, Store)

**Key Fields**:
- `name`: Type name (e.g., "Head Office")
- `code`: Unique code (e.g., "HO")
- `level`: Hierarchy level (0=HO, 1=DC, 2=Store)
- `can_have_parent`: Whether this type can have a parent
- `can_have_children`: Whether this type can have children
- `default_revenue_share`: Default percentage for this type

**Relations**: Referenced by `operating.unit`

---

### 2. operating.unit (extended)
**Purpose**: Extend operating unit with hierarchy and revenue sharing

**Added Fields**:
- `ou_type_id`: Link to operating unit type
- `parent_id`: Parent operating unit
- `child_ids`: Child operating units
- `parent_path`: Full hierarchy path (computed)
- `level`: Level in hierarchy (computed)
- `revenue_share_percentage`: Percentage of revenue this OU gets
- `auto_share_revenue`: Enable automatic revenue sharing
- `default_source_ou_id`: Default source for stock requests
- `auto_request_from_parent`: Auto-route stock requests to parent

**Key Methods**:
- `_compute_parent_path()`: Calculate full hierarchy path
- `_compute_level()`: Calculate level from parent
- `_check_hierarchy_loop()`: Prevent circular references
- `get_all_parents()`: Get all parent OUs
- `get_all_children()`: Get all child OUs
- `action_view_children()`: View child OUs

---

### 3. revenue.sharing.rule
**Purpose**: Define revenue sharing rules

**Key Fields**:
- `name`: Rule name
- `sequence`: Priority order
- `apply_to`: 'all', 'category', or 'product'
- `categ_id`: Product category (if apply_to='category')
- `product_id`: Specific product (if apply_to='product')
- `line_ids`: Revenue sharing lines (percentages per OU type)
- `total_percentage`: Computed total (must = 100%)

**Key Methods**:
- `get_sharing_for_product()`: Find applicable rule for a product
- `_check_total_percentage()`: Validate 100% total

**Relations**: Referenced by `revenue.sharing.entry`

---

### 4. revenue.sharing.rule.line
**Purpose**: Define percentage per OU type in a rule

**Key Fields**:
- `rule_id`: Parent rule
- `ou_type_id`: OU type (Store, DC, HO)
- `percentage`: Revenue share percentage (0-100)
- `description`: Notes

**Constraints**:
- Percentage must be 0-100
- Total across lines must = 100%

---

### 5. revenue.sharing.period
**Purpose**: Monthly revenue sharing calculation period

**Key Fields**:
- `name`: Period name (e.g., "January 2026")
- `date_from`: Start date (first day of month)
- `date_to`: End date (last day of month)
- `state`: draft/calculated/validated/posted/closed
- `entry_ids`: Revenue sharing entries for this period
- `total_revenue`: Sum of all revenue (computed)
- `total_shared`: Sum of all shared amounts (computed)

**Key Methods**:
- `get_or_create_period()`: Get or create period for a date
- `action_calculate_revenue_sharing()`: Process POS orders and create entries
- `action_validate()`: Lock calculations
- `action_post_accounting()`: Create journal entries (future)
- `action_close_period()`: Finalize period
- `action_reset_to_draft()`: Reset for recalculation

**Workflow**: Draft → Calculated → Validated → Posted → Closed

---

### 6. revenue.sharing.entry
**Purpose**: Individual revenue sharing entry (one per order line per OU)

**Key Fields**:
- `period_id`: Parent period
- `pos_order_id`: POS order reference
- `pos_order_line_id`: POS order line
- `source_ou_id`: Selling OU (Store)
- `target_ou_id`: Receiving OU (Store/DC/HO)
- `rule_id`: Applied rule
- `rule_line_id`: Applied rule line
- `product_id`: Product sold
- `total_amount`: Total revenue from sale
- `share_percentage`: Percentage for this OU
- `share_amount`: Amount for this OU
- `state`: draft/validated/posted
- `move_id`: Accounting entry (future)

**Relations**: 
- Links POS orders to revenue distribution
- Groups by period for batch processing

---

### 7. pos.order (extended)
**Purpose**: Link POS orders to revenue sharing periods

**Added Fields**:
- `revenue_sharing_period_id`: Auto-assigned based on order date

**Key Methods**:
- `_compute_revenue_sharing_period()`: Auto-assign period

**Note**: Revenue calculation happens at period level, not per order

---

## View Structure

### Operating Unit Type Views
- Tree: List of OU types with levels and settings
- Form: Configure OU type details
- Menu: Under Operating Units → Configuration

### Operating Unit Views
- Form (extended): Add hierarchy tab with parent/child, revenue settings
- Tree (extended): Add type, parent, level columns
- Hierarchy Tree: Special view showing hierarchy structure
- Search (extended): Filters by type (HO/DC/Store), level, auto-share
- Menu: OU Hierarchy under Operating Units → Configuration

### Revenue Sharing Rule Views
- Tree: List rules with apply_to and total percentage
- Form: Configure rule with lines (percentages per OU type)
- Search: Filter by active, apply_to type, category
- Menu: Under Point of Sale → Revenue Sharing

### Revenue Sharing Period Views
- Tree: List periods with dates, counts, totals, state
- Form: Period details with buttons for workflow actions
- Search: Filter by state, current month, last month
- Menu: Under Point of Sale → Revenue Sharing

### Revenue Sharing Entry Views
- Tree: List entries with amounts, percentages, state
- Form: Entry details (read-only, created by system)
- Search: Filter by state, month, group by period/OU/product
- Pivot: Analysis view (OU x Period)
- Graph: Bar chart by target OU
- Menu: Under Point of Sale → Revenue Sharing

---

## Security

### Access Rights (ir.model.access.csv)

| Model | User | Manager | Accountant |
|-------|------|---------|------------|
| operating.unit.type | Read | Full | Full |
| revenue.sharing.rule | Read | Full | Full |
| revenue.sharing.rule.line | Read | Full | Full |
| revenue.sharing.period | Read | Read/Write | Full |
| revenue.sharing.entry | Read | Read | Full |

### Record Rules (revenue_sharing_security.xml)

- Multi-company rules for all revenue sharing models
- Domain: `['|',('company_id','=',False),('company_id', 'in', company_ids)]`

---

## Data Flow

### 1. Setup Phase
```
1. Create OU Types (HO, DC, Store)
2. Create Operating Units with hierarchy
3. Configure Revenue Sharing Rules
```

### 2. Daily Operations
```
Store makes POS sale
→ POS order created with operating_unit_id
→ Period auto-assigned based on date
→ (Revenue calculation happens later)
```

### 3. Monthly Processing
```
End of month
→ Open Revenue Sharing Period
→ Click "Calculate Revenue Sharing"
→ System processes all POS orders for the month:
   - For each order line:
     - Find applicable revenue sharing rule
     - Find parent OUs in hierarchy
     - Create entry for each OU type in rule
     - Calculate share amounts
→ Review entries (pivot/graph views)
→ Validate
→ Post Accounting (future)
→ Close Period
```

### 4. Revenue Distribution Example
```
POS Order Line:
- Product: Laptop
- Amount: Rp 10,000,000
- Selling OU: Store Jakarta 01 (parent: DC Jakarta → HO Jakarta)

Rule Applied: Default (70-20-10)

Entries Created:
1. Store Jakarta 01: 70% = Rp 7,000,000
2. DC Jakarta: 20% = Rp 2,000,000
3. HO Jakarta: 10% = Rp 1,000,000
```

---

## Dependencies

### Required Modules
- `operating_unit` (OCA): Base operating unit framework
- `account_operating_unit` (OCA): Accounting integration
- `point_of_sale`: POS module
- `weha_pos_operating_unit`: POS + OU integration

### Optional Modules
- `stock_request` (OCA): For stock flow features
- `weha_stock_request_operating_unit`: Stock request + OU

---

## Customization Points

### 1. Add New OU Types
Create new records in `operating.unit.type` with appropriate level and settings.

### 2. Custom Revenue Sharing Rules
Create rules in `revenue.sharing.rule` with different percentages or application criteria.

### 3. Accounting Integration
Extend `revenue.sharing.period.action_post_accounting()` to create journal entries.

### 4. Stock Request Routing
Extend `operating.unit` with methods for automatic stock request routing based on hierarchy.

### 5. Additional Reports
Create new views/reports using `revenue.sharing.entry` data.

---

## Performance Considerations

### Monthly Batch Processing
- Processes all orders at once (better than per-order)
- Can handle thousands of orders efficiently
- Uses search + create in batches

### Hierarchy Traversal
- `parent_path` field avoids recursive queries
- `get_all_parents()` is efficient (split parent_path)
- Cached computed fields (level, parent_path)

### Database Indexes
- Recommended indexes:
  - `revenue.sharing.period(date_from, date_to, company_id)`
  - `revenue.sharing.entry(period_id, target_ou_id, product_id)`
  - `pos.order(date_order, operating_unit_id, state)`

---

## Testing Recommendations

### 1. Unit Tests
- Test hierarchy loop detection
- Test revenue sharing calculation
- Test rule matching (all/category/product)
- Test percentage validation (must = 100%)

### 2. Integration Tests
- Test end-to-end period processing
- Test with multiple stores/DCs
- Test different revenue sharing rules
- Test state transitions

### 3. Manual Testing
1. Install demo data
2. Create test POS orders in different stores
3. Process revenue sharing period
4. Verify entries in pivot view
5. Check totals match order amounts

---

## Troubleshooting

### Issue: Total percentage not 100%
**Solution**: Check revenue sharing rule lines, ensure total = 100%

### Issue: No revenue sharing entries created
**Causes**:
- auto_share_revenue disabled on OU
- No revenue sharing rule found for product
- POS order not in paid/done/invoiced state
- POS order has no operating_unit_id

### Issue: Wrong OU receiving revenue
**Solution**: Check OU hierarchy and rule line OU types

### Issue: Entries created twice
**Solution**: Click "Reset to Draft" before recalculating

---

## Future Development Roadmap

### Phase 1 (Current)
✅ OU hierarchy
✅ Monthly revenue sharing
✅ Basic reporting

### Phase 2 (Next)
- [ ] Accounting integration (journal entries)
- [ ] Stock request hierarchy routing
- [ ] Commission payments

### Phase 3 (Future)
- [ ] Advanced analytics dashboard
- [ ] Multi-currency support
- [ ] Email notifications
- [ ] API for external integration
