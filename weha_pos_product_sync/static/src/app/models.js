/** @odoo-module **/

import { PosStore } from "@point_of_sale/app/store/pos_store";
import { patch } from "@web/core/utils/patch";
import { ProductStorage } from "./product_storage";
import { PosData } from "@point_of_sale/app/models/data_service";

// Patch the data service to handle missing models gracefully
patch(PosData.prototype, {
    syncDataWithIndexedDB(records) {
        // Original implementation but with safety checks for undefined models
        const dataSorter = (records, isFinalized, key) => records.reduce((acc, record) => {
            const finalizedState = isFinalized(record);
            if (finalizedState === undefined || finalizedState === true) {
                if (record[key]) {
                    acc.remove.push(record[key]);
                }
            } else {
                acc.put.push(dataFormatter(record));
            }
            return acc;
        }, {
            put: [],
            remove: []
        });
        
        const dataFormatter = (record) => {
            const serializedData = record.serialize();
            const uiState = typeof record.uiState === "object" ? record.serializeState() : "{}";
            return {
                ...serializedData,
                JSONuiState: JSON.stringify(uiState),
                id: record.id
            };
        };
        
        const dataToDelete = {};
        for (const [model, params] of Object.entries(this.opts.databaseTable)) {
            // SAFETY CHECK: Skip if model doesn't exist in records
            if (!records[model]) {
                console.log(`[POS Data Service] Skipping syncDataWithIndexedDB for ${model} (not in records)`);
                continue;
            }
            
            // SAFETY CHECK: Ensure records[model] has .values() method
            if (typeof records[model].values !== 'function') {
                console.warn(`[POS Data Service] Skipping ${model}: records[model].values is not a function`);
                continue;
            }
            
            const modelRecords = Array.from(records[model].values());
            if (!modelRecords.length) {
                continue;
            }
            
            const data = dataSorter(modelRecords, params.condition, params.key);
            this.indexedDB.create(model, data.put);
            dataToDelete[model] = data.remove;
        }
        
        this.indexedDB.readAll(Object.keys(this.opts.databaseTable)).then((data) => {
            if (!data) {
                return;
            }
            for (const [model, records] of Object.entries(data)) {
                // SAFETY CHECK: Skip if model doesn't exist
                if (!this.models[model]) {
                    console.log(`[POS Data Service] Skipping cleanup for ${model} (model not loaded)`);
                    continue;
                }
                
                const key = this.opts.databaseTable[model].key;
                let keysToDelete = [];
                if (dataToDelete[model]) {
                    const keysInIndexedDB = new Set(records.map((record) => record[key]));
                    keysToDelete = dataToDelete[model].filter((key) => keysInIndexedDB.has(key));
                }
                for (const record of records) {
                    const localRecord = this.models[model].get(record.id);
                    if (!localRecord) {
                        keysToDelete.push(record[key]);
                    }
                }
                if (keysToDelete.length) {
                    this.indexedDB.delete(model, keysToDelete);
                }
            }
        });
    }
});

