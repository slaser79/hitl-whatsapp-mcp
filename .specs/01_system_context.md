# System Context & Architecture

## Tech Stack
*   **Language/Framework:** Python 3.12 (uv) — `whatsapp-mcp-server/` (FastMCP/FastAPI MCP server); Go (whatsmeow) — `whatsapp-bridge/` (WhatsApp Web multidevice bridge).
*   **Infrastructure:** Self-hosted on the user's host; Tailscale for private remote exposure; local SQLite for messages/contacts.

## Development Constraints
*   **Build Command:** `uv sync --all-extras` (in `whatsapp-mcp-server/`)
*   **Test Command:** `uv run pytest -v` (in `whatsapp-mcp-server/`)
*   **Linter:** `uv run ruff check .`

## Repository Structure
*   `whatsapp-mcp-server/` - Python MCP server (transport + auth layers added by the empire)
*   `whatsapp-bridge/` - Go whatsmeow bridge (upstream; do not modify protocol internals)
*   `.specs/` - Source of Truth (Docs-as-Code)
*   `.specs/features/` - Feature specs (some synced from HQ via SpecRouter)
*   `.specs/knowledge/` - Research and domain docs (some synced from HQ)
