# Visual Hierarchy Tree Dashboard (OWL Component)

## Overview

The Visual Hierarchy Tree Dashboard is a custom OWL (Odoo Web Library) component that provides an interactive, graphical tree view of your operating unit hierarchy. Unlike the standard list view, this component offers:

- **Interactive Tree Visualization**: Expand/collapse nodes to explore hierarchy
- **Color-Coded Display**: Visual distinction between OU types
- **Real-time Interaction**: Click nodes to view details
- **Modern UI**: Responsive design with smooth animations
- **Single Page Experience**: All data on one screen without pagination

## Features

### 🎨 Visual Elements

#### 1. **Color-Coded OU Types**
- 🔵 **Blue**: Head Office (HO) - Primary level
- 🟢 **Teal**: Distribution Centers (DC) - Secondary level  
- 🟢 **Green**: Stores - Tertiary level

#### 2. **Interactive Tree Structure**
- **Expandable Nodes**: Click chevron to expand/collapse
- **Hierarchical Indentation**: Visual depth indication
- **Connecting Lines**: Visual parent-child connections
- **Smooth Animations**: Fade-in effects for better UX

#### 3. **Node Information Display**
```
[Icon] OU Name [Code Badge]
       [Type Badge] [Level Badge] [Children Count]
```

Each node shows:
- **Icon**: Visual indicator of OU type (building/warehouse/store)
- **Name**: Operating unit name
- **Code**: OU code in badge
- **Type**: OU type with color-coded badge
- **Level**: Hierarchy level (0, 1, 2)
- **Children Count**: Number of direct children

### 🛠️ Toolbar Actions

#### Expand All
- Expands all nodes in the tree
- Shows complete hierarchy at once
- Useful for getting full overview

#### Collapse All  
- Collapses all nodes except root
- Returns to top-level view
- Useful for resetting view

#### Refresh
- Reloads data from backend
- Updates tree with latest changes
- Maintains expansion state when possible

### 📱 Responsive Design

The dashboard adapts to different screen sizes:

**Desktop (>768px)**:
- Full toolbar with all buttons
- Wide node display
- Large indentation (40px per level)

**Tablet/Mobile (≤768px)**:
- Stacked toolbar buttons
- Compact node display
- Reduced indentation (20px per level)
- Vertical legend layout

## Access the Dashboard

### Main Menu Location
```
Operating Unit Hierarchy → Visual Hierarchy Tree
```

### Alternative Access
1. Go to **Operating Unit Hierarchy** module
2. Click **Visual Hierarchy Tree** menu item
3. Dashboard opens as full-screen client action

## Using the Dashboard

### Basic Navigation

#### 1. **View Hierarchy**
- Tree loads automatically on open
- Root nodes (HO) are expanded by default
- Scroll to view entire hierarchy

#### 2. **Expand/Collapse Nodes**
- **Expand**: Click ▶️ chevron next to node name
- **Collapse**: Click 🔽 chevron next to node name
- **Expand All**: Click "Expand All" button in toolbar
- **Collapse All**: Click "Collapse All" button in toolbar

#### 3. **View OU Details**
- Click anywhere on a node (except chevron)
- Opens OU form view in current window
- View/edit full OU details
- Use browser back to return to tree

#### 4. **Refresh Data**
- Click "Refresh" button in toolbar
- Reloads all OU data from database
- Updates tree with latest changes

### Visual Indicators

#### Node Colors
Each node has a colored left border:
- **Blue Border**: Head Office (HO)
- **Teal Border**: Distribution Center (DC)
- **Green Border**: Store

#### Background Gradients
Nodes have subtle gradient backgrounds:
- Lighter gradient on left (border color)
- Fades to light gray on right
- Provides depth and visual hierarchy

#### Badges
- **Type Badge**: Colored badge showing OU type
  - Blue background: HO
  - Teal background: DC
  - Green background: Store
- **Level Badge**: Light gray badge showing hierarchy level
- **Children Badge**: Info badge showing child count (if > 0)

#### Icons
- **🏢 Building**: Head Office (HO)
- **🏭 Warehouse**: Distribution Center (DC)
- **🏪 Store**: Store

