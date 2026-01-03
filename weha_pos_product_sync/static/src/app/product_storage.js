/** @odoo-module **/

/**
 * IndexedDB Product Storage Manager
 * Handles local storage of products for offline-first POS loading
 */

export class ProductStorage {
    constructor(posId) {
        this.posId = posId;
        this.dbName = `pos_products_${posId}`;
        this.dbVersion = 2; // Increment version for schema changes
        this.db = null;
        
        // Define all stores for product-related models
        this.stores = {
            'product.product': 'products',
            'product.template': 'product_templates',
            'product.category': 'product_categories',
            'product.pricelist': 'pricelists',
            'product.pricelist.item': 'pricelist_items',
            'product.packaging': 'product_packaging',
            'product.tag': 'product_tags',
            'product.attribute': 'product_attributes',
            'product.attribute.value': 'product_attribute_values',
            'product.template.attribute.line': 'product_template_attribute_lines',
            'product.template.attribute.value': 'product_template_attribute_values'
        };
        
        this.metaStoreName = 'metadata';
    }

    /**
     * Initialize IndexedDB with all product-related stores
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

                // Create object stores for each model
                for (const [modelName, storeName] of Object.entries(this.stores)) {
                    if (!db.objectStoreNames.contains(storeName)) {
                        const objectStore = db.createObjectStore(storeName, { keyPath: 'id' });
                        objectStore.createIndex('write_date', 'write_date', { unique: false });
                        
                        // Add model-specific indexes
                        if (modelName === 'product.product') {
                            objectStore.createIndex('barcode', 'barcode', { unique: false });
                            objectStore.createIndex('default_code', 'default_code', { unique: false });
                        } else if (modelName === 'product.category') {
                            objectStore.createIndex('name', 'name', { unique: false });
                        } else if (modelName === 'product.pricelist') {
                            objectStore.createIndex('name', 'name', { unique: false });
                        }
                    }
                }

                // Metadata store (for tracking sync info)
                if (!db.objectStoreNames.contains(this.metaStoreName)) {
                    db.createObjectStore(this.metaStoreName, { keyPath: 'key' });
                }
            };
        });
    }

    /**
     * Save records for any model to local storage
     * @param {string} modelName - e.g., 'product.product', 'product.category'
     * @param {Array} records - Array of records to save
     */
    async saveRecords(modelName, records) {
        if (!this.db) await this.init();
        
        const storeName = this.stores[modelName] || this.stores['product.product'];

        return new Promise((resolve, reject) => {
            const transaction = this.db.transaction([storeName], 'readwrite');
            const store = transaction.objectStore(storeName);

            let saved = 0;
            let errors = 0;
            
            records.forEach((record, index) => {
                try {
                    // Ensure record has an id
                    if (!record.id) {
                        console.error(`[ProductStorage] ${modelName} record missing id:`, record);
                        errors++;
                        return;
                    }
                    
                    const request = store.put(record);
                    request.onsuccess = () => {
                        saved++;
                        if (saved % 100 === 0) {
                            console.log(`[ProductStorage] Saved ${saved} ${modelName} to IndexedDB`);
                        }
                    };
                    request.onerror = (e) => {
                        console.error(`[ProductStorage] Error saving ${modelName} ${record.id}:`, e.target.error);
                        errors++;
                    };
                } catch (error) {
                    console.error(`[ProductStorage] Exception saving ${modelName}:`, error, record);
                    errors++;
                }
            });

            transaction.oncomplete = () => {
                console.log(`[ProductStorage] ${modelName} transaction complete: ${saved} saved, ${errors} errors`);
                resolve(saved);
            };
            transaction.onerror = (e) => {
                console.error(`[ProductStorage] ${modelName} transaction error:`, e.target.error);
                reject(transaction.error);
            };
            transaction.onabort = (e) => {
                console.error(`[ProductStorage] ${modelName} transaction aborted:`, e.target.error);
                reject(new Error('Transaction aborted'));
            };
        });
    }

