# Development Quick-Start

## 🧪 Development Testing with **MCP Inspector**

```bash
# Gateway & auth
export MCP_GATEWAY_BASE_URL=http://localhost:4444
export MCP_SERVER_URL=http://localhost:4444/servers/UUID_OF_SERVER_1/mcp
export MCP_AUTH="Bearer <your_bearer_token>"
```

| Mode                                                        | Command                                                                      | Notes                                                                         |
| ----------------------------------------------------------- | ---------------------------------------------------------------------------- | ----------------------------------------------------------------------------- |
| **SSE (direct)**                                            | `npx @modelcontextprotocol/inspector`                                        | Connects straight to the Gateway's SSE endpoint.                              |
| **Stdio wrapper** <br/>*(for clients that can't speak SSE)* | `npx @modelcontextprotocol/inspector python3 -m mcpgateway.wrapper`           | Spins up the wrapper **in-process** and points Inspector to its stdio stream. |
| **Stdio wrapper via uv / uvx**                            | `npx @modelcontextprotocol/inspector uvx python3 -m mcpgateway.wrapper` | Uses the lightning-fast `uv` virtual-env if installed.                        |

🔍 MCP Inspector boots at **[http://localhost:5173](http://localhost:5173)** - open it in a browser and add:

```text
Server URL: http://localhost:4444/servers/UUID_OF_SERVER_1/sse
Headers:    Authorization: Bearer <your_bearer_token>
```

---

## 🌉 SuperGateway (stdio-in ⇢ SSE-out bridge)

SuperGateway lets you expose *any* MCP **stdio** server over **SSE** with a single command - perfect for
remote debugging or for clients that only understand SSE.

```bash
# Using uvx (ships with uv)
pip install uv
npx -y supergateway --stdio "uvx mcp-server-git"
```

| Endpoint                 | Method | URL                                                            |
| ------------------------ | ------ | -------------------------------------------------------------- |
| **SSE stream**           | `GET`  | [http://localhost:8000/sse](http://localhost:8000/sse)         |
| **Message back-channel** | `POST` | [http://localhost:8000/message](http://localhost:8000/message) |

Combine this with the Gateway:

```bash
# Register the SuperGateway SSE endpoint as a peer
curl -X POST -H "Authorization: Bearer $MCPGATEWAY_BEARER_TOKEN" \
     -H "Content-Type: application/json" \
     -d '{"name":"local-supergateway","url":"http://localhost:8000/sse"}' \
     http://localhost:4444/gateways
```

The tools hosted by **`mcp-server-git`** are now available in the Gateway catalog, and therefore
also visible through `mcpgateway.wrapper` or any other MCP client.

```
