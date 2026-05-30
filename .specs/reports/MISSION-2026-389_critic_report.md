# 🕵️ Critic Report: MISSION-2026-389 — WhatsApp Remote-MCP (SPEC-WAMCP-001)

**Date:** 2026-05-30
**Status:** ✅ SUCCESS (delivered scope P-IMPL-1..3)
**Commit Verified:** `699956f` (`main` tip; PRs #4, #6, #8, #11 squash-merged)
**Report To:** CEO (Direct Accountability)

## 1. Verification Strategy
- **Environment:** Satellite `hitl-whatsapp-mcp` — local Python 3.12 (uv) per repo CRITIC guide.
- **Tooling Used:** `uv run pytest`, `uv run ruff`, live `uv run python main.py` HTTP/SSE servers
  exercised with `curl`, `bash -n`, real fail-closed startup smoke tests.
- **Scope:** P-IMPL-1 transport (#4), P-IMPL-2A auth + fail-closed guard (#6),
  P-IMPL-2B typed errors + privacy assertion (#8), P-IMPL-3 tailscale serve + SETUP.md (#11).
- **Explicitly out of scope:** P-IMPL-4 hitl-app client integration (cross-repo to
  `slaser79/hitl-app`, spec §4.2/§7). BO1/BO2 reported as *server-side ready, client
  integration pending P-IMPL-4* — NOT a defect.

## 2. CEO Business Outcomes Verification
| Business Outcome | Status | Evidence |
|-----------------|--------|----------|
| **BO1** — Phone reads WhatsApp | ⏳ SERVER-READY | All read tools (`list_chats`, `list_messages`, `search_contacts`, `get_chat`, `get_contact`…) registered + unit-tested; exposed over authed remote transport. End-to-end from phone gated on P-IMPL-4 (out of scope). |
| **BO2** — Phone sends WhatsApp | ⏳ SERVER-READY | `send_message`/`send_file`/`send_audio_message` registered, typed-error wrapped, unit-tested. Phone integration = P-IMPL-4. |
| **BO3** — 15-minute setup | ✅ READY | `SETUP.md` is a copy-paste 8-step flow (bridge QR → `openssl rand -hex 24` token → one `./scripts/run-tailscale-serve.sh` command → connect). Timed cross-device dry-run is a manual mile (see §6/AC6). |
| **BO4** — Secure by default | ✅ PASS | Loopback default bind + Tailscale proxy; every non-stdio request without a valid token → 401 (live-verified); fail-closed guard exits non-zero on both unsafe arms (live-verified). |
| **BO5** — Privacy preserved | ✅ PASS | `test_privacy` asserts local-only absolute SQLite paths, no remote URI schemes; no empire egress in code; SETUP §6 documents an egress sanity check. |

**Business Value Delivered:** YES for the delivered server-side scope (BO3/BO4/BO5 met;
BO1/BO2 server-ready, awaiting the cross-repo client phase by design).

## 3. Full Spec Review (not just Acceptance Criteria)
| Spec Section | Status | Notes |
|--------------|--------|-------|
| §1 Executive Summary | ✅ | Secure remote MCP fork delivered; intent met. |
| §2 CEO Business Outcomes | ✅ / ⏳ | See §2. BO1/BO2 client phase is explicitly §7-deferred. |
| §3 User Stories | ✅ | URL+token connect, copy-paste guide, tailnet-only + token, refuse unsafe start — all addressed. |
| §4.1 Architecture | ✅ | Loopback + `tailscale serve` default; bearer/API-key ASGI middleware; fail-closed guard both arms. |
| §4.1.1 Env contract | ✅ | `WHATSAPP_MCP_TRANSPORT/HOST/PORT(8089)/AUTH/TOKEN` honoured exactly; stdio ignores host/port/auth. |
| §4.3 Edge Cases EC1–EC5 | ✅ | Typed errors for session-expiry, bridge-down, chat-not-found; ffmpeg→SystemDependencyError; EC3 fail-fast + EC4 guard. |
| §5 Acceptance Criteria | ✅ | See §4 (AC table). |
| §6 Verification Plan | ✅ | Ran §6.1 + §6.2 commands live. |
| §8 Non-Goals | ✅ | Go bridge protocol untouched; Funnel not default; no empire storage. |
| **Gaps Found** | ⚠️ P2 | One minor placeholder-detector edge (see §7). Non-blocking. |

## 4. Acceptance Criteria Checks
| Criterion | Status | Evidence |
|-----------|--------|----------|
| **AC1** Repo/MIT/registration/CI | ✅ PASS* | MIT attribution chain intact (`LICENSE`: Harries → Very Good Plugins). `.github/workflows/ci.yml` present. Empire registration done in HQ (PR #2887, out-of-repo). *CI caveat below.* |
| **AC2** http+sse start; stdio regression-safe | ✅ PASS | Live: `…listening on 127.0.0.1:8089 via streamable-http` and `…via sse`. stdio with `PORT=not-a-port HOST=0.0.0.0` did **not** crash (exit 0, clean) — stdio ignores host/port. `test_transport.py` parametrizes all four. |
| **AC3** 401 w/o token, accept valid | ✅ PASS | Live `/mcp`: no token → **401**, bad token → **401**, valid Bearer → **406** (non-401 protocol response), valid `X-API-Key` → **406**. Timing-safe `hmac.compare_digest`. |
| **AC4a** non-loopback + auth=off → exit≠0 | ✅ PASS | Live: `HOST=0.0.0.0 AUTH=off` → exit 1, "Unsafe MCP configuration … only permitted when WHATSAPP_MCP_HOST is loopback". |
| **AC4b** auth=on + missing/weak/placeholder → exit≠0 | ✅ PASS | Live: `TOKEN=short`→exit1 (`…at least 32 characters`); `TOKEN=` empty→exit1 (`…is required`); 35-char `changeme_…`→exit1 (`…must not be a placeholder`). |
| **AC5** tailnet-reachable, not public | ✅ READY (manual mile) | `run-tailscale-serve.sh` binds loopback + `tailscale serve https / http://127.0.0.1:$PORT`. Cross-device/public-internet reachability is a live-tailnet manual verification (Setup Report below). |
| **AC6** ≤15-min copy-paste SETUP | ✅ READY (manual mile) | `SETUP.md` is copy-paste, 8 steps, one run command. Timed fresh-user dry-run requires a real WhatsApp QR + tailnet — manual mile for CEO. |
| **AC7** core tools end-to-end over remote+auth | ✅ / ⏳ | Tools registered + auth-gated + unit-tested; full live send/read needs a linked WhatsApp account (P-IMPL-4 / manual). |
| **AC8** unit tests for transport/auth/guard/typed-errors | ✅ PASS | 78 tests pass: `test_transport.py` (guard both arms parametrized), `test_failure_modes.py` (EC1/EC2/EC5 + ffmpeg), `test_privacy.py`, `test_tailscale_serve_script.py`. |
| **AC9** privacy / local-only DB | ✅ PASS | `test_db_paths_are_local` (absolute paths, no remote URI, stdlib sqlite3). No empire egress in code. |
| **AC10** EC1/EC2/EC3 typed/fail-fast not 500/hang | ✅ PASS | EC1 503→`whatsapp_session_expired`; EC2 ConnectionError→`bridge_unavailable`; EC5 400→`chat_not_found`; ffmpeg→`internal_error` (SystemDependencyError, **not** chat_not_found); EC3 script fails fast "Tailscale is not connected — run `tailscale up`". |

\* **AC1 CI caveat (flagged, not a defect):** this is a GitHub fork; Actions auto-run on
PRs is blocked by GitHub's one-time fork UI-enable gate, so each PR (#4/#6/#8/#11) was
verified manually rather than by a green Actions check on `main`. The `ci.yml` workflow
is present and correct; the gate is a GitHub-platform artifact of forking, not a code or
spec defect. **Recommendation:** CEO/owner clicks "I understand … enable Actions" once on
the fork so future PRs auto-run. I do **not** consider this an AC1 failure.

## 5. E2E / Tests Verified
| Test File | Coverage | Result |
|-----------|----------|--------|
| `test_transport.py` | transport selection, auth middleware accept/reject, guard both arms, port/transport errors | ✅ |
| `test_failure_modes.py` | EC1/EC2/EC5 typed errors, ffmpeg→internal_error, 500→bridge_unavailable, invalid params | ✅ |
| `test_privacy.py` | AC9 local-only DB paths | ✅ |
| `test_tailscale_serve_script.py` | EC3 fail-fast, missing-binary, loopback+serve launch, **early-exit must-not-reset** | ✅ |
| `test_get_contact.py` / `test_list_chats.py` / `test_whatsapp.py` | tool/data conversions | ✅ |

**Totals:** `78 passed`, `ruff: All checks passed`, `bash -n: CLEAN`.

## 6. Evidence
- [Raw verification output](assets/MISSION-2026-389/verification_output.log)
- Live HTTP auth gate: 401 / 401 / 406 / 406 (no / bad / Bearer / X-API-Key).
- Live fail-closed: 4/4 unsafe configs exit non-zero with precise var-naming messages.

### Setup Report (manual mile for CEO — AC5/AC6/BO1/BO2)
The automated + spec-verifiable surface is fully green. The remaining verification requires a
physical/live context the sandbox cannot provide:
1. **WhatsApp QR login** on the host (`cd whatsapp-bridge && go run .`, scan QR).
2. **Tailscale up** on host + a **second tailnet device**.
3. `export WHATSAPP_MCP_TOKEN="$(openssl rand -hex 24)"` then `./scripts/run-tailscale-serve.sh`.
4. From device 2: open the tailnet DNS name → confirm reachable; confirm public internet is NOT.
5. Time the walkthrough (BO3/AC6 ≤15 min). The mechanism is in place and self-consistent.

## 7. Findings (non-blocking)
- **P2 (observation):** the placeholder guard blocks tokens `<32` chars and tokens containing
  known markers (`changeme`, `placeholder`, …). A deliberately crafted ≥32-char low-entropy
  string with no marker substring (e.g. `"test"×8`) would pass. Realistically a non-issue —
  the setup flow generates `openssl rand -hex 24` and never hand-picks tokens — but an entropy
  check could close it. Not a defect against AC4/§4.1.1.

## 8. Conclusion (to the CEO)
**VERDICT: ✅ SUCCESS for the delivered scope (P-IMPL-1..3).** Every automated and
spec-verifiable acceptance criterion passes against live behavior, not just green tests:
remote http/sse transports start, the auth gate returns 401 unauthenticated and accepts a
valid Bearer/API-key, the fail-closed guard refuses to start in all four unsafe
configurations, typed failure-mode errors surface correctly (no generic 500s/hangs), the
DB stays local-only, and the Tailscale run script fails fast and never wipes unrelated
Serve routes on early exit. 78/78 tests pass, ruff clean, MIT attribution intact.

BO1/BO2 (phone read/send end-to-end) are **server-side ready**; their final verification is
owned by the explicitly-deferred cross-repo phase **P-IMPL-4 (hitl-app)** per spec §4.2/§7 —
correctly out of scope here and **not** a defect. AC5/AC6 mechanisms are in place and require
a one-time CEO-side live-tailnet/QR dry-run (Setup Report §6). The only finding is a single
non-blocking P2 observation.

**Recommendation:** Sign off MISSION-2026-389 for the server-side scope; dispatch P-IMPL-4
to `hitl-app` to close BO1/BO2 end-to-end.
