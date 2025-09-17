#!/usr/bin/env python3
"""
Script to fix indentation issues in the fr_filter_tasks function.
"""

def fix_fr_filter_tasks_indentation():
    """Fix indentation in fr_filter_tasks function."""
    
    with open('src/freshrelease_mcp/server.py', 'r') as f:
        lines = f.readlines()
    
    # Find the start and end of fr_filter_tasks function
    start_line = None
    end_line = None
    in_function = False
    indent_level = 0
    
    for i, line in enumerate(lines):
        if 'async def fr_filter_tasks(' in line:
            start_line = i
            in_function = True
            continue
            
        if in_function:
            if line.strip().startswith('@mcp.tool()') and i > start_line + 10:
                end_line = i
                break
                
            if line.strip().startswith('async def ') and i > start_line + 10:
                end_line = i
                break
    
    if start_line is None or end_line is None:
        print("Could not find fr_filter_tasks function boundaries")
        return
    
    print(f"Found fr_filter_tasks function from line {start_line} to {end_line}")
    
    # Fix indentation for the function body
    # The function should start with 'try:' and all content should be indented
    fixed_lines = []
    
    for i in range(start_line, end_line):
        line = lines[i]
        
        # Skip the function signature and docstring
        if i <= start_line + 50:  # Skip first 50 lines (signature + docstring)
            fixed_lines.append(line)
            continue
            
        # Skip the 'try:' line and the env validation lines
        if 'try:' in line or 'Validate environment variables' in line or 'env_data = validate_environment()' in line or 'base_url = env_data' in line or 'headers = env_data' in line or 'project_id = get_project_identifier' in line:
            fixed_lines.append(line)
            continue
            
        # Skip empty lines after the try block
        if line.strip() == '' and i < start_line + 60:
            fixed_lines.append(line)
            continue
            
        # Add proper indentation (8 spaces for function body inside try block)
        if line.strip() and not line.startswith('    '):
            fixed_lines.append('        ' + line)
        else:
            fixed_lines.append(line)
    
    # Write the fixed content back
    with open('src/freshrelease_mcp/server.py', 'w') as f:
        f.writelines(fixed_lines)
    
    print("Fixed indentation for fr_filter_tasks function")

if __name__ == "__main__":
    fix_fr_filter_tasks_indentation()