    /**
     * Legacy method - save products (backwards compatible)
     */
    async saveProducts(products) {
        return this.saveRecords('product.product', products);
    }

    /**
     * Get all records for a model from local storage
     * @param {string} modelName - e.g., 'product.product', 'product.category'
     */
    async getAllRecords(modelName) {
        if (!this.db) await this.init();
        
        const storeName = this.stores[modelName] || this.stores['product.product'];

        return new Promise((resolve, reject) => {
            const transaction = this.db.transaction([storeName], 'readonly');
            const store = transaction.objectStore(storeName);
            const request = store.getAll();

            request.onsuccess = () => resolve(request.result);
            request.onerror = () => reject(request.error);
        });
    }

    /**
     * Legacy method - get all products (backwards compatible)
     */
    async getAllProducts() {
        return this.getAllRecords('product.product');
    }

    /**
     * Get record by ID for any model
     * @param {string} modelName - e.g., 'product.product', 'product.category'
     * @param {number} recordId - Record ID
     */
    async getRecord(modelName, recordId) {
        if (!this.db) await this.init();
        
        const storeName = this.stores[modelName] || this.stores['product.product'];

        return new Promise((resolve, reject) => {
            const transaction = this.db.transaction([storeName], 'readonly');
            const store = transaction.objectStore(storeName);
            const request = store.get(recordId);

            request.onsuccess = () => resolve(request.result);
            request.onerror = () => reject(request.error);
        });
    }

    /**
     * Legacy method - get product by ID (backwards compatible)
     */
    async getProduct(productId) {
        return this.getRecord('product.product', productId);
    }

    /**
     * Search products locally
     */
    async searchProducts(searchTerm) {
        const products = await this.getAllProducts();
        const term = searchTerm.toLowerCase();

        return products.filter(p => 
            (p.name && p.name.toLowerCase().includes(term)) ||
            (p.default_code && p.default_code.toLowerCase().includes(term)) ||
            (p.barcode && p.barcode.toLowerCase().includes(term)) ||
            (p.display_name && p.display_name.toLowerCase().includes(term))
        );
    }

    /**
     * Delete records by IDs for any model
     * @param {string} modelName - e.g., 'product.product', 'product.category'
     * @param {Array} recordIds - Array of record IDs to delete
     */
    async deleteRecords(modelName, recordIds) {
        if (!this.db) await this.init();
        
        const storeName = this.stores[modelName] || this.stores['product.product'];

        return new Promise((resolve, reject) => {
            const transaction = this.db.transaction([storeName], 'readwrite');
            const store = transaction.objectStore(storeName);

            let deleted = 0;
            recordIds.forEach(id => {
                const request = store.delete(id);
                request.onsuccess = () => deleted++;
            });

            transaction.oncomplete = () => resolve(deleted);
            transaction.onerror = () => reject(transaction.error);
        });
    }

    /**
     * Legacy method - delete products (backwards compatible)
     */
    async deleteProducts(productIds) {
        return this.deleteRecords('product.product', productIds);
    }

    /**
     * Get record count for any model
     * @param {string} modelName - e.g., 'product.product', 'product.category'
     */
    async getRecordCount(modelName) {
        if (!this.db) await this.init();
        
        const storeName = this.stores[modelName] || this.stores['product.product'];

        return new Promise((resolve, reject) => {
            const transaction = this.db.transaction([storeName], 'readonly');
            const store = transaction.objectStore(storeName);
            const request = store.count();

            request.onsuccess = () => resolve(request.result);
            request.onerror = () => reject(request.error);
        });
    }

    /**
     * Legacy method - get product count (backwards compatible)
     */
    async getProductCount() {
        return this.getRecordCount('product.product');
    }

