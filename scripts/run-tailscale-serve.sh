#!/usr/bin/env bash

set -euo pipefail

script_dir="$(cd "${BASH_SOURCE[0]%/*}" && pwd)"
repo_root="$(cd "$script_dir/.." && pwd)"
server_dir="$repo_root/whatsapp-mcp-server"
server_pid=""
serve_configured=0
serve_https_port=""

fail() {
  printf '%s\n' "$1" >&2
  exit 1
}

cleanup() {
  if [[ -n "$server_pid" ]]; then
    kill "$server_pid" >/dev/null 2>&1 || true
    wait "$server_pid" >/dev/null 2>&1 || true
  fi
  # Remove only our own HTTPS route, never `serve reset` (which would wipe any
  # other Serve routes this host publishes).
  if [[ "$serve_configured" == "1" && -n "$serve_https_port" ]]; then
    tailscale serve --https="$serve_https_port" off >/dev/null 2>&1 || true
  fi
}

trap cleanup EXIT INT TERM

# Load config (e.g. WHATSAPP_MCP_TOKEN) from a gitignored .env if present.
# WHATSAPP_ENV_FILE overrides the path (tests point it at a throwaway file).
env_file="${WHATSAPP_ENV_FILE:-$repo_root/.env}"
if [[ -f "$env_file" ]]; then
  set -a
  # shellcheck disable=SC1090
  . "$env_file"
  set +a
fi

command -v tailscale >/dev/null 2>&1 || fail "Tailscale is not installed — install Tailscale, then run \`tailscale up\`"

if [[ -z "${WHATSAPP_MCP_TOKEN:-}" ]]; then
  fail 'WHATSAPP_MCP_TOKEN is required. Generate one with: export WHATSAPP_MCP_TOKEN="$(openssl rand -hex 24)"'
fi

# Verify the tailnet is up and capture this node's MagicDNS name so we can
# auto-trust it as a Host header (Tailscale Serve forwards the original Host,
# which FastMCP's DNS-rebinding guard rejects unless explicitly allowed).
tailnet_dns="$(
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

print((status.get("Self") or {}).get("DNSName", "").rstrip("."))
PY
)" || exit 1

serve_https_port="${WHATSAPP_MCP_SERVE_HTTPS_PORT:-443}"
mcp_port="${WHATSAPP_MCP_PORT:-8089}"

# Merge the node's tailnet name into the allow-list (wildcard port).
allowed_hosts="${WHATSAPP_MCP_ALLOWED_HOSTS:-}"
if [[ -n "$tailnet_dns" ]]; then
  host_pattern="${tailnet_dns}:*"
  if [[ -z "$allowed_hosts" ]]; then
    allowed_hosts="$host_pattern"
  else
    allowed_hosts="${allowed_hosts},${host_pattern}"
  fi
fi

export WHATSAPP_MCP_TRANSPORT=http
export WHATSAPP_MCP_HOST=127.0.0.1
export WHATSAPP_MCP_PORT="$mcp_port"
export WHATSAPP_MCP_AUTH=on
export WHATSAPP_MCP_ALLOWED_HOSTS="$allowed_hosts"

cd "$server_dir"
uv run main.py &
server_pid=$!

# Expose the loopback MCP server over the tailnet via TLS (tailnet-only, no Funnel).
tailscale serve --bg --https "$serve_https_port" "$mcp_port"
serve_configured=1

if [[ -n "$tailnet_dns" ]]; then
  printf 'WhatsApp MCP available on your tailnet at: https://%s:%s/mcp\n' "$tailnet_dns" "$serve_https_port"
fi

wait "$server_pid"
