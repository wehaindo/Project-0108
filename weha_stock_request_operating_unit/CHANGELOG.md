# Changelog

All notable changes to the Stock Request Operating Unit module will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.0.0] - 2026-01-11

### Added
- Initial release of Stock Request Operating Unit module
- Operating unit field on `stock.request` model (required)
- Operating unit field on `stock.request.order` model (required)
- Default operating unit from user settings
- Automatic operating unit propagation from order to requests
- Automatic operating unit propagation from request to stock moves
- Automatic operating unit propagation to procurement groups
- Company-based domain restriction on operating unit selection
- Operating unit reset when company changes
- Stock request link field on `stock.move` model
- Stock request smart button on `stock.picking` model
- Stock request count field on picking
- Enhanced form views with operating unit field
- Enhanced tree views with operating unit column (optional)
- Enhanced search views with operating unit filters
- Group by operating unit functionality
- Multi-operating unit security rules for stock.request
- Multi-operating unit security rules for stock.request.order
- Security group for stock request operating unit access
- Comprehensive README documentation
- Technical documentation (MODULE_STRUCTURE.md)
- Quick installation guide (INSTALLATION_GUIDE.md)
- HTML description page for Apps menu
- Complete module structure with proper OCA compliance

### Dependencies
- stock_request (OCA) >= 18.0.1.1.3
- operating_unit (OCA) >= 18.0
- stock_operating_unit (OCA) >= 18.0

### Technical Details
- Models: 4 files (stock_request, stock_request_order, stock_move, stock_picking)
- Views: 2 files (stock_request_views, stock_request_order_views)
- Security: 1 file (stock_request_security)
- Documentation: 5 files (README, MODULE_STRUCTURE, INSTALLATION_GUIDE, CREATION_SUMMARY, CHANGELOG)

### Integration Points
- Integrates with OCA's operating_unit framework
- Integrates with OCA's stock_operating_unit module
- Integrates with OCA's stock_request module
- Compatible with multi-company and multi-operating unit setups

### Use Cases Supported
- Multi-store replenishment (Store → DC → Supplier)
- Department-based stock management
- Multi-branch operations with shared warehouse
- Operating unit-based inventory tracking
- Operating unit-based accounting and reporting

### Known Limitations
- None

### Notes
- This is the initial stable release
- Tested with Odoo 18.0
- Follows OCA coding standards and guidelines
- LGPL-3 licensed

---

## Future Versions (Planned)

### [1.1.0] - TBD
- Operating unit-based approval workflows
- Operating unit stock limit rules
- Dashboard for operating unit stock requests
- Email notifications by operating unit

### [1.2.0] - TBD
- Operating unit-based reordering rules integration
- Automatic operating unit assignment based on location
- Operating unit stock request templates
- Enhanced reporting and analytics

---

## Version Compatibility Matrix

| Module Version | Odoo Version | OCA operating_unit | OCA stock_request |
|----------------|--------------|-------------------|-------------------|
| 1.0.0          | 18.0         | 18.0.x           | 18.0.1.1.3+      |

---

## Migration Notes

### Migrating to v1.0.0
- First release, no migration needed
- Install prerequisites before installing this module
- Configure operating units before creating stock requests
- Assign operating units to existing users

---

## Support & Contact

- **Author**: Weha
- **Website**: https://weha-id.com
- **License**: LGPL-3
- **Repository**: Private
- **Issues**: Contact your Odoo implementation partner

---

**Last Updated**: January 11, 2026
