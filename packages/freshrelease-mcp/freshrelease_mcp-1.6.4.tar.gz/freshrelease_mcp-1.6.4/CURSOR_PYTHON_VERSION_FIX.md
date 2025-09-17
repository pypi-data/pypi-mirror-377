# Cursor IDE MCP Tools Not Showing - Python Version Issue

## Problem Identified
The available tools aren't showing in Cursor settings because of a **Python version compatibility issue**.

**Current Python Version**: 3.9.6  
**Required Python Version**: 3.10+  
**Package**: freshrelease-mcp requires Python 3.10 or higher

## Solutions

### Solution 1: Install Python 3.10+ (Recommended)

#### Option A: Using Homebrew (macOS)
```bash
# Install Homebrew if not already installed
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

# Install Python 3.10+
brew install python@3.10

# Verify installation
python3.10 --version
```

#### Option B: Using pyenv (Cross-platform)
```bash
# Install pyenv
curl https://pyenv.run | bash

# Add to shell profile
echo 'export PYENV_ROOT="$HOME/.pyenv"' >> ~/.zshrc
echo 'command -v pyenv >/dev/null || export PATH="$PYENV_ROOT/bin:$PATH"' >> ~/.zshrc
echo 'eval "$(pyenv init -)"' >> ~/.zshrc

# Restart shell or source profile
source ~/.zshrc

# Install Python 3.10
pyenv install 3.10.12
pyenv global 3.10.12

# Verify installation
python --version
```

### Solution 2: Use the Source Code Directly

Since you have the source code, you can run it directly without installing the package:

#### Step 1: Install Dependencies
```bash
pip3 install httpx mcp pydantic
```

#### Step 2: Create a Wrapper Script
Create a file called `run_freshrelease_mcp.py`:

```python
#!/usr/bin/env python3
import sys
import os

# Add the source directory to Python path
sys.path.insert(0, '/Users/kmani/Documents/GitHub/personal/freshrelease_mcp/src')

# Import and run the server
from freshrelease_mcp.server import main

if __name__ == "__main__":
    main()
```

#### Step 3: Make it Executable
```bash
chmod +x run_freshrelease_mcp.py
```

#### Step 4: Update Cursor Configuration
```json
{
  "mcpServers": {
    "freshrelease-mcp": {
      "command": "python3",
      "args": ["/Users/kmani/Documents/GitHub/personal/freshrelease_mcp/run_freshrelease_mcp.py"],
      "env": {
        "FRESHRELEASE_API_KEY": "your_api_key_here",
        "FRESHRELEASE_DOMAIN": "your_domain.freshrelease.io",
        "FRESHRELEASE_PROJECT_KEY": "your_default_project_key_here"
      }
    }
  }
}
```

### Solution 3: Use Docker (Alternative)

#### Create a Dockerfile
```dockerfile
FROM python:3.10-slim

WORKDIR /app
COPY . .
RUN pip install freshrelease-mcp

CMD ["freshrelease-mcp"]
```

#### Run with Docker
```bash
docker build -t freshrelease-mcp .
docker run -e FRESHRELEASE_API_KEY=your_key \
           -e FRESHRELEASE_DOMAIN=your_domain.freshrelease.io \
           -e FRESHRELEASE_PROJECT_KEY=your_project_key \
           freshrelease-mcp
```

## Quick Fix (Recommended)

### Step 1: Install Python 3.10+
```bash
# Using Homebrew
brew install python@3.10
```

### Step 2: Install the Package
```bash
python3.10 -m pip install freshrelease-mcp
```

### Step 3: Update Cursor Configuration
```json
{
  "mcpServers": {
    "freshrelease-mcp": {
      "command": "python3.10",
      "args": ["-m", "freshrelease_mcp.server"],
      "env": {
        "FRESHRELEASE_API_KEY": "your_api_key_here",
        "FRESHRELEASE_DOMAIN": "your_domain.freshrelease.io",
        "FRESHRELEASE_PROJECT_KEY": "your_default_project_key_here"
      }
    }
  }
}
```

### Step 4: Restart Cursor IDE

## Verification Steps

### Test 1: Check Python Version
```bash
python3.10 --version
# Should show Python 3.10.x
```

### Test 2: Test Package Installation
```bash
python3.10 -c "import freshrelease_mcp.server; print('Success!')"
```

### Test 3: Test MCP Server
```bash
FRESHRELEASE_API_KEY="your_key" \
FRESHRELEASE_DOMAIN="your_domain.freshrelease.io" \
FRESHRELEASE_PROJECT_KEY="your_project_key" \
python3.10 -m freshrelease_mcp.server
```

## Why This Happens

1. **Python Version Requirement**: The package requires Python 3.10+
2. **System Python**: macOS often comes with older Python versions
3. **MCP Server Startup**: Cursor can't start the MCP server due to version incompatibility
4. **Tool Discovery**: If the server doesn't start, tools won't be discovered

## Alternative: Modify Package Requirements

If you want to use Python 3.9, you can modify the package requirements:

### Step 1: Edit pyproject.toml
```toml
requires-python = ">=3.9"
```

### Step 2: Rebuild and Install
```bash
python3 -m build
pip3 install dist/freshrelease_mcp-1.5.0-py3-none-any.whl --force-reinstall
```

**Note**: This might cause compatibility issues with some features that require Python 3.10+.

## Troubleshooting

### If tools still don't show:

1. **Check Cursor IDE logs**:
   - Help → Toggle Developer Tools
   - Look for MCP-related errors

2. **Verify MCP configuration**:
   - Ensure JSON is valid
   - Check environment variables

3. **Test server manually**:
   - Run the server outside Cursor
   - Check for error messages

4. **Restart Cursor IDE**:
   - Close completely
   - Reopen
   - Check MCP settings

## Support

If you continue having issues:
- Check the [GitHub repository](https://github.com/your-repo/freshrelease-mcp)
- Review the [PyPI package page](https://pypi.org/project/freshrelease-mcp/)
- Contact support at kalidass.mani@freshworks.com



