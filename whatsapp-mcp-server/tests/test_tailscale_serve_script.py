"""Tests for the Tailscale Serve run script."""

import os
import shutil
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
    env["WHATSAPP_ENV_FILE"] = str(tmp_path / "absent.env")

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


def test_run_tailscale_serve_reports_missing_tailscale_binary(tmp_path):
    bin_dir = tmp_path / "bin"
    bin_dir.mkdir()
    log_file = tmp_path / "calls.log"

    for exe in ("bash", "python3"):
        target = shutil.which(exe)
        assert target is not None
        (bin_dir / exe).symlink_to(target)

    _write_executable(
        bin_dir / "uv",
        f"""#!/usr/bin/env bash
set -euo pipefail
echo "uv:$*" >>"{log_file}"
exit 0
""",
    )

    env = os.environ.copy()
    env["PATH"] = str(bin_dir)
    env["WHATSAPP_MCP_TOKEN"] = VALID_TOKEN
    env["WHATSAPP_ENV_FILE"] = str(tmp_path / "absent.env")

    result = subprocess.run(
        [str(SCRIPT)],
        cwd=REPO_ROOT,
        env=env,
        capture_output=True,
        text=True,
        check=False,
    )

    assert result.returncode != 0
    assert "Tailscale is not installed" in result.stderr
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
  printf '%s' '{{"BackendState":"Running","Self":{{"DNSName":"node.example.ts.net."}}}}'
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
    env["WHATSAPP_ENV_FILE"] = str(tmp_path / "absent.env")

    result = subprocess.run(
        [str(SCRIPT)],
        cwd=REPO_ROOT,
        env=env,
        capture_output=True,
        text=True,
        check=False,
    )

    assert result.returncode == 0
    calls = log_file.read_text()
    assert "uv:run main.py" in calls
    # Modern Serve syntax, default HTTPS port 443 -> loopback MCP port 8089.
    assert "tailscale:serve --bg --https 443 8089" in calls
    uv_env = uv_env_file.read_text()
    assert "WHATSAPP_MCP_TRANSPORT=http" in uv_env
    assert "WHATSAPP_MCP_HOST=127.0.0.1" in uv_env
    assert "WHATSAPP_MCP_AUTH=on" in uv_env
    # The node's own MagicDNS name is auto-added to the Host allow-list.
    assert "WHATSAPP_MCP_ALLOWED_HOSTS=node.example.ts.net:*" in uv_env
    # Tailnet URL is surfaced to the user.
    assert "https://node.example.ts.net:443/mcp" in result.stdout


def test_run_tailscale_serve_does_not_reset_serve_on_early_exit(tmp_path):
    """P1 regression: an early validation-failure exit (missing token) must NOT
    run `tailscale serve reset`, which would wipe the user's unrelated Serve routes."""
    bin_dir = tmp_path / "bin"
    bin_dir.mkdir()
    log_file = tmp_path / "calls.log"

    # Fake tailscale: tailnet is UP, and EVERY call (incl. `serve reset`) is logged.
    _write_executable(
        bin_dir / "tailscale",
        f"""#!/usr/bin/env bash
set -euo pipefail
echo "tailscale:$*" >>"{log_file}"
if [[ "$1" == "status" && "$2" == "--json" ]]; then
  printf '%s' '{{"BackendState":"Running"}}'
  exit 0
fi
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
    env["WHATSAPP_ENV_FILE"] = str(tmp_path / "absent.env")
    env.pop("WHATSAPP_MCP_TOKEN", None)  # force the early token-validation failure

    result = subprocess.run([str(SCRIPT)], cwd=REPO_ROOT, env=env, capture_output=True, text=True, check=False)

    assert result.returncode != 0
    assert "WHATSAPP_MCP_TOKEN is required" in result.stderr
    calls = log_file.read_text() if log_file.exists() else ""
    assert "serve reset" not in calls  # cleanup must NOT have reset the user's serve config
