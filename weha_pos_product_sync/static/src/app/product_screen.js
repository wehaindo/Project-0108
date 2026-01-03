/** @odoo-module **/

import { ProductsWidget } from "@point_of_sale/app/screens/product_screen/product_list/product_list";
import { patch } from "@web/core/utils/patch";
import { onMounted, useRef } from "@odoo/owl";

patch(ProductsWidget.prototype, {
    setup() {
        super.setup(...arguments);
        this.scrollableRef = useRef("scrollable-products");
        this.isLoadingMore = false;

        onMounted(() => {
            if (this.pos.config.fast_product_loading) {
                this.setupInfiniteScroll();
            }
        });
    },

    setupInfiniteScroll() {
        const scrollable = this.scrollableRef.el?.querySelector('.product-list');
        if (!scrollable) return;

        scrollable.addEventListener('scroll', async (event) => {
            const { scrollTop, scrollHeight, clientHeight } = event.target;
            
            // Load more when scrolled to 80% of the content
            if (scrollTop + clientHeight >= scrollHeight * 0.8) {
                await this.loadMoreProducts();
            }
        });
    },

    async loadMoreProducts() {
        if (this.isLoadingMore || this.pos.allProductsLoaded) {
            return;
        }

        this.isLoadingMore = true;
        
        try {
            const result = await this.pos.loadMoreProducts();
            
            if (result && result.products && result.products.length > 0) {
                // Products are already added to the store in loadMoreProducts
                // Just trigger a re-render if needed
                this.render();
            }
        } catch (error) {
            console.error('Failed to load more products:', error);
        } finally {
            this.isLoadingMore = false;
        }
    },

    async _onSearchInput(event) {
        const searchTerm = event.target.value;
        
        if (this.pos.config.fast_product_loading && searchTerm && searchTerm.length >= 2) {
            // Use optimized search
            await this.pos.searchProducts(searchTerm);
        }
        
        // Call the original search handler
        return super._onSearchInput?.(event);
    }
});
