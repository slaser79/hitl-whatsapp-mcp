# Lessons Learned: HITL WhatsApp Remote-MCP

*Product-specific lessons. The empire-wide lessons database lives in HQ (`agent_workflows/.specs/lessons_learned.md`).*

## Protocols
- Preserve the upstream MIT attribution chain (lharries -> Very Good Plugins) in LICENSE on every change.
- Auth is mandatory on any non-stdio transport; a missing/weak token must fail closed (never silently run open).

## Chronological Lessons
- 2026-05-30: Repo bootstrapped from `verygoodplugins/whatsapp-mcp` per MISSION-2026-389. Remote transport via upstream PR-112; empire value-add = auth + Tailscale gating + setup guides.

- **Lesson:** In this satellite worktree the Bash tool cwd starts inside `whatsapp-mcp-server/`, so the spec's `cd whatsapp-mcp-server && ...` commands fail with "No such file or directory"; run `uv`/`pytest` directly (already in the server dir) or `pwd` first. **Context:** MISSION-2026-389 CRITIC verification.

- **Lesson:** The documented Tailscale Serve remote flow was broken out of the box. FastMCP's `streamable_http_app()` auto-enables DNS-rebinding protection trusting only loopback `Host` headers when bound to `127.0.0.1`; a reverse proxy (Tailscale Serve) forwards the original tailnet `Host`, so every proxied request returned **HTTP 421**. Fix: a `WHATSAPP_MCP_ALLOWED_HOSTS` env var that widens the allow-list via `mcp.settings.transport_security`, plus `run-tailscale-serve.sh` auto-deriving the node's MagicDNS name. Also: the old `tailscale serve https / <url>` syntax is superseded by `tailscale serve --bg --https <port> <localport>`, and teardown must use `serve --https=<port> off` (never `serve reset`, which wipes a host's *other* Serve routes). **Context:** CEO self-host setup, 2026-05-30.
