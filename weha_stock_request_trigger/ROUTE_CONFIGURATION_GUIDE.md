# Route Configuration Guide for Stock Request Trigger

## Problem Statement

When a Store creates a stock request to a DC (Distribution Center), Odoo needs a **route** to know how to transfer the inventory. Without a proper route configuration:

- ❌ Stock request created but can't be fulfilled
- ❌ No picking/transfer generated
- ❌ Inventory stuck at source

With proper route configuration:

- ✅ Stock request auto-generates picking
- ✅ Transfer moves from DC warehouse to Store warehouse
- ✅ Inventory flows through the hierarchy

## Understanding Routes in Odoo

### What is a Route?

A route defines **how products move** between locations:
- From: Source location (e.g., DC/Stock)
- To: Destination location (e.g., Store/Stock)
- Via: Operations (pick, pack, ship)

### Route Components

1. **Route** (`stock.route`)
   - Name: "DC East → Store A"
   - Type: Warehouse internal transfer

2. **Push Rule** (`stock.rule`)
   - Action: Pull From or Push To
   - Source: DC East/Stock
   - Destination: Store A/Stock
   - Picking Type: Internal Transfer

## Solution Options

### Option 1: Manual Route Configuration (Recommended for Start)

Configure routes manually through Odoo UI. Good for understanding the system.

### Option 2: Auto-Generate Routes (Advanced)

Create routes automatically when setting up OU hierarchy. Better for scaling.

### Option 3: Use Default Warehouse Routes

Leverage existing multi-warehouse setup if already configured.

---

## Option 1: Manual Route Configuration

### Step 1: Enable Multi-Warehouse

```
Settings > Inventory > Warehouse
☑ Storage Locations
☑ Multi-Step Routes
```

### Step 2: Create Warehouses for Each OU

```
Inventory > Configuration > Warehouses

Create for HO:
- Name: HO Warehouse
- Short Name: HO
- Operating Unit: Head Office

Create for DC East:
- Name: DC East Warehouse
- Short Name: DCE
- Operating Unit: DC East

Create for Store A:
- Name: Store A Warehouse
- Short Name: STA
- Operating Unit: Store A
```

### Step 3: Create Route (DC → Store)

```
Inventory > Configuration > Routes > Create

Name: DC East → Store A
Applicable On: Warehouse

Add Rule (Push/Pull):
- Action: Pull From
- Source Location: DC East/Stock
- Destination Location: Store A/Stock
- Picking Type: Store A: Internal Transfers
- Procurement Method: Take From Stock
```

### Step 4: Link Route to Replenishment Rule

```
Inventory > Replenishment > Replenishment Rules

Edit Rule for Store A - Product X:
- Operating Unit: Store A
- Warehouse: Store A Warehouse
- Route: DC East → Store A  ← SELECT THIS
- Source OU: DC East
```

### Step 5: Test the Flow

```
1. Set stock below minimum:
   - Store A: Product X = 5 units
   - Rule: Min=10, Max=50

2. Trigger replenishment (auto or manual)

3. Check stock request:
   - Inventory > Stock Requests
   - Should show: Route = "DC East → Store A"

4. Confirm stock request

5. Check picking:
   - Inventory > Operations > Transfers
   - Should show: DC East → Store A
   - Type: Internal Transfer

6. Process transfer:
   - Validate picking
   - Stock moves from DC to Store
```

---

## Option 2: Auto-Generate Routes

### Create Helper Model for Route Management

Create a new model to auto-generate routes based on OU hierarchy.

#### Add to weha_operating_unit_hierarchy module:

**models/stock_route_manager.py:**

