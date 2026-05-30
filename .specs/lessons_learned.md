# Lessons Learned: HITL WhatsApp Remote-MCP

*Product-specific lessons. The empire-wide lessons database lives in HQ (`agent_workflows/.specs/lessons_learned.md`).*

## Protocols
- Preserve the upstream MIT attribution chain (lharries -> Very Good Plugins) in LICENSE on every change.
- Auth is mandatory on any non-stdio transport; a missing/weak token must fail closed (never silently run open).

## Chronological Lessons
- 2026-05-30: Repo bootstrapped from `verygoodplugins/whatsapp-mcp` per MISSION-2026-389. Remote transport via upstream PR-112; empire value-add = auth + Tailscale gating + setup guides.

- **Lesson:** In this satellite worktree the Bash tool cwd starts inside `whatsapp-mcp-server/`, so the spec's `cd whatsapp-mcp-server && ...` commands fail with "No such file or directory"; run `uv`/`pytest` directly (already in the server dir) or `pwd` first. **Context:** MISSION-2026-389 CRITIC verification.
