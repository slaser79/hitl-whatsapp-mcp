---
title: "Remote MCP behind a reverse proxy (DNS-rebinding / HTTP 421)"
type: lesson
products: [hitl-whatsapp-mcp]
last_updated: 2026-05-30
sources:
  - .specs/lessons_learned.md
  - .specs/features/SPEC-WAMCP-001_whatsapp_remote_mcp.md
  - PR slaser79/hitl-whatsapp-mcp#16
cross_refs:
  - ../index.md
  - ../../features/SPEC-WAMCP-001_whatsapp_remote_mcp.md
---

# Remote MCP behind a reverse proxy

> Doctrine verified at commit `427098b` (PR #16) + live `401`/`200` over the
> tailnet URL `https://<node>.ts.net:8443/mcp`.

### Symptom

Exposing the streamable-HTTP MCP server over the tailnet — whether by binding
directly to the Tailscale IP **or** proxying via `tailscale serve` — returns
**HTTP 421 (Misdirected Request)** on every authenticated request. Loopback
clients work fine.

### Root cause

FastMCP's `streamable_http_app()` auto-enables DNS-rebinding protection and
trusts **only loopback `Host` headers** when the server binds to `127.0.0.1`
(`mcp/server/fastmcp/server.py`: `allowed_hosts=["127.0.0.1:*","localhost:*","[::1]:*"]`).
A reverse proxy such as **Tailscale Serve forwards the original tailnet `Host`**
(e.g. `node.ts.net:8443`), which is not in that allow-list → 421. The bearer
auth check runs first (so a tokenless request still 401s), then the Host check
rejects the authenticated one.

This made the **documented** remote flow (`SETUP.md` + `run-tailscale-serve.sh`)
non-functional out of the box — and the serve-script test only mocked
`tailscale` and asserted the command string, so it never exercised a proxied
(non-loopback `Host`) request.

### Fix

- `WHATSAPP_MCP_ALLOWED_HOSTS` (comma-separated; loopback always retained;
  `host:*` matches any port) widens `mcp.settings.transport_security` before the
  app is built. Bearer auth is unchanged.
- `run-tailscale-serve.sh` auto-derives the node's MagicDNS name into that
  allow-list, uses modern `tailscale serve --bg --https <port> <localport>`
  (the old `serve https / <url>` positional form is superseded), and tears down
  with `serve --https=<port> off` — **never `serve reset`**, which wipes a
  host's *other* Serve routes.

### Rule

- Any reverse-proxied MCP deployment must add the proxy's public hostname to the
  Host allow-list; loopback-only is the default and will 421 everything else.
- A user-facing remote flow is not "done" until a test sends a **non-loopback
  `Host` header** and asserts 200 (with allow-list) / 421 (without). Asserting
  the proxy command string is not enough.
- Teardown of a shared proxy must be route-scoped, never global `reset`.