```python
from odoo import api, fields, models, _
from odoo.exceptions import UserError


class OperatingUnit(models.Model):
    _inherit = 'operating.unit'
    
    warehouse_id = fields.Many2one(
        'stock.warehouse',
        string='Default Warehouse',
        help='Default warehouse for this operating unit'
    )
    
    def action_generate_routes(self):
        """Generate routes from parent to child OUs"""
        self.ensure_one()
        
        if not self.warehouse_id:
            raise UserError(_('Please configure warehouse for %s first!') % self.name)
        
        if not self.parent_id or not self.parent_id.warehouse_id:
            raise UserError(_('Parent OU must have a warehouse configured!'))
        
        # Check if route already exists
        route_name = '%s → %s' % (self.parent_id.name, self.name)
        existing_route = self.env['stock.route'].search([
            ('name', '=', route_name)
        ], limit=1)
        
        if existing_route:
            raise UserError(_('Route %s already exists!') % route_name)
        
        # Create route
        route = self.env['stock.route'].create({
            'name': route_name,
            'warehouse_selectable': True,
            'warehouse_ids': [(4, self.warehouse_id.id)],
            'company_id': self.company_id.id,
        })
        
        # Create pull rule
        self.env['stock.rule'].create({
            'name': '%s: Pull from %s' % (self.name, self.parent_id.name),
            'route_id': route.id,
            'location_src_id': self.parent_id.warehouse_id.lot_stock_id.id,
            'location_dest_id': self.warehouse_id.lot_stock_id.id,
            'action': 'pull',
            'picking_type_id': self.warehouse_id.int_type_id.id,
            'procure_method': 'make_to_stock',
            'company_id': self.company_id.id,
        })
        
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': _('Route Created'),
                'message': _('Route %s created successfully!') % route_name,
                'type': 'success',
                'sticky': False,
            }
        }
```

**Add button to OU form view:**

```xml
<record id="view_operating_unit_form_route" model="ir.ui.view">
    <field name="name">operating.unit.form.route</field>
    <field name="model">operating.unit</field>
    <field name="inherit_id" ref="operating_unit.view_operating_unit_form"/>
    <field name="arch" type="xml">
        <field name="parent_id" position="after">
            <field name="warehouse_id" options="{'no_create': True}"/>
        </field>
        
        <xpath expr="//div[@name='button_box']" position="inside">
            <button name="action_generate_routes" 
                    type="object" 
                    class="oe_stat_button" 
                    icon="fa-route"
                    invisible="not parent_id">
                <span>Generate Route</span>
            </button>
        </xpath>
    </field>
</record>
```

### Usage:

```
1. Configure warehouses for all OUs
2. Open each child OU (Store, DC)
3. Click "Generate Route" button
4. Route auto-created: Parent → Child
5. Use in replenishment rules
```

---

## Option 3: Use Default Warehouse Routes

If you already have multi-warehouse setup with internal transfers:

### Configuration:

```
Inventory > Configuration > Warehouses > [DC East]

Resupply:
☑ Resupply From: [HO Warehouse]

This creates default route: HO → DC East
```

Then link in replenishment rule:

```
Route: DC East: Resupply from HO Warehouse
```

---

## Recommended Approach

### For New Implementation:

1. **Start with Manual (Option 1)**
   - Create 2-3 routes manually
   - Understand the flow
   - Test thoroughly

2. **Scale with Auto-Generation (Option 2)**
   - Once comfortable, implement auto-generation
   - Create routes for all OU pairs
   - Maintain consistency

3. **Leverage Defaults (Option 3)**
   - Use for standard warehouse setups
   - Combine with manual routes as needed

### For Existing Multi-Warehouse:

1. **Use Option 3** if already configured
2. **Supplement with Option 1** for special cases
3. **Consider Option 2** for new OUs

---

## Route Naming Convention

Recommended format:

```
[Source OU] → [Destination OU]

Examples:
- HO → DC East
- HO → DC West
- DC East → Store A
- DC East → Store B
- DC West → Store C
```

Benefits:
- Clear direction
- Easy to search
- Consistent naming

---

## Troubleshooting

### Problem: Stock request created but no picking

**Cause:** No route configured

**Solution:**
```
1. Check replenishment rule has route_id set
2. Check route is active
3. Check route has proper rules
4. Check source/destination locations correct
```

### Problem: Picking created but can't validate

**Cause:** No stock at source location

**Solution:**
```
1. Check DC has stock
2. If DC also low, create request DC → HO
3. Ensure cascading replenishment
```

### Problem: Route not appearing in dropdown

**Cause:** Route not applicable to warehouse

**Solution:**
```
1. Edit route
2. Check "Applicable On" = Warehouse
3. Add warehouse to "Warehouse" field
```

---

## Complete Setup Example

### Scenario: HO → DC East → Store A

#### 1. Create Warehouses

```
HO Warehouse (HO)
├─ Stock Location: HO/Stock
└─ Operating Unit: Head Office

DC East Warehouse (DCE)
├─ Stock Location: DCE/Stock
└─ Operating Unit: DC East

Store A Warehouse (STA)
├─ Stock Location: STA/Stock
└─ Operating Unit: Store A
```

