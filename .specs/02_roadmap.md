# Roadmap: HITL WhatsApp Remote-MCP

*Product-specific roadmap. The empire-wide roadmap lives in HQ (`agent_workflows/.specs/02_roadmap.md`).*

## Phase 1: Bootstrapping (Current)
- [x] Fork upstream + preserve MIT attribution
- [x] Establish `.specs` governance structure
- [x] Register in HQ `config/empire.yaml`
- [ ] CI green on `main` + webhook to HQ

## Phase 2: Remote-MCP MVP (SPEC-WAMCP-001)
- [ ] P-IMPL-1: Remote transport (adopt PR-112 `WHATSAPP_MCP_TRANSPORT` http/sse)
- [ ] P-IMPL-2: Auth middleware + fail-closed guard (bearer/API-key, weak-token refusal)
- [ ] P-IMPL-3: Tailscale `tailscale serve` run scripts + SETUP.md (≤15-min)
- [ ] P-IMPL-4: hitl-app client integration (cross-repo to `hitl-app`)
