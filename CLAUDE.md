# CLAUDE.md

This file is here for Claude Code (claude.ai/code), which looks for `CLAUDE.md` by name.

The actual contributor + agent guide for this repository lives in **[`AGENTS.md`](./AGENTS.md)**. Read it first.

Companion docs:

- [`ROADMAP.md`](./ROADMAP.md) — what this fork is (and is not) trying to be.
- [`CONTRIBUTING.md`](./CONTRIBUTING.md) — human-facing contribution guide.
- [`README.md`](./README.md) — installation and usage.

---

# HITL Empire Satellite — Agent Operational Protocol

**ATTENTION AGENT:** This repository is a **Satellite** of the **HITL Empire**, managed by Mission Control (HQ: `slaser79/agent_workflows`). It is a fork of `verygoodplugins/whatsapp-mcp` (MIT) — **preserve the upstream attribution chain in `LICENSE`**. For upstream contributor/agent guidance see **[`AGENTS.md`](./AGENTS.md)**; the rules below are the empire overlay and take precedence for empire missions.

## 1. The Constitution (Non-Negotiable)
- **Spec-First Doctrine:** No code without a spec. Read `.specs/features/` first; code must match the spec. No spec for your task → escalate to CoS.
- **Atomic Work:** Don't break the build. Run tests before finishing. Every PR independently verifiable.
- **Communication:** `empire_ask` (blocking) for decisions, `empire_notify` (async) for updates; fall back to human-in-the-loop tools. Never use native `input()`/`print()` to communicate.
- **Kaizen:** Read `.specs/lessons_learned.md` before each mission; add a lesson after each failure.
- **Stuck Escalation:** If stuck >30 min or the same approach failed 2+ times — commit/push WIP, escalate with a structured report, then wait.

## 2. Tooling
- **Stack:** Python 3.12 (uv) MCP server in `whatsapp-mcp-server/`; Go whatsmeow bridge in `whatsapp-bridge/`.
- **Test:** `cd whatsapp-mcp-server && uv run pytest -v`
- **Lint:** `cd whatsapp-mcp-server && uv run ruff check .`

## 3. Empire Topology
- **Product ID:** `hitl-whatsapp-mcp`
- **Mission manifests live in HQ** (`agent_workflows/.specs/missions/`), NOT here. Never create manifests in this repo.
- **Specs may be synced from HQ** via SpecRouter — check `.specs/features/` for synced specs.

## 4. Manifest Placement (Critical)
- **Manifests** → `upsert_mission_manifest()` → always HQ.
- **Specs** → `upsert_spec_file(product_id="hitl-whatsapp-mcp")` → this satellite.
- **NEVER git commit mission manifests into this repo's worktree.**

## 5. Known Constraints
- **Secrets:** Never commit keys/tokens. Generate the MCP bearer token at setup; request infra secrets via HITL.
- **Security:** Any non-stdio transport MUST require auth and fail closed on a missing/weak token (SPEC-WAMCP-001 AC4).
- **Do not modify the Go bridge protocol internals** (project Non-Goal).
- **Tests:** New features MUST have tests. PRs include `Closes #<issue>` and target the correct branch.
