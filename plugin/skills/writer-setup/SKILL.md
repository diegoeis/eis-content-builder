---
name: writer-setup
description: Create the writer workspace from scratch and populate the reference files the rest of the plugin reads (author profile, voice fingerprint, style rules, channel templates, opinion map, optional article index). Use when the user says "set up my writing profile", "configure my writer workspace", "learn my tone and style", "meu perfil de escrita", "configurar workspace", or runs `/writer-setup`. Also trigger when another writer skill detects that the local config (`.claude/eis-content-builder.local.json`) is missing and points the user back to setup. This skill is for FIRST-TIME setup. For pinpoint voice corrections on a single piece use `/writer-calibrate`; to map or refine the author's positions on topics use `/writer-opinion-mine`. v0.6.0 first-time only.
argument-hint: "[optional: path-or-link hints]"
allowed-tools: Read, Write, Edit, Bash, Glob, AskUserQuestion, TodoWrite, WebFetch, Task, Skill
---

# SKILL

> **Synopsis.** First-time creation of the writer workspace.
> Step 0 detects state (this version handles only first-time — update and
> repair are out of scope for v0.6.0 and short-circuit with a clear message).
> Step 1 collects user input through TWO grouped `AskUserQuestion` calls
> (workspace details + channels) — rich clients render these as forms.
> Step 2 materializes the structure and runs three agents and one Python
> script in parallel. Step 3 shows a single confirmation screen with the
> inferred data and applies surgical edits. Step 4 writes the canonical
> config, writes the pointer in `$HOME/.claude/`, and (if archive is enabled)
> runs `/writer-index` to produce the article index. Sample interpretation
> is delegated to agents — the skill orchestrates only.

# Writer Setup (v0.6.0)

Build the writer workspace from scratch. This is the **only** skill that
creates the workspace structure or rewrites the canonical config. Every
other skill in the plugin reads from what this skill produces.

## Invariants

These apply at every step. Violating any of them is a bug, not a tradeoff.

1. **Never fabricate data.** If a value cannot be inferred or measured,
   it stays `null` / `_(not detected)_`. The user fills it later.
2. **Skill prose (this file) is in English; user-facing prompts follow
   `${OUTPUT_LANGUAGE}`.** The text the user reads in the UI — questions,
   error messages, confirmation screens — is written in their language
   (detected from the conversation; see Step 2.0). The English text in
   this SKILL.md is for the skill author / orchestrator, not the user.
   Reference files inside the workspace also follow the user's language.
3. **Never write outside the chosen workspace path** (and the pointer in
   `$HOME/.claude/`). No exceptions.
4. **Ephemeral paths are refused.** `/tmp/`, `/sessions/`, `/var/folders/`,
   `/private/tmp/`, top-level `/mnt/`, `/worktrees/*` are rejected at
   parse time. `realpath` validates after `mkdir`.
5. **The skill orchestrates; agents interpret.** Voice analysis, profile
   inference, opinion extraction, archive schema detection, language
   detection — all delegated. The skill must never tokenize, count,
   classify, or parse natural-language content from samples on its own.
6. **Fetch budget.** Step 1 has a hard cap of **5 page fetches total**
   across Step 1.3 (first-name detection) and Step 1.7 (URL samples),
   with 8-second timeout per call regardless of method. A "fetch" is
   one of: a browser-tool navigate+read pair, or a WebFetch call. Issue
   all fetches in the same Step in a single parallel batch. If the
   budget would be exceeded, prefer Step 1.7 (samples) over Step 1.3
   (first-name) — first name has a cheap fallback (ask the user),
   samples do not.
10. **Browser tool first, WebFetch fallback, ask the user if both fail.**
   For every URL fetch, try in this order:
   (a) If a browser-tool MCP is connected in the current runtime
       (Claude in Chrome, Playwright, or similar — detect at runtime
       via tool availability, not by hardcoded name), use it.
       It runs with the user's logged session, so it handles LinkedIn,
       Twitter/X, Medium paywalls, etc.
   (b) If no browser tool is available, fall back to `WebFetch`.
       Expect it to fail on social networks; that's normal.
   (c) If both fail or return empty, do not retry — record the URL
       under `links_failed` with reason `"all-fetch-methods-failed"`
       and ask the user directly for the missing info later.
   Never silently skip a URL the user explicitly provided. Every URL
   gets at least one attempt. Browser-tool usage carries an implicit
   "navigates as the logged-in user" warning — the user was informed
   of this in Step 1.1.
7. **Do not narrate tool calls or internals.** The user does not need
   to read "Vou renderizar o formulário", "rendering elicitation",
   "I'll call AskUserQuestion now", "agora vou rodar o voice-analyzer",
   etc. Tool names, agent names, and internal step numbers stay out of
   user-facing prose. When a connector sentence is genuinely useful
   (e.g. "Vamos começar."), keep it under 8 words and let the tool/UI
   do the rest of the work.
