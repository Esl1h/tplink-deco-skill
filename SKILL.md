---
name: tplink-deco
description: Manage a TP-Link Deco mesh Wi-Fi network through the router's local web API. List Deco nodes and connected clients, check internet, WAN and WLAN status, cut a client off from the internet, and manage DHCP address reservations. Use when the user mentions Deco, mesh nodes, Wi-Fi clients or devices on the home network.
---

# TP-Link Deco

Thin CLI over the `tplink-deco-api` SDK, which talks to the Deco's local web API on the LAN (the same interface the Deco app uses at home). No cloud account involved. Read-only by default.

## Setup

- Python 3.14+ with `pip install tplink-deco-api`.
- The Deco must expose its web management interface; not all models do. Verify from a browser on the network: https://tplinkdeco.net or http://192.168.68.1
- Credentials are the web admin login: the owner TP-Link ID and its password.
- This machine must be on the Deco network.
- Environment: `DECO_HOST` (default `192.168.68.1`), `DECO_USER`, `DECO_PASSWORD`.
- Never print the password or write it into files. Environment only.

## Commands

Run from this skill's directory. All output is JSON.

| Command | Purpose |
| --- | --- |
| `python3 scripts/deco.py status` | Internet status (IPv4/IPv6/link), device mode, CPU and memory |
| `python3 scripts/deco.py nodes` | Deco units: model, firmware, role, IP, signal |
| `python3 scripts/deco.py clients [--node MAC]` | Connected clients: name, IP, MAC, band/interface, online, speeds |
| `python3 scripts/deco.py totals` | Aggregated up/down speeds |
| `python3 scripts/deco.py wan` | WAN and LAN IP configuration, including DNS servers |
| `python3 scripts/deco.py wlan` | Wi-Fi config: SSIDs, channels, guest network (contains Wi-Fi passwords) |
| `python3 scripts/deco.py blocked` | Clients cut off from the internet |
| `python3 scripts/deco.py block <mac> [--name N] [--type T]` | Cut a client off from the internet (state-changing) |
| `python3 scripts/deco.py unblock <mac>` | Restore internet access (state-changing) |
| `python3 scripts/deco.py rename <mac> <name>` | Rename a client (state-changing) |
| `python3 scripts/deco.py forget <mac>` | Forget an offline client (state-changing) |
| `python3 scripts/deco.py reservations` | DHCP address reservation table |
| `python3 scripts/deco.py reserve <mac> <ip>` | Reserve a fixed IP (state-changing) |
| `python3 scripts/deco.py unreserve <mac>` | Remove a reservation (state-changing) |
| `python3 scripts/deco.py dsl` | DSL link status (DSL models only) |
| `python3 scripts/deco.py raw <path> <form> [json]` | Raw request to any endpoint in the SDK catalogue |

`--name` and `--type` on `block` default to the client's current name and type from the client list.

## Workflows

- **Who is online?** `clients`, then filter by `online: true`. `totals` shows the aggregated load.
- **Is the internet down?** `status` (`link_status`, IPv4/IPv6 `inet_status`). `wan` shows the DNS servers in use, which pairs well with the NextDNS skill when diagnosing DNS issues.
- **Cut a kid's device off now:** confirm with the user, then `block <mac>`. To restore later, `unblock <mac>`. `blocked` lists everyone currently cut off.
- **Fixed IP for a server or NAS:** `reserve AA:BB:CC:DD:EE:FF 192.168.68.50`.

## Rules

- Read-only by default. Ask the user before `block`, `unblock`, `rename`, `forget`, `reserve`, `unreserve`.
- `block` cuts a device off from the internet. Treat it as high-impact.
- `wlan` output contains Wi-Fi passwords. Print it only when the user asks.
- Prefer one-shot calls. Do not poll the router in a loop; the API is rate-sensitive.
- Not all models support the web interface or every command (for example `dsl`). Failures raise transport, auth or API errors; report the message as it is, do not guess.

## Limitations

- The router's API is internal and undocumented by TP-Link; firmware updates can break it.
- Local network only. Cloud or remote control is out of scope.
- On login failures, verify the credentials by signing in at https://tplinkdeco.net or http://<deco-ip> in a browser.