#### 2. Create Routes

**Route 1: HO → DC East**
```
Name: HO → DC East
Rule:
- Action: Pull From
- Source: HO/Stock
- Destination: DCE/Stock
- Picking Type: DCE: Internal Transfers
```

**Route 2: DC East → Store A**
```
Name: DC East → Store A
Rule:
- Action: Pull From
- Source: DCE/Stock
- Destination: STA/Stock
- Picking Type: STA: Internal Transfers
```

#### 3. Configure Replenishment Rules

**Store A - Product X**
```
Operating Unit: Store A
Warehouse: Store A Warehouse
Location: STA/Stock
Product: Product X
Minimum: 10
Maximum: 50
Route: DC East → Store A  ← KEY!
Source OU: DC East
Auto Trigger: Yes
```

**DC East - Product X**
```
Operating Unit: DC East
Warehouse: DC East Warehouse
Location: DCE/Stock
Product: Product X
Minimum: 50
Maximum: 200
Route: HO → DC East  ← KEY!
Source OU: HO
Auto Trigger: Yes
```

#### 4. Test Flow

```
Initial Stock:
- HO: 1000 units
- DC East: 40 units (below min=50)
- Store A: 5 units (below min=10)

Automatic Flow:
1. Store A triggers: Request 45 units from DC East
   → Creates stock request with route "DC East → Store A"
   → Generates picking: DCE/Stock → STA/Stock

2. DC East stock drops: 40 - 45 = -5 (triggers replenishment)
   → Request 200 - 40 = 160 units from HO
   → Creates stock request with route "HO → DC East"
   → Generates picking: HO/Stock → DCE/Stock

3. HO processes transfer to DC East (160 units)
   → DC East receives: 40 + 160 = 200 units

4. DC East processes transfer to Store A (45 units)
   → Store A receives: 5 + 45 = 50 units

Final Stock:
- HO: 840 units (1000 - 160)
- DC East: 155 units (200 - 45)
- Store A: 50 units (5 + 45)
```

---

## Integration with Replenishment Module

The `route_id` field is now part of the replenishment rule:

```python
# In stock_replenishment_rule.py
route_id = fields.Many2one(
    'stock.route',
    string='Route',
    help='Route for stock transfer from source to destination OU'
)

# When creating stock request
stock_request = self.env['stock.request'].create({
    ...
    'route_id': self.route_id.id if self.route_id else False,
    ...
})
```

This ensures every auto-generated stock request has the proper route!

---

## Best Practices

### 1. One Route Per OU Pair
```
✅ Create: DC East → Store A
✅ Create: DC East → Store B
❌ Don't use: DC East → All Stores
```

### 2. Bidirectional Routes (Optional)
```
For returns or reverse logistics:
- Store A → DC East (return route)
- DC East → Store A (supply route)
```

### 3. Route Maintenance
```
- Archive unused routes
- Update when OU hierarchy changes
- Document route purposes
```

### 4. Test Before Auto-Trigger
```
1. Create rule with Auto Trigger = No
2. Test manual replenishment
3. Verify picking created correctly
4. Enable Auto Trigger
```

---

## Summary

| Aspect | Manual | Auto-Generate | Default |
|--------|--------|---------------|---------|
| Setup Time | Medium | High | Low |
| Flexibility | High | Medium | Low |
| Maintenance | Manual | Automatic | Automatic |
| Best For | Small setups | Large setups | Existing multi-WH |

**Recommendation:** Start with **Manual**, scale with **Auto-Generate**, leverage **Default** where available.

---

## Next Steps

1. ✅ Add `route_id` field to replenishment rule (DONE)
2. ✅ Update stock request creation to include route (DONE)
3. ✅ Add route to form view (DONE)
4. ⬜ Create routes manually for testing
5. ⬜ Test complete flow: Store → DC → HO
6. ⬜ Consider implementing auto-generation
7. ⬜ Document your route setup

---

## Questions?

- **Q: Do I need routes for every product?**
  - A: No, one route per OU pair serves all products

- **Q: Can I have multiple routes for same OU pair?**
  - A: Yes, for different scenarios (e.g., urgent vs normal)

- **Q: What if I don't set a route?**
  - A: Stock request created but no picking generated

- **Q: How to test if route is working?**
  - A: Create manual stock request, check if picking appears

---

Ready to configure your routes! 🚀
