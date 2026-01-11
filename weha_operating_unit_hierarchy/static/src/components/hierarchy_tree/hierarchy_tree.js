/** @odoo-module **/

import { Component, useState, onWillStart } from "@odoo/owl";
import { registry } from "@web/core/registry";
import { useService } from "@web/core/utils/hooks";

/**
 * Operating Unit Hierarchy Tree Component
 * 
 * Displays operating units in an interactive tree structure with:
 * - Expandable/collapsible nodes
 * - Color coding by OU type
 * - Click to view details
 * - Visual hierarchy representation
 */
export class HierarchyTreeComponent extends Component {
    setup() {
        this.orm = useService("orm");
        this.action = useService("action");
        
        this.state = useState({
            rootNodes: [],
            allNodes: [],
            expandedNodes: new Set(),
            loading: true,
            searchQuery: '',
            filteredRootNodes: [],
        });

        onWillStart(async () => {
            await this.loadHierarchyData();
        });
    }

    /**
     * Load hierarchy data from backend
     */
    async loadHierarchyData() {
        try {
            const operatingUnits = await this.orm.searchRead(
                "operating.unit",
                [],
                ["id", "name", "code", "ou_type_id", "parent_id", "child_ids", "level", "parent_path"],
                { order: "parent_path" }
            );

            // Build tree structure
            const nodeMap = {};
            const rootNodes = [];

            // First pass: create all nodes
            operatingUnits.forEach(ou => {
                nodeMap[ou.id] = {
                    id: ou.id,
                    name: ou.name,
                    code: ou.code,
                    ou_type: ou.ou_type_id ? ou.ou_type_id[1] : '',
                    ou_type_code: this.getOUTypeCode(ou.ou_type_id ? ou.ou_type_id[1] : ''),
                    level: ou.level,
                    parent_path: ou.parent_path,
                    parent_id: ou.parent_id ? ou.parent_id[0] : null,
                    children: [],
                    child_count: ou.child_ids.length,
                };
            });

            // Second pass: build parent-child relationships
            Object.values(nodeMap).forEach(node => {
                if (node.parent_id && nodeMap[node.parent_id]) {
                    nodeMap[node.parent_id].children.push(node);
                } else if (!node.parent_id) {
                    rootNodes.push(node);
                }
            });

            this.state.rootNodes = rootNodes;
            this.state.allNodes = Object.values(nodeMap);
            this.state.filteredRootNodes = rootNodes;
            this.state.loading = false;

            // Auto-expand root nodes
            rootNodes.forEach(node => {
                this.state.expandedNodes.add(node.id);
            });
        } catch (error) {
            console.error("Error loading hierarchy data:", error);
            this.state.loading = false;
        }
    }

    /**
     * Get OU type code from full name
     */
    getOUTypeCode(ouTypeName) {
        if (ouTypeName.includes('HO') || ouTypeName.includes('Head Office')) return 'HO';
        if (ouTypeName.includes('DC') || ouTypeName.includes('Distribution')) return 'DC';
        if (ouTypeName.includes('Store') || ouTypeName.includes('STORE')) return 'STORE';
        return 'OTHER';
    }

    /**
     * Get CSS class for OU type
     */
    getOUTypeClass(ouTypeCode) {
        switch (ouTypeCode) {
            case 'HO':
                return 'ou-type-ho';
            case 'DC':
                return 'ou-type-dc';
            case 'STORE':
                return 'ou-type-store';
            default:
                return 'ou-type-other';
        }
    }

    /**
     * Get icon for OU type
     */
    getOUTypeIcon(ouTypeCode) {
        switch (ouTypeCode) {
            case 'HO':
                return 'fa-building';
            case 'DC':
                return 'fa-warehouse';
            case 'STORE':
                return 'fa-store';
            default:
                return 'fa-circle';
        }
    }

    /**
     * Toggle node expansion
     */
    toggleNode(nodeId) {
        if (this.state.expandedNodes.has(nodeId)) {
            this.state.expandedNodes.delete(nodeId);
        } else {
            this.state.expandedNodes.add(nodeId);
        }
    }

    /**
     * Check if node is expanded
     */
    isExpanded(nodeId) {
        return this.state.expandedNodes.has(nodeId);
    }

    /**
     * Open OU form view
     */
    async openOUForm(ouId) {
        this.action.doAction({
            type: 'ir.actions.act_window',
            res_model: 'operating.unit',
            res_id: ouId,
            views: [[false, 'form']],
            target: 'current',
        });
    }

    /**
     * Expand all nodes
     */
    expandAll() {
        const expandRecursive = (nodes) => {
            nodes.forEach(node => {
                this.state.expandedNodes.add(node.id);
                if (node.children.length > 0) {
                    expandRecursive(node.children);
                }
            });
        };
        expandRecursive(this.state.rootNodes);
    }

    /**
     * Collapse all nodes except root
     */
    collapseAll() {
        this.state.expandedNodes.clear();
        this.state.rootNodes.forEach(node => {
            this.state.expandedNodes.add(node.id);
        });
    }

    /**
     * Refresh data
     */
    async refresh() {
        this.state.loading = true;
        this.state.searchQuery = '';
        await this.loadHierarchyData();
    }

    /**
     * Search operating units by name
     */
    onSearchInput(event) {
        const query = event.target.value.toLowerCase();
        this.state.searchQuery = query;
        
        if (!query) {
            this.state.filteredRootNodes = this.state.rootNodes;
            return;
        }

        // Filter nodes that match search
        const matchingNodes = this.state.allNodes.filter(node => 
            node.name.toLowerCase().includes(query) || 
            node.code.toLowerCase().includes(query)
        );

        if (matchingNodes.length === 0) {
            this.state.filteredRootNodes = [];
            return;
        }

        // Build filtered tree with matching nodes and their ancestors
        const matchingIds = new Set(matchingNodes.map(n => n.id));
        const ancestorIds = new Set();

        // Get all ancestors of matching nodes
        matchingNodes.forEach(node => {
            let current = node;
            while (current.parent_id) {
                ancestorIds.add(current.parent_id);
                current = this.state.allNodes.find(n => n.id === current.parent_id);
                if (!current) break;
            }
        });

        // Auto-expand matching nodes and ancestors
        matchingNodes.forEach(node => {
            this.state.expandedNodes.add(node.id);
            if (node.parent_id) {
                ancestorIds.forEach(id => this.state.expandedNodes.add(id));
            }
        });

        // Filter tree to show only relevant nodes
        const filteredNodeMap = {};
        this.state.allNodes.forEach(node => {
            if (matchingIds.has(node.id) || ancestorIds.has(node.id)) {
                filteredNodeMap[node.id] = {
                    ...node,
                    children: node.children.filter(child => 
                        matchingIds.has(child.id) || ancestorIds.has(child.id)
                    )
                };
            }
        });

        const filteredRootNodes = [];
        Object.values(filteredNodeMap).forEach(node => {
            if (!node.parent_id || !filteredNodeMap[node.parent_id]) {
                filteredRootNodes.push(node);
            }
        });

        this.state.filteredRootNodes = filteredRootNodes;
    }

    /**
     * Clear search
     */
    clearSearch() {
        this.state.searchQuery = '';
        this.state.filteredRootNodes = this.state.rootNodes;
    }
}

HierarchyTreeComponent.template = "weha_operating_unit_hierarchy.HierarchyTreeTemplate";
HierarchyTreeComponent.props = {};

// Register as a view
registry.category("actions").add("hierarchy_tree_dashboard", HierarchyTreeComponent);
