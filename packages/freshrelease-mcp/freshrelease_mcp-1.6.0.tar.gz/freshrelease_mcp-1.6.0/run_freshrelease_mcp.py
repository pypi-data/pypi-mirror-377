#!/usr/bin/env python3
"""
Wrapper script to run freshrelease-mcp with Python 3.9
This bypasses the Python version requirement by running the source directly.
"""
import sys
import os

# Add the source directory to Python path
current_dir = os.path.dirname(os.path.abspath(__file__))
src_dir = os.path.join(current_dir, 'src')
sys.path.insert(0, src_dir)

# Import and run the server
try:
    from freshrelease_mcp.server import main
    if __name__ == "__main__":
        main()
except ImportError as e:
    print(f"Error importing freshrelease_mcp.server: {e}")
    print("Make sure you have installed the required dependencies:")
    print("pip3 install httpx mcp pydantic")
    sys.exit(1)
except Exception as e:
    print(f"Error running freshrelease_mcp server: {e}")
    sys.exit(1)



