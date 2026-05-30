# SETUP

Copy-paste self-hosting flow for a non-developer.

## 1. Prerequisites

- Tailscale installed and signed in
- Go 1.24+
- Python 3.11+
- `uv`
- This repo cloned locally

## 2. Start the WhatsApp bridge

```bash
cd whatsapp-bridge
go run .
```

On first start, scan the QR code with WhatsApp on your phone. The bridge also
writes its local REST token to `whatsapp-bridge/store/.bridge-token`.

## 3. Generate a strong MCP token

```bash
export WHATSAPP_MCP_TOKEN="$(openssl rand -hex 24)"
```

That token is for the MCP client/UI, not the bridge.

## 4. Start the remote MCP server behind Tailscale Serve

```bash
./scripts/run-tailscale-serve.sh
```

This keeps the MCP server on `127.0.0.1`, requires auth, and exposes it over
your tailnet via Tailscale TLS.

### Tailnet-only exposure check

From a second device on the same tailnet, open the Tailscale DNS name shown by
`tailscale status` or the admin console. The server should work there and stay
unreachable from the public internet.

## 5. Connect the client

Use the tailnet URL plus the token from step 3 in your MCP client or hitl-app.
Send `Authorization: Bearer $WHATSAPP_MCP_TOKEN` or `X-API-Key: $WHATSAPP_MCP_TOKEN`.

## 6. Quick egress sanity check

While the server is running, verify there is no empire-infra egress; traffic
should stay local to the host plus Tailscale.

```bash
sudo lsof -nP -iTCP -sTCP:ESTABLISHED | grep -vE '127.0.0.1|localhost|100\.' || true
```

## 7. Token rotation

To rotate access, generate a new token, restart `./scripts/run-tailscale-serve.sh`,
then update the client with the new value. The old token stops working after the
restart.

## 8. Stop / reset

Press `Ctrl+C` in the run script terminal. It stops the server and resets the
Tailscale Serve configuration.
