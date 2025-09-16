#!/usr/bin/env python3.10
"""Test script to verify MCP tools are working locally."""

import asyncio
import json
import sys
from freshrelease_mcp.server import mcp

async def test_tools():
    """Test that all MCP tools are properly registered."""
    print("Testing MCP tools registration...")
    
    # Get the tools from the MCP server
    tools = await mcp.list_tools()
    
    print(f"Found {len(tools)} tools:")
    for i, tool in enumerate(tools, 1):
        print(f"{i:2d}. {tool.name}")
        print(f"    Description: {tool.description[:100]}...")
        print()
    
    return len(tools)

if __name__ == "__main__":
    try:
        tool_count = asyncio.run(test_tools())
        print(f"✅ Successfully found {tool_count} MCP tools!")
        sys.exit(0)
    except Exception as e:
        print(f"❌ Error testing MCP tools: {e}")
        sys.exit(1)
