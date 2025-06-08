# tunebat-mcp

MCP with access Tunebat Search

## Requirements

This assumes you have [direnv](https://direnv.net/) and [uv](https://github.com/astral-sh/uv) installed

Simply run `direnv allow` to setup the environment, you can read the contents of [.envrc](.envrc) to see what it does behind the scenes.


## MCP Client Configuration

### Cursor

1. [Cursor MCP Config](.cursor/mcp.json) is already filled in for you

2. **Restart Cursor** for the changes to take effect

That's it! The server will automatically pick up your environment variables from the `.env` file.

### Calude

Update the claud desktop config to this

```
{
  "mcpServers": {
    "tunebat-mcp": {
      "command": "/PATH/TO/.local/bin/uv",
      "args": [
        "--directory",
        "/PATH/TO/tunebat-mcp",
        "run",
        "--refresh-package",
        "tunebat-mcp",
        "--with",
        ".",
        "tunebat-mcp"
      ],
      "cwd": ".",

    }
  }
}
```
