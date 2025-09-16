# Cursor IDE MCP Tools Not Showing - Complete Solution

## 🔍 Problem Identified

**Root Cause**: Python version incompatibility
- **Your Python Version**: 3.9.6
- **Required Version**: 3.10+
- **Impact**: MCP server cannot start, so tools don't appear in Cursor IDE

## 🚀 Solution Options

### Option 1: Install Python 3.10+ (RECOMMENDED)

#### Step 1: Install Python 3.10 using Homebrew
```bash
# Install Homebrew if not already installed
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

# Install Python 3.10
brew install python@3.10

# Verify installation
python3.10 --version
```

#### Step 2: Install the MCP package
```bash
python3.10 -m pip install freshrelease-mcp
```

#### Step 3: Configure Cursor IDE
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

#### Step 4: Restart Cursor IDE

### Option 2: Use pyenv (Alternative)

#### Step 1: Install pyenv
```bash
curl https://pyenv.run | bash

# Add to shell profile
echo 'export PYENV_ROOT="$HOME/.pyenv"' >> ~/.zshrc
echo 'command -v pyenv >/dev/null || export PATH="$PYENV_ROOT/bin:$PATH"' >> ~/.zshrc
echo 'eval "$(pyenv init -)"' >> ~/.zshrc

# Restart shell
source ~/.zshrc
```

#### Step 2: Install Python 3.10
```bash
pyenv install 3.10.12
pyenv global 3.10.12
python --version  # Should show 3.10.12
```

#### Step 3: Install package and configure
```bash
pip install freshrelease-mcp
```

Then use the same Cursor configuration as Option 1.

### Option 3: Modify Package for Python 3.9 (Advanced)

#### Step 1: Modify pyproject.toml
```toml
requires-python = ">=3.9"
```

#### Step 2: Install compatible dependencies
```bash
pip3 install "httpx<0.28" "mcp<1.3" "pydantic<2.10"
```

#### Step 3: Build and install
```bash
python3 -m build
pip3 install dist/freshrelease_mcp-1.5.0-py3-none-any.whl --force-reinstall
```

**Note**: This might cause compatibility issues.

## 🧪 Testing Your Setup

### Test 1: Verify Python Version
```bash
python3.10 --version
# Should show Python 3.10.x
```

### Test 2: Test Package Installation
```bash
python3.10 -c "import freshrelease_mcp.server; print('✅ Package installed successfully!')"
```

### Test 3: Test MCP Server
```bash
FRESHRELEASE_API_KEY="your_key" \
FRESHRELEASE_DOMAIN="your_domain.freshrelease.io" \
FRESHRELEASE_PROJECT_KEY="your_project_key" \
python3.10 -m freshrelease_mcp.server
```

### Test 4: Check Cursor IDE
1. Open Cursor IDE
2. Go to Settings → MCP
3. Verify the configuration is there
4. Look for "freshrelease-mcp" in the MCP servers list
5. Check if tools appear in the MCP tools section

## 🔧 Troubleshooting

### If tools still don't show:

#### Check 1: Cursor IDE Logs
1. Open Cursor IDE
2. Go to Help → Toggle Developer Tools
3. Check Console for MCP errors
4. Look for "freshrelease-mcp" related messages

#### Check 2: MCP Configuration
1. Ensure JSON is valid (no syntax errors)
2. Check that environment variables are set
3. Verify the command path is correct

#### Check 3: Server Startup
1. Test the server manually outside Cursor
2. Check for error messages
3. Verify all dependencies are installed

#### Check 4: Restart Everything
1. Close Cursor IDE completely
2. Restart Cursor IDE
3. Check MCP settings again

## 📋 Complete Working Configuration

### For Python 3.10+ (Recommended)
```json
{
  "mcpServers": {
    "freshrelease-mcp": {
      "command": "python3.10",
      "args": ["-m", "freshrelease_mcp.server"],
      "env": {
        "FRESHRELEASE_API_KEY": "your_actual_api_key",
        "FRESHRELEASE_DOMAIN": "your_actual_domain.freshrelease.io",
        "FRESHRELEASE_PROJECT_KEY": "your_actual_project_key"
      }
    }
  }
}
```

### For pyenv users
```json
{
  "mcpServers": {
    "freshrelease-mcp": {
      "command": "python",
      "args": ["-m", "freshrelease_mcp.server"],
      "env": {
        "FRESHRELEASE_API_KEY": "your_actual_api_key",
        "FRESHRELEASE_DOMAIN": "your_actual_domain.freshrelease.io",
        "FRESHRELEASE_PROJECT_KEY": "your_actual_project_key"
      }
    }
  }
}
```

## 🎯 Why This Happens

1. **Python Version Requirement**: The package requires Python 3.10+
2. **System Python**: macOS comes with older Python versions
3. **MCP Server Startup**: Cursor can't start the server due to version incompatibility
4. **Tool Discovery**: If the server doesn't start, tools won't be discovered
5. **Dependency Chain**: All dependencies also require Python 3.10+

## ✅ Success Indicators

When working correctly, you should see:
1. **In Cursor Settings**: MCP server "freshrelease-mcp" appears in the list
2. **In MCP Tools**: 28 Freshrelease tools are available
3. **In Console**: No MCP-related errors
4. **Manual Test**: Server starts without errors

## 🆘 Still Having Issues?

If you continue having problems:

1. **Check Python Installation**:
   ```bash
   which python3.10
   python3.10 --version
   ```

2. **Check Package Installation**:
   ```bash
   python3.10 -m pip list | grep freshrelease
   ```

3. **Check Cursor IDE Version**: Ensure you're using a recent version

4. **Check MCP Support**: Verify Cursor IDE supports MCP servers

5. **Contact Support**: 
   - GitHub: [freshrelease-mcp repository]
   - Email: kalidass.mani@freshworks.com

## 🚀 Quick Start (Recommended Path)

1. **Install Python 3.10**: `brew install python@3.10`
2. **Install Package**: `python3.10 -m pip install freshrelease-mcp`
3. **Configure Cursor**: Use the JSON configuration above
4. **Restart Cursor**: Close and reopen Cursor IDE
5. **Test**: Check MCP tools section for Freshrelease tools

This should resolve the issue and make all 28 Freshrelease MCP tools available in Cursor IDE! 🎉



