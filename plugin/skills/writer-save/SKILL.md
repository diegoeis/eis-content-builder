---
name: writer-save
description: Move a draft produced by `/writer-create` from `drafts/` to its final destination - a user-chosen path, a CMS, or a scheduled slot - applying saved save-preferences rules when they match. Use when the user says "save this draft", "move my draft to the blog folder", "publish this draft", "salvar esse draft", "agenda esse draft pro blog", "publica esse draft", or runs `/writer-save`. Supports `--remember` to record a new save-preferences rule for a type/channel combination. Merges frontmatter, updates the `updated` field, handles file conflicts, and confirms the final path or CMS URL. Does not create content - only moves and transforms existing drafts.
argument-hint: "[draft_path] [--publish | --schedule \"YYYY-MM-DD HH:MM\" | --remember]"
allowed-tools: Read, Write, Edit, Bash, Glob, AskUserQuestion, TodoWrite
---

# SKILL

> **Synopsis.** Move a draft from `drafts/` to its final destination. Applies saved save-preferences rules automatically. Modes: save to path (default), publish to CMS (`--publish`), schedule (`--schedule`), or record a new preference rule (`--remember`).


# Writer Save

Move a piece from `drafts/` to where it belongs. Applies saved preferences when they match. Records new preferences when asked.

## Invariant rules

Inherit from `{workspace}/CLAUDE.md`. Key ones:

- Never publish to an external CMS without explicit confirmation.
- Never overwrite a file in the destination without asking.
- Never modify draft content — only frontmatter and path.

## Step 1 — Load workspace

1. **Locate the plugin config.** Use the canonical probe in `../writer-setup/references/load-config.md` (pointer → env var → walk-up, all targeting `.local.json`). Empty result → `"Run /writer-setup first."` Stop. Otherwise `Read "$CONFIG_PATH"` and parse as JSON.
2. Extract `workspace_path`.
3. `Read` `{workspace}/references/save-preferences.md`. If missing, treat as empty rules list.

## Step 2 — Detect mode

Parse `$ARGUMENTS`:

- `--remember` present → **Mode R**: record a new preference. Skip to Step R.
- `--publish` present → **Mode P**: publish to CMS (requires integration).
- `--schedule "..."` present → **Mode S**: schedule.
- Otherwise → **Mode F**: save to workspace path (default).

## Step 3 — Identify the draft

If `$ARGUMENTS` contains a path → use it. Validate it's inside `{workspace}/drafts/` and exists.

If no path → `Glob` `{workspace}/drafts/*.md` sorted by mtime desc. Show the user the top 3 (title + created date) and ask:

> "Which draft are we saving?"

Options: the top 3 drafts + "Paste a different path".

Reject any path outside `{workspace}/drafts/` — save skill only moves drafts, not arbitrary files.

`Read` the chosen draft. Parse its frontmatter. Extract `type`, `channel`, `tags`.

## Step 4 — Match against preferences

Walk through rules in `save-preferences.md`. A rule matches when:

- `type` matches the rule's `type` (or rule says `*`)
- `channel` matches the rule's `channel` (or rule says `*`)
- `tags` intersection with rule's tag list is non-empty (or rule tags are empty = any)

First matching rule wins (top of file = highest priority).

**If matched:** tell the user which rule applied (1 line). Use its `directory` + `filename_pattern` + `frontmatter` overrides. Skip Step 5, go to Step 6.

**If not matched:** proceed to Step 5.

## Step 5 — Ask for destination (no rule matched)

Use `AskUserQuestion`:

> "No saved rule for this {type}/{channel}. Where does it go?"

Options based on mode:

- Mode F: "Save as Markdown in my workspace" (default), "Save to a specific folder (I'll give the path)", "Skip — just leave it in drafts/"
- Mode P: always "Publish to {CMS from .local.json channels}" — if no CMS integration configured for this channel, fall back to Mode F with a warning.
- Mode S: always "Schedule for later" (asks for datetime next).

If the user picks "specific folder", ask for the path + filename pattern preference:

- `{YYYY-MM-DD}-{slugified-title}.md`
- `{slugified-title}.md`
- `{YYYY-MM}-{slugified-title}.md`
- Custom

