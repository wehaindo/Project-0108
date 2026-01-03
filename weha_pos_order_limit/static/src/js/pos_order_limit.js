/** @odoo-module **/

import { patch } from "@web/core/utils/patch";
import { PosStore } from "@point_of_sale/app/store/pos_store";
import { OrderTabs } from "@point_of_sale/app/components/order_tabs/order_tabs";

// Patch PosStore to add order limit functionality
patch(PosStore.prototype, {
    // Override add_new_order method
    async addNewOrder() {
        const config = this.config;
        
        // Check if order limit is enabled
        if (config.enable_order_limit) {
            const currentOrderCount = this.models["pos.order"].filter((o) => !o.finalized).length;
            
            if (currentOrderCount >= config.max_orders) {
                this.env.services.notification.add(
                    `Order limit reached. Maximum ${config.max_orders} orders allowed.`,
                    { type: "warning" }
                );
                return;
            }
        }
        
        // Call the parent method if limit is not reached
        return await super.addNewOrder(...arguments);
    },
    
    // Method to check if add order button should be visible
    canAddNewOrder() {
        const config = this.config;
        
        // Check if button should be hidden
        if (config.hide_add_order_button) {
            return false;
        }
        
        // Check if order limit is enabled and reached
        if (config.enable_order_limit) {
            const currentOrderCount = this.models["pos.order"].filter((o) => !o.finalized).length;
            return currentOrderCount < config.max_orders;
        }
        
        return true;
    }
});

// Patch OrderTabs to conditionally show add order button
patch(OrderTabs.prototype, {
    get shouldShowAddButton() {
        return this.pos.canAddNewOrder();
    }
});
