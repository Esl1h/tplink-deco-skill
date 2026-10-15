# tplink-deco

Agent skill that manages a TP-Link Deco mesh Wi-Fi network through the router's local web API (via the `tplink-deco-api` SDK): Deco nodes, connected clients, internet/WAN/WLAN status, internet blocking and DHCP address reservations.

Thin CLI, one command, one JSON response. Local network only, no cloud account. Read-only by default: the agent asks the user before any state-changing command. Credentials come from the environment only.

## Prerequisites

- Python 3.14+ with `pip install tplink-deco-api`
- A TP-Link Deco that exposes its web management interface (not all models do). Verify from a browser on the network: https://tplinkdeco.net or http://192.168.68.1
- Credentials of the web admin login: the owner TP-Link ID and its password
- A machine on the Deco network

## Install

With the skills CLI (https://skills.sh), which supports OpenCode, Claude Code and other agents:

```sh
npx skills add Esl1h/tplink-deco
```

As a Claude Code plugin:

```text
/plugin marketplace add Esl1h/tplink-deco
/plugin install tplink-deco@tplink-deco
```

For OpenCode, link this repository inside a skills directory (`~/.config/opencode/skills`, `~/.claude/skills`, `.agents/skills`); OpenCode loads skills from those directories and needs no plugin manifest. Do not point OpenCode's `skills` config directly at this repository root: a root-level `SKILL.md` gets the literal ID `SKILL` in OpenCode V2.

```sh
ln -s /path/to/this-repo ~/.config/opencode/skills/tplink-deco
```

## Configuration

| Variable | Required | Where to get it |
| --- | --- | --- |
| `DECO_HOST` | no | Deco IP or host (default `192.168.68.1`) |
| `DECO_USER` | yes | Web admin username (owner TP-Link ID) |
| `DECO_PASSWORD` | yes | Web admin password |

## Usage

See [SKILL.md](SKILL.md) for the full command reference, workflows and limitations. The short version:

```sh
python3 scripts/deco.py status
python3 scripts/deco.py clients
python3 scripts/deco.py wan
python3 scripts/deco.py block <mac>              # cuts the device off (confirm first)
python3 scripts/deco.py reserve <mac> <ip>
```

## Development

No build step. Tests cover CLI plumbing: help, environment and input validation, plus a transport-error path against an unreachable host. No router is needed.

```sh
python3 -m unittest discover -s tests
```

With `tplink-deco-api` installed, all tests run; without it, the networked test skips on its own.

## License

MIT
