/** @odoo-module **/

import { patch } from "@web/core/utils/patch";
import { PosOrder } from "@point_of_sale/app/models/pos_order";
import { ProductScreen } from "@point_of_sale/app/screens/product_screen/product_screen";
    import { PaymentScreen } from "@point_of_sale/app/screens/payment_screen/payment_screen";
    import { PinPopup } from "./pin_popup";
import { _t } from "@web/core/l10n/translation";

// Patch Order model for line deletion
patch(PosOrder.prototype, {
    removeOrderline(line) {
        const pos = this.pos || (this.models && this.models["pos.order"] && this.models["pos.order"].pos);
        
        if (!pos) {
            return super.removeOrderline(...arguments);
        }
        
        const config = pos.config;
        
        // Check if PIN is required for deleting order line
        if (config.require_pin_delete_orderline && config.advanced_employee_ids && config.advanced_employee_ids.length > 0) {
            // Request PIN authorization
            const dialog = pos.env.services.dialog;
            
            return dialog.add(PinPopup, {}).then(({ confirmed }) => {
                if (confirmed) {
                    return super.removeOrderline(line);
                }
            }).catch(() => {
                // User cancelled
                return Promise.resolve();
            });
        }
        
        // Call the original method if no PIN required
        return super.removeOrderline(...arguments);
    },
});

// Patch ProductScreen for clear order operation
patch(ProductScreen.prototype, {
    async clearCart() {
        const order = this.pos.getOrder();
        const config = this.pos.config;
        
        if (!order || order.lines.length === 0) {
            return;
        }
        
        // Check if PIN is required for clearing order
        if (config.require_pin_clear_order && config.advanced_employee_ids && config.advanced_employee_ids.length > 0) {
            const { confirmed } = await this.env.services.dialog.add(PinPopup, {});
            
            if (!confirmed) {
                return;
            }
        }
        
        // Clear all lines
        while (order.lines.length > 0) {
            // Temporarily disable PIN check for individual line deletion during clear
            const originalRequire = config.require_pin_delete_orderline;
            config.require_pin_delete_orderline = false;
            
            await order.removeOrderline(order.lines[0]);
            
            config.require_pin_delete_orderline = originalRequire;
        }
    },
});

// Patch PaymentScreen for refund authorization
// patch(PaymentScreen.prototype, {
//     async validateOrder(isForceValidate) {
//         const order = this.pos.get_order();
//         const config = this.pos.config;
        
//         // Check if this is a refund order (negative total)
//         if (config.require_pin_refund && config.advanced_employee_ids && config.advanced_employee_ids.length > 0) {
//             if (order.get_total_with_tax() < 0) {
//                 const { confirmed } = await this.env.services.dialog.add(PinPopup, {});
                
//                 if (!confirmed) {
//                     return;
//                 }
//             }
//         }
        
//         return await super.validateOrder(...arguments);
//     },
// });