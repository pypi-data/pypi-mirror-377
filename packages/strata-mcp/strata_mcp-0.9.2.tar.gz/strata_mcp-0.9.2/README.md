# Strata MCP Router

A unified router for Model Context Protocol (MCP) servers that supports multiple transport types (SSE, HTTP, stdio) and provides tool routing capabilities.

## Quick Start

### Installation

```bash
pipx install strata-mcp
```

Or with pip:
```bash
pip install strata-mcp
```

For development:
```bash
pip install -e .
```

### Tool Integration

Strata can automatically configure itself in various AI assistants and IDEs that support MCP.

#### Add Strata to Claude Code
```bash
# Add to user configuration (default)
strata tool add claude

# Add to project-specific configuration
strata tool add claude --scope project
```

#### Add Strata to Gemini
```bash
strata tool add gemini
```

#### Add Strata to VSCode
```bash
strata tool add vscode
```

#### Add Strata to Cursor
```bash
# Add to user configuration (~/.cursor/mcp.json)
strata tool add cursor --scope user

# Add to project configuration (.cursor/mcp.json)
strata tool add cursor --scope project
```

**Supported scopes:**
- `user`: Global configuration (default)
- `project`: Project-specific configuration
- `local`: Same as project (for Cursor)

Note: VSCode doesn't support scope parameter and will use its default behavior.

### Add MCP Servers

#### Add Servers

**Stdio Server:**
```bash
strata add --type stdio playwright npx @playwright/mcp@latest
```

**SSE Server:**
```bash
strata add --type sse server-name http://localhost:8080/mcp/ --env API_KEY=your_key
```

**HTTP Server:**
```bash
strata add --type http github https://api.githubcopilot.com/mcp/ --header "Authorization=Bearer token"
```
Add server with OAuth
```bash
strata add --type http notion https://mcp.notion.com/mcp --auth_type oauth
```

#### List Servers
```bash
strata list
```

#### Enable/Disable Servers
```bash
strata enable server-name
strata disable server-name
```

#### Remove Servers
```bash
strata remove server-name
```

### Running the Router

#### Stdio Mode (Default)
Run without arguments to start in stdio mode for direct MCP communication:
```bash
python -m strata
# or
strata
```

#### HTTP/SSE Server Mode
Run with port to start as HTTP/SSE server:
```bash
strata run --port 8080
```

## Configuration

Configuration is stored in `~/.config/strata/servers.json` by default. You can specify a custom config path:

```bash
strata --config-path /path/to/config.json add --type stdio ...
```

### Config Format

```json
{
  "mcp": {
    "servers": {
      "github": {
        "command": "npx",
        "args": ["-y", "@modelcontextprotocol/server-github"],
        "env": {
          "GITHUB_TOKEN": "your_token"
        },
        "enabled": true
      },
      "api-server": {
        "type": "http",
        "url": "https://api.example.com/mcp",
        "headers": {
          "Authorization": "Bearer token"
        },
        "enabled": true
      }
    }
  }
}
```

## Available Tools

When running as a router, the following tools are exposed:

- `discover_server_actions` - Discover available actions from configured servers
- `get_action_details` - Get detailed information about a specific action
- `execute_action` - Execute an action on a target server
- `search_documentation` - Search server documentation
- `handle_auth_failure` - Handle authentication issues

## Development

### Running Tests
```bash
pytest
```

### Project Structure
- `src/strata/` - Main source code
  - `cli.py` - Command-line interface
  - `server.py` - Server implementation (stdio/HTTP/SSE)
  - `tools.py` - Tool implementations
  - `mcp_client_manager.py` - MCP client management
  - `config.py` - Configuration management

## Examples

### Running GitHub MCP Server through Router
```bash
# Add GitHub server (official HTTP server)
strata add --type http github https://api.githubcopilot.com/mcp/

# Run router in stdio mode
strata

# Or run as HTTP server
strata run --port 8080
```

### Running Multiple Servers
```bash
# Add multiple servers
strata add --type stdio playwright npx @playwright/mcp@latest
strata add --type http github https://api.githubcopilot.com/mcp/

# List all servers
strata list

# Run router with all enabled servers
strata run --port 8080
```

## Environment Variables

- `MCP_CONFIG_PATH` - Custom config file path
- `MCP_ROUTER_PORT` - Default port for HTTP/SSE server (default: 8080)

## More MCP Servers

For more MCP servers, visit: [Klavis AI (YC X25)](https://github.com/Klavis-AI/klavis)

## License

Apache License 2.0