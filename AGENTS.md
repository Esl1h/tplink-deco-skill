# Agent guide

This file explains how to change this skill without breaking it.

## What this repository contains

An agent skill that controls a TP-Link Deco mesh through the router's local web API, via the Python package `tplink-deco-api`, with a thin CLI that prints JSON.

- `SKILL.md` is the source of truth for the skill.
- `scripts/deco.py` is the CLI (Python 3.14+, `pip install tplink-deco-api`).
- `tests/test_deco.py` covers the CLI plumbing, no router needed.
- `README.md` documents installation, configuration and development.
- `.claude-plugin/plugin.json` and `.claude-plugin/marketplace.json` describe the Claude Code plugin and point the skill loader at the root `SKILL.md`.

There is no build step.

## Rules for changes

- Keep the skill in English and portable across agents. Do not write instructions that tie it to one or two specific agent tools.
- Credentials come from environment variables only (`DECO_HOST`, `DECO_USER`, `DECO_PASSWORD`). Never put passwords in code, examples or logs.
- The skill reads by default. State-changing actions (`block`, `unblock`, `rename`, `forget`, `reserve`, `unreserve`) require user confirmation; keep that rule in `SKILL.md`.
- Keep the `tplink_deco_api` import lazy, inside `load_sdk`: the plumbing tests run without the package installed and `--help` must not require installation.
- Do not add polling loops to the CLI; the router's API is sensitive to excess requests.
- Keep the two `.claude-plugin/` files in sync with `SKILL.md` (name, description, keywords). Bump the version in `plugin.json` whenever the skill's behavior changes.
- OpenCode has no plugin manifest for skills: they are discovered from the skills directories (`~/.config/opencode/skills`, `~/.claude/skills`, `.agents/skills`) or installed by the skills.sh CLI. Do not create a manifest for OpenCode.

## Checks

Before publishing, run the tests:

```sh
python3 -m unittest discover -s tests
```

Without `tplink-deco-api` installed, the test that needs it skips on its own. No router is required.

## Writing style

Plain, direct language: active voice, short sentences, one term per thing. Identifiers, commands, API output and error messages stay exactly as they are. Keep diacritics correct whenever Portuguese appears.
