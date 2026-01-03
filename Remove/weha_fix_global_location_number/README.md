# Fix Global Location Number

## Overview

This module fixes errors related to the `global_location_number` field in the `res.partner` model in Odoo 18.0.

## Problem

The `global_location_number` field is defined in the `account_add_gln` module, but can cause issues when:
- The module is not installed
- The field is referenced but undefined
- There are conflicts with other modules trying to use this field
- The module installation fails but other modules depend on this field

## Solution

This module ensures the `global_location_number` field exists on `res.partner` by:

1. **Field definition**: Explicitly defines the GLN field with proper attributes
2. **Validation**: Adds optional validation to warn about invalid GLN formats
3. **Flexibility**: Allows the field to exist independently of `account_add_gln`
4. **Error handling**: Gracefully handles validation errors with logging instead of blocking

## Features

- **GLN Field**: String field to store Global Location Number
- **Format validation**: Warns if GLN is not 13 digits (standard format)
- **Flexible**: Accepts any string value but logs warnings for non-standard formats
- **Non-blocking**: Does not prevent saving, only logs warnings

## Global Location Number (GLN)

A GLN is a 13-digit number used to uniquely identify:
- Legal entities
- Functions or departments within a company
- Physical locations

It's part of the GS1 system of standards used globally for supply chain management.

## Installation

1. Copy this module to your Odoo addons directory
2. Update the apps list in Odoo
3. Install the "Fix Global Location Number" module

## Dependencies

- `base` module
- `account` module

## Technical Details

The module can coexist with `account_add_gln` if it gets installed later. The field definition will merge properly through Odoo's inheritance mechanism.

## License

LGPL-3