8. **Prefer `cp` over `Read`+`Write` for static files; fall back when
   sandbox blocks.** When materializing a static template (no
   placeholders to substitute), try `Bash: cp` first — it preserves the
   source exactly and avoids "Writing file" noise in the UI. If `cp`
   fails because the source is outside the sandbox mount (Cowork
   plugin cache often resolves outside Bash's accessible paths), fall
   back to `Read` + `Write` for that specific file. Do not retry `cp`
   for the rest of the batch — switch to `Read` + `Write` for the
   remaining static files in the same step. `Write` is also fine for
   files with substituted placeholders (CLAUDE.md, opinion-map.md,
   style-rules.md) and for files the agents produce.

## Inputs

`$ARGUMENTS` may contain free text from the user (a path, a URL, sample
hints). Treat as an early hint when parsing the Step 1 response — it does
not replace Step 1.

## Step 0 — Decide mode

**Read the pointer.**

```bash
test -f "$HOME/.claude/eis-content-builder.pointer.json" && cat "$HOME/.claude/eis-content-builder.pointer.json" || echo "NOT_FOUND"
```

Three outcomes:

- **`NOT_FOUND`** → **first-time mode**. Proceed to Step 1.
- **Pointer exists, `workspace_path` exists on disk** → **update mode**.
  Tell the user: `"You already have a workspace at {workspace_path}.
  Update mode is not implemented in v0.6.0. To re-analyze your voice
  from scratch, delete the workspace folder and re-run /writer-setup;
  for pointwise voice corrections use /writer-calibrate."` Stop.
- **Pointer exists, `workspace_path` does NOT exist on disk** → **repair
  mode**. Tell the user: `"Your pointer points to {workspace_path} but
  that folder no longer exists. Repair mode is not implemented in v0.6.0.
  To start over, delete $HOME/.claude/eis-content-builder.pointer.json
  and re-run /writer-setup."` Stop.

**Why short-circuit:** v0.6.0 is the first cut of the refactor. Update
and repair paths land in a follow-up version.

## Step 1 — Concentrated input

**Use `TodoWrite`** to track Steps 1, 2, 3, 4 as the four big chunks.

### 1.1 — Workspace details (one `AskUserQuestion` call, 4 questions)

Issue ONE call to `AskUserQuestion` with the four questions below in
this exact order. Modern clients (Cowork, Claude Desktop) render this
as a single grouped form — file picker for samples, multi-line text
for the rest, chip-style selectors where applicable. Clients that
don't support rich forms degrade to numbered text prompts; the labels
and descriptions are written to work in either case.

**Do not narrate the tool call.** No "I'll render the form", "Vou
abrir o formulário", "rendering elicitation", "let me ask you", etc.
Open with a single short user-facing sentence in `${OUTPUT_LANGUAGE}`
(e.g. "Vamos configurar seu workspace." / "Let's configure your
workspace.") and issue the `AskUserQuestion` call immediately. The tool
itself is the UI — the form speaks for itself.

The header label of the call: `"Writer workspace details"`.

**Question 1 — Workspace parent folder.**
- `question`: `"Where should I create the workspace folder? (absolute
  path — I'll create {first_name}-writer-workspace inside it)"`
- `header`: `"Workspace"`
- `multiSelect`: `false`
- `options`: two options that the client renders as labels around a
  free-text input:
  - `label`: `"Type your path"` — `description`: `"e.g. /Users/yourname/obsidian-vault"`
  - `label`: `"Current folder"` — `description`: `"Use $PWD and create the subfolder inside it"`

**Question 2 — Identity links.**
- `question`: `"Which links represent you online? (1-3 — blog,
  newsletter, personal site, LinkedIn, GitHub)"`
- `header`: `"Identity links"`
- `multiSelect`: `false`
- `description guidance for the free-text answer`: `"One URL per line.
  I'll try the smart way first: if you have a browser tool connected
  (Claude in Chrome / Playwright MCP), I use it with your logged
  session — works for LinkedIn and other social sites. If no browser
  tool is available, I fall back to plain WebFetch (which usually fails
  on social networks). Heads up: if I use your browser session, I'll
  navigate the page logged in as you — read-only, no posting."`
- `options`:
  - `label`: `"Type your URLs"` — `description`: `"One per line."`
  - `label`: `"Skip — no public links"` — `description`: `"I'll ask for identity fields directly later."`

**Question 3 — Writing samples.**
- `question`: `"Share 2-3 writing samples (required) — paste URLs of
  your published pieces, absolute file paths, or paste full text
  blocks."`
- `header`: `"Samples"`
- `multiSelect`: `false`
- `options`:
  - `label`: `"Paste / attach"` — `description`: `"One sample per block. URLs, paths, or text — I'll detect the type."`

**Question 4 — Article archive (optional).**
- `question`: `"Do you have a folder of already-published articles?
  (optional — paste absolute path, or leave blank)"`
- `header`: `"Article archive"`
- `multiSelect`: `false`
- `options`:
  - `label`: `"Paste path"` — `description`: `"I'll detect Obsidian automatically and infer the YAML frontmatter schema."`
  - `label`: `"Skip"` — `description`: `"I won't index past pieces. You can configure later."`

**Rendering notes for the skill:** the four questions are issued in a
single tool call. Do NOT chain four separate calls — that defeats the
form rendering and forces sequential turns. After this call returns,
proceed directly to Step 1.2 with the user's answers.

### 1.2 — Parse the response

Parse the free-text into:

- `parent_path`: absolute directory path the user wants the workspace
  inside of. Validate:
  - Must be absolute (starts with `/` or `~/`).
  - Must exist (`Bash: test -d` — if not, ask once for a different path,
    then abort).
  - Must NOT be ephemeral (refuse `/tmp/`, `/sessions/`, top-level
    `/mnt/`, `/var/folders/`, `/private/tmp/`, contain `/worktrees/`).
    If ephemeral, refuse with the exact reason and re-ask. Do not fall
    through silently.

- `links`: list of URLs from the input. **No skip-list anymore** — every
  URL is a candidate for fetching. The setup decides which method to
  use per URL based on what tools are available in the current runtime.

  Categorize each URL into one of:
  - `links_easy_fetch` — domains where WebFetch works fine (personal
    blogs, newsletters, GitHub profiles, RSS endpoints, etc.).
  - `links_browser_preferred` — domains that block plain HTTP requests
    and need a real browser session: `linkedin.com`, `lnkd.in`,
    `twitter.com`, `x.com`, `t.co`, `instagram.com`, `facebook.com`,
    `fb.me`, `tiktok.com`, `threads.net`, `medium.com` (sometimes).
    These get tried via browser tool FIRST, WebFetch as fallback.

  The categorization is a hint for the agent (`profile-inferencer`), not
  a hard rule. The agent decides the method at fetch time based on the
  tools available in its tool slot.

- `channels_from_links`: identify channels already declared by the links
  themselves so Step 1.4 does not ask redundant questions. Mark each
  channel as "confirmed" with the URL the user provided:
  - URL on `linkedin.com/in/*` → `linkedin` confirmed.
  - URL on `twitter.com`, `x.com` → `twitter` confirmed.
  - URL the user explicitly labelled as their blog (e.g. "this is my
    blog: https://..." or section 2 of the answer when only one URL is
    there) → `blog` confirmed with that URL.
  - URL on `substack.com`, `beehiiv.com`, `buttondown.email`,
    `convertkit.com`, or labelled as newsletter → `newsletter` confirmed.
  - URL on `youtube.com/@*`, `youtube.com/channel/*` → `youtube` confirmed.
  - URL on `medium.com/@*` → `medium` confirmed.
  - URL on `github.com/*` (user profile, not a repo) → identity link only,
    not a publishing channel.
  - Any other URL → leave unmapped; treat as personal site (blog candidate)
    only if the user said so explicitly. Otherwise ask in Step 1.4.

- `samples_raw`: list of items, each either a file path, a URL, or a
  pasted text block (text blocks are anything > 500 chars that is not a
  path or URL).

- `archive_path` (optional): the user marked something as "my published
  articles folder" — accept any of: explicit label ("archive:"), path
  mentioned in section 4 of the answer, or a single trailing path right
  after the samples block.

If the parse is genuinely ambiguous (e.g. user pasted 4 URLs without
labels), ask ONE disambiguation question via `AskUserQuestion`:

> "I found these URLs in your message. Which is which?"
> For each URL: options = [Identity link | Writing sample | Archive folder | Skip].

### 1.3 — Determine `first_name`

The workspace folder must be named `{first_name}-writer-workspace`. Try in order:

1. From a scrapeable link's `<meta name="author">`, `<meta
   property="og:author">`, or JSON-LD `Person.name`. Do **one** `WebFetch`
   per scrapeable link, capped at 2 fetches total, with a hard 8s timeout
   per fetch. Extract first name = first token of the matched author name.
2. From the LinkedIn URL slug (e.g. `linkedin.com/in/janedoe` →
   `janedoe` → ask user to confirm first name in one short question).
   This DOES NOT scrape LinkedIn — only parses the URL.
3. If still unknown → ask the user via a single short free-text prompt
   (not `AskUserQuestion` — there are no discrete options here):
   `"What's your first name? I'll use it to name the workspace folder
   (no last name needed)."`. Take the first whitespace-separated token
   of the reply as the first name. If the reply is empty or contains
   only whitespace, ask once more; on second empty reply, abort with:
   `"Cannot determine workspace folder name. Re-run /writer-setup with
   a first name when you're ready."`

Slug-normalize the chosen name: lowercase, ASCII-only, hyphens for
spaces. Result: `{first_name_slug}-writer-workspace`.

### 1.4 — Channel declarations (`AskUserQuestion`)

**Only ask about channels NOT already confirmed by Step 1.2's
`channels_from_links`.** If the user gave you a blog URL explicitly,
do not ask "do you publish to a blog?" — you already know. The goal
is to confirm the remaining channels with one short batched question,
not to re-collect what's on the table.

**Same no-narration rule as Step 1.1.** Do not announce the call.
Issue the `AskUserQuestion` directly. If you want a single connector
sentence first (in `${OUTPUT_LANGUAGE}`), keep it short and
user-facing — never reveal tool names or describe what is about to
render.

Build the question list dynamically. For each candidate channel
(`blog`, `newsletter`, `linkedin`, `other`), include a question only if
that channel is NOT in `channels_from_links`:

- **Blog** (skip if confirmed): `Do you publish to a blog?` → `[Yes — I'll share the URL] | [No]`
- **Newsletter** (skip if confirmed): `Do you have a newsletter?` → `[Yes, standalone platform (Substack, Beehiiv, ...)] | [Yes, on the same site as my blog] | [No]`
- **LinkedIn** (skip if confirmed): `Do you publish on LinkedIn?` → `[Yes, regularly] | [No / rarely]`
- **Other channels** (always ask, multi-select, excluding any already
  confirmed): `Any others?` → `[X / Twitter] | [YouTube] | [Medium] | [None]`

If after subtracting confirmed channels there is nothing left to ask,
**skip Step 1.4 entirely** — proceed directly to 1.5.

If a remaining "Yes" answer would require a URL that was not provided
in Step 1.2 (e.g. blog confirmed via question but no URL given), ask
ONE follow-up free-text after the AskUserQuestion: `"Please paste the
URL(s) for: blog, newsletter."`. URLs already known are never re-asked.

### 1.5 — Compute final workspace path

```
{workspace_path} = {parent_path} / {first_name_slug}-writer-workspace
```

Check if `{workspace_path}` already exists. If yes:

```
"The folder {workspace_path} already exists. Options:
 (a) overwrite — I'll re-materialize everything (existing files get
     replaced)
 (b) pick a different name — type a new suffix and I'll use
     {first_name_slug}-{suffix}-writer-workspace
 (c) abort
What do you want?"
```

`AskUserQuestion` with the three options.

### 1.6 — Materialize structure (Bash + Write)

One Bash call:

```bash
mkdir -p "{workspace_path}/references" \
         "{workspace_path}/sample-sources" \
         "{workspace_path}/drafts" \
         "{workspace_path}/channel-templates" \
         "{workspace_path}/.claude"
```

Then validate via `realpath`:

```bash
realpath "{workspace_path}"
```

If the resolved path matches any ephemeral prefix (symlink trap), abort
with a clear message — do not write anything else.

### 1.7 — Materialize samples in `sample-sources/`

For each item in `samples_raw`:

- **File path** → `Bash: cp` it to `{workspace_path}/sample-sources/{slug}.md`.
- **URL** → `WebFetch` it (parallel batch — see WebFetch budget in
  invariants), strip nav/boilerplate, `Write` to
  `{workspace_path}/sample-sources/{slug}.md`. Cap at 6s timeout per URL.
  All URL samples in this step are issued in a single parallel batch.
- **Pasted text block** → `Write` it directly to
  `{workspace_path}/sample-sources/sample-{n}.md` with a one-line header
  `<!-- pasted by user on YYYY-MM-DD -->`.

After processing, count readable samples. If fewer than 2, ask once for
more samples (free text). If still fewer than 2, abort with:
`"Need at least 2 readable samples to analyze voice. Got: {n}. Setup
cannot continue. Re-run /writer-setup with more samples."`

The workspace folder remains on disk but the pointer is NOT written.
The user can retry with more samples.

## Step 2 — Inference (parallel)

The heavy lifting. Skill orchestrates; agents and the script do the work.

### 2.0 — Establish `output_language`

Before dispatching agents, decide the language for the substantive
content that gets written into the workspace files (positions in
opinion-map, mini-bio in author-profile, voice summary in fingerprint,
voice principles in style-rules). Templates stay English; only the
filled-in prose is localized.

Cascade (first match wins):
1. The language the user is interacting with the assistant in this
   session — if the conversation has been in pt-BR / en / etc., that's
   `output_language`.
2. If ambiguous (mixed or unclear), default to `"en"`.

Cache the result as `${OUTPUT_LANGUAGE}`. Pass it explicitly in every
agent payload below. The `voice-analyzer` will also confirm-or-correct
this via its sample-based `language_detected` field; if the analyzer
returns a different language than the cascade picked, the analyzer's
detection wins for Step 2.7 (style-rules) and the confirmation screen
in Step 3.1 surfaces the mismatch so the user can override.

### 2.1 — Pre-write deterministic files

Materialize only the two files that every workspace needs from day one:
`CLAUDE.md` (workspace contract) and `opinion-map.md` (scaffolded; the
`opinion-extractor` agent fills it). Channel templates are **NOT**
copied here — they are materialized lazily by `/writer-create` on first
use of each channel (see "Lazy channel materialization" below).

**Files to write at this step (both use `Read` + substitute placeholders
+ `Write`, because both have placeholders):**

- **`{workspace_path}/CLAUDE.md`**: read
  `${CLAUDE_PLUGIN_ROOT}/skills/writer-setup/assets/workspace-template/CLAUDE.md`,
  substitute `{{AUTHOR_NAME}}` (use full name if known, else first_name
  capitalized), `{{WORKSPACE_PATH}}`, `{{CREATED_DATE}}` (today). `Write`
  to destination.

- **`{workspace_path}/references/opinion-map.md`**: read
  `${CLAUDE_PLUGIN_ROOT}/skills/writer-setup/assets/workspace-template/references/opinion-map.md`,
  substitute `{{AUTHOR_NAME}}`, leave the section scaffolds empty (no
  positions invented). The `opinion-extractor` agent populates them in
  parallel.

Both writes can happen in a single message (parallel, no dependencies).

**Lazy channel materialization — design contract:**

`/writer-create` is responsible for materializing the channel-template
on first use, inline (no skill delegation). Procedure when
`/writer-create` is invoked with `--channel <name>`:

1. Check if `{workspace}/channel-templates/<name>.md` exists. If yes,
   use it as-is.
2. If no, read the source template at
   `${CLAUDE_PLUGIN_ROOT}/skills/writer-setup/assets/workspace-template/channel-templates/<name>.md`.
3. Apply any `template_customizations` recorded in
   `.local.json` under `channels.<name>.template_customizations` (those
   were proposed by `profile-inferencer` during setup; see Step 2.6).
4. Write the customized template to
   `{workspace}/channel-templates/<name>.md`.
5. Proceed with the draft.

If the channel has no built-in template (`youtube`, `medium`, or any
other declared without an asset file), `/writer-create` falls back to a
generic structure inferred at write time and writes a starter template
to `{workspace}/channel-templates/<name>.md` so subsequent runs have
something concrete to edit.

This skill does NOT pre-materialize any channel template — users only
pay materialization cost for channels they actually write for.

### 2.2 — Dispatch agents in parallel

Send a single message with three `Task` invocations and (if applicable)
one `Bash` invocation, all in parallel:

#### Agent 1 — `voice-analyzer`

```json
{
  "sample_paths": ["<absolute paths to {workspace_path}/sample-sources/*>"],
  "fingerprint_path": "{workspace_path}/references/voice-fingerprint.md",
  "sample_sources_dir": "{workspace_path}/sample-sources",
  "author_name": "<full name if known, else first_name>",
  "output_language": "${OUTPUT_LANGUAGE}",
  "detect_language": true
}
```

The `voice-analyzer` reads every sample and counts characteristic
stopwords as part of its work. Setting `detect_language: true` tells it
to also return `language_detected` in its summary (e.g. `"pt-BR"`,
`"en"`). The setup uses that value in Step 2.8 instead of running its
own counting — sample tokenization is delegated by invariant 5.

#### Agent 2 — `profile-inferencer`

```json
{
  "links_easy_fetch": ["<URLs from links_easy_fetch>"],
  "links_browser_preferred": ["<URLs from links_browser_preferred>"],
  "sample_paths": ["<same absolute paths as voice-analyzer>"],
  "channels_declared": {
    "blog":      { "url": "...", "publish_via": "manual" },
    "newsletter": { "shares_url_with": "blog" } | { "url": "...", "platform": "..." },
    "linkedin":  { "active": true | false },
    "twitter":   { "active": true | false },
    "...":       { ... }
  },
  "workspace_path": "{workspace_path}",
  "output_path": "{workspace_path}/references/author-profile.md",
  "author_first_name": "{first_name}",
  "output_language": "${OUTPUT_LANGUAGE}"
}
```

#### Agent 3 — `opinion-extractor` (bulk mode)

```json
{
  "mode": "bulk",
  "source_paths": ["<absolute paths to {workspace_path}/sample-sources/*>"],
  "workspace_path": "{workspace_path}",
  "existing_opinion_map_path": "{workspace_path}/references/opinion-map.md",
  "output_language": "${OUTPUT_LANGUAGE}",
  "verbose": false
}
```

#### Script — `detect-archive-schema.py` (only if `archive_path` is set)

```bash
python3 "${CLAUDE_PLUGIN_ROOT}/skills/writer-setup/assets/scripts/detect-archive-schema.py" --path "{archive_path}"
```

Capture stdout JSON and the exit code. If the script:
- Returns `ok: true` → use the JSON directly. **Skip the LLM fallback.**
- Returns `ok: false` for a structural reason (`ephemeral-archive-path`,
  `archive-path-not-found`, `no-content-files`) → surface that reason in
  the confirmation screen. Set archive `enabled: false`. **No LLM
  fallback** (the script's "no" is authoritative for these errors).
- Returns `ok: false` with `error: "all-reads-failed-or-no-frontmatter"`,
  or exits non-zero with an uncaught exception, or returns invalid JSON →
  fall back to the `archive-detector` agent with the same `archive_path`.
  Both succeed together = use the script output.
- Python is not on PATH (`bash: python3: command not found`) → fall back
  to the agent.

### 2.3 — Retry policy

Retry once silently on agent failure. After a second failure, take the
action documented in `references/failure-handling.md`:
- `voice-analyzer` → abort (workspace preserved, pointer not written).
- `profile-inferencer` → degrade to inline identity collection (Step 3.0).
- `opinion-extractor` → degrade to scaffolded opinion-map.
- Archive script + agent both fail → degrade to `enabled: false`.

### 2.4 — Collect outputs

When all three agents return, you have:

- `voice-fingerprint.md` written by `voice-analyzer` + a ≤400-word summary
  in the agent's return.
- `author-profile.md` written by `profile-inferencer` + a structured JSON
  report (`fields_inferred`, `fields_null`, `channel_template_proposals`,
  `links_skipped`, `links_failed`).
- `opinion-map.md` patched by `opinion-extractor` (the agent returns
  proposed `Apply patch` blocks; apply them via `Edit` now).
- Archive JSON (from script or agent fallback, if archive_path was set).

### 2.5 — Apply opinion-extractor patches

The `opinion-extractor` returns a structured markdown payload. The
contract (target_section, insert_after, block, conflicts, patch
application order, single-patch failure handling) is documented in
**`references/agent-contracts.md`** — load that file when applying
patches. Conflicts go straight to the confirmation screen for the
user; the setup does not auto-resolve them.

### 2.6 — Persist channel-template customizations to config

For each `channel_template_proposals` entry from `profile-inferencer`,
do NOT edit any channel-template file (they don't exist yet — channel
templates are lazy-materialized by `/writer-create`). Instead, record
the customizations in `.local.json` under
`channels.<channel>.template_customizations` so `/writer-create` can
apply them when it materializes the template on first use.

Schema for each customization block (Step 4.2 writes this into the
config):

```json
"template_customizations": {
  "target_length_words": [600, 900],
  "formatting_notes_addition": "Open with a number or concrete observation; the author rarely uses scene-setting metaphors.",
  "anti_pattern_additions": ["Bullet lists with 7+ items"],
  "rationale": "Across 3 blog samples, the median word count was 780."
}
```

If the agent did not return a proposal for a given channel, the field
stays `null` and the template is materialized verbatim from the plugin
default. Trust the agent's cap of 3 proposals — apply every proposal it
returned.

### 2.7 — Write `style-rules.md`

After `voice-analyzer` returns, generate `style-rules.md` in a single
pass. Use the template at
`${CLAUDE_PLUGIN_ROOT}/skills/writer-setup/assets/workspace-template/references/style-rules.md`
and substitute placeholders according to the source-of-truth table in
**`references/placeholder-map.md`** (sibling file to this SKILL.md).
Load that file when filling placeholders.

**How to populate the placeholders:**

1. The `voice-analyzer` response includes a section called
   `## Style-rules content blocks` with pre-formatted blocks named after
   the placeholders (`VOICE_PRINCIPLES`, `SENTENCE_PATTERNS`,
   `ONE_LINE_PUNCHES`, `OPENING_PATTERNS`, `CLOSING_PATTERNS`,
   `PREFERRED_EXPRESSIONS`, `CONTRAST_FORBIDDEN`, `CHANNEL_OVERRIDES`).
   Copy each block verbatim into the corresponding placeholder. Do not
   summarize, do not strip examples, do not paraphrase.
2. For the static-default placeholders (`{{CAPITALIZATION}}`,
   `{{BOLD_RULE}}`, `{{LISTS_RULE}}`, etc.), translate the source text
   from `placeholder-map.md` to `${OUTPUT_LANGUAGE}` and substitute.
3. For language placeholders (`{{PRIMARY_LANGUAGE}}`, `{{TECH_LANGUAGE}}`,
   `{{CODE_SWITCH}}`), use the resolved `language.default` and
   `language.technical_terms_in` from Step 2.8 (the analyzer's
   `language_detected` wins over the cascade pick).
4. `{{FORBIDDEN_USER}}` always starts as the literal placeholder text
   `_(empty — populated by /writer-calibrate over time)_`.
5. `{{HARD_RULES}}` references the workspace `CLAUDE.md` invariants —
   never duplicate text.

**Critical: `CONTRAST_FORBIDDEN` must be non-empty.** If the analyzer
returned an empty block (regression risk vs v0.5), re-dispatch the
agent once asking specifically for the contrast list. If still empty on
retry, surface a warning in the final summary and continue.

If a metric from `voice-analyzer` is `n/a`, the corresponding
placeholder gets `n/a` plus a one-line reason — do not invent.

### 2.8 — Capture detected language and copy baseline-forbidden file

The `voice-analyzer` agent returned `language_detected` in its summary
(per invariant 5 — language detection is delegated). Cache it as
`language.default`. Set `language.technical_terms_in` to `"en"` unless
`language.default` is already `"en"` (in which case keep `null`).

Then copy the matching baseline-forbidden file from the plugin template
to the workspace:

```bash
case "${language_default}" in
  pt-BR) src="${CLAUDE_PLUGIN_ROOT}/skills/writer-setup/assets/workspace-template/references/baseline-forbidden-pt-BR.md" ;;
  en)    src="${CLAUDE_PLUGIN_ROOT}/skills/writer-setup/assets/workspace-template/references/baseline-forbidden-en.md" ;;
  *)     src="" ;;  # no baseline available for this language
esac
if [ -n "${src}" ] && [ -f "${src}" ]; then
  cp "${src}" "{workspace_path}/references/$(basename "${src}")"
fi
```

If no baseline file exists for the detected language, record a warning
on the confirmation screen: `"No baseline-forbidden file for
{language_default}. /writer-create will rely only on style-rules.md and
voice-fingerprint.md."`. The user can override `language.default` in
Step 3 — if the override changes, copy the matching baseline file
before persisting in Step 4.

## Step 3 — Confirm with real data

### 3.0 — Handle profile-inferencer degrade

If `profile-inferencer` failed twice, ask inline BEFORE showing the
confirmation screen:

```
Profile inference failed. Reason: {error}
Please give me these fields in free text:
- Full name:
- Role/title:
- Company:
- Industry:
- Primary audience:
- Mini-bio (up to 350 chars):
```

Parse the user's response and write `{workspace_path}/references/author-profile.md`
directly from the answers (no agent).

### 3.1 — Confirmation screen

Render a single screen with real values (URLs, numbers, paths — never
placeholders). Use these symbols:

- `✓` high confidence
- `~` medium confidence — please review
- `?` null — needs input or is skippable
- `✗` failure — explain reason

Template (English UI, fill with real inferred data):

```
Workspace materialized at {workspace_path}/

═══ IDENTITY ════════════════════════════════════════════════════════
{✓|~|?} Name: {full_name | _(not detected)_}
{✓|~|?} Role: {role | _(not detected)_}
{✓|~|?} Company: {company | _(not detected)_}
{✓|~|?} Industry: {industry | _(not detected)_}
{✓|~|?} Audience: {audience | _(not detected)_}
{✓|~|?} Mini-bio: "{mini_bio[:120]}..." ({len} chars / 350 max)
{?}     Philosophy / influences: not detected (populate via
        /writer-opinion-mine or edit author-profile.md directly)

═══ LANGUAGE ════════════════════════════════════════════════════════
✓ Default: {pt-BR | en | ...} (detected from {N} samples)
✓ Technical terms in: {en | none}

═══ CHANNELS ════════════════════════════════════════════════════════
{✓|?} Blog: {url | _(not declared)_} (CMS hint: {ghost|wordpress|unknown})
{✓|?} Newsletter: {url or "same as blog" or _(not declared)_}
{✓|?} LinkedIn: {url or "active, no URL" or _(not declared)_}
{✓|?} Other: {comma-separated list or _(none)_}

═══ VOICE ═══════════════════════════════════════════════════════════
✓ {N} samples analyzed, {total_words} words total
✓ Avg sentence: {n} words; short paragraphs: {ratio}%
✓ Top expressions: {top-5 inline}
✓ Forbidden patterns detected: {count}
{✗ if voice-analyzer warned about anything — list one-liner reasons}

═══ OPINIONS MAPPED ═════════════════════════════════════════════════
{✓|✗} {N} positions in Núcleo duro, {N} in formation, {N} tensions
        (or "Failed: {reason}. Run /writer-opinion-mine after setup to
         populate.")

═══ ARCHIVE ═════════════════════════════════════════════════════════
{✓ if archive enabled, with: path, toolchain, schema summary}
{? if user declined: "Not configured. Re-run /writer-setup later with an
   archive path, or edit .claude/eis-content-builder.local.json by hand."}
{✗ if archive failed: "Failed: {reason}. Archive disabled."}

═══ RESEARCH SOURCES ════════════════════════════════════════════════
? Not configured. Which authors / blogs / newsletters do you consult
  when researching? (Optional — reply with names/URLs or "skip".)

═══ PENDING (handled later) ═════════════════════════════════════════
{One line per pending item, only include rows that apply:}
{- save-preferences: empty — auto-fills as you use /writer-save}
{- channel-templates without defaults: youtube, medium}
{- profile-inferencer or opinion-extractor errors — see above}

──────────────────────────────────────────────────────────────────────
Reply with corrections in free text (e.g. "industry is fintech, not
SaaS B2B; audience is early-stage founders"), OR paste research sources,
OR just say "looks good" / "ok" to finalize.
```

### 3.2 — Apply corrections (one round)

Parse the user's reply. Categorize each statement:

- **Identity correction** → `Edit` `references/author-profile.md`.
- **Channel correction** → `Edit` `.claude/eis-content-builder.local.json`
  (write happens in Step 4; for now record the override).
- **Language correction** → record override.
- **Archive change** → record override.
- **Research source** → record in `research_sources` (parse: blogs vs
  people vs RSS by URL shape).
- **"looks good" / "ok" / "tá bom" / "skip"** → close confirmation, go
  to Step 4.

After applying, show a compact diff:

```
Applied:
- author-profile.md: industry → "product management for fintech"
- author-profile.md: audience → "early-stage founders and PMs"
- .local.json (pending write): research_sources.trusted_blogs → ["lennysnewsletter.com"]
- .local.json (pending write): research_sources.people_to_watch → ["Lenny Rachitsky", "Marty Cagan"]

Anything else? Say "looks good" to finalize.
```

Accept at most one additional surgical correction round, then close.

## Step 4 — Persist and finalize

### 4.1 — Defensive verification

Before writing the config and pointer, verify all critical files exist
and have content:

```bash
test -s "{workspace_path}/references/voice-fingerprint.md" && \
test -s "{workspace_path}/references/style-rules.md" && \
test -s "{workspace_path}/references/author-profile.md" && \
test -s "{workspace_path}/references/opinion-map.md" && \
test -s "{workspace_path}/CLAUDE.md" && echo OK || echo MISSING
```

If `MISSING`, abort Step 4 with a clear message listing which files are
missing. Do not write the config or pointer — the workspace stays in a
"trial" state and the user can retry.

### 4.2 — Write the canonical config

Write JSON to `{workspace_path}/.claude/eis-content-builder.local.json`.
Schema (every field present, nulls allowed):

```json
{
  "workspace_path": "{workspace_path}",
  "initialized_at": "YYYY-MM-DD",
  "version": "0.6.0",

  "author": {
    "first_name": "{first_name_slug}",
    "full_name": "{full name or null}"
  },

  "language": {
    "default": "pt-BR",
    "technical_terms_in": "en"
  },

  "channels": {
    "blog": {
      "url": "https://...",
      "cms": "ghost|wordpress|obsidian|custom|none|null",
      "publish_via": "manual|api",
      "has_template": true,
      "materialized": false,
      "template_customizations": {
        "target_length_words": [800, 1300],
        "formatting_notes_addition": null,
        "anti_pattern_additions": [],
        "rationale": "Median word count across blog samples: 1050"
      }
    },
    "newsletter": {
      "shares_url_with": "blog",
      "platform": "ghost",
      "has_template": true,
      "materialized": false,
      "template_customizations": null
    },
    "linkedin": {
      "profile_url": "https://...",
      "posting_tool": "manual",
      "has_template": true,
      "materialized": false,
      "template_customizations": null
    },
    "twitter": {
      "active": true,
      "has_template": true,
      "materialized": false,
      "template_customizations": null
    },
    "youtube": {
      "active": true,
      "has_template": false,
      "materialized": false,
      "template_customizations": null
    },
    "medium": {
      "active": true,
      "has_template": false,
      "materialized": false,
      "template_customizations": null
    }
  },

  "research_sources": {
    "trusted_blogs": [],
    "rss_feeds": [],
    "people_to_watch": [],
    "avoid_sources": []
  },

  "article_archive": {
    "enabled": true,
    "path": "/abs/path",
    "file_pattern": "**/*.md",
    "toolchain": "obsidian|generic",
    "schema": {
      "title_property": "title",
      "tags_property": "tags",
      "status_property": "status",
      "published_values": ["published"],
      "date_property": "date",
      "url_property": "permalink",
      "excerpt_property": "excerpt"
    },
    "index_file": {
      "path": null,
      "format": null
    }
  },

  "save_preferences": [],

  "ideation": {
    "exclude_themes": [],
    "preferred_angles": [],
    "default_channel": "blog"
  }
}
```

If archive was declined or failed: set `article_archive.enabled: false`
and leave all archive fields as defaults except `enabled`.

### 4.3 — Write the pointer

After the config write succeeds, write
`$HOME/.claude/eis-content-builder.pointer.json`:

```json
{
  "workspace_path": "{workspace_path}",
  "initialized_at": "YYYY-MM-DD"
}
```

`Bash: mkdir -p "$HOME/.claude"` first.

**Order matters:** config first, pointer second. If the process crashes
between the two, local discovery via cwd walk-up still finds the workspace.

### 4.4 — Generate the archive index (if enabled)

If `article_archive.enabled` is `true`, invoke `/writer-index` via the
`Skill` tool. The index skill reads `.local.json`, finds the archive,
generates `{workspace_path}/eis-article-index.json`, and updates
`article_archive.index_file.path` and `.format` in the config.

If `/writer-index` fails, do NOT abort — just include the failure in the
final message. The user can re-run `/writer-index` later.

### 4.5 — Final message

```
✓ Workspace ready at {workspace_path}/

What's ready:
- 4 reference files (voice-fingerprint, style-rules, author-profile, opinion-map)
- {N} channel templates ({list})
- {Article archive index with {M} articles | Archive not configured}
- Canonical config at .claude/eis-content-builder.local.json
- Pointer at ~/.claude/eis-content-builder.pointer.json (lets you invoke skills
  from any folder)

Next steps:
- /writer-create <topic> — write a draft in your voice
- /writer-ideate — brainstorm pieces when you don't have a topic yet
- /writer-opinion-mine — refine the opinion map (more opinions = sharper drafts)

When a draft doesn't sound like you, use /writer-calibrate for surgical
voice corrections.
```

## Failure handling — summary

See **`references/failure-handling.md`** for the full table of failure
modes and the retry/abort/degrade policy. The table covers all steps
(1.2, 1.6, 1.7, 2.3, 4.1, 4.2/4.3, 4.4) plus terminal-failure messages.

## TodoWrite usage

Create four todos at the start, one per step (1, 2, 3, 4). Mark each
complete as you finish. Do not create sub-todos.

## Rules

- The workspace records the plugin version it was created under in
  `.local.json` (Step 4.2). When bumping the plugin, update both
  `plugin.json` (top-level manifest) and the hardcoded string in
  Step 4.2 of this skill.
- UI strings in this skill are English. Reference files inside the
  workspace follow the user's language (`voice-analyzer` reports
  `language_detected`; the skill uses it in Step 2.8).
- `sample-sources/` is read by the `voice-analyzer` agent only; the
  skill itself does not read those files after Step 2.
- Other writer skills (`/writer-calibrate`, `/writer-create`,
  `/writer-ideate`, `/writer-opinion-mine`) are next steps for the user
  — they are not chained from setup.
- The only skill this one invokes is `/writer-index`, and only in
  Step 4.4 when `article_archive.enabled` is true.
