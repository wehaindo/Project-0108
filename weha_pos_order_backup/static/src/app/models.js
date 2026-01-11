/** @odoo-module **/

import { PosStore } from "@point_of_sale/app/store/pos_store";
import { PaymentScreen } from "@point_of_sale/app/screens/payment_screen/payment_screen";
import { ReceiptScreen } from "@point_of_sale/app/screens/receipt_screen/receipt_screen";
import { patch } from "@web/core/utils/patch";
import { OrderBackupStorage } from "./order_backup_storage";

patch(PosStore.prototype, {
    async afterProcessServerData() {
        await super.afterProcessServerData(...arguments);
        
        console.log('[Order Backup] Initializing backup system');
        
        // Initialize order backup storage
        this.orderBackupStorage = new OrderBackupStorage(this.config.id);
        await this.orderBackupStorage.init();
        
        console.log('[Order Backup] Database initialized:', this.orderBackupStorage.dbName);
        
        // Sync any unsynced backups immediately
        setTimeout(() => this.syncOrderBackups(), 3000);
        
        // Auto sync every 30 seconds
        this.orderBackupSyncInterval = setInterval(() => this.syncOrderBackups(), 30000);
    },

    async _flush_orders(orders) {
        console.log('[Order Backup] _flush_orders called with', orders.length, 'orders');
        
        // Continue with normal order flush
        return await super._flush_orders(...arguments);
    },

    /**
     * Sync order backups to server
     */
    async syncOrderBackups() {
        try {
            const unsyncedBackups = await this.orderBackupStorage.getUnsyncedBackups();
            
            if (unsyncedBackups.length === 0) {
                console.log('[Order Backup] No backups to sync');
                return;
            }

            console.log(`[Order Backup] Syncing ${unsyncedBackups.length} backups to server`);
            console.log('[Order Backup] Session ID:', this.config.current_session_id.id);

            const result = await this.data.call(
                'pos.session',
                'sync_order_backups',
                [unsyncedBackups]
            );

            // Mark synced backups
            for (const accessToken of result.success) {
                await this.orderBackupStorage.markAsSynced(accessToken);
            }

            console.log(`[Order Backup] Synced: ${result.success.length}, Failed: ${result.failed.length}, Duplicates: ${result.duplicates.length}`);

            if (result.failed.length > 0) {
                console.error('[Order Backup] Failed syncs:', result.failed);
            }

        } catch (error) {
            console.error('[Order Backup] Sync error:', error);
            console.log('[Order Backup] Will retry in 10 seconds...');
            setTimeout(() => this.syncOrderBackups(), 10000);
        }
    },

    
    /**
     * Get backup statistics
     */
    async getBackupStats() {
        try {
            const count = await this.orderBackupStorage.getBackupCount();
            const unsynced = await this.orderBackupStorage.getUnsyncedBackups();
            
            return {
                total: count,
                unsynced: unsynced.length,
                synced: count - unsynced.length
            };
        } catch (error) {
            console.error('[Order Backup] Stats error:', error);
            return { total: 0, unsynced: 0, synced: 0 };
        }
    }
});

// Patch PaymentScreen to save backup after order validation
patch(PaymentScreen.prototype, {
    // async validateOrder(isForceValidate) {
    //     const order = this.pos.get_order();
    //     await super.validateOrder(...arguments);
        
    //     // Save backup after validation
    //     if (this.currentOrder && this.currentOrder.finalized) {
    //         try {
    //             console.log('[Order Backup] Saving backup for order:', order.pos_reference);
                
    //             // Prepare order for sync and serialize
    //             await this.pos.preSyncAllOrders([order]);
    //             order.recomputeOrderData();
    //             const serialized = order.serialize({ orm: true });
                
    //             // Get full line data
    //             const linesData = order.lines.map(line => [0, 0, line.serialize({ orm: true })]);
                
    //             // Get full payment data
    //             const paymentsData = order.payment_ids.map(payment => [0, 0, payment.serialize({ orm: true })]);
                
    //             // Create new order data object with full details
    //             const orderData = {
    //                 ...serialized,
    //                 lines: linesData,
    //                 payment_ids: paymentsData
    //             };
                
    //             // Calculate data size
    //             const dataString = JSON.stringify(orderData);
    //             const dataSize = dataString.length;
    //             const dataSizeKB = (dataSize / 1024).toFixed(2);
                
    //             console.log('[Order Backup] Order data:', orderData);
    //             console.log('[Order Backup] Data size:', dataSizeKB, 'KB');
                
    //             // Ensure uid exists (use either uid, pos_reference, or id)
    //             if (!orderData.uid) {
    //                 orderData.uid = orderData.pos_reference || orderData.id || order.uid;
    //             }
                
    //             console.log('[Order Backup] Order validated, saving backup:', orderData.uid || orderData.pos_reference);
    //             await this.pos.orderBackupStorage.saveOrderBackup(orderData);
    //             console.log('[Order Backup] Order backed up successfully:', orderData.uid || orderData.pos_reference);
    //         } catch (error) {
    //             console.error('[Order Backup] Backup failed:', error);
    //         }
    //     }
    // },

    async _finalizeValidation() {
        console.log('[Order Backup] _finalizeValidation called');
        console.log('[Order Backup] Current order:', this.currentOrder);
        
        // Call parent finalization first to ensure order is fully processed
        await super._finalizeValidation(...arguments);
        
        // Now serialize the finalized order with access_token
        const orderData = this.currentOrder.serialize({ orm: true });
        
        // Ensure access_token exists (required for IndexedDB key)
        if (!orderData.access_token) {
            orderData.access_token = this.currentOrder.access_token || this.currentOrder.uid || orderData.pos_reference;
        }
        
        console.log('[Order Backup] Saving backup for order with access_token:', orderData.access_token);
        
        try {
            await this.pos.orderBackupStorage.saveOrderBackup(orderData);
            console.log('[Order Backup] Order backup saved successfully (receipt will be captured on receipt screen)');
        } catch (error) {
            console.error('[Order Backup] Failed to save backup:', error);
        }
    }       
});