After saving, ask: "Want me to remember this for future {type}/{channel} pieces?" If yes, after Step 7 run Step R with the details already filled in.

## Step 6 — Write to destination

1. Compute destination path from `directory` + `filename_pattern`. Expand tokens: `{YYYY}`, `{MM}`, `{DD}`, `{slugified-title}`, `{type}`, `{channel}`.

2. Check if destination directory exists. If not, `mkdir -p` it.

3. Check if destination file exists. If yes, `AskUserQuestion`:

   - "Overwrite"
   - "Save with `-v2` suffix"
   - "Cancel"

4. Build final frontmatter by merging (later wins):
   - Draft's current frontmatter
   - Matched rule's `frontmatter_additions` (if any)
   - `updated: {today}`
   - If `--publish`: `published: true`, `published_at: {now ISO 8601}`
   - If `--schedule`: `published: false`, `scheduled_for: "{datetime}"`

5. Write the file: `Write` destination path with merged frontmatter + original body.

6. Remove the draft file from `drafts/` only after confirming the destination write succeeded. Use `Bash`: `rm "{draft_path}"`. Ask confirmation if the user ran without `--remember` and no rule matched — otherwise auto-remove for matched rules.

## Step 7 — CMS publish / schedule

**If Mode P and CMS integration exists** (check `.claude/eis-content-builder.local.json` `channels.{channel}` for a `cms` value and `publish_via: api`):

1. Confirm: "Ready to publish `{title}` to {CMS}? This will be visible immediately once confirmed."
2. Wait for explicit yes.
3. Currently: no built-in CMS integration is wired. Tell the user: "CMS API publishing is not yet implemented in this plugin version. I've saved the file locally at `{path}`. You can import it manually." Fall back to Mode F.
4. Future: will call the CMS MCP / REST API. Keep this step minimal for now.

**If Mode S:**

1. If no datetime was provided with `--schedule`, ask once: "When should this publish?" Accept `YYYY-MM-DD HH:MM` format. Validate it's in the future.
2. Save with `scheduled_for` frontmatter. No external scheduling is triggered — this is a tag for the user to act on, not an automation.

## Step 8 — Confirm

Tell the user:

- Destination path or CMS URL
- Status (`draft`, `published`, `scheduled_for {date}`)
- Whether a preference was applied or newly recorded
- Next suggestion: `/writer-calibrate` if this is the first save after `/writer-create` in a while

## Step R — Record a preference

Runs when `--remember` is in `$ARGUMENTS`, or when Step 5 asked "remember this for the future?" and the user said yes.

1. **Collect scope.** `AskUserQuestion`:

   > "What does this rule apply to?"

   Options:
   - "A specific type: {type}" (pre-filled from the last-saved draft if in continuation)
   - "A specific channel: {channel}"
   - "A combination of type + channel"
   - "Tags-specific"
   - "Custom — I'll tell you"

2. **Collect directory.** Free text: "Where should these be saved? Path relative to workspace or absolute."

3. **Collect filename pattern.** `AskUserQuestion`:

   - `{YYYY-MM-DD}-{slugified-title}.md`
   - `{slugified-title}.md`
   - `{YYYY-MM}-{slugified-title}.md`
   - Custom (user provides pattern using allowed tokens)

4. **Collect frontmatter additions.** Ask: "Any extra frontmatter fields for this type? Paste YAML, or describe in words." Parse; validate YAML if pasted.

5. **Preview the rule.** Show the user the full rule block using the format in `save-preferences.md`. Ask: "Save?"

6. **Write.** Append the new rule block to `{workspace}/references/save-preferences.md` (append at the bottom, not prepend — preserves priority order). Use `Edit` to append, or `Write` if the file only has the template placeholder.

7. Confirm: "Rule saved. Next time you save a {scope} piece, this rule applies automatically."

## TodoWrite usage

Not needed for simple Mode F. Use for Mode P + Mode R sequences where 3+ substeps depend on each other.

## Failure handling

- Draft path outside `{workspace}/drafts/` → refuse. Skill only handles workspace drafts.
- Destination permission denied → surface error, ask for a different path.
- Invalid datetime in `--schedule` → ask for reformat.
- User cancels mid-flow → leave the draft untouched in `drafts/`. Confirm: "No changes — draft still at {path}."
