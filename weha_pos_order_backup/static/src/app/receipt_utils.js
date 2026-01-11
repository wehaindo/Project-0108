/** @odoo-module **/

/**
 * Utility to capture receipt HTML matching POS receipt format
 * Based on point_of_sale/static/src/app/screens/receipt_screen/receipt/order_receipt.xml
 */
export async function captureReceiptHtml(order, pos) {
    try {
        // Get the receipt data exactly as POS generates it
        const receiptData = await order.export_for_printing();
        
        // Build HTML matching the POS receipt template structure
        let html = '<div class="pos-receipt">';
        
        // Receipt Header
        html += '<div class="pos-receipt-header">';
        if (receiptData.headerData) {
            const hd = receiptData.headerData;
            if (hd.company) {
                if (hd.company.logo) {
                    html += `<img class="pos-receipt-logo" src="${hd.company.logo}" alt="Logo"/>`;
                }
                if (hd.company.name) {
                    html += `<h2 class="pos-receipt-company-name">${hd.company.name}</h2>`;
                }
                if (hd.company.contact_address) {
                    html += `<div class="pos-receipt-contact">${hd.company.contact_address}</div>`;
                }
                if (hd.company.phone) {
                    html += `<div class="pos-receipt-phone">Tel: ${hd.company.phone}</div>`;
                }
                if (hd.company.vat) {
                    html += `<div class="pos-receipt-vat">VAT: ${hd.company.vat}</div>`;
                }
            }
        }
        html += '</div>';
        
        // Order Information
        html += '<div class="pos-receipt-order-data">';
        if (receiptData.name) {
            html += `<div><strong>${receiptData.name}</strong></div>`;
        }
        if (receiptData.date) {
            const dateStr = receiptData.date.localestring || receiptData.date.toString() || new Date().toLocaleString();
            html += `<div>${dateStr}</div>`;
        }
        if (receiptData.cashier) {
            html += `<div>Cashier: ${receiptData.cashier}</div>`;
        }
        if (receiptData.client) {
            html += `<div>Customer: ${receiptData.client}</div>`;
        }
        html += '</div>';
        
        // Order Lines
        html += '<div class="orderlines">';
        if (receiptData.orderlines && receiptData.orderlines.length > 0) {
            for (const line of receiptData.orderlines) {
                html += '<div class="orderline">';
                
                // Product name
                html += `<div class="product-name">${line.product_name || ''}</div>`;
                
                // Quantity and price
                html += '<div class="price-and-quantity">';
                html += `<span class="quantity">${line.quantity || 0}</span>`;
                html += ' x ';
                html += `<span class="price">${line.price_display || line.price || 0}</span>`;
                
                // Discount
                if (line.discount) {
                    html += ` <span class="discount">(-${line.discount}%)</span>`;
                }
                
                // Line total
                html += `<span class="price_display pos-receipt-right-align">${line.price_display_with_tax || line.price_with_tax || 0}</span>`;
                html += '</div>';
                
                // Tax labels
                if (line.taxGroupLabels && Array.isArray(line.taxGroupLabels) && line.taxGroupLabels.length > 0) {
                    html += '<div class="tax-label">';
                    for (const label of line.taxGroupLabels) {
                        if (label) html += `<span>${label}</span>`;
                    }
                    html += '</div>';
                }
                
                html += '</div>';
            }
        }
        html += '</div>';
        
        // Total section
        html += '<div class="pos-receipt-amount">';
        
        // Subtotal
        if (receiptData.subtotal !== undefined) {
            html += '<div class="pos-receipt-subtotal">';
            html += `<span>Subtotal:</span>`;
            html += `<span class="pos-receipt-right-align">${receiptData.subtotal}</span>`;
            html += '</div>';
        }
        
        // Discount
        if (receiptData.total_discount) {
            html += '<div class="pos-receipt-discount">';
            html += `<span>Discount:</span>`;
            html += `<span class="pos-receipt-right-align">${receiptData.total_discount}</span>`;
            html += '</div>';
        }
        
        // Taxes
        if (receiptData.tax_details && Array.isArray(receiptData.tax_details) && receiptData.tax_details.length > 0) {
            for (const tax of receiptData.tax_details) {
                if (tax) {
                    html += '<div class="pos-receipt-tax">';
                    html += `<span>${tax.name || 'Tax'}:</span>`;
                    html += `<span class="pos-receipt-right-align">${tax.amount || 0}</span>`;
                    html += '</div>';
                }
            }
        }
        
        // Total
        html += '<div class="pos-receipt-total">';
        html += `<span>TOTAL:</span>`;
        html += `<span class="pos-receipt-right-align">${receiptData.total_with_tax || receiptData.total || 0}</span>`;
        html += '</div>';
        
        html += '</div>';
        
        // Payment Lines
        if (receiptData.paymentlines && Array.isArray(receiptData.paymentlines) && receiptData.paymentlines.length > 0) {
            html += '<div class="pos-receipt-payment-lines">';
            for (const payment of receiptData.paymentlines) {
                if (payment) {
                    html += '<div class="payment-line">';
                    html += `<span>${payment.name || 'Payment'}:</span>`;
                    html += `<span class="pos-receipt-right-align">${payment.amount || 0}</span>`;
                    html += '</div>';
                }
            }
            
            // Change
            if (receiptData.change) {
                html += '<div class="payment-line change">';
                html += `<span>Change:</span>`;
                html += `<span class="pos-receipt-right-align">${receiptData.change}</span>`;
                html += '</div>';
            }
            html += '</div>';
        }
        
        // Footer
        if (receiptData.footerData) {
            html += '<div class="pos-receipt-footer">';
            if (receiptData.footerData.footer) {
                html += `<div>${receiptData.footerData.footer}</div>`;
            }
            if (receiptData.ticket_code) {
                html += `<div class="pos-receipt-order-code">Ticket Code: ${receiptData.ticket_code}</div>`;
            }
            html += '</div>';
        }
        
        html += '</div>'; // Close pos-receipt
        
        // Add inline styles to match POS receipt appearance
        const styledHtml = `
        <style>
            .pos-receipt { font-family: monospace; max-width: 350px; margin: 0 auto; padding: 10px; }
            .pos-receipt-header { text-align: center; margin-bottom: 15px; }
            .pos-receipt-logo { max-width: 150px; margin-bottom: 10px; }
            .pos-receipt-company-name { font-size: 18px; font-weight: bold; margin: 5px 0; }
            .pos-receipt-contact, .pos-receipt-phone, .pos-receipt-vat { font-size: 12px; }
            .pos-receipt-order-data { margin: 15px 0; border-top: 1px dashed #000; border-bottom: 1px dashed #000; padding: 10px 0; }
            .orderlines { margin: 15px 0; }
            .orderline { margin-bottom: 10px; }
            .product-name { font-weight: bold; margin-bottom: 3px; }
            .price-and-quantity { display: flex; justify-content: space-between; font-size: 12px; }
            .discount { color: #e74c3c; }
            .tax-label { font-size: 10px; color: #666; margin-top: 2px; }
            .pos-receipt-amount { margin: 15px 0; border-top: 1px dashed #000; padding-top: 10px; }
            .pos-receipt-subtotal, .pos-receipt-discount, .pos-receipt-tax { display: flex; justify-content: space-between; margin: 5px 0; font-size: 13px; }
            .pos-receipt-total { display: flex; justify-content: space-between; margin: 10px 0; font-size: 16px; font-weight: bold; border-top: 1px solid #000; padding-top: 10px; }
            .pos-receipt-right-align { text-align: right; }
            .pos-receipt-payment-lines { margin: 15px 0; border-top: 1px dashed #000; padding-top: 10px; }
            .payment-line { display: flex; justify-content: space-between; margin: 5px 0; }
            .payment-line.change { font-weight: bold; border-top: 1px solid #000; padding-top: 5px; margin-top: 10px; }
            .pos-receipt-footer { text-align: center; margin-top: 15px; border-top: 1px dashed #000; padding-top: 10px; font-size: 11px; }
        </style>
        ${html}`;
        
        return styledHtml;
        
    } catch (error) {
        console.error('[Receipt Capture] Error:', error);
        return null;
    }
}
