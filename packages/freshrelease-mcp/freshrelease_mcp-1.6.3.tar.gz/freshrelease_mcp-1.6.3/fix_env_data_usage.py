#!/usr/bin/env python3
"""
Script to fix _env_data usage in function bodies
"""
import re

def fix_env_data_usage(file_path):
    with open(file_path, 'r') as f:
        content = f.read()
    
    # Pattern 1: Replace _env_data["base_url"] with env_data["base_url"]
    content = re.sub(r'_env_data\["base_url"\]', 'env_data["base_url"]', content)
    
    # Pattern 2: Replace _env_data["headers"] with env_data["headers"]
    content = re.sub(r'_env_data\["headers"\]', 'env_data["headers"]', content)
    
    # Pattern 3: Add environment validation at the beginning of functions that use env_data
    # Find functions that use env_data but don't have validate_environment call
    functions_to_fix = [
        'fr_get_project',
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
        # Pattern to find the function and add env validation
        pattern = f'(async def {func_name}\\([^)]*\\) -> [^:]*:\n[^"]*"""[^"]*"""\n[^"]*try:\n[^"]*)(project_id = get_project_identifier)'
        replacement = r'\1        # Validate environment variables\n        env_data = validate_environment()\n        if "error" in env_data:\n            return env_data\n        \n        \2'
        content = re.sub(pattern, replacement, content, flags=re.MULTILINE | re.DOTALL)
    
    with open(file_path, 'w') as f:
        f.write(content)
    
    print(f"Fixed _env_data usage in {file_path}")

if __name__ == "__main__":
    fix_env_data_usage("src/freshrelease_mcp/server.py")
    print("Environment data usage fixed!")