    /**
     * Get last sync date
     */
    async getLastSyncDate() {
        if (!this.db) await this.init();

        return new Promise((resolve, reject) => {
            const transaction = this.db.transaction([this.metaStoreName], 'readonly');
            const store = transaction.objectStore(this.metaStoreName);
            const request = store.get('last_sync_date');

            request.onsuccess = () => {
                const result = request.result;
                resolve(result ? result.value : null);
            };
            request.onerror = () => reject(request.error);
        });
    }

    /**
     * Set last sync date
     */
    async setLastSyncDate(date) {
        if (!this.db) await this.init();

        return new Promise((resolve, reject) => {
            const transaction = this.db.transaction([this.metaStoreName], 'readwrite');
            const store = transaction.objectStore(this.metaStoreName);
            const request = store.put({ key: 'last_sync_date', value: date });

            request.onsuccess = () => resolve();
            request.onerror = () => reject(request.error);
        });
    }

    /**
     * Save metadata (categories, taxes, uoms, etc.)
     */
    async saveMetadata(metadata) {
        if (!this.db) await this.init();

        return new Promise((resolve, reject) => {
            const transaction = this.db.transaction([this.metaStoreName], 'readwrite');
            const store = transaction.objectStore(this.metaStoreName);

            // Save each metadata type
            if (metadata.pos_categories) {
                store.put({ key: 'pos_categories', value: metadata.pos_categories });
            }
            if (metadata.product_categories) {
                store.put({ key: 'product_categories', value: metadata.product_categories });
            }
            if (metadata.taxes) {
                store.put({ key: 'taxes', value: metadata.taxes });
            }
            if (metadata.uoms) {
                store.put({ key: 'uoms', value: metadata.uoms });
            }

            transaction.oncomplete = () => resolve();
            transaction.onerror = () => reject(transaction.error);
        });
    }

    /**
     * Get metadata by key
     */
    async getMetadata(key) {
        if (!this.db) await this.init();

        return new Promise((resolve, reject) => {
            const transaction = this.db.transaction([this.metaStoreName], 'readonly');
            const store = transaction.objectStore(this.metaStoreName);
            const request = store.get(key);

            request.onsuccess = () => {
                const result = request.result;
                resolve(result ? result.value : null);
            };
            request.onerror = () => reject(request.error);
        });
    }

    /**
     * Clear all records for a specific model
     * @param {string} modelName - e.g., 'product.product', 'product.category'
     */
    async clearRecords(modelName) {
        if (!this.db) await this.init();
        
        const storeName = this.stores[modelName];
        if (!storeName) {
            console.warn(`[ProductStorage] Unknown model: ${modelName}`);
            return;
        }

        return new Promise((resolve, reject) => {
            const transaction = this.db.transaction([storeName], 'readwrite');
            const store = transaction.objectStore(storeName);
            const request = store.clear();

            request.onsuccess = () => resolve();
            request.onerror = () => reject(request.error);
        });
    }

    /**
     * Legacy method - clear products (backwards compatible)
     */
    async clearProducts() {
        return this.clearRecords('product.product');
    }

    /**
     * Clear metadata
     */
    async clearMetadata() {
        if (!this.db) await this.init();

        return new Promise((resolve, reject) => {
            const transaction = this.db.transaction([this.metaStoreName], 'readwrite');
            const store = transaction.objectStore(this.metaStoreName);
            const request = store.clear();

            request.onsuccess = () => resolve();
            request.onerror = () => reject(request.error);
        });
    }

    /**
     * Clear all data (all models + metadata)
     */
    async clearAll() {
        // Clear all model stores
        for (const modelName of Object.keys(this.stores)) {
            await this.clearRecords(modelName);
        }
        await this.clearMetadata();
    }

    /**
     * Get counts for all models
     * @returns {Object} Object with model names as keys and counts as values
     */
    async getAllCounts() {
        const counts = {};
        for (const modelName of Object.keys(this.stores)) {
            counts[modelName] = await this.getRecordCount(modelName);
        }
        return counts;
    }
}
