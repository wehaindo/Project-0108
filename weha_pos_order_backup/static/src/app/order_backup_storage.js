/** @odoo-module **/

/**
 * Order Backup Storage using IndexedDB
 * Stores validated POS orders as backup
 */

export class OrderBackupStorage {
    constructor(configId) {
        this.configId = configId;
        this.dbName = `pos_order_backup_${configId}`;
        this.dbVersion = 1;
        this.db = null;
        this.storeName = 'orders';
    }

    /**
     * Initialize IndexedDB for order backup
     */
    async init() {
        return new Promise((resolve, reject) => {
            const request = indexedDB.open(this.dbName, this.dbVersion);

            request.onerror = () => reject(request.error);
            request.onsuccess = () => {
                this.db = request.result;
                resolve(this.db);
            };

            request.onupgradeneeded = (event) => {
                const db = event.target.result;

                // Orders backup store
                if (!db.objectStoreNames.contains(this.storeName)) {
                    const objectStore = db.createObjectStore(this.storeName, { keyPath: 'uid' });
                    objectStore.createIndex('pos_reference', 'pos_reference', { unique: false });
                    objectStore.createIndex('date_order', 'date_order', { unique: false });
                    objectStore.createIndex('backup_date', 'backup_date', { unique: false });
                    objectStore.createIndex('synced', 'synced', { unique: false });
                }
            };
        });
    }

    /**
     * Save order backup to IndexedDB
     */
    async saveOrderBackup(orderData) {
        if (!this.db) await this.init();

        return new Promise((resolve, reject) => {
            const transaction = this.db.transaction([this.storeName], 'readwrite');
            const store = transaction.objectStore(this.storeName);

            // Add backup metadata
            const backupData = {
                ...orderData,
                backup_date: new Date().toISOString(),
                synced: false,
                config_id: this.configId
            };

            const request = store.put(backupData);

            request.onsuccess = () => {
                console.log('[Order Backup] Saved:', orderData.uid);
                resolve(backupData);
            };
            request.onerror = () => reject(request.error);
        });
    }

    /**
     * Get all unsynced order backups
     */
    async getUnsyncedBackups() {
        if (!this.db) await this.init();

        return new Promise((resolve, reject) => {
            const transaction = this.db.transaction([this.storeName], 'readonly');
            const store = transaction.objectStore(this.storeName);
            const request = store.getAll();

            request.onsuccess = () => {
                const allBackups = request.result;
                const unsynced = allBackups.filter(backup => backup.synced === false);
                resolve(unsynced);
            };
            request.onerror = () => reject(request.error);
        });
    }

    /**
     * Mark backup as synced
     */
    async markAsSynced(orderUid) {
        if (!this.db) await this.init();

        return new Promise((resolve, reject) => {
            const transaction = this.db.transaction([this.storeName], 'readwrite');
            const store = transaction.objectStore(this.storeName);
            const getRequest = store.get(orderUid);

            getRequest.onsuccess = () => {
                const data = getRequest.result;
                if (data) {
                    data.synced = true;
                    data.sync_date = new Date().toISOString();
                    const updateRequest = store.put(data);
                    updateRequest.onsuccess = () => resolve(true);
                    updateRequest.onerror = () => reject(updateRequest.error);
                } else {
                    resolve(false);
                }
            };
            getRequest.onerror = () => reject(getRequest.error);
        });
    }

    /**
     * Get all backups
     */
    async getAllBackups() {
        if (!this.db) await this.init();

        return new Promise((resolve, reject) => {
            const transaction = this.db.transaction([this.storeName], 'readonly');
            const store = transaction.objectStore(this.storeName);
            const request = store.getAll();

            request.onsuccess = () => resolve(request.result);
            request.onerror = () => reject(request.error);
        });
    }

    /**
     * Get backup by UID
     */
    async getBackup(orderUid) {
        if (!this.db) await this.init();

        return new Promise((resolve, reject) => {
            const transaction = this.db.transaction([this.storeName], 'readonly');
            const store = transaction.objectStore(this.storeName);
            const request = store.get(orderUid);

            request.onsuccess = () => resolve(request.result);
            request.onerror = () => reject(request.error);
        });
    }

    /**
     * Delete backup
     */
    async deleteBackup(orderUid) {
        if (!this.db) await this.init();

        return new Promise((resolve, reject) => {
            const transaction = this.db.transaction([this.storeName], 'readwrite');
            const store = transaction.objectStore(this.storeName);
            const request = store.delete(orderUid);

            request.onsuccess = () => resolve(true);
            request.onerror = () => reject(request.error);
        });
    }

    /**
     * Get backup count
     */
    async getBackupCount() {
        if (!this.db) await this.init();

        return new Promise((resolve, reject) => {
            const transaction = this.db.transaction([this.storeName], 'readonly');
            const store = transaction.objectStore(this.storeName);
            const request = store.count();

            request.onsuccess = () => resolve(request.result);
            request.onerror = () => reject(request.error);
        });
    }

    /**
     * Clear all backups
     */
    async clearAll() {
        if (!this.db) await this.init();

        return new Promise((resolve, reject) => {
            const transaction = this.db.transaction([this.storeName], 'readwrite');
            const store = transaction.objectStore(this.storeName);
            const request = store.clear();

            request.onsuccess = () => resolve();
            request.onerror = () => reject(request.error);
        });
    }
}
