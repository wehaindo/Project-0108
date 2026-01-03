/** @odoo-module **/

import { Component, useState } from "@odoo/owl";
import { useService } from "@web/core/utils/hooks";

export class ProductSyncButton extends Component {
    static template = "weha_pos_product_sync.ProductSyncButton";
    static props = {};

    setup() {
        try {
            this.pos = useService("pos");
            this.notification = useService("notification");
        } catch (error) {
            console.warn('[Sync Button] Services not available:', error);
            this.pos = null;
            this.notification = null;
        }
        
        this.state = useState({
            showDetails: false,
            syncRequired: null,
            productCount: 0
        });

        // Check sync status on mount (only if services are available)
        if (this.pos && this.notification) {
            this.checkSyncStatus();
        }
    }

    get isEnabled() {
        return this.pos?.config?.enable_local_product_storage || false;
    }

    get syncStatus() {
        if (!this.isEnabled) {
            return { is_syncing: false, last_sync_date: null, local_storage_enabled: false, all_products_loaded: false };
        }
        return this.pos.getSyncStatus();
    }

    get lastSyncFormatted() {
        if (!this.syncStatus.last_sync_date) {
            return "Never";
        }
        const date = new Date(this.syncStatus.last_sync_date);
        return date.toLocaleString();
    }

    get syncStatusIcon() {
        if (this.syncStatus.is_syncing) {
            return "fa fa-spinner fa-spin";
        }
        if (this.state.syncRequired?.sync_required) {
            return "fa fa-exclamation-triangle text-warning";
        }
        if (this.syncStatus.last_sync_date) {
            return "fa fa-check-circle text-success";
        }
        return "fa fa-cloud";
    }

    get syncStatusText() {
        if (this.syncStatus.is_syncing) {
            return "Syncing...";
        }
        if (this.state.syncRequired?.sync_required) {
            return `${this.state.syncRequired.modified_count || 0} updates available`;
        }
        if (this.syncStatus.last_sync_date) {
            return "Up to date";
        }
        return "Not synced";
    }

    async checkSyncStatus() {
        if (!this.isEnabled || !this.pos || !this.pos.checkSyncRequired) {
            return;
        }

        try {
            const result = await this.pos.checkSyncRequired();
            this.state.syncRequired = result;
            
            // Get local product count
            if (this.pos.productStorage) {
                this.state.productCount = await this.pos.productStorage.getProductCount();
            }
        } catch (error) {
            console.error('[Sync Button] Error checking sync status:', error);
        }
    }

    toggleDetails() {
        this.state.showDetails = !this.state.showDetails;
        if (this.state.showDetails) {
            this.checkSyncStatus();
        }
    }

    async onClickSync(forceFull = false) {
        if (!this.notification || !this.pos) {
            console.warn('[Sync Button] Services not available');
            return;
        }
        
        if (this.syncStatus.is_syncing) {
            this.notification.add("Sync already in progress", { type: "warning" });
            return;
        }

        const syncType = forceFull ? "Full sync" : "Incremental sync";
        this.notification.add(`Starting ${syncType.toLowerCase()}...`, { type: "info" });

        try {
            const result = await this.pos.manualSync(forceFull);
            
            if (result.success) {
                this.notification.add(result.message, { type: "success" });
                await this.checkSyncStatus();
            } else {
                this.notification.add(result.message, { type: "warning" });
            }
        } catch (error) {
            this.notification.add("Sync failed: " + error.message, { type: "danger" });
        }
    }

    async onClickFullSync() {
        if (!confirm("Full sync will reload all products from the server. This may take a while. Continue?")) {
            return;
        }
        await this.onClickSync(true);
    }

    async onClickClearDB() {
        if (!this.notification || !this.pos) {
            console.warn('[Sync Button] Services not available');
            return;
        }
        
        if (!confirm("Are you sure you want to clear the local product database? This will reload all products from the server.")) {
            return;
        }

        this.notification.add("Clearing local database...", { type: "info" });

        try {
            const result = await this.pos.clearLocalProductDB();
            
            if (result.success) {
                this.notification.add(result.message, { type: "success" });
                this.state.productCount = 0;
                this.state.syncRequired = null;
            } else {
                this.notification.add(result.message, { type: "danger" });
            }
        } catch (error) {
            this.notification.add("Failed to clear database: " + error.message, { type: "danger" });
        }
    }
}