### Legend

Bottom of dashboard shows legend:
```
Legend:
🏢 Head Office (HO)  |  🏭 Distribution Center (DC)  |  🏪 Store
```

## Example Hierarchy Display

### Visual Representation

```
┌─────────────────────────────────────────────────────────┐
│ 🏢 Weha Indonesia [HO001]                               │
│    [HO] [Level: 0] [👥 2 children]                      │
├─────────────────────────────────────────────────────────┤
│   🏭 DC East [DC001]                                    │
│      [DC] [Level: 1] [👥 3 children]                    │
│   ├──────────────────────────────────────────────────   │
│   │  🏪 Store A [STR001]                                │
│   │     [Store] [Level: 2]                              │
│   │                                                      │
│   │  🏪 Store B [STR002]                                │
│   │     [Store] [Level: 2]                              │
│   │                                                      │
│   │  🏪 Store C [STR003]                                │
│   │     [Store] [Level: 2]                              │
│   │                                                      │
│   🏭 DC West [DC002]                                    │
│      [DC] [Level: 1] [👥 2 children]                    │
│   ├──────────────────────────────────────────────────   │
│   │  🏪 Store D [STR004]                                │
│   │     [Store] [Level: 2]                              │
│   │                                                      │
│   │  🏪 Store E [STR005]                                │
│   │     [Store] [Level: 2]                              │
└─────────────────────────────────────────────────────────┘
```

## Use Cases

### 1. **Quick Hierarchy Overview**
**Scenario**: Need to understand org structure quickly

**Steps**:
1. Open Visual Hierarchy Tree
2. Click "Expand All"
3. See complete hierarchy at a glance
4. Use color coding to identify OU types

**Benefit**: Fast visual comprehension of organization structure

### 2. **Find Specific OU in Hierarchy**
**Scenario**: Locate "Store A" and see its parents

**Steps**:
1. Open Visual Hierarchy Tree
2. Expand HO level
3. Expand DC East
4. See Store A with full hierarchy context

**Benefit**: Understand OU's position in organization

### 3. **Check DC Distribution**
**Scenario**: Verify which stores are under DC East

**Steps**:
1. Open Visual Hierarchy Tree
2. Expand "DC East" node
3. See all child stores listed
4. Check children count badge

**Benefit**: Quick verification of DC-Store relationships

### 4. **Verify Hierarchy Levels**
**Scenario**: Ensure all stores are at level 2

**Steps**:
1. Open Visual Hierarchy Tree
2. Click "Expand All"
3. Check level badges on all stores
4. All should show "Level: 2"

**Benefit**: Visual verification of hierarchy correctness

### 5. **Edit OU from Tree**
**Scenario**: Update OU details while viewing hierarchy

**Steps**:
1. Navigate to OU in tree
2. Click on OU node
3. Form view opens
4. Edit and save
5. Click Refresh to see updated tree

**Benefit**: Seamless editing without losing context

## Technical Details

### Technology Stack

#### Frontend
- **OWL (Odoo Web Library)**: Component framework
- **JavaScript ES6+**: Modern JS features
- **XML Templates**: QWeb templates
- **SCSS**: Advanced styling

#### Backend
- **Odoo ORM**: Data access via `orm.searchRead`
- **Python Models**: `operating.unit` model
- **Client Actions**: Custom action type

### Component Architecture

```
HierarchyTreeComponent (JS)
├── State Management
│   ├── rootNodes: Array of root OUs
│   ├── expandedNodes: Set of expanded node IDs
│   └── loading: Boolean loading state
│
├── Data Loading
│   └── loadHierarchyData(): Fetches and builds tree
│
├── Tree Operations
│   ├── toggleNode(): Expand/collapse
│   ├── expandAll(): Expand all nodes
│   ├── collapseAll(): Collapse all nodes
│   └── refresh(): Reload data
│
└── UI Interactions
    └── openOUForm(): Open OU details
```

### Data Structure