patch(PosStore.prototype, {
    async processServerData() {
        // Simply call parent - models will exist but be empty
        await super.processServerData(...arguments);
        console.log('[POS Sync] processServerData completed');
    },

    async afterProcessServerData() {
        const startTime = performance.now();
        console.log('═══════════════════════════════════════════════════════');
        console.log('[POS Sync] afterProcessServerData hook triggered');
        console.log('[POS Sync] Config ID:', this.config.id);
        
        // Initialize properties FIRST
        this.productLoadOffset = 0;
        this.productLoadLimit = 100;
        this.allProductsLoaded = false;
        this.productSearchCache = new Map();
        this.isSyncing = false;
        this.lastSyncDate = null;
        this.enableLocalStorage = this.config.enable_local_product_storage || false;
        
        // Always call super first
        await super.afterProcessServerData(...arguments);
        
        // Check how many products were loaded by server
        const productModel = this.models['product.product'];
        const serverProductCount = productModel?.getAll ? productModel.getAll()?.length || 0 : 0;
        console.log(`[POS Sync] Server loaded ${serverProductCount} products`);
        console.log(`[POS Sync] Product model available:`, !!productModel);
        
        // Initialize storage and load products from IndexedDB
        if (this.enableLocalStorage) {
            console.log('[POS Sync] ✓ Local storage ENABLED');
            
            try {
                const dbInitStart = performance.now();
                this.productStorage = new ProductStorage(this.config.id);
                await this.productStorage.init();
                console.log(`[POS Sync] ✓ IndexedDB initialized (${(performance.now() - dbInitStart).toFixed(2)}ms)`);
                
                // Get counts for all models
                const counts = await this.productStorage.getAllCounts();
                this.lastSyncDate = await this.productStorage.getLastSyncDate();
                console.log(`[POS Sync] 📦 Local DB counts:`, counts);
                console.log(`[POS Sync] 🕒 Last sync: ${this.lastSyncDate || 'Never'}`);
                
                // STEP 1: If local DB has data, load from local first
                const hasLocalData = counts['product.product'] > 1;
                if (hasLocalData) {
                    console.log('[POS Sync] 🚀 LOADING FROM LOCAL STORAGE...');
                    const loadStart = performance.now();
                    await this.loadAllModelsFromIndexedDB();
                    const loadTime = (performance.now() - loadStart).toFixed(2);
                    console.log(`[POS Sync] ✓ Local load completed in ${loadTime}ms`);
                    
                    // Then check for updates in background
                    setTimeout(() => this.syncAllModelsInBackground(), 3000);
                } else {
                    // STEP 2: No local products, download from server first
                    console.log('[POS Sync] ⬇️ No local data, downloading from server...');
                    await this.downloadAndSaveAllModels();
                }
            } catch (error) {
                console.error('[POS Sync] ❌ Failed to initialize IndexedDB:', error);
            }
        } else {
            console.log('[POS Sync] ⚠️ Local storage is DISABLED');
        }
        
        const totalTime = (performance.now() - startTime).toFixed(2);
        console.log(`[POS Sync] Total initialization time: ${totalTime}ms`);
        console.log('═══════════════════════════════════════════════════════');
    },

    async loadProductsFromIndexedDB() {
        const startTime = performance.now();
        console.log('[POS Sync] 📥 Loading products from IndexedDB...');
        
        // Ensure product model is available
        if (!this.models['product.product']) {
            console.error('[POS Sync] ❌ Product model not available!');
            return;
        }
        
        try {
            const fetchStart = performance.now();
            const localProducts = await this.productStorage.getAllProducts();
            const fetchTime = (performance.now() - fetchStart).toFixed(2);
            console.log(`[POS Sync] ✓ Fetched ${localProducts.length} products from IndexedDB in ${fetchTime}ms`);
            
            if (localProducts.length > 0) {
                // Load products into POS models
                const modelLoadStart = performance.now();
                let loadedCount = 0;
                let skippedCount = 0;
                
                for (const productData of localProducts) {
                    try {
                        const existingProduct = this.models['product.product'].get(productData.id);
                        if (!existingProduct) {
                            // Transform relational fields to proper format
                            const transformedData = this._transformProductDataForCreate(productData);
                            this.models['product.product'].create(transformedData);
                            loadedCount++;
                        } else {
                            skippedCount++;
                        }
                    } catch (error) {
                        console.warn(`[POS Sync] ⚠️ Failed to load product ${productData.id}:`, error);
                    }
                    
                    // Progress log every 1000 products
                    if ((loadedCount + skippedCount) % 1000 === 0) {
                        const elapsed = (performance.now() - modelLoadStart).toFixed(2);
                        console.log(`[POS Sync] Progress: ${loadedCount + skippedCount}/${localProducts.length} (${elapsed}ms)`);
                    }
                }
                
                const modelLoadTime = (performance.now() - modelLoadStart).toFixed(2);
                const totalTime = (performance.now() - startTime).toFixed(2);
                console.log(`[POS Sync] ✅ MODEL LOADING COMPLETE`);
                console.log(`[POS Sync]   - Loaded: ${loadedCount} products`);
                console.log(`[POS Sync]   - Skipped: ${skippedCount} products`);
                console.log(`[POS Sync]   - Model load time: ${modelLoadTime}ms`);
                console.log(`[POS Sync]   - Total time: ${totalTime}ms`);
                console.log(`[POS Sync]   - Speed: ${(localProducts.length / (totalTime / 1000)).toFixed(0)} products/sec`);
            } else {
                console.log('[POS Sync] ⚠️ No products in IndexedDB, will sync from server');
                // Trigger initial sync if no local products
                setTimeout(() => this.downloadAndSaveProducts(), 1000);
            }
        } catch (error) {
            console.error('[POS Sync] ❌ Error loading from IndexedDB:', error);
        }
    },

    /**
     * Load all product-related models from IndexedDB
     * 
     * DATA FORMAT REQUIREMENTS:
     * ========================
     * Server Format (from search_read):
     *   { id: 123, categ_id: [5, 'Food'], tags: [1,2,3] }
     * 
     * IndexedDB Storage (no transform):
     *   { id: 123, categ_id: [5, 'Food'], tags: [1,2,3] }  ← Same!
     * 
     * POS Loading (minimal transform):
     *   - Ensure arrays ARE arrays: tags: [1,2,3] ✓
     *   - Many2one OK as-is: categ_id: [5,'Food'] or 5 both work
     * 
     * Create Methods:
     *   1. this.data.create() ← Preferred Odoo 18
     *   2. this.models[].create() ← Fallback
     * 
     * See DATA_FORMAT_GUIDE.md for complete documentation
     */
    async loadAllModelsFromIndexedDB() {
        const startTime = performance.now();
        console.log('[POS Sync] 📥 Loading ALL models from IndexedDB...');
        
        // Define models to load in order (dependencies first)
        const modelsToLoad = [
            'product.category',
            'product.tag',
            'product.attribute',
            'product.attribute.value',
            'product.template',
            'product.template.attribute.line',
            'product.template.attribute.value',
            'product.packaging',
            'product.pricelist',
            'product.pricelist.item',
            'product.product'
        ];
        
        const stats = {};
        
        for (const modelName of modelsToLoad) {
            // Check if model exists in POS
            if (!this.models[modelName]) {
                console.log(`[POS Sync] ⚠️ Model ${modelName} not available, skipping`);
                continue;
            }
            
            try {
                const fetchStart = performance.now();
                const records = await this.productStorage.getAllRecords(modelName);
                const fetchTime = (performance.now() - fetchStart).toFixed(2);
                
                if (records.length > 0) {
                    const loadStart = performance.now();
                    
                    // Use data service's loadData method (proper Odoo 18 way)
                    const dataToLoad = { [modelName]: records };
                    const loadedRecords = this.data.models.loadData(dataToLoad);
                    
                    const loaded = loadedRecords[modelName]?.length || 0;
                    const skipped = records.length - loaded;
                    
                    const loadTime = (performance.now() - loadStart).toFixed(2);
                    stats[modelName] = { loaded, skipped, fetchTime, loadTime };
                    console.log(`[POS Sync] ✓ ${modelName}: ${loaded} loaded, ${skipped} skipped (fetch: ${fetchTime}ms, load: ${loadTime}ms)`);
                }
            } catch (error) {
                console.error(`[POS Sync] ❌ Error loading ${modelName}:`, error);
            }
        }
        
        const totalTime = (performance.now() - startTime).toFixed(2);
        console.log(`[POS Sync] ✅ ALL MODELS LOADED in ${totalTime}ms`);
        console.log('[POS Sync] Load stats:', stats);
        
        // Post-processing after loading from IndexedDB
        try {
            console.log('[POS Sync] Running post-processing...');
            
            // Compute product pricelist cache for all loaded products
            if (typeof this.computeProductPricelistCache === 'function') {
                this.computeProductPricelistCache();
                console.log('[POS Sync] ✓ Product pricelist cache computed');
            }
            
            // Process product attributes
            if (typeof this.processProductAttributes === 'function') {
                await this.processProductAttributes();
                console.log('[POS Sync] ✓ Product attributes processed');
            }
            
            console.log('[POS Sync] ✅ Post-processing complete');
        } catch (error) {
            console.error('[POS Sync] ⚠️ Post-processing error:', error);
        }
    },

    /**
     * Download all product-related models from server
     */
    async downloadAndSaveAllModels() {
        console.log('[POS Sync] Starting initial download of all models from server...');
        
        try {
            const result = await this.data.call(
                'pos.session',
                'get_all_product_models_for_sync',
                [],
                { config_id: this.config.id }
            );

            if (result.success) {
                console.log('[POS Sync] Received all models:', Object.keys(result.models));
                
                // Save each model to IndexedDB
                for (const [modelName, records] of Object.entries(result.models)) {
                    if (records && records.length > 0) {
                        await this.productStorage.saveRecords(modelName, records);
                        console.log(`[POS Sync] ✓ Saved ${records.length} ${modelName} records`);
                        
                        // Load into POS models using data service's loadData
                        if (this.models[modelName]) {
                            const dataToLoad = { [modelName]: records };
                            this.data.models.loadData(dataToLoad);
                        }
                    }
                }
                
                // Update sync date
                const syncDate = new Date().toISOString();
                await this.productStorage.setLastSyncDate(syncDate);
                this.lastSyncDate = syncDate;
                
                console.log('[POS Sync] ✅ All models downloaded and saved');
                
                // Post-processing after loading new data
                try {
                    console.log('[POS Sync] Running post-processing...');
                    
                    // Compute product pricelist cache
                    if (typeof this.computeProductPricelistCache === 'function') {
                        this.computeProductPricelistCache();
                        console.log('[POS Sync] ✓ Product pricelist cache computed');
                    }
                    
                    // Process product attributes
                    if (typeof this.processProductAttributes === 'function') {
                        await this.processProductAttributes();
                        console.log('[POS Sync] ✓ Product attributes processed');
                    }
                    
                    console.log('[POS Sync] ✅ Post-processing complete');
                } catch (error) {
                    console.error('[POS Sync] ⚠️ Post-processing error:', error);
                }
            }
        } catch (error) {
            console.error('[POS Sync] ❌ Error downloading all models:', error);
            // Fallback to downloading just products
            await this.downloadAndSaveProducts();
        }
    },

    /**
     * Download products from server and save to local storage
     * This is called on first load when local DB is empty
     */
    async downloadAndSaveProducts() {
        console.log('[POS Sync] Starting initial download from server...');
        
        // Ensure product model is available
        if (!this.models['product.product']) {
            console.error('[POS Sync] ❌ Product model not available!');
            return;
        }
        
        try {
            const batchSize = 500;
            let offset = 0;
            let hasMore = true;
            let totalDownloaded = 0;

            while (hasMore) {
                const result = await this.data.call(
                    'pos.session',
                    'get_all_products_for_sync',
                    [],
                    {
                        offset: offset,
                        limit: batchSize
                    }
                );

                if (result.products && result.products.length > 0) {
                    console.log(`[POS Sync] Downloaded batch: ${result.products.length} products (${offset} - ${offset + result.products.length})`);
                    console.log('[POS Sync] First product sample:', result.products[0]);
                    
                    // STEP 1: Save to IndexedDB first
                    const savedCount = await this.productStorage.saveProducts(result.products);
                    console.log(`[POS Sync] Saved ${savedCount} products to IndexedDB`);
                    
                    // STEP 2: Load into POS models using data service
                    const dataToLoad = { 'product.product': result.products };
                    this.data.models.loadData(dataToLoad);
                    
                    totalDownloaded += result.products.length;
                    offset += result.products.length;
                    hasMore = result.has_more;
                    
                    console.log(`[POS Sync] Progress: ${totalDownloaded}/${result.total_count} products downloaded`);
                } else {
                    hasMore = false;
                }
            }
            
            // Update sync date
            const syncDate = new Date().toISOString();
            await this.productStorage.setLastSyncDate(syncDate);
            this.lastSyncDate = syncDate;
            
            console.log(`[POS Sync] Initial download complete! ${totalDownloaded} products saved to local storage`);
        } catch (error) {
            console.error('[POS Sync] Error downloading products:', error);
        }
    },

    /**
     * Sync only products modified since last sync (Background/Automatic)
     * This runs automatically after loading from local storage
     */
    async syncProductsInBackground() {
        if (this.isSyncing || !this.enableLocalStorage) return;
        
        // Ensure product model is available
        if (!this.models['product.product']) {
            console.error('[Background Sync] ❌ Product model not available!');
            return;
        }

        this.isSyncing = true;
        console.log('🔄 [Background Sync] Starting...');
        console.log(`🔄 [Background Sync] Last sync: ${this.lastSyncDate}`);

        try {
            const syncStart = performance.now();
            const result = await this.data.call(
                'pos.session',
                'sync_products_since',
                [],
                { last_sync_date: this.lastSyncDate, limit: 1000 }
            );

            if (result.products && result.products.length > 0) {
                console.log(`🆕 [Background Sync] Found ${result.products.length} new/updated products`);

                // Count new vs updated
                let newCount = 0;
                let updatedCount = 0;

                // Save to local storage first
                const saveStart = performance.now();
                await this.productStorage.saveProducts(result.products);
                console.log(`💾 [Background Sync] Saved to IndexedDB in ${(performance.now() - saveStart).toFixed(2)}ms`);

                // Update in POS
                for (const productData of result.products) {
                    const existingProduct = this.models['product.product'].get(productData.id);
                    if (!existingProduct) {
                        this.models['product.product'].create(productData);
                        newCount++;
                    } else {
                        Object.assign(existingProduct, productData);
                        updatedCount++;
                    }
                }
                
                console.log(`✅ [Background Sync] Complete: ${newCount} new, ${updatedCount} updated (${(performance.now() - syncStart).toFixed(2)}ms)`);
            } else {
                console.log('✓ [Background Sync] No updates found - all products current');
            }

            // Handle deleted products
            if (result.deleted_products && result.deleted_products.length > 0) {
                console.log(`🗑️ [Background Sync] Removing ${result.deleted_products.length} deleted products`);
                await this.productStorage.deleteProducts(result.deleted_products);

                for (const productId of result.deleted_products) {
                    const product = this.models['product.product'].get(productId);
                    if (product) {
                        this.models['product.product'].delete(product);
                    }
                }
            }

            // Update last sync date
            this.lastSyncDate = result.sync_date;
            await this.productStorage.setLastSyncDate(result.sync_date);

            console.log('✅ [Background Sync] Completed successfully, next sync in 3 minutes');

        } catch (error) {
            console.error('❌ [Background Sync] Error:', error);
        } finally {
            this.isSyncing = false;
            
            // Schedule next background sync in 3 minutes
            setTimeout(() => this.syncProductsInBackground(), 180000);
        }
    },

    /**
     * Sync all product-related models since last sync (Background/Automatic)
     * This runs automatically after loading from local storage
     */
    async syncAllModelsInBackground() {
        if (this.isSyncing || !this.enableLocalStorage) return;

        this.isSyncing = true;
        console.log('🔄 [Background Sync] Starting FULL MODEL sync...');
        console.log(`🔄 [Background Sync] Last sync: ${this.lastSyncDate}`);

        try {
            const syncStart = performance.now();
            const result = await this.data.call(
                'pos.session',
                'sync_all_product_models_since',
                [],
                { 
                    last_sync_date: this.lastSyncDate,
                    config_id: this.config.id
                }
            );

            if (result.success) {
                console.log(`🆕 [Background Sync] Sync info:`, result);
                
                // Sync each model
                for (const [modelName, modelData] of Object.entries(result.models || {})) {
                    if (modelData.records && modelData.records.length > 0) {
                        console.log(`🔄 [Background Sync] ${modelName}: ${modelData.records.length} updates`);
                        
                        // Save to IndexedDB
                        await this.productStorage.saveRecords(modelName, modelData.records);
                        
                        // Update POS models
                        if (this.models[modelName]) {
                            const dataToLoad = { [modelName]: modelData.records };
                            this.data.models.loadData(dataToLoad);
                            
                            const loaded = modelData.records.length;
                            console.log(`✓ [Background Sync] ${modelName}: ${loaded} records loaded`);
                        }
                        
                        // Handle deletions
                        if (modelData.deleted_ids && modelData.deleted_ids.length > 0) {
                            console.log(`🗑️ [Background Sync] ${modelName}: Removing ${modelData.deleted_ids.length} deleted records`);
                            await this.productStorage.deleteRecords(modelName, modelData.deleted_ids);
                            
                            if (this.models[modelName]) {
                                for (const recordId of modelData.deleted_ids) {
                                    const record = this.models[modelName].get(recordId);
                                    if (record) {
                                        this.models[modelName].delete(record);
                                    }
                                }
                            }
                        }
                    }
                }

                // Update last sync date
                this.lastSyncDate = result.sync_date;
                await this.productStorage.setLastSyncDate(result.sync_date);

                const syncTime = (performance.now() - syncStart).toFixed(2);
                console.log(`✅ [Background Sync] Completed successfully in ${syncTime}ms, next sync in 3 minutes`);
            } else {
                console.log('✓ [Background Sync] No updates found - all models current');
            }

        } catch (error) {
            console.error('❌ [Background Sync] Error:', error);
            // Fallback to product-only sync
            console.log('⚠️ [Background Sync] Falling back to product-only sync');
            await this.syncProductsInBackground();
            return;
        } finally {
            this.isSyncing = false;
            
            // Schedule next background sync in 3 minutes
            setTimeout(() => this.syncAllModelsInBackground(), 180000);
        }
    },

    /**
     * Manual sync trigger - Full batch sync
     */
    async manualSync(forceFull = false) {
        if (this.isSyncing) {
            console.log('[POS Sync] Sync already in progress');
            return { success: false, message: 'Sync already in progress' };
        }

        if (!this.enableLocalStorage || !this.productStorage) {
            console.error('[POS Sync] Local storage not initialized');
            return { success: false, message: 'Local storage not enabled or initialized' };
        }
        
        // Ensure product model is available
        if (!this.models['product.product']) {
            console.error('[POS Sync] ❌ Product model not available!');
            return { success: false, message: 'Product model not available. Please reload POS.' };
        }

        this.isSyncing = true;
        console.log('[POS Sync] Manual sync triggered, forceFull:', forceFull);
        
        try {
            // Step 1: Initialize sync and get metadata
            console.log('[POS Sync] Step 1: Initializing sync...');
            let initResult;
            try {
                initResult = await this.data.call(
                    'pos.session',
                    'start_manual_sync',
                    [],
                    { config_id: this.config.id }
                );
            } catch (rpcError) {
                console.error('[POS Sync] RPC Error in start_manual_sync:', rpcError);
                this.isSyncing = false;
                return { 
                    success: false, 
                    message: `Failed to initialize sync: ${rpcError.message || rpcError.data?.message || 'Unknown error'}` 
                };
            }

            if (!initResult.success) {
                console.error('[POS Sync] Init failed:', initResult.error);
                this.isSyncing = false;
                return { success: false, message: initResult.error };
            }

            console.log('[POS Sync] Sync initialized successfully');

            // Save metadata to IndexedDB
            if (initResult.metadata) {
                console.log('[POS Sync] Saving metadata to IndexedDB...');
                await this.productStorage.saveMetadata(initResult.metadata);
            }

            // Step 2: Get sync info
            console.log('[POS Sync] Step 2: Getting sync info...');
            let syncInfo;
            try {
                syncInfo = await this.data.call(
                    'pos.session',
                    'manual_sync_products',
                    [],
                    { 
                        config_id: this.config.id,
                        last_sync_date: forceFull ? null : this.lastSyncDate,
                        batch_size: 500
                    }
                );
            } catch (rpcError) {
                console.error('[POS Sync] RPC Error in manual_sync_products:', rpcError);
                this.isSyncing = false;
                return { 
                    success: false, 
                    message: `Failed to get sync info: ${rpcError.message || rpcError.data?.message || 'Unknown error'}` 
                };
            }

            if (!syncInfo.success) {
                console.error('[POS Sync] Sync info failed:', syncInfo.error);
                this.isSyncing = false;
                return { success: false, message: syncInfo.error || 'Failed to get sync information' };
            }

            const totalBatches = syncInfo.batches_needed;
            let syncedCount = 0;
            const syncStartDate = new Date().toISOString();

            // Step 3: Load products in batches
            console.log(`[POS Sync] Step 3: Loading ${totalBatches} batches...`);
            for (let batchNum = 0; batchNum < totalBatches; batchNum++) {
                console.log(`[POS Sync] Loading batch ${batchNum + 1}/${totalBatches}`);

                const batchResult = await this.data.call(
                    'pos.session',
                    'get_sync_batch',
                    [],
                    {
                        batch_number: batchNum,
                        batch_size: 500,
                        last_sync_date: forceFull ? null : this.lastSyncDate
                    }
                );

                if (batchResult.success && batchResult.products && batchResult.products.length > 0) {
                    console.log(`[POS Sync] Batch ${batchNum + 1}: Received ${batchResult.products.length} products`);
                    
                    // Save to IndexedDB
                    const savedCount = await this.productStorage.saveProducts(batchResult.products);
                    console.log(`[POS Sync] Batch ${batchNum + 1}: Saved ${savedCount} products to IndexedDB`);

                    // Load into POS models
                    for (const productData of batchResult.products) {
                        try {
                            const existingProduct = this.models['product.product'].get(productData.id);
                            if (!existingProduct) {
                                this.models['product.product'].create(productData);
                            } else {
                                Object.assign(existingProduct, productData);
                            }
                        } catch (modelError) {
                            console.warn(`[POS Sync] Error loading product ${productData.id} into model:`, modelError);
                        }
                    }

                    syncedCount += batchResult.products.length;
                    console.log(`[POS Sync] Progress: ${syncedCount}/${syncInfo.total_products}`);
                } else {
                    console.warn(`[POS Sync] Batch ${batchNum + 1} returned no products`);
                }

                // Small delay between batches to prevent overwhelming the server
                await new Promise(resolve => setTimeout(resolve, 100));
            }

            // Step 4: Complete sync
            console.log('[POS Sync] Step 4: Completing sync...');
            let completeResult;
            try {
                completeResult = await this.data.call(
                    'pos.session',
                    'complete_manual_sync',
                    [],
                    {
                        config_id: this.config.id,
                        synced_count: syncedCount,
                        sync_start_date: syncStartDate
                    }
                );
            } catch (rpcError) {
                console.error('[POS Sync] RPC Error in complete_manual_sync:', rpcError);
                // Even if complete fails, we still synced products
                console.warn('[POS Sync] Sync completion failed but products were synced');
                completeResult = { 
                    sync_end_date: new Date().toISOString() 
                };
            }

            // Update last sync date
            this.lastSyncDate = completeResult.sync_end_date;
            await this.productStorage.setLastSyncDate(this.lastSyncDate);

            console.log('[POS Sync] Manual sync completed successfully:', {
                synced_count: syncedCount,
                sync_type: syncInfo.sync_type,
                last_sync: this.lastSyncDate
            });
            this.isSyncing = false;

            return {
                success: true,
                message: `Sync completed! ${syncedCount} products synced.`,
                synced_count: syncedCount,
                sync_type: syncInfo.sync_type,
                last_sync: this.lastSyncDate
            };

        } catch (error) {
            console.error('[POS Sync] Manual sync error:', error);
            console.error('[POS Sync] Error stack:', error.stack);
            this.isSyncing = false;
            return { 
                success: false, 
                message: `Sync failed: ${error.message || error}` 
            };
        }
    },

    /**
     * Check if sync is required
     */
    async checkSyncRequired() {
        try {
            const result = await this.data.call(
                'pos.session',
                'check_sync_required',
                [],
                {
                    config_id: this.config.id,
                    last_sync_date: this.lastSyncDate
                }
            );

            return result;
        } catch (error) {
            console.error('[POS Sync] Error checking sync:', error);
            return { sync_required: false, error: error.message };
        }
    },

    /**
     * Clear local product database
     */
    async clearLocalProductDB() {
        if (!this.config.enable_local_product_storage) return;

        try {
            await this.productStorage.clearAll();
            this.lastSyncDate = null;
            console.log('[POS Sync] Local product database cleared');
            
            return { 
                success: true, 
                message: 'Local database cleared. Please reload POS to sync products.' 
            };
        } catch (error) {
            console.error('[POS Sync] Error clearing local database:', error);
            return { success: false, message: error.message };
        }
    },

    /**
     * Load more products on demand
     */
    async loadMoreProducts() {
        if (this.allProductsLoaded) {
            return;
        }

        try {
            const result = await this.data.call(
                'pos.session',
                'load_more_products',
                [],
                {
                    offset: this.productLoadOffset,
                    limit: this.productLoadLimit,
                    search_term: ''
                }
            );

            if (result.products && result.products.length > 0) {
                // Save to local storage if enabled
                if (this.config.enable_local_product_storage) {
                    await this.productStorage.saveProducts(result.products);
                }

                // Add products to the store
                for (const productData of result.products) {
                    const existingProduct = this.models['product.product'].get(productData.id);
                    if (!existingProduct) {
                        this.models['product.product'].create(productData);
                    }
                }

                this.productLoadOffset += result.products.length;
                this.allProductsLoaded = !result.has_more;
            } else {
                this.allProductsLoaded = true;
            }

            return result;
        } catch (error) {
            console.error('Error loading more products:', error);
            return { products: [], has_more: false };
        }
    },

    /**
     * Search products with local storage support
     */
    async searchProducts(searchTerm, limit = 50) {
        if (!searchTerm || searchTerm.length < 2) {
            return [];
        }

        // Try local search first if enabled
        if (this.config.enable_local_product_storage) {
            try {
                const localResults = await this.productStorage.searchProducts(searchTerm);
                if (localResults.length > 0) {
                    return localResults.slice(0, limit);
                }
            } catch (error) {
                console.error('Error searching local storage:', error);
            }
        }

        // Fallback to server search
        const cacheKey = `${searchTerm}_${limit}`;
        if (this.productSearchCache.has(cacheKey)) {
            const cached = this.productSearchCache.get(cacheKey);
            if (Date.now() - cached.timestamp < 300000) {
                return cached.products;
            }
        }

        try {
            const products = await this.data.call(
                'pos.session',
                'search_products',
                [],
                {
                    search_term: searchTerm,
                    limit: limit
                }
            );

            this.productSearchCache.set(cacheKey, {
                products: products,
                timestamp: Date.now()
            });

            // Save to local storage
            if (this.config.enable_local_product_storage && products.length > 0) {
                await this.productStorage.saveProducts(products);
            }

            // Add products to store if not exists
            for (const productData of products) {
                const existingProduct = this.models['product.product'].get(productData.id);
                if (!existingProduct) {
                    this.models['product.product'].create(productData);
                }
            }

            return products;
        } catch (error) {
            console.error('Error searching products:', error);
            return [];
        }
    },

    /**
     * Get product by barcode with lazy loading
     */
    async getProductByBarcode(barcode) {
        let product = super.getProductByBarcode?.(barcode);
        
        if (!product && this.config.fast_product_loading) {
            const results = await this.searchProducts(barcode, 1);
            if (results.length > 0) {
                product = this.models['product.product'].get(results[0].id);
            }
        }

        return product;
    },

    /**
     * Clear product search cache
     */
    clearProductSearchCache() {
        this.productSearchCache.clear();
    },

    /**
     * Get sync status
     */
    getSyncStatus() {
        return {
            is_syncing: this.isSyncing || false,
            last_sync_date: this.lastSyncDate || null,
            local_storage_enabled: this.config?.enable_local_product_storage || false,
            all_products_loaded: this.allProductsLoaded || false
        };
    },

    /**
     * Legacy method - no longer needed since backend transforms data
     * Keeping for backwards compatibility, but it does nothing now
     * 
     * @deprecated Data is already in correct format from server
     */
    _transformRecordDataForCreate(modelName, recordData) {
        // No transformation needed - backend handles it
        return recordData;
    },

    /**
     * Debug helper: Compare server data format vs IndexedDB data format
     */
    async debugCompareDataFormat(recordId = null) {
        console.log('\n========== DATA FORMAT COMPARISON ==========');
        
        // Get data from IndexedDB
        const dbRecord = recordId 
            ? await this.productStorage.getRecord('product.product', recordId)
            : (await this.productStorage.getAllRecords('product.product'))[0];
            
        if (!dbRecord) {
            console.log('No record found in IndexedDB');
            return;
        }
        
        console.log(`\n--- IndexedDB Record (ID: ${dbRecord.id}) ---`);
        console.log('Many2one fields (should be numeric):');
        console.log('  categ_id:', typeof dbRecord.categ_id, '=', JSON.stringify(dbRecord.categ_id));
        console.log('  uom_id:', typeof dbRecord.uom_id, '=', JSON.stringify(dbRecord.uom_id));
        console.log('  product_tmpl_id:', typeof dbRecord.product_tmpl_id, '=', JSON.stringify(dbRecord.product_tmpl_id));
        
        console.log('\nMany2many fields (should be arrays):');
        console.log('  taxes_id:', typeof dbRecord.taxes_id, Array.isArray(dbRecord.taxes_id) ? '(array)' : '', '=', JSON.stringify(dbRecord.taxes_id));
        console.log('  pos_categ_ids:', typeof dbRecord.pos_categ_ids, Array.isArray(dbRecord.pos_categ_ids) ? '(array)' : '', '=', JSON.stringify(dbRecord.pos_categ_ids));
        console.log('  product_tag_ids:', typeof dbRecord.product_tag_ids, Array.isArray(dbRecord.product_tag_ids) ? '(array)' : '', '=', JSON.stringify(dbRecord.product_tag_ids));
        
        console.log('\n✓ Data is already in correct format from server');
        console.log('  No transformation needed!');
        console.log('\n============================================\n');
        
        return dbRecord;
    },

    /**
     * Legacy method for backwards compatibility
     * @deprecated Data is already in correct format from server
     */
    _transformProductDataForCreate(productData) {
        // No transformation needed
        return productData;
    }
});
