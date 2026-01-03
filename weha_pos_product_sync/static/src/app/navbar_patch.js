/** @odoo-module **/

import { Navbar } from "@point_of_sale/app/navbar/navbar";
import { patch } from "@web/core/utils/patch";
import { ProductSyncButton } from "./sync_button";

patch(Navbar.prototype, {
    get showProductSync() {
        try {
            return this.pos?.config?.enable_local_product_storage || false;
        } catch (error) {
            console.warn('[Navbar Patch] Error accessing pos config:', error);
            return false;
        }
    }
});

Navbar.components = { ...Navbar.components, ProductSyncButton };
