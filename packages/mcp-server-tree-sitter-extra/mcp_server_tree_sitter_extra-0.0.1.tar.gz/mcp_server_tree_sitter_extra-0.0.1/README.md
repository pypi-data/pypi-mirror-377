# MCP Tree-sitter Server (Extended)

An extension over https://github.com/wrale/mcp-server-tree-sitter

## Features

- Extra language mappings by default
- Compact AST tree (table-of-content)

## Installation

### Prerequisites

- Python 3.10+
- Tree-sitter language parsers for your preferred languages

### Basic Installation

```bash
pip install mcp-server-tree-sitter-extra
```

## Quick Start

### Setting up with AIRun

1. Open your server.json configuration file:

2. Add the server to the `mcpServers` section:

   ```json
   "tree_sitter": {
      "command": "uvx",
      "args": [
        "--index-url",
        "https://nexus-ci.core.kuberocketci.io/repository/krci-python-group/simple/",
        "--from",
        "mcp-server-tree-sitter-extra",
        "mcp-server-tree-sitter-extra"
      ]
    }
   ```

## License

MIT