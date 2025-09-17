#!/usr/bin/env python3
"""
Script to fix all MCP functions to use proper environment validation
"""
import re

def fix_all_functions(file_path):
    with open(file_path, 'r') as f:
        content = f.read()
    
    # Remove _env_data from docstrings
    content = re.sub(r'\s*_env_data: Environment data \(injected by decorator\)\n', '', content)
    
    # Fix functions that use env_data but don't have proper validation
    functions_to_fix = [
        'fr_create_task',
        'fr_get_task', 
        'fr_get_all_tasks',
        'fr_get_issue_type_by_name',
        'fr_filter_tasks',
        'fr_save_filter',
        'fr_filter_testcases',
        'fr_get_testcase_form_fields'
    ]
    
    for func_name in functions_to_fix:
        # Pattern to find function body and add proper validation
        pattern = f'(async def {func_name}\\([^)]*\\) -> [^:]*:\n[^"]*"""[^"]*"""\n[^"]*)(base_url = env_data\\["base_url"\\])'
        replacement = r'\1    try:\n        # Validate environment variables\n        env_data = validate_environment()\n        if "error" in env_data:\n            return env_data\n        \n        \2'
        content = re.sub(pattern, replacement, content, flags=re.MULTILINE | re.DOTALL)
    
    # Fix functions that don't have proper try-catch blocks
    for func_name in functions_to_fix:
        # Add try-catch if missing
        pattern = f'(async def {func_name}\\([^)]*\\) -> [^:]*:\n[^"]*"""[^"]*"""\n[^"]*try:\n[^"]*)(return await make_api_request[^}]*)(\n\n)'
        replacement = r'\1\2\n    except Exception as e:\n        return create_error_response(f"Failed in {func_name}: {str(e)}")\3'
        content = re.sub(pattern, replacement, content, flags=re.MULTILINE | re.DOTALL)
    
    with open(file_path, 'w') as f:
        f.write(content)
    
    print(f"Fixed all functions in {file_path}")

if __name__ == "__main__":
    fix_all_functions("src/freshrelease_mcp/server.py")
    print("All functions fixed!")

