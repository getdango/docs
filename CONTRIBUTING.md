# Contributing to Dango Documentation

Thank you for your interest in contributing to the Dango documentation! This guide will help you get started.

## Table of Contents

- [Code of Conduct](#code-of-conduct)
- [Getting Started](#getting-started)
- [Development Workflow](#development-workflow)
- [Branch Naming Convention](#branch-naming-convention)
- [Commit Message Guidelines](#commit-message-guidelines)
- [Pull Request Process](#pull-request-process)
- [Documentation Standards](#documentation-standards)
- [Testing](#testing)

---

## Code of Conduct

Be respectful, inclusive, and constructive in all interactions. We're building an open-source community where everyone feels welcome to contribute.

---

## Getting Started

### Prerequisites

- Python 3.10+
- Git
- Text editor or IDE

### Local Setup

1. **Clone the repository**:
   ```bash
   git clone https://github.com/getdango/docs.git
   cd docs
   ```

2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Serve locally**:
   ```bash
   mkdocs serve
   ```

   Open http://localhost:8000 to view the documentation.

4. **Build the site**:
   ```bash
   mkdocs build
   ```

---

## Development Workflow

### Quick Start

```bash
# 1. Pull latest changes
git checkout main
git pull origin main

# 2. Create feature branch (see naming convention below)
git checkout -b <type>/$(date +%Y-%m-%d)-<description>

# 3. Make your changes
# Edit files in docs/ directory

# 4. Test locally
mkdocs serve

# 5. Commit your changes
git add .
git commit -m "Your descriptive commit message"

# 6. Push to remote
git push -u origin $(git branch --show-current)

# 7. Create Pull Request on GitHub
```

---

## Branch Naming Convention

**Format**: `<type>/<date>-<description>`

### Branch Types

- `feature/` - New features or major additions (e.g., new documentation sections)
- `fix/` - Bug fixes or corrections
- `docs/` - Documentation updates or improvements
- `chore/` - Maintenance tasks (dependencies, tooling, CI/CD)
- `refactor/` - Restructuring without changing functionality

### Examples

```bash
feature/2025-12-08-getting-started-section
feature/2025-12-08-data-sources-docs
fix/2025-12-09-broken-links-homepage
docs/2025-12-09-update-installation-guide
chore/2025-12-10-update-mkdocs-version
```

### Creating a Branch

```bash
# Automatic date insertion (recommended)
git checkout -b feature/$(date +%Y-%m-%d)-your-feature-name

# Manual
git checkout -b fix/2025-12-09-your-fix-description
```

---

## Commit Message Guidelines

### Format

```
<type>: <subject>

<body> (optional)

<footer> (optional)
```

### Rules

1. **Use imperative mood** - "Add feature" not "Added feature"
2. **Keep first line under 72 characters**
3. **Reference issues when applicable** - "Fix navigation bug (#123)"
4. **Be descriptive but concise**

### Examples

**Good**:
```
Add Getting Started section

Includes installation, quick start, and troubleshooting guides

Closes #45
```

```
Fix broken links in installation guide
```

```
Update mkdocs.yml navigation structure
```

**Avoid**:
```
Updated stuff
```

```
Fixed things, added some docs, and other changes
```

---

## Pull Request Process

### Before Submitting

1. **Test locally**: Run `mkdocs serve` and verify all pages render correctly
2. **Check links**: Ensure all internal and external links work
3. **Review changes**: Double-check for typos, formatting issues, and accuracy
4. **Build succeeds**: Run `mkdocs build` without errors

### Creating a Pull Request

1. **Push your branch** to origin
   ```bash
   git push -u origin $(git branch --show-current)
   ```

2. **Go to GitHub** - https://github.com/getdango/docs

3. **Click "New Pull Request"**

4. **Select your branch** from the dropdown

5. **Fill in PR template**:
   - **Title**: Clear, descriptive summary (e.g., "Add troubleshooting guide for OAuth sources")
   - **Description**:
     - What changes were made?
     - Why were these changes necessary?
     - Any related issues? (e.g., "Fixes #123")
     - Screenshots (if applicable)

6. **Request review** from maintainers

### PR Review Process

- Maintainers will review your PR within 48 hours
- Address any requested changes by pushing new commits to your branch
- Once approved, a maintainer will merge your PR
- Your branch will be deleted after merge

### After Merge

```bash
# Switch back to main
git checkout main

# Pull latest changes
git pull origin main

# Delete your local branch
git branch -d <your-branch-name>
```

---

## Documentation Standards

### Writing Style

- **Clear and concise** - Avoid jargon when possible
- **Active voice** - "Dango creates..." not "The data is created by Dango..."
- **Second person** - Use "you" to address the reader
- **Present tense** - "The command runs..." not "The command will run..."

### Formatting

- **Use code blocks** for commands, code, and configuration files
- **Add language hints** to code blocks for syntax highlighting:
  ````markdown
  ```bash
  dango init
  ```

  ```python
  import dango
  ```

  ```yaml
  sources:
    - name: example
  ```
  ````

- **Use admonitions** for notes, warnings, and tips:
  ```markdown
  !!! note
      This is a helpful note.

  !!! warning
      This is a warning about potential issues.

  !!! tip
      This is a pro tip for users.
  ```

- **Link to related pages** using relative paths:
  ```markdown
  See [Installation Guide](../getting-started/installation.md) for setup instructions.
  ```

### Accuracy

**Critical**: All documentation must accurately reflect the actual Dango codebase.

- **Never document commands that don't exist**
- **Verify command flags** against the actual CLI implementation
- **Test code examples** before publishing
- **Cross-reference with source code** when documenting features

When in doubt, check the Dango codebase at https://github.com/getdango/dango

### File Organization

```
docs/
├── index.md                    # Homepage
├── getting-started/            # Installation, quick start, troubleshooting
├── core-concepts/              # Architecture, data layers, CLI overview
├── data-sources/               # CSV, OAuth, database, custom sources
├── transformations/            # dbt basics, staging, custom models, testing
├── dashboards/                 # Metabase overview, creating dashboards, SQL queries
├── web-ui/                     # Web UI overview, managing sources, monitoring
├── cli/                        # CLI reference, commands by category
├── reference/                  # API reference, configuration files
└── community/                  # Contributing, support, resources
```

---

## Testing

### Local Testing

```bash
# Serve locally and test in browser
mkdocs serve

# Build to verify no errors
mkdocs build

# Check for broken links (if tool installed)
linkchecker http://localhost:8000
```

### What to Test

1. **All pages render correctly** - No formatting issues
2. **All internal links work** - Navigate between pages
3. **All code blocks display properly** - Syntax highlighting works
4. **All admonitions render** - Notes, warnings, tips
5. **Navigation is correct** - Sidebar and tabs
6. **Search works** - Try searching for key terms

---

## Questions?

- **Documentation Issues**: https://github.com/getdango/docs/issues
- **General Questions**: https://github.com/getdango/dango/discussions
- **Main Dango Repo**: https://github.com/getdango/dango

---

Thank you for contributing to Dango documentation!
