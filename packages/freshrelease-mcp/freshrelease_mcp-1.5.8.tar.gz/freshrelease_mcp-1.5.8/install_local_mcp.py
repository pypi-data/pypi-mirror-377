#!/usr/bin/env python3.10
"""Install the local MCP package for testing."""

import subprocess
import sys
import os

def install_local_package():
    """Install the local package using pip."""
    try:
        # Get the current directory
        current_dir = os.path.dirname(os.path.abspath(__file__))
        wheel_path = os.path.join(current_dir, "dist", "freshrelease_mcp-1.5.7-py3-none-any.whl")
        
        if not os.path.exists(wheel_path):
            print("❌ Wheel file not found. Please run 'python3 -m build' first.")
            return False
        
        # Install the local package
        print("Installing local MCP package...")
        result = subprocess.run([
            sys.executable, "-m", "pip", "install", wheel_path, "--force-reinstall"
        ], capture_output=True, text=True)
        
        if result.returncode == 0:
            print("✅ Successfully installed local MCP package!")
            return True
        else:
            print(f"❌ Failed to install package: {result.stderr}")
            return False
            
    except Exception as e:
        print(f"❌ Error installing package: {e}")
        return False

def test_installation():
    """Test that the installation works."""
    try:
        print("Testing MCP server...")
        result = subprocess.run([
            sys.executable, "-c", 
            "from freshrelease_mcp.server import mcp; import asyncio; print('✅ MCP server imports successfully')"
        ], capture_output=True, text=True)
        
        if result.returncode == 0:
            print("✅ MCP server test passed!")
            return True
        else:
            print(f"❌ MCP server test failed: {result.stderr}")
            return False
            
    except Exception as e:
        print(f"❌ Error testing installation: {e}")
        return False

if __name__ == "__main__":
    print("Installing local Freshrelease MCP package...")
    
    if install_local_package():
        if test_installation():
            print("\n🎉 Installation successful!")
            print("You can now use the MCP server with:")
            print("  python3.10 -m freshrelease_mcp.server")
        else:
            print("\n❌ Installation failed testing")
    else:
        print("\n❌ Installation failed")
