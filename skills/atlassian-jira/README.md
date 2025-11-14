# Atlassian Jira Skill

An Anthropic Skill for interacting with Jira through type-safe Python tools.

## Quick Start

### 1. Set Environment Variables

```bash
export JIRA_URL="https://your-domain.atlassian.net"
export JIRA_USERNAME="your-email@example.com"
export JIRA_API_TOKEN="your-api-token"
```

### 2. Install the Package

```bash
cd /Users/bono/Documents/01.Projects/MCP_Internalization/atlassian-internalized
pip install -e .
```

### 3. List Available Tools

```bash
python scripts/execute_tool.py --list-tools
```

### 4. Execute a Tool

```bash
python scripts/execute_tool.py jira_get_issue --input '{"issue_key": "PROJ-123"}'
```

## Installation for Claude Code

### Global Installation (recommended)

```bash
cd /Users/bono/Documents/01.Projects/MCP_Internalization/atlassian-internalized
ln -s "$(pwd)/skills/atlassian-jira" ~/.claude/skills/atlassian-jira
```

### Project-Local Installation

```bash
cd /Users/bono/Documents/01.Projects/MCP_Internalization/atlassian-internalized
mkdir -p .claude/skills
ln -s "$(pwd)/skills/atlassian-jira" .claude/skills/atlassian-jira
```

### Verify Installation

```bash
# Check if symlink exists
ls -la ~/.claude/skills/atlassian-jira

# Test the skill
python ~/.claude/skills/atlassian-jira/scripts/execute_tool.py --list-tools
```

## Usage

### Command-Line Interface

The `execute_tool.py` script provides three main operations:

#### List Tools

```bash
python scripts/execute_tool.py --list-tools
```

Output:
```json
{
  "success": true,
  "tools": ["jira_get_issue"],
  "count": 1
}
```

#### Get Tool Schema

```bash
python scripts/execute_tool.py jira_get_issue --schema
```

Output includes complete JSON schemas for input and output.

#### Execute Tool

```bash
python scripts/execute_tool.py jira_get_issue --input '{
  "issue_key": "PROJ-123",
  "fields": "summary,status,assignee",
  "comment_limit": 5
}'
```

### Using Examples

Example files are provided in the `examples/` directory:

```bash
# Extract and use an example
cat examples/get_issue_basic.json | jq -c .input | \
  xargs -I {} python scripts/execute_tool.py jira_get_issue --input '{}'
```

Or manually:

```bash
python scripts/execute_tool.py jira_get_issue --input '{"issue_key": "PROJ-123"}'
```

## Available Tools

### jira_get_issue

Get comprehensive information about a Jira issue.

**Parameters**:
- `issue_key` (required): Issue key like "PROJ-123"
- `fields` (optional): Comma-separated fields or "*all"
- `expand` (optional): Fields to expand (e.g., "changelog")
- `comment_limit` (optional): Max comments (0-100, default: 10)

**Examples**: See `examples/` directory

## Troubleshooting

### Import Error

If you see "Failed to import atlassian_tools":

```bash
# Reinstall the package
cd /Users/bono/Documents/01.Projects/MCP_Internalization/atlassian-internalized
pip install -e .
```

### Environment Variable Error

If you see "JIRA_URL environment variable is required":

```bash
# Set all required variables
export JIRA_URL="https://your-domain.atlassian.net"
export JIRA_USERNAME="your-email@example.com"
export JIRA_API_TOKEN="your-api-token"
```

### Authentication Failed

If you see "Authentication failed":

1. Verify your API token is correct
2. Check that JIRA_USERNAME is your email address (not username)
3. Ensure JIRA_URL includes the protocol (https://)

### JSON Parsing Error

If you see "Invalid JSON input":

- Use single quotes around JSON, double quotes inside: `'{"key": "value"}'`
- Escape quotes if needed: `"{\"key\": \"value\"}"`
- Verify JSON is valid: `echo '{"test": "json"}' | jq`

## Development

### Project Structure

```
atlassian-jira/
├── SKILL.md              # Skill definition and instructions
├── README.md             # This file
├── scripts/
│   └── execute_tool.py   # CLI interface
└── examples/
    ├── get_issue_basic.json
    ├── get_issue_specific_fields.json
    ├── get_issue_with_changelog.json
    └── get_issue_no_comments.json
```

### Adding New Tools

When new Jira tools are added to the main package:

1. They automatically appear in `--list-tools`
2. Update SKILL.md to document the new tool
3. Add example JSON files for common use cases
4. Test with `--schema` and `--input`

### Testing

```bash
# Run all tests
cd /Users/bono/Documents/01.Projects/MCP_Internalization/atlassian-internalized
pytest tests/

# Test the skill script
python skills/atlassian-jira/scripts/execute_tool.py --list-tools
python skills/atlassian-jira/scripts/execute_tool.py jira_get_issue --schema
```

## Documentation

- **Main Docs**: `../../docs/internalization-log.md`
- **API Reference**: Use `--schema` flag for each tool
- **Skill Instructions**: See `SKILL.md`

## Support

For issues or questions:
- Check `SKILL.md` for detailed usage instructions
- Review `examples/` for common patterns
- See main project docs in `../../docs/`

## License

MIT License - See main project LICENSE file
