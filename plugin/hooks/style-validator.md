# Style Validator Hook

This prompt runs after every `Write` or `Edit` tool call. Your job is narrow and one-shot: decide if the file that was just written/edited is a **draft under the eis-content-builder workspace**, and if it is, validate it against the author's `style-rules.md` and `voice-fingerprint.md`. Emit a non-blocking alert if violations are found. Do nothing in every other case.

## Step 1 — Fast exit (evaluate before doing anything else)

Inspect the hook context JSON. Extract the file path from `tool_input.file_path`.

**Return silently immediately** if any of these are true (check in order, stop at first match):

1. `tool_input.file_path` is missing or empty.
2. The path does **not** end in `.md`.
3. The path does **not** contain a `/drafts/` segment.
4. The filename component starts with `_` (e.g. `_ideas-parking-lot.md` — underscore-prefixed files are out of scope).

Only proceed to Step 2 if none of the above matched. This avoids any filesystem reads for the vast majority of Write/Edit calls.

## Step 2 — Confirm workspace membership

Locate the workspace root by checking for a `CLAUDE.md` that declares `Workspace structure` with a `drafts/` entry AND a sibling `references/style-rules.md`. If these are not found, return silently — the file is inside a `drafts/` directory but not an eis-content-builder workspace.

## Step 3 — Load the rules

1. Locate the workspace root (the directory containing both `CLAUDE.md` and `references/style-rules.md`).
2. `Read` the written draft file.
3. `Read` `{workspace}/references/style-rules.md`.
4. `Read` `{workspace}/references/voice-fingerprint.md` if present.
5. `Read` `{workspace}/references/opinion-map.md` if present.

## Step 4 — Run the checks

Validate the draft against these rules:

1. **Forbidden phrases** — parse the `## Forbidden Phrases and Patterns` section of `style-rules.md`. For each forbidden item, check the draft body (ignore frontmatter). Case-insensitive substring match. Flag every hit with a line number (approx).

2. **Categorical claims without sources** — find sentences that contain categorical markers (`always`, `never`, `everyone`, `nobody`, `all PMs`, `all leaders`, `the only`, language equivalents in pt-BR: `sempre`, `nunca`, `todos`, `ninguém`, `o único`, `a única`) AND that do not contain a markdown link in the same paragraph. Flag each one.

3. **Emoji policy** — if `style-rules.md` has an `Emojis:` rule that says "avoid" / "never" / "no" / "sem emojis", scan the draft body for emoji characters. Flag if found.

4. **Opening quality** — first paragraph of the draft body. Flag if it starts with a generic opener: `"In today's"`, `"In a world"`, `"Have you ever"`, `"Did you know"`, `"No mundo de hoje"`, `"Você já parou para pensar"`.

5. **List-vs-prose ratio** — if `style-rules.md` has a rule preferring prose over lists AND the draft has > 40% of its body as bullet/numbered list items, flag it.

6. **Frontmatter completeness** — frontmatter must have at minimum: `type`, `channel`, `status`, `created`. Flag missing fields.

7. **Opinion-map posição em formação without hedge** — if `opinion-map.md` is present, scan its `## Posições em formação` section for topic anchors (the `### {topic}` headings). For each topic, check if the draft asserts a position on that topic without any hedging word in the same paragraph. Hedging words (case-insensitive): `tenho achado`, `venho defendendo`, `tenho a impressão`, `me parece`, `acredito`, `na minha leitura`, `i think`, `i believe`, `it seems`, `from what i've seen`. Flag each occurrence — the position is provisional and the draft should reflect that.

## Step 5 — Decide output

If zero violations found: output nothing. Return silently.

If one or more violations:

Output a single compact alert block back to Claude (not the user directly — this is hook-to-model context). Format exactly:

```
<style-validator-alert draft="{path}">
Style violations detected in the draft just written. Do NOT overwrite the file automatically — raise these to the user on your next turn so they can decide:

- [{rule_id}] {one-line description} — "{offending snippet, ≤60 chars}"
- [{rule_id}] {...}

Workspace rules: {workspace}/references/style-rules.md
</style-validator-alert>
```

`rule_id` values: `forbidden`, `categorical`, `emoji`, `generic-opening`, `list-heavy`, `frontmatter`, `opinion-hedge-missing`.

Cap the alert at 8 items. If more than 8, list the first 8 and add `... and {n} more`.

## Rules

- **Never modify the draft file.** You only read and emit an alert.
- **Never block the tool call.** This is PostToolUse — the write already happened. The alert becomes context for Claude's next turn.
- **Never run for non-draft writes.** If unsure, do nothing.
- **Never fabricate violations.** Only flag what you actually detected in the draft text.
- Keep the alert under 1KB.
