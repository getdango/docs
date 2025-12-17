# Changelog

Version history and release notes for Dango.

---

## Version Numbering

Dango follows [Semantic Versioning](https://semver.org/):

- **MAJOR.MINOR.PATCH** (e.g., 0.1.0)
- **MAJOR**: Breaking changes
- **MINOR**: New features (backwards compatible)
- **PATCH**: Bug fixes

---

## Current Version

### v0.1.0 (Current)

*Released: December 17, 2025*

**Status**: MVP Release - First stable release for early adopters

This is the v0.1.0 MVP release marking Dango as ready for early adopters.

#### What's New in v0.1.0

- **Google Ads** - Full OAuth support (tested and working)
- **Shorter install URLs** - Now available at `getdango.dev/install.sh`
- **Windows support** - Fully tested and documented

#### Features

**Data Ingestion**
- 8 wizard-supported data sources with guided setup
  - CSV files
  - Stripe
  - Google Sheets
  - Google Analytics (GA4)
  - Facebook Ads
  - Google Ads
  - REST API
  - dlt Native
- 25+ additional sources via dlt native configuration
- File watcher for automatic CSV sync
- OAuth authentication for Google and Facebook

**Transformations**
- Auto-generated dbt staging models
- Support for custom intermediate and mart models
- dbt test integration
- dbt docs generation

**Storage**
- DuckDB warehouse
- Automatic schema management
- Incremental loading support

**Visualization**
- Metabase integration
- Auto-provisioned dashboards
- Dashboard export/import

**CLI**
- 30+ CLI commands
- Web UI for monitoring
- Source management wizard

#### Known Limitations

- Local deployment only (cloud support planned)
- Single-user (no team features)
- Shopify source blocked due to OAuth issue

---

## Previous Releases

### v0.0.5

*Released: December 8, 2025*

- `dango sync --dry-run` to preview without executing
- Unreferenced custom sources warning
- Better validation output (database check, model count)

---

## Planned Releases

### v0.2.0 (Planned)

*Target: Q2 2025*

**Focus**: Production readiness

Planned features:
- [ ] Production deployment guides
- [ ] Team collaboration features
- [ ] Enhanced monitoring
- [ ] Performance optimizations

### Future

- Cloud deployment options
- More data source wizards
- Scheduling and orchestration
- Enterprise features

---

## Upgrade Guide

### Upgrading Dango

```bash
# Check current version
dango --version

# Upgrade to latest
pip install --upgrade getdango

# Verify upgrade
dango --version
```

### Breaking Changes

When a release has breaking changes, we'll document:
1. What changed
2. How to migrate
3. Deprecation timeline

---

## Release Process

### How Releases Work

1. Features developed on feature branches
2. Merged to main after review
3. Tagged releases published to PyPI
4. Release notes added to this changelog

### Release Cadence

- **Patch releases**: As needed for bug fixes
- **Minor releases**: Monthly or as features complete
- **Major releases**: When breaking changes are necessary

---

## Contributing

Want to contribute to the next release?

- [Report bugs](https://github.com/getdango/dango/issues/new)
- [Suggest features](https://github.com/getdango/dango/discussions)
- [Submit pull requests](https://github.com/getdango/dango/pulls)

See the [Contributing Guide](https://github.com/getdango/docs/blob/main/CONTRIBUTING.md) for details.

---

## Links

- [GitHub Releases](https://github.com/getdango/dango/releases)
- [PyPI Package](https://pypi.org/project/getdango/)
- [GitHub Issues](https://github.com/getdango/dango/issues)
