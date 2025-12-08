# Dango Documentation Website

Official documentation for Dango - Open Source Data Platform

**Status**: In Development

## Repository Information

- **Live URL**: https://docs.getdango.dev (coming soon)
- **Framework**: MkDocs Material
- **Deployment**: Cloudflare Pages

## Development

### Local Setup

```bash
# Install dependencies
pip install -r requirements.txt

# Serve locally
mkdocs serve

# Build site
mkdocs build
```

### Git Workflow

**Branch Protection**:
- `main` branch is protected
- All changes must go through Pull Requests
- Force pushes are blocked

**Branch Naming Convention**:

Format: `YYYY-MM-DD/<type>/<short-description>`

**Types**:
- `feature/` - New features or major additions (e.g., new documentation sections)
- `fix/` - Bug fixes or corrections
- `docs/` - Documentation updates or improvements
- `chore/` - Maintenance tasks (dependencies, tooling, CI/CD)
- `refactor/` - Restructuring without changing functionality

**Examples**:
- `2025-12-08/feature/getting-started-section`
- `2025-12-08/feature/data-sources-docs`
- `2025-12-09/fix/broken-links-homepage`
- `2025-12-09/docs/update-installation-guide`
- `2025-12-10/chore/update-mkdocs-version`

**Workflow Steps**:

1. **Pull latest main**:
   ```bash
   git checkout main
   git pull origin main
   ```

2. **Create feature branch**:
   ```bash
   git checkout -b $(date +%Y-%m-%d)/feature/your-feature-name
   ```

3. **Make changes and commit**:
   ```bash
   git add .
   git commit -m "Your descriptive commit message"
   ```

4. **Push to remote**:
   ```bash
   git push -u origin $(git branch --show-current)
   ```

5. **Create Pull Request**:
   - Go to https://github.com/getdango/docs
   - Click "New Pull Request"
   - Select your branch
   - Fill in PR description
   - Request review

6. **After PR is merged**:
   ```bash
   git checkout main
   git pull origin main
   git branch -d <your-branch-name>
   ```

### Commit Message Guidelines

- Use imperative mood ("Add feature" not "Added feature")
- Keep first line under 72 characters
- Reference issues when applicable: "Fix navigation bug (#123)"
- Use clear, descriptive messages

**Examples**:
- `Add Getting Started section`
- `Fix broken links in installation guide`
- `Update mkdocs.yml configuration`
- `Refactor navigation structure`

## Project Plan

See `/Users/aaronteoh/Desktop/code/getdango/DOCS_WEBSITE_PLAN.md` for the complete implementation plan.

## Related Repositories

- **Main Application**: https://github.com/getdango/dango
- **Marketing Website**: https://github.com/getdango/website

---

**Last Updated**: December 8, 2025
