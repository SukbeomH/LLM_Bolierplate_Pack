# Option A: Manual Mode Instructions

## Overview
This mode gives you the raw tools (MCP Servers) running in Docker. You are responsible for prompting your LLM (Claude/GPT) to use them.

## Setup
1.  **Configure Environment**:
    Copy `.env.example` to `.env` and set `PROJECT_MODE="option_a"`.

2.  **Start Services**:
    ```bash
    docker-compose -f mcp/docker-compose.mcp.yml up -d
    ```

3.  **Connect your LLM**:
    -   **Cursor**: Add the MCP servers in `Cursor Settings > MCP`.
        -   Start Command: `docker exec -i mcp-serena serena-mcp` (example)
    -   **Claude Desktop**: Config `claude_desktop_config.json` to point to the docker containers.

## Available Tools
-   **Serena**: Symbol-based code search (`search_symbol`).
-   **Codanna**: Semantic search (`search_semantic`).
-   **Shrimp**: Task management.

## Workflow
1.  Open your Chat.
2.  Type: `@Serena Find the definition of Auth class`
3.  Type: `@Codanna Explain how authentication works in this repo`
