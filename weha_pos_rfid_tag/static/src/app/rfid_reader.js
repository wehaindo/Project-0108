/** @odoo-module */

import { Component, useState } from "@odoo/owl";
import { useService } from "@web/core/utils/hooks";
import { usePos } from "@point_of_sale/app/store/pos_hook";

/**
 * RFID Reader Status Component
 * Displays connection status and allows manual connect/disconnect
 */
export class RfidReader extends Component {
    static template = "weha_pos_rfid_tag.RfidReader";
    
    setup() {
        this.pos = usePos();
        this.rfid = useService("rfid");
        this.notification = useService("notification");
        
        this.state = useState({
            connected: false,
            lastTag: null,
            tagCount: 0,
        });
        
        // Listen to RFID events
        this.removeListener = this.rfid.addEventListener((event, data) => {
            if (event === 'connected') {
                this.state.connected = true;
            } else if (event === 'disconnected') {
                this.state.connected = false;
            } else if (event === 'tag_read') {
                this.onTagRead(data);
            }
        });
        
        // Update initial connection state
        this.state.connected = this.rfid.isConnected();
    }
    
    willUnmount() {
        if (this.removeListener) {
            this.removeListener();
        }
    }
    
    /**
     * Handle tag read event
     */
    async onTagRead(rfidTag) {
        console.log('[RFID Reader] Tag read:', rfidTag);
        
        this.state.lastTag = rfidTag;
        this.state.tagCount++;
        
        // Get RFID tag info and product
        const tagInfo = this.pos.getRfidTagInfo(rfidTag);
        
        if (tagInfo && tagInfo.product) {
            const product = tagInfo.product;
            
            try {
                // Add product to cart
                const currentOrder = this.pos.get_order();
                if (currentOrder) {
                    await currentOrder.add_product(product, {
                        quantity: 1,
                    });
                    
                    this.notification.add(`Added: ${product.display_name}`, {
                        type: 'success',
                        sticky: false,
                    });
                    
                    // Update scan info on server
                    this.updateScanInfo(tagInfo.id);
                }
            } catch (error) {
                console.error('[RFID Reader] Error adding product:', error);
                this.notification.add('Error adding product to cart', {
                    type: 'danger',
                });
            }
        } else {
            this.notification.add(`Unknown RFID tag: ${rfidTag}`, {
                type: 'warning',
            });
        }
    }
    
    /**
     * Update scan info on server
     */
    async updateScanInfo(tagId) {
        try {
            await this.pos.env.services.orm.call(
                'product.rfid.tag',
                'update_scan_info',
                [[tagId]]
            );
        } catch (error) {
            console.error('[RFID Reader] Error updating scan info:', error);
        }
    }
    
    /**
     * Toggle connection
     */
    toggleConnection() {
        if (this.state.connected) {
            this.rfid.disconnect();
        } else {
            this.rfid.connect();
        }
    }
    
    /**
     * Get status class
     */
    get statusClass() {
        return this.state.connected ? 'connected' : 'disconnected';
    }
    
    /**
     * Get status text
     */
    get statusText() {
        return this.state.connected ? 'Connected' : 'Disconnected';
    }
    
    /**
     * Get button text
     */
    get buttonText() {
        return this.state.connected ? 'Disconnect' : 'Connect';
    }
}
