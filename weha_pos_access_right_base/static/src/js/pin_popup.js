/** @odoo-module **/

import { Dialog } from "@web/core/dialog/dialog";
import { Component, useState } from "@odoo/owl";
import { usePos } from "@point_of_sale/app/store/pos_hook";
import { _t } from "@web/core/l10n/translation";

export class PinPopup extends Component {
    static components = { Dialog };
    static template = "weha_pos_access_right_base.PinPopup";
    static props = ["close"];

    setup() {
        this.pos = usePos();
        
        // Get advanced employees from pos_hr module
        const allEmployees = this.pos.models["hr.employee"].getAll();
        const advancedEmployeeIds = this.pos.config.advanced_employee_ids || [];
        
        this.advancedEmployees = allEmployees.filter(
            (emp) => advancedEmployeeIds.includes(emp.id)
        );
        
        this.state = useState({
            selectedEmployeeId: this.advancedEmployees.length > 0 ? this.advancedEmployees[0].id : null,
            pin: "",
            error: false,
            errorMessage: "",
        });
    }

    get selectedEmployee() {
        return this.advancedEmployees.find(
            (emp) => emp.id === this.state.selectedEmployeeId
        );
    }

    onSelectEmployee(event) {
        this.state.selectedEmployeeId = parseInt(event.target.value);
        this.state.pin = "";
        this.state.error = false;
        this.state.errorMessage = "";
    }

    onInputPin(event) {
        this.state.pin = event.target.value;
        this.state.error = false;
        this.state.errorMessage = "";
    }

    confirm() {
        if (!this.advancedEmployees || this.advancedEmployees.length === 0) {
            this.state.error = true;
            this.state.errorMessage = _t("No advanced employees configured for this POS");
            this.pos.env.services.notification.add(
                this.state.errorMessage,
                { type: "danger" }
            );
            return;
        }

        if (!this.state.selectedEmployeeId) {
            this.state.error = true;
            this.state.errorMessage = _t("Please select an employee");
            this.pos.env.services.notification.add(
                this.state.errorMessage,
                { type: "warning" }
            );
            return;
        }

        if (!this.state.pin) {
            this.state.error = true;
            this.state.errorMessage = _t("Please enter PIN");
            this.pos.env.services.notification.add(
                this.state.errorMessage,
                { type: "warning" }
            );
            return;
        }

        const employee = this.selectedEmployee;
        
        // Compare entered PIN with selected employee's PIN
        if (employee && employee.pin === this.state.pin) {
            this.state.error = false;
            this.props.close({ confirmed: true, employee: employee });
        } else {
            this.state.error = true;
            this.state.errorMessage = _t("Invalid PIN for selected employee");
            this.pos.env.services.notification.add(
                this.state.errorMessage,
                { type: "danger" }
            );
        }
    }

    cancel() {
        this.state.pin = "";
        this.state.error = false;
        this.state.errorMessage = "";
        this.props.close({ confirmed: false });
    }
}
