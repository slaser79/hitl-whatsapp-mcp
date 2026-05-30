# CRITIC Verification Guide: HITL WhatsApp Remote-MCP

*Read by the CRITIC agent when verifying missions for this product.*

## Environment Setup
```bash
cd whatsapp-mcp-server
uv sync --all-extras
```

## Test Suites
| Suite | Command | What It Covers |
|-------|---------|----------------|
| Unit | `cd whatsapp-mcp-server && uv run pytest -v` | Transport selection, auth accept/reject, fail-closed guard, typed failure-mode errors |
| Lint | `cd whatsapp-mcp-server && uv run ruff check .` | Style/lint |

## Known Quirks
- WhatsApp (whatsmeow) requires re-auth roughly every ~20 days (QR rescan on host). Failure-mode handling is specced in SPEC-WAMCP-001 §4.3 (EC1).
- The Go `whatsapp-bridge/` is upstream; do not modify protocol internals (Non-Goal).
- Upstream already ships `.github/workflows/ci.yml`; empire CI must not regress it.

## Verification Checklist (SPEC-WAMCP-001)
- [ ] AC2 transport selection (stdio/http/sse) works
- [ ] AC3 401 on missing token; accepted with valid token
- [ ] AC4 fail-closed guard: (a) non-loopback+auth-off AND (b) weak/empty token both exit non-zero
- [ ] AC5 reachable from a 2nd tailnet device, NOT public internet
- [ ] AC6 timed ≤15-min SETUP walkthrough
- [ ] AC9 no empire egress; local-only DB
- [ ] AC10 typed errors for session-expiry / bridge-down / no-Tailscale
- [ ] All tests pass; ruff clean; no secrets committed; MIT attribution intact
