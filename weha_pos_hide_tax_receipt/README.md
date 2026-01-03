# POS Hide Tax on Receipt

This module hides tax information from POS receipts.

## Features

- Hides tax lines from receipt
- Hides tax details section
- Shows only total amount without tax breakdown
- Works for both regular receipts and bill/invoice receipts

## Installation

1. Copy this module to your Odoo addons directory
2. Update the apps list
3. Install "POS Hide Tax on Receipt"
4. Restart POS session

## Configuration

No configuration needed. Tax information will be automatically hidden on all receipts after installation.

## Technical Details

- Inherits POS receipt templates (XML and OWL)
- Patches Order model to remove tax_details from receipt data
- Compatible with Odoo 18.0

## Usage

After installation, all POS receipts will show:
- Product lines with total price
- Subtotal
- Total amount
- NO tax breakdown or details

## Author

Your Company
