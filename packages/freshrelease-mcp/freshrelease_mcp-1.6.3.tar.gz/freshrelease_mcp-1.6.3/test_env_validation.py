#!/usr/bin/env python3
"""
Test script to verify environment validation for Freshrelease MCP server.
"""

import os
import sys
sys.path.insert(0, 'src')

from freshrelease_mcp.server import validate_environment

def test_environment_validation():
    """Test environment validation with different scenarios."""
    
    print("Testing Freshrelease MCP Environment Validation")
    print("=" * 50)
    
    # Test 1: No environment variables set
    print("\n1. Testing with no environment variables:")
    original_api_key = os.environ.get("FRESHRELEASE_API_KEY")
    original_domain = os.environ.get("FRESHRELEASE_DOMAIN")
    
    # Clear environment variables
    if "FRESHRELEASE_API_KEY" in os.environ:
        del os.environ["FRESHRELEASE_API_KEY"]
    if "FRESHRELEASE_DOMAIN" in os.environ:
        del os.environ["FRESHRELEASE_DOMAIN"]
    
    try:
        result = validate_environment()
        print("❌ ERROR: Should have failed with no environment variables")
    except ValueError as e:
        print(f"✅ Expected error: {e}")
    
    # Test 2: Only API key set
    print("\n2. Testing with only API key:")
    os.environ["FRESHRELEASE_API_KEY"] = "test_api_key"
    
    try:
        result = validate_environment()
        print("❌ ERROR: Should have failed with only API key")
    except ValueError as e:
        print(f"✅ Expected error: {e}")
    
    # Test 3: Both required variables set
    print("\n3. Testing with both required variables:")
    os.environ["FRESHRELEASE_DOMAIN"] = "test.freshrelease.com"
    
    try:
        result = validate_environment()
        print("✅ Success! Environment validation passed")
        print(f"   Base URL: {result['base_url']}")
        print(f"   Headers: {result['headers']}")
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
    
    # Test 4: Test with project key
    print("\n4. Testing with project key:")
    os.environ["FRESHRELEASE_PROJECT_KEY"] = "TEST"
    
    try:
        result = validate_environment()
        print("✅ Success! Environment validation with project key passed")
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
    
    # Restore original environment
    if original_api_key:
        os.environ["FRESHRELEASE_API_KEY"] = original_api_key
    else:
        os.environ.pop("FRESHRELEASE_API_KEY", None)
        
    if original_domain:
        os.environ["FRESHRELEASE_DOMAIN"] = original_domain
    else:
        os.environ.pop("FRESHRELEASE_DOMAIN", None)
    
    print("\n" + "=" * 50)
    print("Environment validation test completed!")

if __name__ == "__main__":
    test_environment_validation()
