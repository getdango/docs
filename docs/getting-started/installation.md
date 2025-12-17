# Installation

This guide will help you install Dango on macOS, Linux, or Windows.

## Prerequisites

### Python 3.10-3.12 (Required)

!!! info "Recommended Version"
    **Python 3.11 or 3.12** are recommended for best performance and compatibility.

**Check if you have Python:**

=== "macOS / Linux"

    ```bash
    # Try these commands in order:
    python3.12 --version  # Check for Python 3.12
    python3.11 --version  # Check for Python 3.11
    python3.10 --version  # Check for Python 3.10

    # If any show "3.10" or higher, you're good!
    ```

=== "Windows"

    ```powershell
    python --version     # Should show 3.10 or higher
    ```

**Install Python if needed:**

=== "macOS"

    1. Install Homebrew (if you don't have it):
       ```bash
       /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
       ```

    2. Install Python:
       ```bash
       brew install python@3.11
       ```

    3. Verify:
       ```bash
       python3.11 --version
       ```

=== "Linux (Ubuntu/Debian)"

    ```bash
    sudo apt update
    sudo apt install python3.11 python3.11-venv python3-pip
    ```

=== "Linux (Fedora)"

    ```bash
    sudo dnf install python3.11
    ```

=== "Windows"

    - Download from [python.org](https://www.python.org/downloads/)
    - OR install from Microsoft Store (search "Python 3.11")
    - **Important:** Check "Add Python to PATH" during installation

### Docker Desktop (Required)

!!! warning "Required For"
    Docker is required for Metabase dashboards, Web UI, and dbt docs visualization.

**Install Docker Desktop:**

1. Download from [docs.docker.com/desktop](https://docs.docker.com/desktop/)
2. Install for your platform (macOS, Linux, or Windows)
3. Start Docker Desktop
4. Verify installation:

```bash
docker --version
```

### Disk Space Requirements

| Component | Space Required |
|-----------|----------------|
| Docker Desktop | ~4.5GB |
| Python packages | ~400MB |
| Dango platform | ~100MB |
| **Total Installation** | **~5GB** |

**Data Storage** (varies by data volume):

- Small datasets (< 100K rows): < 100MB
- Medium datasets (100K - 1M rows): 100MB - 1GB
- Large datasets (> 1M rows): 1GB+

!!! tip "Recommendation"
    Have at least **10GB free space** before installing.

### Supported Platforms

- macOS (Intel and Apple Silicon)
- Linux (Ubuntu 20.04+, Debian 11+, Fedora 35+)
- Windows 10/11

---

## Verify Prerequisites

Before installing, verify you have everything:

=== "macOS / Linux"

    ```bash
    # Check Python (any of these should work):
    python3.12 --version  # 3.12.x ✓
    python3.11 --version  # 3.11.x ✓
    python3.10 --version  # 3.10.x ✓

    # Check Docker (required):
    docker --version

    # Check disk space:
    df -h .
    ```

=== "Windows"

    ```powershell
    python --version     # Should show 3.10 or higher
    docker --version
    ```

---

## Installation Methods

### Quick Install (Recommended)

The bootstrap installer creates a project directory, sets up a virtual environment, and installs Dango automatically.

=== "macOS / Linux"

    ```bash
    curl -sSL https://getdango.dev/install.sh | bash
    ```

=== "Windows"

    ```powershell
    irm https://getdango.dev/install.ps1 | iex
    ```

The installer will:

1. Create a project directory
2. Set up an isolated virtual environment
3. Install Dango from PyPI
4. Initialize your project interactively

### What the Installer Does

The installer detects your situation and responds appropriately:

| Scenario | What Happens |
|----------|--------------|
| **Fresh install** | Creates project directory, sets up venv, installs Dango, runs `dango init` |
| **Run in existing directory** | Prompts for confirmation, creates venv in current directory |
| **Dango already installed** | Offers to upgrade to the latest version |
| **Existing project (e.g., cloned from GitHub)** | Detects existing structure, installs/upgrades Dango, skips init |

You'll be prompted at each decision point—nothing runs without your confirmation.

### Security-Conscious Installation

If you prefer to inspect the installer first:

=== "macOS / Linux"

    ```bash
    # Download the installer
    curl -sSL https://getdango.dev/install.sh -o install.sh

    # Review what it does
    cat install.sh

    # Run when ready
    bash install.sh
    ```

=== "Windows"

    ```powershell
    # Download the installer
    Invoke-WebRequest -Uri https://getdango.dev/install.ps1 -OutFile install.ps1

    # Review what it does
    Get-Content install.ps1

    # Run when ready
    .\install.ps1
    ```

View the installer source: [install.sh](https://github.com/getdango/dango/blob/main/install.sh) | [install.ps1](https://github.com/getdango/dango/blob/main/install.ps1)

### Manual Installation

If you prefer to set things up yourself:

=== "macOS / Linux"

    ```bash
    # Create project directory
    mkdir my-analytics
    cd my-analytics

    # Create virtual environment
    python3 -m venv venv
    source venv/bin/activate

    # Install Dango
    pip install getdango

    # Initialize project
    dango init
    ```

=== "Windows"

    ```powershell
    # Create project directory
    New-Item -ItemType Directory -Path my-analytics
    Set-Location my-analytics

    # Create virtual environment
    python -m venv venv
    .\venv\Scripts\Activate.ps1

    # Install Dango
    pip install getdango

    # Initialize project
    dango init
    ```

---

## Verify Installation

After installation, verify Dango is working:

=== "macOS / Linux"

    ```bash
    # Activate virtual environment (if not already active)
    cd my-analytics
    source venv/bin/activate

    # Check version
    dango --version
    # Should show: dango, version X.X.X

    # Check installation
    dango validate
    ```

=== "Windows"

    ```powershell
    # Activate virtual environment (if not already active)
    cd my-analytics
    .\venv\Scripts\Activate.ps1

    # Check version
    dango --version
    # Should show: dango, version X.X.X

    # Check installation
    dango validate
    ```

---

## Upgrading Dango

### Automatic Upgrade (Recommended)

If you installed with the bootstrap script:

```bash
cd your-project
curl -sSL https://getdango.dev/install.sh | bash
# Select [u] to upgrade when prompted
```

### Manual Upgrade

=== "macOS / Linux"

    ```bash
    cd your-project
    source venv/bin/activate

    # Upgrade to latest version
    pip install --upgrade getdango

    # Verify new version
    dango --version
    ```

=== "Windows"

    ```powershell
    cd your-project
    .\venv\Scripts\Activate.ps1

    # Upgrade to latest version
    pip install --upgrade getdango

    # Verify new version
    dango --version
    ```

### After Upgrading

```bash
# Validate project still works
dango validate

# Restart the platform
dango stop
dango start
```

!!! warning "Breaking Changes"
    Check [CHANGELOG.md](https://github.com/getdango/dango/blob/main/CHANGELOG.md) for breaking changes between versions.

---

## Uninstall

### Virtual Environment Installation

If you installed in a virtual environment (recommended), simply delete the project directory:

=== "macOS / Linux"

    ```bash
    rm -rf my-analytics/
    ```

=== "Windows"

    ```powershell
    Remove-Item -Recurse -Force my-analytics
    ```

That's it! Everything (venv, data, config) is contained in the project directory.

### Global Installation

If you installed globally:

**Step 1: Find which Python has Dango**

=== "macOS / Linux"

    ```bash
    # Check each Python version
    python3.11 -m pip list | grep getdango
    python3.10 -m pip list | grep getdango
    python3 -m pip list | grep getdango

    # Or find the command location
    which dango
    # Example output: /Users/you/Library/Python/3.11/bin/dango
    # This means use python3.11
    ```

=== "Windows"

    ```powershell
    # Check Python versions
    python -m pip list | findstr getdango
    py -3.11 -m pip list | findstr getdango
    ```

**Step 2: Uninstall Dango**

=== "macOS / Linux"

    ```bash
    # Use the Python version that has it (e.g., python3.11)
    python3.11 -m pip uninstall getdango
    ```

=== "Windows"

    ```powershell
    python -m pip uninstall getdango
    ```

### Remove Docker Containers (Optional)

If you're done with Dango entirely:

```bash
# List running containers
docker ps

# Stop Metabase container
docker stop <metabase-container-id>

# Remove Metabase image (saves disk space)
docker rmi metabase/metabase
```

---

## Next Steps

Now that Dango is installed:

1. **[Quick Start](quick-start.md)** - Get your first pipeline running
2. **[Troubleshooting](troubleshooting.md)** - If you encounter issues
3. **[Core Concepts](../core-concepts/index.md)** - Learn about Dango's architecture

---

## Need Help?

If installation fails:

1. Check the **[Troubleshooting](troubleshooting.md)** guide
2. Search [GitHub Issues](https://github.com/getdango/dango/issues)
3. Open a new issue with your error message
