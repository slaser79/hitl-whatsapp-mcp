"""Tests for the Tailscale Serve run script."""

import os
import subprocess
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
SCRIPT = REPO_ROOT / "scripts" / "run-tailscale-serve.sh"
VALID_TOKEN = "0123456789abcdef0123456789abcdef"


def _write_executable(path: Path, content: str) -> None:
    path.write_text(content)
    path.chmod(0o755)


def test_run_tailscale_serve_fails_fast_when_tailnet_is_down(tmp_path):
    bin_dir = tmp_path / "bin"
    bin_dir.mkdir()
    log_file = tmp_path / "calls.log"

    _write_executable(
        bin_dir / "tailscale",
        f"""#!/usr/bin/env bash
set -euo pipefail
if [[ "$1" == "status" && "$2" == "--json" ]]; then
  printf '%s' '{{"BackendState":"Stopped"}}'
  exit 0
fi
if [[ "$1" == "serve" && "$2" == "reset" ]]; then
  exit 0
fi
echo "tailscale:$*" >>"{log_file}"
exit 0
""",
    )
    _write_executable(
        bin_dir / "uv",
        f"""#!/usr/bin/env bash
set -euo pipefail
echo "uv:$*" >>"{log_file}"
exit 0
""",
    )

    env = os.environ.copy()
    env["PATH"] = f"{bin_dir}:{env['PATH']}"
    env["WHATSAPP_MCP_TOKEN"] = VALID_TOKEN

    result = subprocess.run(
        [str(SCRIPT)],
        cwd=REPO_ROOT,
        env=env,
        capture_output=True,
        text=True,
        check=False,
    )

    assert result.returncode != 0
    assert "Tailscale is not connected" in result.stderr
    assert "tailscale up" in result.stderr
    assert not log_file.exists()


def test_run_tailscale_serve_launches_loopback_server_and_serve(tmp_path):
    bin_dir = tmp_path / "bin"
    bin_dir.mkdir()
    log_file = tmp_path / "calls.log"
    uv_env_file = tmp_path / "uv-env.log"

    _write_executable(
        bin_dir / "tailscale",
        f"""#!/usr/bin/env bash
set -euo pipefail
if [[ "$1" == "status" && "$2" == "--json" ]]; then
  printf '%s' '{{"BackendState":"Running"}}'
  exit 0
fi
if [[ "$1" == "serve" && "$2" == "https" && "$3" == "/" && "$4" == "http://127.0.0.1:8089" ]]; then
  echo "tailscale:$*" >>"{log_file}"
  exit 0
fi
if [[ "$1" == "serve" && "$2" == "reset" ]]; then
  exit 0
fi
echo "tailscale:$*" >>"{log_file}"
exit 0
""",
    )
    _write_executable(
        bin_dir / "uv",
        f"""#!/usr/bin/env bash
set -euo pipefail
echo "uv:$*" >>"{log_file}"
env | sort >"{uv_env_file}"
exit 0
""",
    )

    env = os.environ.copy()
    env["PATH"] = f"{bin_dir}:{env['PATH']}"
    env["WHATSAPP_MCP_TOKEN"] = VALID_TOKEN

    result = subprocess.run(
        [str(SCRIPT)],
        cwd=REPO_ROOT,
        env=env,
        capture_output=True,
        text=True,
        check=False,
    )

    assert result.returncode == 0
    assert "uv:run main.py" in log_file.read_text()
    assert "tailscale:serve https / http://127.0.0.1:8089" in log_file.read_text()
    uv_env = uv_env_file.read_text()
    assert "WHATSAPP_MCP_TRANSPORT=http" in uv_env
    assert "WHATSAPP_MCP_HOST=127.0.0.1" in uv_env
    assert "WHATSAPP_MCP_AUTH=on" in uv_env
