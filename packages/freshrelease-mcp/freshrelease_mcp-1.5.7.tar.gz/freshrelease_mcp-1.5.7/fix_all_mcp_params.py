#!/usr/bin/env python3
"""
Script to fix all MCP tool parameters by removing _env_data parameters
"""
import re

def fix_mcp_file(file_path):
    with open(file_path, 'r') as f:
        content = f.read()
    
    # Remove _env_data parameters from function signatures
    # Pattern: , _env_data: Optional[Dict[str, str]] = None
    pattern1 = r',\s*_env_data:\s*Optional\[Dict\[str,\s*str\]\]\s*=\s*None'
    content = re.sub(pattern1, '', content)
    
    # Pattern: _env_data: Optional[Dict[str, str]] = None, (at end of line)
    pattern2 = r'_\s*env_data:\s*Optional\[Dict\[str,\s*str\]\]\s*=\s*None,?\s*'
    content = re.sub(pattern2, '', content)
    
    # Remove _env_data from function calls
    # Pattern: _env_data=_env_data
    pattern3 = r',\s*_env_data=_env_data'
    content = re.sub(pattern3, '', content)
    
    # Pattern: _env_data=_env_data,
    pattern4 = r'_\s*env_data=_env_data,?\s*'
    content = re.sub(pattern4, '', content)
    
    # Fix function calls that pass _env_data
    # Pattern: get_project_identifier(project_identifier, _env_data)
    pattern5 = r'get_project_identifier\(([^,]+),\s*_env_data\)'
    content = re.sub(pattern5, r'get_project_identifier(\1)', content)
    
    with open(file_path, 'w') as f:
        f.write(content)
    
    print(f"Fixed {file_path}")

if __name__ == "__main__":
    fix_mcp_file("src/freshrelease_mcp/server.py")
    print("All MCP parameters fixed!")



