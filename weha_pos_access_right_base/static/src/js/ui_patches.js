/** @odoo-module **/

import { Orderline } from "@point_of_sale/app/generic_components/orderline/orderline";
import { ActionpadWidget } from "@point_of_sale/app/screens/product_screen/action_pad/action_pad";
import { patch } from "@web/core/utils/patch";
import { PinPopup } from "./pin_popup";
import { _t } from "@web/core/l10n/translation";
import { usePos } from "@point_of_sale/app/store/pos_hook";

// Patch Orderline to add delete functionality
patch(Orderline.prototype, {
    setup() {
        super.setup(...arguments);
        this.pos = usePos();
    },

    async onClickDelete() {
        const order = this.pos.get_order();
        const config = this.pos.config;
        const line = this.props.line;

        // Check if PIN is required for deleting order line
        if (config.require_pin_delete_orderline && config.advanced_employee_ids && config.advanced_employee_ids.length > 0) {
            const { confirmed } = await this.env.services.dialog.add(PinPopup, {});
            
            if (!confirmed) {
                return;
            }
        }

        // Delete the line
        await order.removeOrderline(line);
    },
});

// Patch ActionpadWidget to add clear all button functionality
patch(ActionpadWidget.prototype, {
    setup() {
        super.setup(...arguments);
        this.pos = usePos();
    },

    async onClickClearAll() {
        const order = this.pos.get_order();
        const config = this.pos.config;

        if (!order || order.lines.length === 0) {
            this.env.services.notification.add(
                _t("No order lines to clear"),
                { type: "info" }
            );
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
        const linesToDelete = [...order.lines];
        
        // Temporarily disable PIN check for individual line deletion
        const originalRequire = config.require_pin_delete_orderline;
        config.require_pin_delete_orderline = false;
        
        for (const line of linesToDelete) {
            await order.removeOrderline(line);
        }
        
        config.require_pin_delete_orderline = originalRequire;

        this.env.services.notification.add(
            _t("All order lines cleared"),
            { type: "success" }
        );
    },
});
