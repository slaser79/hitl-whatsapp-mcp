# Product Vision: HITL WhatsApp Remote-MCP

## Executive Summary
A secure, self-hosted **remote MCP server** (fork of `verygoodplugins/whatsapp-mcp`, MIT) that lets mobile agents in the **hitl-app** read, search, and send a user's WhatsApp messages — the WhatsApp analogue of how `wacli` serves `openclaw`/`hermes` desktop agents. Exposed over a Tailscale-gated, bearer-authenticated transport with dead-simple, ≤15-minute setup.

## Core Value Proposition
1. **Reliability:** Battle-tested whatsmeow bridge + Python MCP server; remote transport via upstream PR-112.
2. **Security by default:** Tailnet-only exposure + bearer/API-key auth + fail-closed guard; nothing leaves the user's host.
3. **Autonomy:** Designed to be managed by AI Agents within the HITL Empire.

## Empire Registration
- **Product ID:** hitl-whatsapp-mcp
- **HQ Repo:** slaser79/agent_workflows
- **Registered in:** config/empire.yaml
- **Upstream:** verygoodplugins/whatsapp-mcp (fork of lharries/whatsapp-mcp), MIT — attribution preserved in LICENSE.
