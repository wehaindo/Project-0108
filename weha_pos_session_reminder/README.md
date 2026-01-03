# POS Session Date Reminder

## Overview

This module provides a warning mechanism for POS users when they try to access a POS session whose date doesn't match the current date.

## Features

- **Automatic Date Check**: When users access the POS login screen, the system automatically checks if the session date matches today's date
- **Warning Dialog**: If dates don't match, a clear warning dialog appears
- **User Guidance**: The warning reminds users to close the old session before proceeding

## Technical Details

- **Depends on**: `pos_hr`, `point_of_sale`
- **Inherits**: POS HR Login Screen component
- **Date Comparison**: Uses JavaScript date comparison on the client side

## Usage

1. Install the module
2. When accessing POS, if a session from a previous date is open, users will see a warning
3. Users should close the old session and start a new one for the current date

## Configuration

No configuration needed - the module works automatically after installation.
