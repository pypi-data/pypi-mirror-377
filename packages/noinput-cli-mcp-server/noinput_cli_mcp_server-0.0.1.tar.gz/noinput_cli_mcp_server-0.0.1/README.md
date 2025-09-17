# Non-interactive CLI MCP Server

This server is a fork of https://github.com/MladenSU/cli-mcp-server by MLaden. It short-circuits the child process 
STDIN to /dev/null, thus preventing sporadic application timeouts on Windows platforms.