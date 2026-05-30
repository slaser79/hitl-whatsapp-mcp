# Meta-Learning Log — `hitl-whatsapp-mcp`

One line per `empire-self-reflect` session. Newest last.

- 2026-05-30 | what:hitl-whatsapp-mcp how:~/.claude | session:WhatsApp MCP setup + Nix flake + remote Tailscale (PR #16) | direct:3 issues:1 | recurrences:0
  (Discovered the documented Tailscale Serve remote flow never worked — FastMCP's loopback-only DNS-rebinding guard 421s proxied `Host` headers; shipped `WHATSAPP_MCP_ALLOWED_HOSTS` + modernized the serve script in PR #16. Reflection bootstrapped this brain, added the `remote-mcp-reverse-proxy` lesson, an AGENTS.md bg-process gotcha, a flake shellHook→stderr fix, and filed an issue for a proxied-Host integration test. Friction: `pkill -f` self-match killing its own shell; shellHook stdout pollution of `nix develop -c` captures.)
