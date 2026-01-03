# Fix Duplicate Bank Partner IDs

## Overview

This module fixes computation errors in the `duplicate_bank_partner_ids` field of the `res.partner.bank` model in Odoo 18.0.

## Problem

The original `_compute_duplicate_bank_partner_ids` method in the `account` module can sometimes fail due to:
- Edge cases with empty recordsets
- Null values in SQL array aggregations
- Issues with new (unsaved) records
- Database query errors

These errors can cause crashes when viewing or editing bank accounts.

## Solution

This module inherits `res.partner.bank` and overrides the `_compute_duplicate_bank_partner_ids` method with:

1. **Empty recordset handling**: Properly handles cases where `self.ids` is empty
2. **Null value filtering**: Removes None values from the aggregated partner IDs
3. **Error handling**: Wraps the computation in try-except to prevent crashes
4. **Proper origin handling**: Uses `bank._origin.id` for new records
5. **Logging**: Logs warnings when errors occur for debugging

## Installation

1. Copy this module to your Odoo addons directory
2. Update the apps list in Odoo
3. Install the "Fix Duplicate Bank Partner IDs" module

## Dependencies

- `account` module (Odoo 18.0)

## Technical Details

The fix ensures that even if the SQL query fails or returns unexpected results, the field computation will gracefully handle the error and set an empty value instead of crashing.

## License

LGPL-3
