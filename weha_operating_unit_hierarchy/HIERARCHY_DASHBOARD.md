# Operating Unit Hierarchy Dashboard

## Overview

The Hierarchy Dashboard provides a visual representation of your organization's operating unit structure in a tree format, making it easy to understand parent-child relationships and hierarchy levels.

## Features

### 1. List View (Hierarchical)
- **Visual Hierarchy**: See parent-child relationships at a glance
- **Color Coding**: 
  - 🔵 **Blue/Bold**: Head Office (HO)
  - 🔷 **Light Blue**: Distribution Centers (DC)
  - 🟢 **Green**: Stores
- **Hierarchy Path**: Full path from HO to current OU
- **Level Indicator**: Shows hierarchy level (0=HO, 1=DC, 2=Store)
- **Child Count**: Number of direct children

### 2. Kanban View
- **Mobile-Friendly**: Optimized for tablets and phones
- **Quick Overview**: See key information in card format
- **Badge Indicators**:
  - OU Type badge with color coding
  - Level badge showing hierarchy depth
- **Relationship Info**: Shows parent and number of children

### 3. Graph View
- **Distribution Analysis**: Bar chart showing OU distribution by type
- **Level Distribution**: Stacked bars showing hierarchy levels

### 4. Pivot View
- **Cross-Analysis**: Analyze OUs by type, parent, and level
- **Metrics**:
  - Child count per parent
  - Level distribution
  - OU type breakdown

## Accessing the Dashboard

### Main Menu
```
Operating Units → Hierarchy Dashboard
```

Or navigate to:
```
Operating Units → Configuration → OU Hierarchy
```

## Understanding the List View

### Example Organization Structure
```
📦 Weha Indonesia (HO) - Level 0
├── 📦 DC East (DC) - Level 1
│   ├── 🏪 Store A (Store) - Level 2
│   ├── 🏪 Store B (Store) - Level 2
│   └── 🏪 Store C (Store) - Level 2
└── 📦 DC West (DC) - Level 1
    ├── 🏪 Store D (Store) - Level 2
    └── 🏪 Store E (Store) - Level 2
```

### List View Display
```
Name             | Code    | OU Type | Level | Path                        | Children
-----------------|---------|---------|-------|-----------------------------|---------
Weha Indonesia   | HO001   | HO      | 0     | Weha Indonesia              | 2
DC East          | DC001   | DC      | 1     | Weha Indonesia / DC East    | 3
  Store A        | STR001  | Store   | 2     | ... / DC East / Store A     | 0
  Store B        | STR002  | Store   | 2     | ... / DC East / Store B     | 0
  Store C        | STR003  | Store   | 2     | ... / DC East / Store C     | 0
DC West          | DC002   | DC      | 1     | Weha Indonesia / DC West    | 2
  Store D        | STR004  | Store   | 2     | ... / DC West / Store D     | 0
  Store E        | STR005  | Store   | 2     | ... / DC West / Store E     | 0
```

## Filters and Grouping

### Available Filters
1. **Head Office**: Show only HO level OUs
2. **Distribution Center**: Show only DC level OUs
3. **Store**: Show only Store level OUs
4. **Auto Share Revenue**: Filter OUs with auto revenue sharing enabled

### Group By Options
1. **OU Type**: Group by HO, DC, Store
2. **Parent OU**: Group by parent operating unit
3. **Level**: Group by hierarchy level (0, 1, 2)

## Using the Dashboard

### View Hierarchy Structure
1. Open **Hierarchy Dashboard**
2. Tree view shows all OUs with indentation for children
3. Click on any OU to see details

### Find OUs by Level
1. Use **Group By > Level** filter
2. See all HOs (Level 0), DCs (Level 1), Stores (Level 2) separately

### Analyze Distribution
1. Switch to **Graph** view
2. See bar chart of OU distribution by type
3. Identify if hierarchy is balanced

### Find OUs by Parent
1. Use **Group By > Parent OU** filter
2. See all children grouped under each parent
3. Quickly identify which DC manages which stores

### Check Children Count
1. Look at **Children** column in tree view
2. Identifies how many direct children each OU has
3. Helps balance distribution

## View Modes

### 1. List View (Default)
Best for: Understanding full hierarchy structure

**Features**:
- Hierarchical display
- All levels visible
- Easy navigation
- Sortable columns

### 2. Kanban View
Best for: Mobile access and quick overview

