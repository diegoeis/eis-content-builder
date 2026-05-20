# Agent contracts referenced by `/writer-setup`

Loaded by Step 2.5 of the parent `SKILL.md`. The setup dispatches three
agents in parallel; each returns a structured payload that the skill
applies. The agent files themselves (`agents/*.md`) are the source of
truth for their own behavior — this file just summarizes the contract
each one offers to the orchestrator.

---

## `opinion-extractor` (bulk mode)

The agent returns plain markdown structured exactly as documented in
`agents/opinion-extractor.md`. Key sections the setup consumes:

### `### New positions`

A list of items `P1, P2, ...`, each ending with an **`Apply patch`**
sub-bullet that gives:

- `target_section`: one of `## Hard core`, `## Forming positions`,
  `## Tensions and synergies between topics`.
- `insert_after`: either an existing heading inside the target section
  (e.g. `### Topic`) or `EOF` for end-of-section.
- `block`: a ready-to-paste markdown block. Already includes the
  heading and bullets — no further editing needed. The block's content
  is in the author's language; the field labels stay English.

### `### Promotions` (bulk only)

Items `PR1, PR2, ...` that move an existing block between sections.
Apply as a two-step `Edit`: remove from source section, append to
target section.

### `### Tensions and synergies`

Items `T1, T2, ...` whose `Apply patch` appends a single bullet to
`## Tensions and synergies between topics`.

### `### Conflicts`

Items `C1, C2, ...`. **No patch is proposed.** These exist when an
extracted position contradicts an existing `## Hard core` entry or a
`## Refusals` entry. Do not auto-resolve. Forward them to the
confirmation screen for the user.

### `### Changelog entries`

One literal line per applied patch. The setup appends each to the
file's `## Changelog` section, substituting `{trigger_skill}` with
`writer-setup`. The verb-of-record body inside each line is in the
author's language; date, `(trigger: ...)`, and `(source: ...)` keys
stay English.

### Patch application order (per file, to keep anchors stable)

1. `## Hard core` patches in declared order.
2. `## Forming positions` patches in declared order.
3. `Promotions` (move between sections).
4. `## Tensions and synergies between topics` patches.
5. `## Changelog` appends.

Each patch is a separate `Edit` call. If any single `Edit` fails
(anchor not found, ambiguous match), skip that patch, record the
failure in the final summary, and continue with the rest — do not
abort opinion-map population over one bad patch. The agent's
`insert_after: EOF` semantics mean "append at end of section" —
implement by finding the next `##` heading and inserting before it.

---

## `voice-analyzer`

Writes `voice-fingerprint.md` (single file, includes `## Few-shot
examples` section since v0.6.0). Returns a ≤400-word summary plus,
when invoked with `detect_language: true`, a `language_detected` field
(`"pt-BR"`, `"en"`, `"es"`, `"other"`). The setup consumes
`language_detected` in Step 2.8 — the skill does not tokenize samples
itself (invariant 5).

If the analyzer returns `examples_path-ignored` as a warning, it means
the caller passed the deprecated v0.5 input — safe to ignore in v0.6.

---

## `profile-inferencer`

Writes `author-profile.md`. Returns a compact JSON report (≤1.5 KB)
with `fields_inferred` (each `value`, `confidence`, `source`),
`fields_null`, `links_scraped` (each `url` + `method` used),
`links_failed` (each `url` + `reason`), `links_skipped` (rare — only
unparseable/non-HTML URLs), and `channel_template_proposals` (one per
channel, capped at 3 by the agent). The setup persists each proposal
to `.local.json` under `channels.<channel>.template_customizations`,
which `/writer-create` applies when it materializes the channel template
on first use. The cap is the agent's responsibility, not the skill's.

Source citations are mandatory — the agent rejects vague sources like
`"inferred"` alone. The agent tries browser tool first for every URL
when a browser MCP is available (Claude in Chrome, Playwright, etc.),
falls back to WebFetch, and records the method used. Social URLs only
succeed via browser tool; if no browser MCP is connected, expect them
under `links_failed` with reason `"all-fetch-methods-failed"`.

---

## `archive-detector` (LLM fallback for the Python script)

Returns JSON identical in shape to `detect-archive-schema.py`. The
setup uses whichever runs first successfully: tries the Python script
first, falls back to this agent only when the script fails with
`all-reads-failed-or-no-frontmatter`, an uncaught exception, invalid
JSON, or Python is not on PATH. Structural errors from the script
(`ephemeral-archive-path`, `archive-path-not-found`, `no-content-files`)
are authoritative — no fallback in those cases.
