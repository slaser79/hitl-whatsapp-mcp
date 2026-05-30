# Brain Index — `hitl-whatsapp-mcp`

Curated lessons and entities for this satellite. See [`README.md`](./README.md)
for the curation protocol.

## Lessons

- [Remote MCP behind a reverse proxy](lessons/remote-mcp-reverse-proxy.md) —
  FastMCP DNS-rebinding protection rejects proxied (non-loopback) `Host` headers
  with HTTP 421; `WHATSAPP_MCP_ALLOWED_HOSTS` is the contract that makes the
  Tailscale Serve flow work.

## Meta

- [meta-learning.md](lessons/meta-learning.md) — reflection-session log.
