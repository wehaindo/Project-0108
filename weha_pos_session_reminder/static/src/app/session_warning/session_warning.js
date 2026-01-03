/** @odoo-module */

import { Component } from "@odoo/owl";
import { usePos } from "@point_of_sale/app/store/pos_hook";
import { useService } from "@web/core/utils/hooks";
import { Navbar } from "@point_of_sale/app/navbar/navbar";
import { patch } from "@web/core/utils/patch";

export class SessionDateWarning extends Component {
    static template = "weha_pos_session_reminder.SessionDateWarning";

    setup() {
        this.pos = usePos();
        this.dialog = useService("dialog");
    }

    /**
     * Check if session date is different from current date
     */
    get isSessionDateOld() {
        if (!this.pos.session || !this.pos.session.start_at) {
            return false;
        }

        // Get session date (start_at is in format: "YYYY-MM-DD HH:MM:SS")
        const sessionStartAt = this.pos.session.start_at;
        const sessionDate = sessionStartAt.split(' ')[0];
        
        // Get current date in YYYY-MM-DD format
        const today = new Date();
        const currentDate = today.toISOString().split('T')[0];
        
        return sessionDate !== currentDate;
    }

    /**
     * Get session date for display
     */
    get sessionDate() {
        if (!this.pos.session || !this.pos.session.start_at) {
            return "";
        }
        const sessionStartAt = this.pos.session.start_at;
        return sessionStartAt.split(' ')[0];
    }

    /**
     * Get current date for display
     */
    get currentDate() {
        const today = new Date();
        return today.toISOString().split('T')[0];
    }
}

// Patch Navbar to register SessionDateWarning component
patch(Navbar.prototype, {
    setup() {
        super.setup(...arguments);
    }
});

// Register the component in Navbar's components
patch(Navbar, {
    components: {
        ...Navbar.components,
        SessionDateWarning,
    }
});
