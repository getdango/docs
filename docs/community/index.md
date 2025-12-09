# Community

Get help, contribute, and connect with other Dango users.

---

## Get Help

<div class="grid cards" markdown>

-   :material-github: **GitHub Issues**

    ---

    Report bugs, request features, or ask questions.

    [:octicons-arrow-right-24: Open an Issue](https://github.com/getdango/dango/issues)

-   :material-chat-question-outline: **GitHub Discussions**

    ---

    Ask questions, share ideas, and connect with the community.

    [:octicons-arrow-right-24: Join Discussions](https://github.com/getdango/dango/discussions)

</div>

---

## Contributing

We welcome contributions! See the [Contributing Guide](https://github.com/getdango/docs/blob/main/CONTRIBUTING.md) for details.

### Ways to Contribute

- **Report Bugs** - Found an issue? [Open a bug report](https://github.com/getdango/dango/issues/new)
- **Suggest Features** - Have an idea? [Start a discussion](https://github.com/getdango/dango/discussions)
- **Improve Docs** - Fix typos or add examples in [getdango/docs](https://github.com/getdango/docs)
- **Submit Code** - Fix bugs or add features via pull request

### Development Setup

```bash
# Clone the repository
git clone https://github.com/getdango/dango.git
cd dango

# Install in development mode
pip install -e ".[dev]"

# Run tests
pytest
```

---

## Resources

| Resource | Link |
|----------|------|
| GitHub Repository | [github.com/getdango/dango](https://github.com/getdango/dango) |
| Documentation Repo | [github.com/getdango/docs](https://github.com/getdango/docs) |
| PyPI Package | [pypi.org/project/getdango](https://pypi.org/project/getdango/) |
| Issue Tracker | [GitHub Issues](https://github.com/getdango/dango/issues) |

---

## Current Version

**Dango v0.0.5** (MVP)

### What's Working

- 8 wizard-supported data sources (CSV, Stripe, Google Sheets, GA4, Facebook Ads, Google Ads, REST API, dlt Native)
- 25+ manual dlt sources via `dlt_native` configuration
- Auto-generated dbt staging models
- DuckDB warehouse
- Metabase dashboards
- Web UI for monitoring
- File watcher for auto-sync

### Roadmap

Planned for upcoming releases:

- **v0.1.0**: Google Ads wizard support, improved error handling
- **v0.2.0**: Production deployment guides, team collaboration features
- **Future**: Cloud deployment options, more data source wizards

---

## License

Dango is open source under the [Apache 2.0 License](https://github.com/getdango/dango/blob/main/LICENSE).
