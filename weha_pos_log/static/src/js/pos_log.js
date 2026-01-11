/** @odoo-module **/

import { patch } from "@web/core/utils/patch";
import { PosStore } from "@point_of_sale/app/store/pos_store";
import { Order } from "@point_of_sale/app/store/models";

// Extend PosStore to add logging capabilities
patch(PosStore.prototype, {
    /**
     * Initialize logging system
     */
    async setup() {
        await super.setup(...arguments);
        this.posLogs = [];
        this.syncInterval = null;
        this.startLogSync();
    },

    /**
     * Create a log entry
     * @param {string} eventType - Type of event (login, logout, order_create, etc.)
     * @param {object} data - Additional data to log
     * @returns {object} The created log entry
     */
    createLog(eventType, data = {}) {
        const logEntry = {
            event_type: eventType,
            user_id: this.user.id,
            session_id: this.pos_session?.id || false,
            config_id: this.config?.id || false,
            description: data.description || '',
            event_data: JSON.stringify(data),
            create_date: new Date().toISOString(),
            is_synced: false,
        };

        // Add order_id if provided
        if (data.order_id) {
            logEntry.order_id = data.order_id;
        }

        // Store locally
        this.posLogs.push(logEntry);
        
        // Try to sync immediately if online
        if (this.isOnline) {
            this.syncLogs();
        }

        console.log('[POS Log]', eventType, data);
        return logEntry;
    },

    /**
     * Sync logs to server
     */
    async syncLogs() {
        const unsyncedLogs = this.posLogs.filter(log => !log.is_synced);
        
        if (unsyncedLogs.length === 0) {
            return;
        }

        try {
            const result = await this.orm.call(
                'pos.log',
                'sync_logs_from_pos',
                [unsyncedLogs]
            );

            // Mark logs as synced
            if (result.success > 0) {
                unsyncedLogs.forEach(log => {
                    log.is_synced = true;
                    log.sync_date = new Date().toISOString();
                });
                console.log(`[POS Log] Synced ${result.success}/${result.total} logs`);
            }

            // Clean up old synced logs (keep last 1000)
            const syncedLogs = this.posLogs.filter(log => log.is_synced);
            if (syncedLogs.length > 1000) {
                this.posLogs = this.posLogs.slice(-1000);
            }
        } catch (error) {
            console.error('[POS Log] Sync failed:', error);
        }
    },

    /**
     * Start periodic log sync
     */
    startLogSync() {
        // Sync every 5 minutes
        this.syncInterval = setInterval(() => {
            if (this.isOnline) {
                this.syncLogs();
            }
        }, 5 * 60 * 1000);
    },

    /**
     * Stop log sync
     */
    stopLogSync() {
        if (this.syncInterval) {
            clearInterval(this.syncInterval);
            this.syncInterval = null;
        }
    },

    /**
     * Get unsynced logs count
     */
    getUnsyncedLogsCount() {
        return this.posLogs.filter(log => !log.is_synced).length;
    },

    /**
     * Override close_pos to sync logs before closing
     */
    async closePos() {
        // Sync any remaining logs
        await this.syncLogs();
        this.stopLogSync();
        return super.closePos(...arguments);
    },
});

// Patch Order model to log order events
patch(Order.prototype, {
    constructor() {
        super.constructor(...arguments);
        
        // Log order creation
        if (this.pos) {
            this.pos.createLog('order_create', {
                order_id: this.id,
                description: `Order ${this.name} created`,
            });
        }
    },

    /**
     * Log payment
     */
    add_paymentline(payment_method) {
        const result = super.add_paymentline(...arguments);
        
        if (this.pos && result) {
            this.pos.createLog('payment', {
                order_id: this.id,
                description: `Payment added: ${payment_method.name}`,
                payment_method: payment_method.name,
                payment_method_id: payment_method.id,
            });
        }
        
        return result;
    },

    /**
     * Log order finalization
     */
    finalize() {
        const result = super.finalize(...arguments);
        
        if (this.pos) {
            this.pos.createLog('order_paid', {
                order_id: this.id,
                description: `Order ${this.name} finalized`,
                amount: this.get_total_with_tax(),
            });
        }
        
        return result;
    },
});

// Log cashier login when session starts
patch(PosStore.prototype, {
    async _loadPosSession() {
        const result = await super._loadPosSession(...arguments);
        
        if (result && this.pos_session) {
            this.createLog('session_open', {
                description: `Session ${this.pos_session.name} opened`,
            });
            
            this.createLog('login', {
                description: `Cashier ${this.user.name} logged in`,
            });
        }
        
        return result;
    },

    /**
     * Log session closing
     */
    async closeSession() {
        this.createLog('session_close', {
            description: `Session ${this.pos_session.name} closing`,
        });
        
        this.createLog('logout', {
            description: `Cashier ${this.user.name} logged out`,
        });
        
        // Sync logs before closing
        await this.syncLogs();
        
        return super.closeSession(...arguments);
    },
});