#### Node Object
```javascript
{
    id: 1,
    name: "DC East",
    code: "DC001",
    ou_type: "Distribution Center",
    ou_type_code: "DC",
    level: 1,
    parent_path: "Weha Indonesia / DC East",
    parent_id: 1,
    children: [...],  // Array of child nodes
    child_count: 3
}
```

### Performance Optimization

1. **Single Query**: Loads all OUs in one query
2. **Client-Side Tree Building**: Constructs tree in browser
3. **Efficient Rendering**: Only renders visible nodes
4. **State Management**: Tracks expansion state efficiently
5. **CSS Animations**: Hardware-accelerated transitions

### Styling Features

#### Color Scheme
- **Primary Blue**: #3498db (HO)
- **Teal**: #1abc9c (DC)
- **Green**: #2ecc71 (Store)
- **Gray**: #95a5a6 (Other)

#### Responsive Breakpoints
- **Desktop**: > 768px
- **Mobile**: ≤ 768px

#### Animations
- **Fade In**: 0.3s ease-in
- **Hover Effects**: 0.3s transition
- **Smooth Expansion**: CSS transitions

## Comparison: OWL Tree vs Standard Views

### Visual Hierarchy Tree (OWL)

**Advantages**:
✅ Interactive tree visualization
✅ Expand/collapse functionality
✅ Visual hierarchy with indentation
✅ Single-page view (no pagination)
✅ Modern, animated UI
✅ Color-coded nodes
✅ Quick parent-child comprehension

**Best For**:
- Understanding hierarchy structure
- Quick navigation
- Visual presentations
- Mobile/tablet access
- Executive dashboards

### Standard List View

**Advantages**:
✅ Sortable columns
✅ Bulk operations
✅ Advanced filtering
✅ Export capabilities
✅ Standard Odoo features

**Best For**:
- Data analysis
- Bulk editing
- Reporting
- Export/import
- Complex filters

### Recommendation
Use both views for different purposes:
- **OWL Tree**: Visual exploration and presentations
- **List View**: Data management and analysis

## Troubleshooting

### Issue: Tree doesn't load
**Solution**:
1. Check browser console for errors
2. Verify module is upgraded
3. Clear browser cache
4. Check access rights to `operating.unit`

### Issue: Nodes show incorrect hierarchy
**Solution**:
1. Verify `parent_id` is set correctly on OUs
2. Check OU types have correct level configuration
3. Recalculate `parent_path` by saving OUs
4. Click Refresh button in dashboard

### Issue: Expand/collapse doesn't work
**Solution**:
1. Check if OU has children (child_count > 0)
2. Refresh the page
3. Clear browser cache
4. Check browser console for JS errors

### Issue: Styling looks broken
**Solution**:
1. Clear browser cache (Ctrl+F5)
2. Check if SCSS compiled correctly
3. Verify assets loaded (browser dev tools → Network)
4. Update module

### Issue: Can't click on nodes
**Solution**:
1. Check if you have form view access
2. Verify user permissions
3. Check browser console for errors
4. Try different browser

## Browser Compatibility

**Fully Supported**:
- ✅ Chrome 90+
- ✅ Firefox 88+
- ✅ Edge 90+
- ✅ Safari 14+

**Mobile Browsers**:
- ✅ Chrome Mobile
- ✅ Safari iOS
- ✅ Firefox Mobile

## Future Enhancements

Planned features for future versions:

1. **Search/Filter**: Search within tree
2. **Drag & Drop**: Reorder hierarchy by dragging
3. **Export**: Export tree as image/PDF
4. **Zoom**: Zoom in/out on large hierarchies
5. **Minimap**: Overview map for large trees
6. **Node Actions**: Context menu on right-click
7. **Custom Colors**: User-defined color schemes
8. **Print View**: Optimized print layout

## Support

For issues or questions:
- **Documentation**: This file and README.md
- **Technical Support**: support@weha-id.com
- **Repository**: GitHub issues

## Version History

**v1.0.0** (January 11, 2026)
- Initial release
- Basic tree visualization
- Expand/collapse functionality
- Color-coded nodes
- Responsive design
- Click to open form

---

Last Updated: January 11, 2026
Module Version: 18.0.1.0.0
