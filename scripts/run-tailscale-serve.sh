#!/usr/bin/env bash

set -euo pipefail

script_dir="$(cd "${BASH_SOURCE[0]%/*}" && pwd)"
repo_root="$(cd "$script_dir/.." && pwd)"
server_dir="$repo_root/whatsapp-mcp-server"
server_pid=""
serve_configured=0

fail() {
  printf '%s\n' "$1" >&2
  exit 1
}

cleanup() {
  if [[ -n "$server_pid" ]]; then
    kill "$server_pid" >/dev/null 2>&1 || true
    wait "$server_pid" >/dev/null 2>&1 || true
  fi
  if [[ "$serve_configured" == "1" ]]; then
    tailscale serve reset >/dev/null 2>&1 || true
  fi
}

trap cleanup EXIT INT TERM

command -v tailscale >/dev/null 2>&1 || fail "Tailscale is not installed — install Tailscale, then run \`tailscale up\`"

python3 - <<'PY'
import json
import subprocess
import sys

result = subprocess.run(["tailscale", "status", "--json"], capture_output=True, text=True)
if result.returncode != 0:
    print("Tailscale is not connected — run `tailscale up`", file=sys.stderr)
    raise SystemExit(1)

try:
    status = json.loads(result.stdout)
except json.JSONDecodeError as exc:
    print(f"Tailscale status output was invalid JSON: {exc}", file=sys.stderr)
    raise SystemExit(1)

backend_state = status.get("BackendState")
if backend_state != "Running":
    print(f"Tailscale is not connected (BackendState={backend_state!r}) — run `tailscale up`", file=sys.stderr)
    raise SystemExit(1)
PY

if [[ -z "${WHATSAPP_MCP_TOKEN:-}" ]]; then
  fail 'WHATSAPP_MCP_TOKEN is required. Generate one with: export WHATSAPP_MCP_TOKEN="$(openssl rand -hex 24)"'
fi

export WHATSAPP_MCP_TRANSPORT=http
export WHATSAPP_MCP_HOST=127.0.0.1
export WHATSAPP_MCP_PORT="${WHATSAPP_MCP_PORT:-8089}"
export WHATSAPP_MCP_AUTH=on

cd "$server_dir"
uv run main.py &
server_pid=$!

tailscale serve https / "http://127.0.0.1:${WHATSAPP_MCP_PORT}"
serve_configured=1

wait "$server_pid"
