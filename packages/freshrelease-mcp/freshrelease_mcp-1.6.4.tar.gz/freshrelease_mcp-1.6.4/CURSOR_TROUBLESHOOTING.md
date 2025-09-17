# Cursor IDE MCP Troubleshooting Guide

## Why MCP Tools Aren't Showing in Cursor IDE

If you don't see the Freshrelease MCP tools in Cursor IDE, here are the most common issues and solutions:

## Issue 1: Package Not Installed

### Problem
The `freshrelease-mcp` package is not installed in your Python environment.

### Solution
```bash
# Install the package
pip3 install freshrelease-mcp

# Or if you're using a virtual environment
pip install freshrelease-mcp
```

### Verify Installation
```bash
# Check if the package is installed
pip3 list | grep freshrelease-mcp

# Test if the command works
python3 -m freshrelease_mcp.server --help
```

## Issue 2: Wrong Command Configuration

### Problem
Cursor IDE can't find the `freshrelease-mcp` command.

### Solution
Use the Python module approach instead of the command:

```json
{
  "mcpServers": {
    "freshrelease-mcp": {
      "command": "python3",
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

## Issue 3: Python Path Issues

### Problem
Cursor IDE can't find the correct Python executable.

### Solution
Use the absolute path to Python:

```json
{
  "mcpServers": {
    "freshrelease-mcp": {
      "command": "/Library/Developer/CommandLineTools/usr/bin/python3",
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

## Issue 4: Virtual Environment

### Problem
You're using a virtual environment but Cursor is using the system Python.

### Solution
1. **Activate your virtual environment:**
   ```bash
   source venv/bin/activate  # On macOS/Linux
   # or
   venv\Scripts\activate     # On Windows
   ```

2. **Find the Python path in your virtual environment:**
   ```bash
   which python
   # or
   where python  # On Windows
   ```

3. **Use that path in your MCP configuration:**
   ```json
   {
     "mcpServers": {
       "freshrelease-mcp": {
         "command": "/path/to/your/venv/bin/python",
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

## Issue 5: Missing Environment Variables

### Problem
The MCP server starts but fails due to missing or incorrect environment variables.

### Solution
1. **Verify your credentials:**
   - API Key: Go to Freshrelease → Settings → API Keys
   - Domain: Your Freshrelease domain (e.g., `mycompany.freshrelease.io`)
   - Project Key: Your project key (e.g., `PROJ`)

2. **Test the configuration:**
   ```bash
   FRESHRELEASE_API_KEY="your_key" \
   FRESHRELEASE_DOMAIN="your_domain.freshrelease.io" \
   FRESHRELEASE_PROJECT_KEY="your_project_key" \
   python3 -m freshrelease_mcp.server
   ```

## Issue 6: Cursor IDE Configuration

### Problem
The MCP configuration is not properly set in Cursor IDE.

### Solution
1. **Open Cursor IDE**
2. **Go to Settings** (Cmd/Ctrl + ,)
3. **Search for "MCP"** or "Model Context Protocol"
4. **Add the configuration** in the MCP Servers section
5. **Restart Cursor IDE** after making changes

## Issue 7: Port Conflicts

### Problem
The MCP server can't bind to the required port.

### Solution
1. **Check if the port is in use:**
   ```bash
   lsof -i :3000  # Check port 3000
   ```

2. **Kill any conflicting processes:**
   ```bash
   kill -9 <PID>
   ```

## Issue 8: Permission Issues

### Problem
Insufficient permissions to run the MCP server.

### Solution
1. **Make sure Python has execute permissions:**
   ```bash
   chmod +x /path/to/python
   ```

2. **Check if the package is installed for the correct user:**
   ```bash
   pip3 install --user freshrelease-mcp
   ```

## Debugging Steps

### Step 1: Test the MCP Server Manually
```bash
# Set environment variables
export FRESHRELEASE_API_KEY="your_api_key"
export FRESHRELEASE_DOMAIN="your_domain.freshrelease.io"
export FRESHRELEASE_PROJECT_KEY="your_project_key"

# Run the server
python3 -m freshrelease_mcp.server
```

### Step 2: Check Cursor IDE Logs
1. Open Cursor IDE
2. Go to Help → Toggle Developer Tools
3. Check the Console for MCP-related errors

### Step 3: Verify MCP Configuration
1. In Cursor IDE, go to Settings
2. Search for "MCP"
3. Verify the configuration is properly formatted JSON

## Common Error Messages

### "Command not found"
- **Solution**: Use `python3 -m freshrelease_mcp.server` instead of `freshrelease-mcp`

### "Module not found"
- **Solution**: Install the package with `pip3 install freshrelease-mcp`

### "Authentication failed"
- **Solution**: Check your API key and domain

### "Project not found"
- **Solution**: Verify your project key

## Working Configuration Examples

### Example 1: Basic Configuration
```json
{
  "mcpServers": {
    "freshrelease-mcp": {
      "command": "python3",
      "args": ["-m", "freshrelease_mcp.server"],
      "env": {
        "FRESHRELEASE_API_KEY": "abc123def456",
        "FRESHRELEASE_DOMAIN": "mycompany.freshrelease.io",
        "FRESHRELEASE_PROJECT_KEY": "PROJ"
      }
    }
  }
}
```

### Example 2: With Virtual Environment
```json
{
  "mcpServers": {
    "freshrelease-mcp": {
      "command": "/Users/username/venv/bin/python",
      "args": ["-m", "freshrelease_mcp.server"],
      "env": {
        "FRESHRELEASE_API_KEY": "abc123def456",
        "FRESHRELEASE_DOMAIN": "mycompany.freshrelease.io",
        "FRESHRELEASE_PROJECT_KEY": "PROJ"
      }
    }
  }
}
```

### Example 3: With Absolute Path
```json
{
  "mcpServers": {
    "freshrelease-mcp": {
      "command": "/Library/Developer/CommandLineTools/usr/bin/python3",
      "args": ["-m", "freshrelease_mcp.server"],
      "env": {
        "FRESHRELEASE_API_KEY": "abc123def456",
        "FRESHRELEASE_DOMAIN": "mycompany.freshrelease.io",
        "FRESHRELEASE_PROJECT_KEY": "PROJ"
      }
    }
  }
}
```

## Still Having Issues?

If you're still having problems:

1. **Check the Cursor IDE documentation** for MCP setup
2. **Verify your Python installation** and package installation
3. **Test the MCP server independently** before configuring in Cursor
4. **Check Cursor IDE logs** for specific error messages
5. **Try different Python paths** (system vs virtual environment)

## Support

For additional help:
- Check the [GitHub repository](https://github.com/your-repo/freshrelease-mcp)
- Review the [PyPI package page](https://pypi.org/project/freshrelease-mcp/)
- Contact support at kalidass.mani@freshworks.com



