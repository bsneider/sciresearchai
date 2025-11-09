# Bach MCP Server Setup Guide

This guide explains how to install and configure existing MCP servers for use with the Bach research system.

## Prerequisites

- Node.js 18+ (for npm-based MCP servers)
- Python 3.8+ with uv (for arxiv-mcp-server)
- Claude Desktop or another MCP-compatible client

## Available MCP Servers

### 1. arXiv MCP Server

**Purpose**: Access arXiv preprints with search, download, and metadata extraction

**Installation**:
```bash
# Install via uv
uv tool install arxiv-mcp-server

# Or via smithery (automatic)
npx -y @smithery/cli install arxiv-mcp-server --client claude
```

**Configuration** (add to Claude Desktop `claude_desktop_config.json`):
```json
{
  "mcpServers": {
    "arxiv-mcp-server": {
      "command": "uv",
      "args": [
        "tool",
        "run", 
        "arxiv-mcp-server",
        "--storage-path", "/path/to/paper/storage"
      ]
    }
  }
}
```

**Environment Variables**:
```bash
export ARXIV_STORAGE_PATH="~/.arxiv-mcp-server/papers"  # Optional
export TRANSPORT="stdio"  # Default
```

### 2. Brave Search MCP Server

**Purpose**: Web search for academic content and real-time research

**Installation**:
```bash
npm install -g @modelcontextprotocol/server-brave-search
```

**Configuration**:
```json
{
  "mcpServers": {
    "brave-search": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-brave-search"],
      "env": {
        "BRAVE_API_KEY": "your-brave-api-key"
      }
    }
  }
}
```

**Environment Variables**:
```bash
export BRAVE_API_KEY="your-brave-api-key"  # Required - get from https://brave.com/search/api/
```

### 3. GitHub MCP Server

**Purpose**: Search repositories for research code and datasets

**Installation**:
```bash
npm install -g @modelcontextprotocol/server-github
```

**Configuration**:
```json
{
  "mcpServers": {
    "github": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-github"],
      "env": {
        "GITHUB_PERSONAL_ACCESS_TOKEN": "your-github-token"
      }
    }
  }
}
```

**Environment Variables**:
```bash
export GITHUB_TOKEN="your-github-personal-access-token"  # Required
```

### 4. Filesystem MCP Server

**Purpose**: Local file operations and research data management

**Installation**:
```bash
npm install -g @modelcontextprotocol/server-filesystem
```

**Configuration**:
```json
{
  "mcpServers": {
    "filesystem": {
      "command": "npx",
      "args": [
        "-y", 
        "@modelcontextprotocol/server-filesystem",
        "--allowed-directory", "/path/to/research/data"
      ]
    }
  }
}
```

### 5. PostgreSQL MCP Server (Optional)

**Purpose**: Database storage for research results and metadata

**Installation**:
```bash
npm install -g @modelcontextprotocol/server-postgres
```

**Configuration**:
```json
{
  "mcpServers": {
    "postgres": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-postgres"],
      "env": {
        "POSTGRES_CONNECTION_STRING": "postgresql://user:pass@localhost:5432/research_db"
      }
    }
  }
}
```

## Complete Claude Desktop Configuration

Here's a complete `claude_desktop_config.json` example for Bach research:

```json
{
  "mcpServers": {
    "arxiv-mcp-server": {
      "command": "uv",
      "args": [
        "tool", "run", "arxiv-mcp-server",
        "--storage-path", "~/.arxiv-mcp-server/papers"
      ]
    },
    "brave-search": {
      "command": "npx", 
      "args": ["-y", "@modelcontextprotocol/server-brave-search"],
      "env": {
        "BRAVE_API_KEY": "your-brave-api-key"
      }
    },
    "filesystem": {
      "command": "npx",
      "args": [
        "-y", "@modelcontextprotocol/server-filesystem", 
        "--allowed-directory", "."
      ]
    },
    "github": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-github"],
      "env": {
        "GITHUB_PERSONAL_ACCESS_TOKEN": "your-github-token"
      }
    }
  }
}
```

## Environment Setup

Create a `.env` file in your Bach project:

```bash
# Required for Brave Search
BRAVE_API_KEY=your-brave-api-key

# Required for GitHub access
GITHUB_TOKEN=your-github-personal-access-token

# Optional for arXiv storage
ARXIV_STORAGE_PATH=~/.arxiv-mcp-server/papers

# Optional for PostgreSQL
POSTGRES_CONNECTION_STRING=postgresql://user:pass@localhost:5432/research_db

# API keys for direct API fallbacks
SEMANTIC_SCHOLAR_API_KEY=your-semantic-scholar-key
PUBMED_EMAIL=your-email@example.com
```

## Verification

Test your MCP setup:

```python
from bach.utils.mcp.mcp_client import create_research_mcp_client

# Test MCP connections
client = await create_research_mcp_client()
health = await client.health_check()

for server, status in health.items():
    print(f"{server}: {'✓' if status['healthy'] else '✗'}")
```

## Usage in Bach Commands

The Bach system will automatically use available MCP servers:

```bash
# This will use arxiv-mcp-server if available, fallback to API
/bach:research-search "quantum computing"

# MCP servers provide faster response times and additional features:
# - arXiv: Full paper download and local storage
# - Brave: Real-time web search for latest research
# - GitHub: Code and dataset discovery
# - Filesystem: Organized result storage
```

## Troubleshooting

### Common Issues:

1. **MCP server not starting**: Check installation and permissions
2. **API key errors**: Verify environment variables are set correctly
3. **Path issues**: Use absolute paths in configuration
4. **Network errors**: Check firewall and proxy settings

### Debug Commands:

```bash
# Test arXiv MCP server directly
uv tool run arxiv-mcp-server --help

# Test npm-based servers
npx @modelcontextprotocol/server-brave-search --help

# Check environment variables
env | grep -E "(BRAVE|GITHUB|ARXIV)"
```

## Performance Benefits

Using MCP servers provides:

- **Faster response times** (local caching)
- **Offline capabilities** (downloaded papers)
- **Enhanced features** (full-text search, metadata extraction)
- **Organized storage** (automatic file management)
- **API rate limit bypass** (for cached content)

The Bach system automatically optimizes between MCP and direct API calls based on availability and performance characteristics.