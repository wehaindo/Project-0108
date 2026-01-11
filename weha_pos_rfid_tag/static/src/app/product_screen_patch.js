/** @odoo-module */

import { patch } from "@web/core/utils/patch";
import { ProductScreen } from "@point_of_sale/app/screens/product_screen/product_screen";
import { PosStore } from "@point_of_sale/app/store/pos_store";
import { RfidReader } from "./rfid_reader";

/**
 * Patch ProductScreen to add RFID Reader component
 */
patch(ProductScreen.prototype, {
    get components() {
        return {
            ...super.components,
            RfidReader,
        };
    },
});

/**
 * Patch PosStore to load RFID tags and create lookup index
 */
patch(PosStore.prototype, {
    /**
     * Override after_load_server_data to load RFID tags
     */
    async after_load_server_data() {
        await super.after_load_server_data(...arguments);
        await this._loadRfidTags();
    },
    
    /**
     * Load RFID tags from server
     */
    async _loadRfidTags() {
        try {
            console.log('[RFID] Loading RFID tags...');
            
            // Load all active RFID tags
            const rfidTags = await this.env.services.orm.searchRead(
                'product.rfid.tag',
                [['status', '=', 'active']],
                ['name', 'product_id'],
                { limit: 10000 }
            );
            
            // Create RFID tag lookup index
            this.db.rfid_tag_by_name = {};
            
            for (const tag of rfidTags) {
                const productId = tag.product_id[0];
                const product = this.db.get_product_by_id(productId);
                
                if (product) {
                    this.db.rfid_tag_by_name[tag.name] = {
                        id: tag.id,
                        name: tag.name,
                        product: product,
                        product_id: productId
                    };
                }
            }
            
            console.log(`[RFID] Loaded ${Object.keys(this.db.rfid_tag_by_name).length} active RFID tags`);
            
        } catch (error) {
            console.error('[RFID] Error loading RFID tags:', error);
        }
    },
    
    /**
     * Get product by RFID tag name
     */
    getProductByRfidTag(tagName) {
        const tagInfo = this.db.rfid_tag_by_name?.[tagName];
        return tagInfo ? tagInfo.product : null;
    },
    
    /**
     * Get RFID tag info by tag name
     */
    getRfidTagInfo(tagName) {
        return this.db.rfid_tag_by_name?.[tagName] || null;
    },
});