// Patch ReceiptScreen to capture receipt HTML when print button is clicked
patch(ReceiptScreen.prototype, {
    setup() {
        super.setup(...arguments);
        
        // Wrap the doFullPrint method
        const originalDoFullPrint = this.doFullPrint;
        this.doFullPrint = {
            ...originalDoFullPrint,
            call: async () => {
                console.log('[Order Backup] Print Full Receipt button clicked, capturing receipt...');
                await this.captureReceiptForBackup();
                return await originalDoFullPrint.call();
            }
        };
        
        // Wrap the doBasicPrint method if it exists
        if (this.doBasicPrint) {
            const originalDoBasicPrint = this.doBasicPrint;
            this.doBasicPrint = {
                ...originalDoBasicPrint,
                call: async () => {
                    console.log('[Order Backup] Print Basic Receipt button clicked, capturing receipt...');
                    await this.captureReceiptForBackup();
                    return await originalDoBasicPrint.call();
                }
            };
        }
    },
    
    async captureReceiptForBackup() {
        console.log('[Order Backup] Starting receipt capture...');
        try {
            const order = this.currentOrder;
            if (!order) {
                console.log('[Order Backup] No current order');
                return;
            }
            
            console.log('[Order Backup] Current order:', order.pos_reference || order.uid);
            
            // Find the receipt element in the DOM
            const receiptElement = document.querySelector('.pos-receipt-container .pos-receipt') || 
                                 document.querySelector('.receipt-screen .pos-receipt') ||
                                 document.querySelector('.order-receipt');
            
            if (!receiptElement) {
                console.warn('[Order Backup] Receipt element not found in DOM');
                console.log('[Order Backup] Available elements:', {
                    'pos-receipt-container': !!document.querySelector('.pos-receipt-container'),
                    'receipt-screen': !!document.querySelector('.receipt-screen'),
                    'order-receipt': !!document.querySelector('.order-receipt'),
                });
                return;
            }
            
            console.log('[Order Backup] Receipt element found');
            
            // Clone the element to capture all styles
            const clone = receiptElement.cloneNode(true);
            
            // Get computed styles and embed them inline
            let styleString = '<style>';
            
            // Capture all POS receipt styles
            const styleSheets = document.styleSheets;
            for (let sheet of styleSheets) {
                try {
                    const rules = sheet.cssRules || sheet.rules;
                    for (let rule of rules) {
                        if (rule.selectorText && rule.selectorText.includes('pos-receipt')) {
                            styleString += rule.cssText + '\n';
                        }
                    }
                } catch (e) {
                    // Skip cross-origin stylesheets
                }
            }
            styleString += '</style>';
            
            // Combine styles with cloned HTML
            const receiptHtml = styleString + clone.outerHTML;
            
            console.log('[Order Backup] Receipt HTML captured from DOM, length:', receiptHtml.length);
            
            // Update the backup with receipt HTML
            const accessToken = order.access_token || order.uid;
            console.log('[Order Backup] Updating backup with access_token:', accessToken);
            
            await this.pos.orderBackupStorage.updateBackupReceipt(accessToken, receiptHtml);
            
            console.log('[Order Backup] Receipt HTML saved to backup successfully');
            
        } catch (error) {
            console.error('[Order Backup] Failed to capture receipt:', error);
        }
    }
});
