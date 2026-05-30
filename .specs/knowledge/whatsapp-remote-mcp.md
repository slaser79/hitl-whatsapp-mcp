---
title: "WhatsApp Remote-MCP for HITL Mobile Agents — Research Findings"
type: knowledge
products: ["hitl-whatsapp-mcp"]
mission: "MISSION-2026-389"
last_updated: 2026-05-30
author: cos
sources:
  - https://github.com/verygoodplugins/whatsapp-mcp
  - https://github.com/verygoodplugins/whatsapp-mcp/pull/112
  - https://github.com/lharries/whatsapp-mcp
  - .specs/brain/entities/tailscale-funnel.md
  - .specs/brain/products/hitl-cli.md
---

# WhatsApp Remote-MCP — Research Findings (MISSION-2026-389)

## 1. Goal

Let mobile agents inside the **hitl-app** read/search/send a user's WhatsApp
messages, the same way `wacli` exposes capabilities to `openclaw`/`hermes`
desktop agents. The vehicle is a **remote MCP server** the phone can reach over
the user's private network.

## 2. Upstream landscape (verified 2026-05-30)

### 2.1 `lharries/whatsapp-mcp` (original)
- **License:** MIT.
- **Architecture:** two components — a **Go bridge** (`whatsmeow`, connects to
  WhatsApp Web multidevice API; **QR-code login**; **~20-day re-auth**; syncs
  history to a **local SQLite** DB) + a **Python MCP server**.
- **Transport:** **stdio only.** No remote/HTTP/SSE exposure.

### 2.2 `verygoodplugins/whatsapp-mcp` (CEO-pinned base — "best/most up to date")
- **License:** MIT (same lineage).
- **Adds over upstream:** webhook forwarding (inbound w/ reply context + image
  media), media auto-download (collision-safe names), `get_contact` tool +
  `sender_display` + LID↔phone matching, voice/video **call-history capture**,
  `/api/typing` + `/api/health` endpoints, `--full-history-pair` extended
  history, `StreamReplaced` session-conflict recovery, GitHub Actions +
  Release-Please CI.
- **Transport on `main`:** still **stdio**; the MCP server talks to the Go
  bridge over a **local REST API** (`http://localhost:8080/api`). Bridge already
  uses **bearer tokens** internally; media paths are sandboxed.

### 2.3 PR #112 (`verygoodplugins/whatsapp-mcp`) — the remote-transport enabler
- **Status:** **OPEN** (awaiting maintainer `jack-arturo`; Copilot review done;
  35 tests pass incl. 8 new; style clean).
- **What it adds:** network transports for the MCP layer via env vars:
  - `WHATSAPP_MCP_TRANSPORT` = `stdio` (default) | `http` (streamable-http) | `sse`
  - `WHATSAPP_MCP_HOST`, `WHATSAPP_MCP_PORT` = bind address/port
- **Security posture:** host defaults to **loopback `127.0.0.1`**. PR notes
  there is **NO built-in auth** — README tells operators to "put an
  authenticating proxy in front before binding to a non-loopback address."

> ⚠️ Note: PR #112 on the *original* `lharries` repo is an unrelated
> "don't trigger webhook on group message" change. The transport PR #112 is on
> the **verygoodplugins** fork.

## 3. The empire value-add (the gap we fill)

Forking + PR-112 alone gives an **unauthenticated** HTTP/SSE MCP server. The
mission's "security + easy setup" requirements mean we add:

1. **Auth layer** in front of streamable-http/SSE: **FastMCP / FastAPI bearer
   token or API key** (mirror `hitl-cli`'s FastMCP + bearer pattern). Latest
   FastAPI/Starlette security utilities (`HTTPBearer`, `APIKeyHeader`,
   dependency-injected auth) make this small.
2. **Tailscale-only exposure:** bind to the **tailnet** interface (or
   `tailscale serve`), NOT public Funnel by default. The phone reaches the
   server over the private tailnet — no port-forwarding, TLS handled by
   Tailscale. (See `entities/tailscale-funnel.md`.)
3. **Dead-simple setup guides:** QR-login walkthrough, Tailscale install + auth,
   one-command run (Docker/compose or `uv run`), and how to register the server
   in the hitl-app.
4. **hitl-app client integration:** the mobile app registers this remote MCP
   server (URL + bearer token) like any other agent/tool endpoint — the
   `wacli`-equivalent connection.

## 4. Prior art to mirror (do NOT reinvent)

| Need | Mirror |
|------|--------|
| FastMCP + bearer/API-key auth | `hitl-cli` (FastMCP ≥0.3, PyJWT, Authlib) |
| Remote MCP server hosting | `hitl-shin-relay` (`hitlrelay.app/mcp-server/mcp/`) |
| Secure private exposure | `entities/tailscale-funnel.md` (`tailscale serve` over Funnel) |
| Mobile remote-agent registration UX | hitl-app openclaw/cloud-agent tiles |

## 5. Open questions for the implementation spec

- **Merge PR #112 vs re-implement transport?** PR is open/unmerged — prefer
  cherry-picking it into our fork (keeps attribution + tests) over reinventing.
- **Auth integration point:** FastMCP middleware vs a thin FastAPI reverse
  proxy in front of the streamable-http app. Lean to FastMCP-native auth to keep
  one process and "easy setup."
- **Token provisioning UX:** generated secret in `.env` + shown in setup guide;
  hitl-app stores it locally (no server-side storage, mirroring openclaw).
- **Tailscale binding:** `tailscale serve` (tailnet-only) as default; document
  Funnel only as an explicit opt-in for users who accept public exposure.

## 6. Security defaults (proposed)

- Bind to tailnet interface; **refuse to start bound to `0.0.0.0` without auth
  enabled** (fail-closed).
- Require a bearer token / API key for every MCP request when transport != stdio.
- Keep WhatsApp session DB local-only; never sync messages off-device.
- Document the ~20-day WhatsApp re-auth reality so users aren't surprised.
