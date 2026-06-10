# Shared: locating the plugin config

> **Used by:** writer-create, writer-calibrate, writer-ideate, writer-opinion-mine, writer-save, writer-index.
> **Authority:** writer-setup writes `.local.json` (Step 4.2). All other skills must read it.

## Resolution cascade

Probe in this order, stopping at the first hit:

1. `${HOME}/.claude/eis-content-builder.pointer.json` — read it, extract `workspace_path`, and check `${workspace_path}/.claude/eis-content-builder.local.json` exists. Pointer is the source of truth for ~95% of cases.
2. `${EIS_CONTENT_BUILDER_CONFIG}` env var if set and the file exists.
3. Walk-up from `${PWD}` looking for `.claude/eis-content-builder.local.json` in each ancestor.

Empty result → tell the user `"Run /writer-setup first."` and stop.

## Canonical Bash probe (one call, copy-paste verbatim)

```bash
config=""
if [ -f "$HOME/.claude/eis-content-builder.pointer.json" ]; then
  ws=$(python3 -c 'import json,sys;print(json.load(open(sys.argv[1])).get("workspace_path",""))' "$HOME/.claude/eis-content-builder.pointer.json" 2>/dev/null)
  if [ -n "$ws" ] && [ -f "$ws/.claude/eis-content-builder.local.json" ]; then
    config="$ws/.claude/eis-content-builder.local.json"
  fi
fi
if [ -z "$config" ] && [ -n "$EIS_CONTENT_BUILDER_CONFIG" ] && [ -f "$EIS_CONTENT_BUILDER_CONFIG" ]; then
  config="$EIS_CONTENT_BUILDER_CONFIG"
fi
if [ -z "$config" ]; then
  dir="$PWD"
  while [ "$dir" != "/" ]; do
    if [ -f "$dir/.claude/eis-content-builder.local.json" ]; then
      config="$dir/.claude/eis-content-builder.local.json"
      break
    fi
    dir="$(dirname "$dir")"
  done
fi
echo "$config"
```

Capture as `CONFIG_PATH`. Empty → stop with `error: workspace not found. Run /writer-setup first.`

Then `Read "$CONFIG_PATH"` and parse as JSON.

## Why `.local.json` (not `.local.md`)

`writer-setup` Step 4.2 persists a strict JSON schema. The `.local.md` extension referenced in older drafts of some skills was an inconsistency — every skill in this plugin must read `.local.json`. The pointer at `$HOME/.claude/eis-content-builder.pointer.json` is also JSON.

## What every skill extracts

- `workspace_path` — root of the writer workspace. Validate with `Bash: test -d "{workspace_path}" && test -f "{workspace_path}/CLAUDE.md"`. Either fails → stop with `error: workspace at {workspace_path} is missing or incomplete. Run /writer-setup.`
- `language.default` → `${OUTPUT_LANGUAGE}` used for user-facing prose and draft body. Fallback `pt-BR`.
- Other blocks (`channels`, `research_sources`, `article_archive`, `ideation`, `save_preferences`) — skills extract what they need.

## Ephemeral-path rejection

Reject and stop if `workspace_path` resolves under any of: `/sessions/`, top-level `/mnt/`, `/tmp/`, `/private/tmp/`, `/var/folders/`, `/worktrees/`. Same stop message: `error: workspace at {workspace_path} is on an ephemeral path. Run /writer-setup with a stable location.`
