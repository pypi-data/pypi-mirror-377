# Cursor IDE MCP Configuration for Freshrelease

This guide will help you set up the Freshrelease MCP server in Cursor IDE.

## Prerequisites

1. **Install the package:**
   ```bash
   pip install freshrelease-mcp
   ```

2. **Get your Freshrelease credentials:**
   - API Key: Go to your Freshrelease account settings
   - Domain: Your Freshrelease domain (e.g., `yourcompany.freshrelease.io`)
   - Project Key: The key of your default project (optional but recommended)

## Configuration

### Option 1: Using Cursor's MCP Settings

1. Open Cursor IDE
2. Go to Settings (Cmd/Ctrl + ,)
3. Search for "MCP" or "Model Context Protocol"
4. Add the following configuration:

```json
{
  "mcpServers": {
    "freshrelease-mcp": {
      "command": "freshrelease-mcp",
      "args": [],
      "env": {
        "FRESHRELEASE_API_KEY": "your_api_key_here",
        "FRESHRELEASE_DOMAIN": "your_domain.freshrelease.io",
        "FRESHRELEASE_PROJECT_KEY": "your_default_project_key_here"
      }
    }
  }
}
```

### Option 2: Using Configuration File

1. Create a file named `cursor-mcp-config.json` in your project root
2. Copy the configuration from above
3. Replace the placeholder values with your actual credentials

## Environment Variables

| Variable | Required | Description | Example |
|----------|----------|-------------|---------|
| `FRESHRELEASE_API_KEY` | Yes | Your Freshrelease API key | `abc123def456...` |
| `FRESHRELEASE_DOMAIN` | Yes | Your Freshrelease domain | `mycompany.freshrelease.io` |
| `FRESHRELEASE_PROJECT_KEY` | No | Default project key for operations | `PROJ` |

## Available MCP Tools

The server provides 28 MCP tools for Freshrelease operations:

### Project Management
- `fr_create_project`: Create a new project
- `fr_get_project`: Get project details

### Task Management
- `fr_create_task`: Create tasks with automatic name-to-ID resolution
- `fr_get_task`: Get task details
- `fr_get_all_tasks`: List all tasks in a project
- `fr_filter_tasks`: Advanced task filtering with custom fields
- `fr_save_filter`: Save reusable filters

### Test Case Management
- `fr_list_testcases`: List all test cases
- `fr_get_testcase`: Get specific test case
- `fr_get_testcases_by_section`: Get test cases by section
- `fr_link_testcase_issues`: Link issues to test cases
- `fr_add_testcases_to_testrun`: Add test cases to test runs
- `fr_filter_testcases`: Advanced test case filtering
- `fr_get_testcase_form_fields`: Get available filter fields

### User Management
- `fr_search_users`: Search users by name or email

### Lookup Functions
- `fr_get_sprint_by_name`: Get sprint by name
- `fr_get_release_by_name`: Get release by name
- `fr_get_tag_by_name`: Get tag by name
- `fr_get_subproject_by_name`: Get subproject by name

### Cache Management
- `fr_clear_filter_cache`: Clear filter cache
- `fr_clear_lookup_cache`: Clear lookup cache
- `fr_clear_resolution_cache`: Clear resolution cache
- `fr_clear_testcase_form_cache`: Clear test case form cache
- `fr_clear_all_caches`: Clear all caches

### Performance Monitoring
- `fr_get_performance_stats`: Get performance statistics
- `fr_clear_performance_stats`: Clear performance stats
- `fr_close_http_client`: Close HTTP client

## Usage Examples

### Create a Task
```python
# The MCP tool will automatically resolve names to IDs
fr_create_task(
    title="Fix login bug",
    description="User cannot login with special characters",
    issue_type_name="Bug",
    user="john.doe@company.com",
    status="Open"
)
```

### Filter Test Cases
```python
# Filter by section name (automatically resolved to ID)
fr_filter_testcases(
    filter_rules=[{"condition": "section_id", "operator": "is", "value": "Authentication"}]
)

# Filter by test case type and severity
fr_filter_testcases(
    filter_rules=[
        {"condition": "type_id", "operator": "is", "value": "Functional Test"},
        {"condition": "severity_id", "operator": "is_in", "value": ["High", "Medium"]}
    ]
)
```

### Advanced Task Filtering
```python
# Filter tasks with automatic name resolution
fr_filter_tasks(
    owner_id="John Doe",
    status_id="In Progress",
    issue_type_id="Bug",
    sprint_id="Sprint 1"
)
```

## Troubleshooting

### Common Issues

1. **"Command not found" error:**
   - Make sure the package is installed: `pip install freshrelease-mcp`
   - Check if the `freshrelease-mcp` command is in your PATH

2. **Authentication errors:**
   - Verify your API key is correct
   - Check that your domain is properly formatted
   - Ensure your API key has the necessary permissions

3. **Project not found errors:**
   - Verify your project key is correct
   - Check that the project exists in your Freshrelease account

### Debug Mode

To enable debug logging, add this to your environment variables:
```json
{
  "env": {
    "FRESHRELEASE_API_KEY": "your_api_key",
    "FRESHRELEASE_DOMAIN": "your_domain.freshrelease.io",
    "FRESHRELEASE_PROJECT_KEY": "your_project_key",
    "LOG_LEVEL": "DEBUG"
  }
}
```

## Support

For issues or questions:
1. Check the [GitHub repository](https://github.com/your-repo/freshrelease-mcp)
2. Review the [PyPI package page](https://pypi.org/project/freshrelease-mcp/)
3. Contact support at kalidass.mani@freshworks.com

## Version Information

- **Current Version**: 1.5.0
- **Python Requirement**: >=3.10
- **Dependencies**: httpx, mcp, pydantic
