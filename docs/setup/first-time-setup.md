# First-Time Setup Guide

Complete setup guide for the agent-native enrichment prototype. This guide prioritizes modern tooling (UV, DataGen CLI) for the best developer experience.

---

## Prerequisites by Operating System

### macOS (Recommended Path)

```bash
# 1. Install Homebrew (if not already installed)
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

# 2. Install UV (fast Python package manager)
brew install uv

# 3. Install Git
brew install git

# 4. Verify installations
uv --version    # Should show UV version
git --version   # Should show Git version
```

### Windows

```powershell
# 1. Install UV via PowerShell (Run as Administrator)
powershell -c "irm https://astral.sh/uv/install.ps1 | iex"

# 2. Install Git
# Download from: https://git-scm.com/download/win
# Or via Chocolatey:
choco install git

# 3. Verify installations
uv --version
git --version
```

### Linux (Ubuntu/Debian)

```bash
# 1. Install UV
curl -LsSf https://astral.sh/uv/install.sh | sh

# 2. Install Git
sudo apt update
sudo apt install git -y

# 3. Verify installations
uv --version
git --version
```

### Linux (Fedora/RHEL)

```bash
# 1. Install UV
curl -LsSf https://astral.sh/uv/install.sh | sh

# 2. Install Git
sudo dnf install git -y

# 3. Verify installations
uv --version
git --version
```

---

## Step 1: Clone Repository (Optional)

If you don't have the project yet:

```bash
# Clone the repository
git clone <repository-url>
cd agent-native-prototype
```

If you already have the project, just navigate to it:

```bash
cd /path/to/agent-native-prototype
```

---

## Step 2: Python Environment Setup (UV Method)

UV automatically manages Python versions and dependencies. No need to install Python manually!

```bash
# 1. Create virtual environment (UV handles Python installation automatically)
uv venv

# 2. Activate virtual environment
# macOS/Linux:
source .venv/bin/activate

# Windows:
.venv\Scripts\activate

# 3. Install all dependencies
uv pip install -r requirements.txt

# 4. Verify key packages are installed
uv pip list | grep datagen
uv pip list | grep pydantic
uv pip list | grep openai
```

**Expected output:**
```
datagen-python-sdk   0.1.1
pydantic            2.12.5
openai              2.15.0
```

✅ **Success indicator**: All packages listed above should appear.

---

## Step 3: DataGen CLI Installation

Install the DataGen CLI globally (not in venv):

### One-Line Installation (macOS/Linux)

```bash
curl -fsSL https://cli.datagen.dev/install.sh | sh
```

This installs to `/usr/local/bin` or `~/.local/bin`.

### From Source (Advanced)

```bash
git clone https://github.com/datagendev/datagen-cli
cd datagen-cli
go mod download
go build -o datagen
# Move to PATH location
sudo mv datagen /usr/local/bin/
```

### Verify Installation

```bash
datagen --help
```

**Expected output**: DataGen CLI help text with available commands.

---

## Step 4: DataGen Authentication

```bash
# 1. Login to DataGen (opens browser or prompts for API key)
datagen login

# 2. IMPORTANT: Restart your terminal or source your shell profile
# macOS/Linux (zsh):
source ~/.zshrc

# macOS/Linux (bash):
source ~/.bashrc

# Windows: Close and reopen PowerShell/Terminal

# 3. Verify authentication
datagen whoami
```

**Expected output**: Your DataGen account email/username.

### Manual API Key Setup (Alternative)

If `datagen login` doesn't work, manually add to `.env`:

```bash
# Create .env file in project root
cat > .env << 'EOF'
DATAGEN_API_KEY=your_api_key_here
EOF
```

Get your API key from: https://app.datagen.dev/settings/api-keys

---

## Step 5: MCP Server Setup (Optional but Recommended)

Enable DataGen tools in Claude Desktop and other AI IDEs:

```bash
# Configure MCP server for Claude Desktop/Codex/Gemini
datagen mcp
```

This automatically updates your MCP configuration files.

### Manual MCP Configuration (Alternative)

If you prefer manual setup, add to `~/Library/Application Support/Claude/claude_desktop_config.json` (macOS):

```json
{
  "mcpServers": {
    "datagen": {
      "command": "datagen",
      "args": ["mcp"],
      "env": {
        "DATAGEN_API_KEY": "your_api_key_here"
      }
    }
  }
}
```

**Restart Claude Desktop** after configuration.

---

## Step 6: Verification & Testing

Let's verify everything works:

```bash
# 1. Activate venv (if not already active)
source .venv/bin/activate

# 2. List available lead tables
python scripts/graph_enrich.py --lead example-leads --list

# 3. Run a test enrichment (3 sample rows)
python scripts/graph_enrich.py --lead example-leads --workflow test_workflow --preview --limit 3
```

**Expected output**:
- List of available nodes and workflows
- Preview enrichment completes successfully

### Troubleshooting Common Issues

| Issue | Solution |
|-------|----------|
| `ModuleNotFoundError: pydantic` | Run `uv pip install -r requirements.txt` again |
| `DATAGEN_API_KEY not set` | Restart terminal after `datagen login` or check `.env` file |
| `datagen: command not found` | Add `~/.local/bin` to PATH or verify installation directory |
| `No module named 'datagen_sdk'` | Make sure venv is activated: `source .venv/bin/activate` |
| Web research timeouts | Check internet connection and DataGen API status |

---

## Step 7: Quick Reference Commands

### Daily Workflow

```bash
# Start working (activate venv)
source .venv/bin/activate

# Run enrichment
python scripts/graph_enrich.py --lead <lead-name> --workflow <workflow-name>

# Deactivate when done
deactivate
```

### Package Management with UV

```bash
# Install new package
uv pip install <package-name>

# Update requirements.txt after installing
uv pip freeze > requirements.txt

# Upgrade all packages
uv pip install -r requirements.txt --upgrade

# Run Python script directly (without activating venv)
uv run python scripts/graph_enrich.py --help
```

### DataGen CLI

```bash
# Check authentication
datagen whoami

# Re-authenticate
datagen login

# View available commands
datagen --help
```

---

## Alternative: Traditional Python Setup (Without UV)

If you prefer the traditional Python/pip approach:

```bash
# 1. Install Python 3.13+ from python.org (or via package manager)

# 2. Create virtual environment
python3 -m venv .venv

# 3. Activate
source .venv/bin/activate  # macOS/Linux
# or
.venv\Scripts\activate     # Windows

# 4. Install dependencies
pip install -r requirements.txt

# 5. Verify
pip list | grep datagen
```

**Note**: UV is recommended for better performance and automatic Python version management.

---

## Next Steps

✅ **Setup Complete!** You're ready to enrich leads.

**Learn More:**
- [Enrichment Skill Guide](../.claude/skills/enrichment/SKILL.md) - How to run enrichment workflows
- [Creating Custom Nodes](../examples/node_templates.md) - Build your own enrichment nodes
- [Workflow Examples](../examples/workflow_examples.md) - Pre-built workflow patterns

**Need Help?**
- Check [Troubleshooting Guide](./troubleshooting.md)
- Review [Architecture Documentation](../../CLAUDE.md)
- Open an issue on GitHub