**Features**:
- Card-based layout
- Color-coded badges
- Parent/children information
- Touch-friendly

### 3. Graph View
Best for: Visual analysis of distribution

**Features**:
- Bar charts
- Type distribution
- Level analysis
- Export capabilities

### 4. Pivot View
Best for: Detailed analysis and reporting

**Features**:
- Cross-tabulation
- Custom dimensions
- Measure calculations
- Export to Excel

## Examples

### Scenario 1: Check Store Distribution
**Goal**: See which DC manages which stores

**Steps**:
1. Open Hierarchy Dashboard
2. Apply filter: **Distribution Center**
3. Use Group By: **Parent OU**
4. See stores grouped under each DC

### Scenario 2: Find All Children of a DC
**Goal**: List all stores under DC East

**Steps**:
1. Open Hierarchy Dashboard
2. Search: "DC East"
3. Click on DC East
4. Go to **Hierarchy** tab
5. See **Child Operating Units** section

### Scenario 3: Verify Hierarchy Levels
**Goal**: Ensure all stores are at level 2

**Steps**:
1. Open Hierarchy Dashboard
2. Apply filter: **Store**
3. Check **Level** column
4. All should show "2"

### Scenario 4: Analyze Organization Balance
**Goal**: Check if DCs are evenly loaded

**Steps**:
1. Open Hierarchy Dashboard
2. Switch to **Graph** view
3. Look at bar heights
4. Identify unbalanced DCs

## Dashboard Statistics

The dashboard shows:
- **Total OUs**: Count of all operating units
- **By Type**: Count per type (HO, DC, Store)
- **By Level**: Distribution across levels
- **Children per Parent**: Average and max children

## Color Coding

| Color | OU Type | Level |
|-------|---------|-------|
| 🔵 Blue/Bold | Head Office | 0 |
| 🔷 Light Blue | Distribution Center | 1 |
| 🟢 Green | Store | 2 |

## Tips

### Efficient Navigation
1. Use filters to narrow down view
2. Group by parent to see structure
3. Click on OU name to open details
4. Use breadcrumbs to navigate back

### Finding Information Quickly
1. **Search bar**: Find OU by name or code
2. **Filters**: Quick access to type-specific OUs
3. **Columns**: Sort by any column
4. **Child count**: Identify parents vs. leaf nodes

### Analyzing Structure
1. **List view**: See full hierarchy
2. **Graph view**: Visual distribution
3. **Pivot view**: Detailed cross-analysis
4. **Export**: Download for external analysis

## Troubleshooting

### Issue: Dashboard shows empty
**Solution**: 
- Check if OUs exist in the system
- Clear filters (click X on search)
- Verify user has access rights

### Issue: Hierarchy looks flat
**Solution**:
- Check if parent_id is set on OUs
- Verify OU types have correct hierarchy settings
- Re-save OUs to recalculate paths
- Note: List view shows flat structure, use grouping or filters to see hierarchy

### Issue: Wrong level numbers
**Solution**:
- Verify OU type levels are correct
- Check parent-child relationships
- Update module to recalculate

### Issue: Child count is wrong
**Solution**:
- Refresh the view (F5)
- Recompute using developer mode
- Check for orphaned OUs

## Advanced Features

### Custom Hierarchy Views
You can create custom views by:
1. Saving specific filter combinations
2. Creating personal views with favorite columns
3. Sharing views with team

### Export Options
1. **Excel**: Export pivot data for analysis
2. **CSV**: Export list data for processing
3. **PDF**: Print hierarchy diagrams

### Integration
The dashboard integrates with:
- Stock request system (source OU)
- Revenue sharing (hierarchy levels)
- Access rights (OU-based security)

## Technical Details

### Fields Displayed
- `name`: Operating unit name
- `code`: OU code
- `ou_type_id`: Type (HO, DC, Store)
- `level`: Hierarchy level
- `parent_path`: Full path from HO
- `child_count`: Number of children
- `parent_id`: Parent OU

### Computed Fields
- `parent_path`: Automatically computed from parents
- `level`: Based on OU type or parent chain
- `child_count`: Count of direct children

### Performance
- Tree views are optimized for large hierarchies
- Parent paths are indexed
- Child counts are cached

## Support

For questions or issues:
1. Check this documentation
2. Review OU configuration
3. Contact: support@weha-id.com

## Updates

Last updated: January 11, 2026
Version: 18.0.1.0.0
