# Empire Brain — `hitl-whatsapp-mcp`

Durable, curated knowledge for this satellite. Modelled on the mature
`hitl-shin-relay` brain.

## Two-tier protocol

- **Tier 1 — Worker (raw discovery):** at the end of a mission, dump signal into
  `_pending/<MISSION-ID>.md`. Workers read the curated brain but contribute via
  `_pending/`, not by editing curated files directly.
- **Tier 2 — Librarian (synthesis):** periodically drains `_pending/` into
  curated `lessons/` and `entities/`, deduplicating and maintaining `index.md`.

## Layout

- `lessons/` — durable, **verified** doctrine (`Symptom / Root Cause / Fix /
  Rule`). Never publish an unverified hypothesis as a lesson; label hypotheses
  explicitly.
- `index.md` — the curated index of lessons/entities.
- `_pending/` — low-friction raw dumps awaiting synthesis.
- `meta-learning.md` — one line per reflection session (see `empire-self-reflect`).

## Lesson frontmatter

```yaml
---
title: "..."
type: lesson
products: [hitl-whatsapp-mcp]
last_updated: YYYY-MM-DD
sources: [ ... ]
cross_refs: [ ../index.md ]
---
```
