# MCP server (for AI assistants and agents)

The API is also available as an MCP server (Model Context Protocol), so AI
assistants like Claude, ChatGPT, Cursor or Codex can call it as a tool. No API
key or sign up needed.

Server URL:

```
https://api.sunrise-sunset.org/mcp
```

It is a stateless remote server (Streamable HTTP transport) with two tools:

- `get_sun_times(lat, lng, date?, tz?)`: everything the v2 API returns, for one day.
- `get_sun_times_range(lat, lng, date_start, date_end, tz?)`: up to 366
  consecutive days in a single call.

## How to connect

**Claude** (claude.ai or the apps): Settings → Connectors → Add custom
connector, and paste the URL above.

**Claude Code**, from the terminal:

```sh
claude mcp add --transport http sunrise-sunset https://api.sunrise-sunset.org/mcp
```

**ChatGPT**: Settings → Apps & Connectors → Advanced settings → Developer
mode, then add the URL as a custom connector.

**Codex**, from the terminal:

```sh
codex mcp add sunrise-sunset --url https://api.sunrise-sunset.org/mcp
```

**Cursor**: add this to `~/.cursor/mcp.json` (or `.cursor/mcp.json` inside a
project). The same content is in [cursor-mcp.json](cursor-mcp.json).

```json
{ "mcpServers": { "sunrise-sunset": { "url": "https://api.sunrise-sunset.org/mcp" } } }
```

**Any other MCP client** works too: it is a standard remote MCP server over
Streamable HTTP, with no authentication.

## Things to ask once connected

- "When is golden hour in San Francisco tomorrow?"
- "How much daylight does Seattle lose during November?"
- "Which nights this month will be darkest for stargazing in Moab, Utah?"

## Testing it by hand

The server speaks JSON-RPC 2.0 over POST, so you can try it with curl:

```sh
curl -s https://api.sunrise-sunset.org/mcp \
  -H 'Content-Type: application/json' \
  -H 'Accept: application/json, text/event-stream' \
  -d '{"jsonrpc":"2.0","id":1,"method":"tools/call","params":{"name":"get_sun_times","arguments":{"lat":39.74,"lng":-104.99,"date":"2026-08-15"}}}'
```

## Attribution

Same as the REST API: show a visible link to
[sunrise-sunset.org](https://sunrise-sunset.org) wherever you display the data.

Full setup guide: https://sunrise-sunset.org/mcp
