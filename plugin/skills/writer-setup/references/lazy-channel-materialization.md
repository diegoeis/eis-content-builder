# Lazy channel materialization (design contract)

> **Owner of materialization:** `/writer-create`, not `/writer-setup`.
> **What this file is:** the contract setup honors so `/writer-create` can do its job. Setup never pre-populates `channel-templates/`.

## When `/writer-create` is invoked with `--channel <name>`

1. Check if `{workspace}/channel-templates/<name>.md` exists. If yes → use it as-is.
2. If no, read the source template at `${CLAUDE_PLUGIN_ROOT}/skills/writer-setup/assets/workspace-template/channel-templates/<name>.md`.
3. Apply any `template_customizations` recorded in `.local.json` under `channels.<name>.template_customizations` (those were proposed by `profile-inferencer` during setup; see writer-setup Step 2.6).
4. Write the customized template to `{workspace}/channel-templates/<name>.md`.
5. Proceed with the draft.

## When the channel has no built-in template

If `channels.<name>.has_template == false` (e.g., `youtube`, `medium`, custom channels) OR the source file is missing OR `${CLAUDE_PLUGIN_ROOT}` can't be resolved, `/writer-create` falls back to a generic starter template inferred at write time and writes it to `{workspace}/channel-templates/<name>.md` so subsequent runs have something concrete to edit.

The starter log line must distinguish:
- `channel-starter-template: {channel} (no built-in template; review and refine)` — when has_template is false (expected).
- `channel-starter-template-fallback: {channel} (plugin root unavailable; voice may regress)` — WARN-level; plugin install is broken.
- `channel-starter-template-fallback: {channel} (source file missing at {path})` — WARN-level; broken plugin install.

## Why setup defers this

Users only pay materialization cost for channels they actually write for. Pre-copying all 6 channel templates would inflate setup time and clutter the workspace with files the user may never touch.

## `template_customizations` schema (recorded by setup)

Each entry in `channels.<name>.template_customizations` (writer-setup Step 2.6):

```json
{
  "target_length_words": [600, 900],
  "formatting_notes_addition": "Open with a number or concrete observation; the author rarely uses scene-setting metaphors.",
  "anti_pattern_additions": ["Bullet lists with 7+ items"],
  "rationale": "Across 3 blog samples, the median word count was 780."
}
```

If `profile-inferencer` returned no proposal for a channel, the field stays `null` and the template is materialized verbatim from the plugin default.
