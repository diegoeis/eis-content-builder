---
name: writer-create
description: Supervisor skill that writes a piece of content in the author's voice and orchestrates the draft-evaluator and opinion-extractor sub-agents. Use when the user says "write an article about", "create a LinkedIn post", "draft a newsletter", "escreve um post sobre", "quero um ensaio sobre", "write me a piece on X", "rascunha um texto", or runs `/writer-create`. Default mode is silent and safe for automation - zero questions, mandatory inline self-audit, opt-in stronger eval via `--eval on`. With `--interactive`, asks clarifying questions and proposes outlines for approval. Researches sources (browser-tool first, WebFetch fallback), saves to `drafts/` with complete YAML frontmatter, and emits a `STATUS: OK|WARN|BLOCKED` line on the first output line so pipelines can branch. Never writes draft content into chat - always saves to `drafts/`.
argument-hint: "<topic> [--channel newsletter|blog|linkedin|twitter|youtube|script] [--thesis \"...\"] [--length N] [--sources url1,url2] [--workspace /abs/path] [--interactive] [--eval off|on|verbose] [--opinion-extract on|off]"
allowed-tools: Read, Write, Edit, Bash, Glob, AskUserQuestion, WebSearch, WebFetch, TodoWrite, Task
---

# SKILL

> **Synopsis.** Write a piece in the author's voice. Silent by default (zero questions, mandatory inline self-audit, saves to `drafts/`). The full `draft-evaluator` agent is opt-in via `--eval on` — it costs more tokens and is meant as a strong second opinion when the user wants one. Add `--interactive` for outline approval and step-by-step control. When `article_archive` is enabled in the config, cross-references the author's own past pieces for internal links, repetition checks, and reusable snippets. Outputs `STATUS: OK|WARN|BLOCKED` on the first line for automation pipelines.


# Writer Create

Produce content indistinguishable from the author's own writing. The piece lives in `drafts/`, not in chat.

This skill has **two modes**:

- **Silent / non-interactive (default)**: zero questions, zero outline approvals, mandatory inline self-audit auto-applies fixes, opinion-extractor runs automatically, full `draft-evaluator` agent runs ONLY when `--eval on` is passed. Designed to be safe to run from a cron, hook, or external automation.
- **Interactive (`--interactive`)**: asks for missing inputs, proposes outline for approval, and (when `--eval on` is also passed) surfaces eval violations for user decision.

## Defaults (silent mode)

| Argument | Default |
|---|---|
| `--channel` | `newsletter` |
| `--eval` | `off` (mandatory inline self-audit always runs; full `draft-evaluator` agent only with `--eval on`) |
| `--opinion-extract` | `on` |
| `--interactive` | off |

**Why `--eval off` is the default.** The inline self-audit (Step 9.5)
runs every time and catches the high-frequency hard-rule violations
(pamphleteering inversions, lists when prose is preferred, forbidden
phrases, emoji policy, frontmatter completeness). It costs only one
extra pass of the draft against a compact checklist — same conversation,
same context.

The `draft-evaluator` agent is a stronger, more expensive second pass:
it re-reads the full `style-rules.md`, `voice-fingerprint.md`,
`channel-templates/<channel>.md`, and `opinion-map.md` in a fresh
sub-agent context and runs all 10 dimensions exhaustively. Use
`--eval on` when you want that second opinion (high-stakes pieces,
calibration verification, suspicion the self-audit drifted).

## Authorial stance (non-negotiable)

**Every piece produced by this skill is an authorial article, never a reference piece, summary, explainer, or paraphrase of someone else's work.**

The author's voice, position, and argument are the product. Sources — articles, posts, papers, transcripts, books, links the user passes via `--sources`, candidates surfaced by research, even snippets from the author's own archive — are **raw material** for the author to think with, not the subject to be explained.

What this means in practice:

- The piece is built around the **author's thesis**, not around "here's what X said and here's what Y said." Other people's ideas appear as evidence, contrast, or counterpoint — never as the central spine.
- Do **not** structure the draft as a summary of a source ("In this article, [author] argues…"), a recap ("The piece walks through three ideas…"), a reaction post ("I read X and here are my thoughts on each point…"), or a tutorial about the source material ("Here's what [framework/book/talk] teaches…").
- Quote sparingly and only when the exact wording matters. Default to **synthesis with attribution** — take the idea, run it through the author's lens, link the source. The reader leaves with the author's argument, not a digest of someone else's.
- Even when **no external sources are provided** (just a topic), the same rule holds: write an authorial take, not a generic explainer or "what is X" piece. The author has a position; surface it.
- If the only thing you can write on a topic is a summary or explainer of an external piece (because the author has no distinctive angle yet), this is a signal that the topic belongs to `## Forming positions` or `## Neutral zones` in `opinion-map.md` — flag it in the final log and proceed with an analytical/descriptive framing per Step 5, not as a faux-authorial piece.

This rule overrides any pull toward "balanced coverage," "comprehensive explanation," or "doing justice to the source." The skill exists to produce the author's writing, not to produce study notes about other people's writing.

## Invariant rules

Inherit from `{workspace}/CLAUDE.md`. Critical ones for this skill:

- Never fabricate data, statistics, quotes, or case studies.
- Every factual claim links to a verifiable primary source.
- The draft body and the user-facing prose (log, errors, prompts) follow `${OUTPUT_LANGUAGE}` resolved from `.local.json` (`language.default`). The skill body itself (SKILL.md) stays in English — it is for the orchestrator, not the user.
- Never dump the full piece into chat. Save to `drafts/`, show the path, log a short summary.
- Surgical edits only when the user asks for changes. Do not regenerate.
- Never write outside `{workspace_path}` (drafts, opinion-map, channel-templates only). Archive paths are read-only.
- For research, follow operating principle 6: browser MCP first (uses the user's logged-in session), WebFetch as fallback, ask the user when both fail. No skip-list.

## Step 1 — Parse arguments

Parse `$ARGUMENTS`. Treat the first non-flag token (and any trailing free text up to the first flag) as the **topic**.

- `--channel <c>` → channel. Default: `ideation.default_channel` from `.local.json` (falls back to `newsletter` if absent).
- `--thesis "..."` → user-supplied thesis. If absent, you derive one in Step 5 from opinion-map (`## Hard core`) or the topic itself.
- `--length N` → word target override. If absent, use the `## Target` length declared in the materialized `channel-templates/<channel>.md`.
- `--sources url1,url2` → seed sources. Reuse first; supplement with browser-tool/WebFetch as needed (Step 6).
- `--workspace <abs-path>` → overrides the pointer and walk-up resolution (Step 2). Use when the author maintains multiple workspaces.
- `--interactive` → enables the interactive mode. Without it, silent mode is active.
- `--eval off|on|verbose` → default `off`. `on` runs the `draft-evaluator` agent in an auto-fix loop (max 3 iterations). `verbose` runs the agent and surfaces violations to the user for manual selection. `off` skips the agent entirely — **but the inline self-audit in Step 9.5 still runs**. Use `on` for a strong second opinion; `off` (default) trusts the self-audit.
- `--opinion-extract on|off` → default `on`. Skips opinion-extractor when `off`.

**Topic missing AND silent mode → fail fast.** Output: `error: /writer-create requires a <topic>. Pass it as the first argument or run with --interactive.` Stop. Do not proceed.

**Topic missing AND interactive mode → ask once via `AskUserQuestion`.**

## Step 2 — Discover the workspace

Pointer-first cascade. The pointer at `${HOME}/.claude/eis-content-builder.pointer.json` is the source of truth for ~95% of cases — one file read resolves the workspace. Walk-up is a fallback only.

1. **Pointer.** Read `${HOME}/.claude/eis-content-builder.pointer.json`. Extract `workspace_path` and verify `${workspace_path}/.claude/eis-content-builder.local.json` exists. If both true → use it. Skip the walk-up.
2. **Walk-up fallback.** If the pointer is missing OR its `workspace_path` no longer exists, walk up from `${PWD}` to `/` checking each ancestor for `.claude/eis-content-builder.local.json`. First hit wins.
3. **Ask the user.** Neither resolved → silent mode stops with `error: workspace not found. Run /writer-setup first.`; interactive mode asks for the absolute workspace path.

The user can force a specific workspace for a single run via `--workspace <path>` (overrides both the pointer and walk-up). Useful when the author maintains multiple workspaces (e.g., one per language).

Single `Bash` call:

```bash
config=""
if [ -f "$HOME/.claude/eis-content-builder.pointer.json" ]; then
  ws=$(python3 -c 'import json,sys;print(json.load(open(sys.argv[1])).get("workspace_path",""))' "$HOME/.claude/eis-content-builder.pointer.json" 2>/dev/null)
  if [ -n "$ws" ] && [ -f "$ws/.claude/eis-content-builder.local.json" ]; then
    config="$ws/.claude/eis-content-builder.local.json"
  fi
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

Capture as `CONFIG_PATH`. Empty result → see step (3) above.

Then `Read "$CONFIG_PATH"` and parse JSON.

**Extract and validate:**

- `workspace_path` → `Bash: test -d "{workspace_path}" && test -f "{workspace_path}/CLAUDE.md"`. Either fail → stop with `error: workspace at {workspace_path} is missing or incomplete. Run /writer-setup.`
- Reject ephemeral roots (`/sessions/`, top-level `/mnt/`, `/tmp/`, `/private/tmp/`, `/var/folders/`, anything under `/worktrees/`) even if they currently exist. Same stop + repair message.
- `language.default` → store as `${OUTPUT_LANGUAGE}`. All user-facing prose from now on follows this language. Fallback `pt-BR` if missing.
- `ideation.default_channel` → used as fallback channel when `--channel` is absent. Fallback `newsletter` if missing.
- `article_archive` block → may be absent. Treat absent as `enabled: false`.
  - `enabled: true` → `Bash: test -d "{article_archive.path}"`. Missing path: log `archive-path-missing` warning, downgrade in-memory to `enabled: false` for this run.
  - `toolchain == "obsidian"` → `Bash: which obsidian`. CLI missing → downgrade in-memory to `generic`, log `obsidian-cli-missing`.
- `channels.<channel>` (where `<channel>` is the one resolved in Step 1) → used in Step 3 for lazy materialization. If the channel is not present in the config, treat as `has_template: false` and proceed (Step 3 will write a starter template).

## Step 3 — Lazy channel materialization

This skill is responsible for materializing the channel template on first use. The setup does not pre-populate `channel-templates/`; templates only exist after `/writer-create` has been invoked with that channel.

**Resolve `${CLAUDE_PLUGIN_ROOT}` first.** If the env var is not set, the source templates are unreachable. Try in order: `${CLAUDE_PLUGIN_ROOT}` env var → standard install path (`${HOME}/.claude/plugins/eis-content-builder` if present) → mark `plugin-root-unavailable` and fall through to the starter template fallback (step 3 below). Log the resolution outcome so the STATUS line can distinguish "starter used because no built-in template for this channel" from "starter used because plugin root could not be resolved" — the second is a voice regression risk and must be flagged.

Procedure:

1. `Bash: test -f "{workspace_path}/channel-templates/{channel}.md"`. If exists → use it as-is. Skip to Step 4.

2. If not exists AND `channels.{channel}.has_template == true` (or absent) AND plugin root resolved:
   - Read the source template from `${PLUGIN_ROOT}/skills/writer-setup/assets/workspace-template/channel-templates/{channel}.md`.
   - Apply `channels.{channel}.template_customizations` from `.local.json` if present:
     - `target_length_words: [min, max]` → replace the `## Target` `- **Length**:` line with the customized range.
     - `formatting_notes_addition` → append to `## Formatting rules` as a new bullet.
     - `anti_pattern_additions: [string, ...]` → append each as a new bullet under `## Anti-patterns`.
     - If `template_customizations` is `null` → use the source template verbatim.
   - `Write` the customized template to `{workspace_path}/channel-templates/{channel}.md`.
   - `Edit` `.local.json` to set `channels.{channel}.materialized: true` (and add the channel block if it was absent).

3. **Starter template fallback.** Triggered by any of:
   - `channels.{channel}.has_template == false` (e.g., `youtube`, `medium`, custom),
   - plugin root could not be resolved (no env var, no standard install path),
   - source template path resolves but file is missing (broken plugin install — log `channel-template-source-missing: {path}`).

   Action: write a minimal starter template at `{workspace_path}/channel-templates/{channel}.md` with placeholder sections (`## Target`, `## Structure`, `## Frontmatter`, `## Anti-patterns`, `## Formatting rules`) inferred from the channel name and the author's voice (best-effort from `voice-fingerprint.md`).

   Log the **reason** the starter was used so the STATUS line is unambiguous:
   - `channel-starter-template: {channel} (no built-in template; review and refine)` — when has_template is false.
   - `channel-starter-template-fallback: {channel} (plugin root unavailable; voice may regress)` — when plugin root could not be resolved. **This is a WARN-level signal in the final log.**
   - `channel-starter-template-fallback: {channel} (source file missing at {path})` — when the source path is invalid.

   Update `.local.json` to add/update the channel block with `materialized: true`.

**Hard rule:** never write outside `{workspace_path}/channel-templates/` or the config file. The source template under `${PLUGIN_ROOT}/...` is read-only.

## Step 4 — Load context

`Read` the following files in parallel (one message, multiple Read calls). The list is short on purpose — the fingerprint already distills the corpus.

**Mandatory (voice authenticity):**
- `{workspace}/references/style-rules.md`
- `{workspace}/references/voice-fingerprint.md` (the `## Few-shot examples` section lives inside)
- `{workspace}/channel-templates/{channel}.md` (materialized in Step 3)

**Position authenticity:**
- `{workspace}/references/opinion-map.md` (early-exit if scaffolded; see Step 5)

**Situational context:**
- `{workspace}/references/author-profile.md`
- `{workspace}/CLAUDE.md` (inherited invariants; small file)

The full `eis-article-index.json` is not loaded here; it is consulted with a keyword filter in Step 7.

Any mandatory file missing → silent mode: emit `error: required file {path} missing. Run /writer-setup.` and stop. Interactive mode: same message as a prompt.

If `opinion-map.md` is missing → record `opinion-map-missing` warning and proceed without it (thesis derived from topic only). Do not stop.

If `author-profile.md` or `CLAUDE.md` is missing → log a warning and proceed.

## Step 5 — Cross-reference opinion-map

If `opinion-map.md` is missing (logged in Step 4) → skip this step. Thesis comes from `--thesis` arg or the topic.

**Early-exit for scaffolded files:** if the opinion-map file is < 1 KB OR contains only headers with no entries (regex: no non-header non-blank lines after stripping `## ...` lines), record `opinion-map-scaffolded` warning and skip the scan. Thesis derivation falls back to `--thesis` or the topic.

Otherwise scan `opinion-map.md` for the topic. Headers are in English; content follows `${OUTPUT_LANGUAGE}`:

- **Topic in `## Hard core`** → use the recorded position as thesis; embed the recorded counter-argument inside the piece.
- **Topic in `## Forming positions`** → use the recorded position but apply hedging from the author's register. Record in final log: `thesis based on forming position — review before publishing`.
- **Topic in `## Neutral zones`** → propose an analytical/descriptive framing. Do not fabricate a position. Record in final log: `topic is neutral — piece is descriptive, not opinionated`.
- **Topic in `## Refusals`** →
  - Silent mode: stop. Output (in `${OUTPUT_LANGUAGE}`) the equivalent of: `error: topic "{topic}" is in opinion-map.md ## Refusals. Refusing to write. Remove the refusal first or pick another topic.` Do not write anything.
  - Interactive mode: ask the user before proceeding.
- **Topic appears in `## Tensions and synergies between topics`** → record as a candidate angle in your internal outline.

If the opinion-map uses PT headers (`## Núcleo duro`, `## Posições em formação`, `## Zonas neutras`, `## Não-posições`, `## Sinergias e tensões entre temas`), treat them as equivalents of the EN headers above. Do not rewrite — that is the job of `/writer-opinion-mine` or `/writer-setup`.

## Step 6 — Build internal outline

Always build an outline. In **silent mode** the outline is internal — you proceed directly to writing. In **interactive mode** present it via `AskUserQuestion` and wait for approval (skip the approval step for short-form: LinkedIn, tweets, posts ≤ 250 words).

The outline captures:

- **Working title** (using the author's capitalization preference from `style-rules.md`)
- **Channel** + **target length** (from the `## Target` section of `channel-templates/{channel}.md`, overridden by `--length` if passed)
- **Central thesis** (one sentence — from opinion-map if `## Hard core`, from `--thesis` arg if passed, otherwise inferred from topic)
- **Opening technique** (pick one from `voice-fingerprint.md` signature openings)
- **Development beats** (3–5 numbered, each: claim + data/example, no repetition; respect the `## Structure` outline of the channel template)
- **Closing technique** (pick one from `voice-fingerprint.md` signature closings)
- **Sources needed** (claims that require verification)
- **Excerpt** (≤200 chars for frontmatter)

For multi-beat pieces (blog + newsletter + script combos, or pieces with ≥4 beats), use `TodoWrite` to track each beat. Skip for short-form.

## Step 7 — Consult the author's article archive

Skip if `article_archive.enabled` is `false` (in config or downgraded in Step 2).

Goal: surface past pieces worth linking, flag repetition, find reusable snippet pointers. Fast and shallow — no LLM ranking, no embedding, no deep file reads upfront.

**Always filter before loading.** Do not `Read` the full `eis-article-index.json` into context. Topic keywords = the topic string from `$ARGUMENTS` plus terms surfaced in Step 5. Strip basic stopwords.

Query source by priority:

1. **JSON/CSV index** with `jq`/`awk`/`python` filter on title + excerpt + tags. Cap at 50 results.
2. **Obsidian base** (`toolchain == "obsidian"` + CLI present): `Bash: obsidian base:query --file="{index_file.path}" --format=json | jq <filter>`.
3. **Folder scan fallback**: `Glob "{article_archive.path}/{file_pattern}"` + `head -30` on each to read frontmatter, filter inline.

Rank by relevance (title match > excerpt match > tag match). Keep the top 8 as `candidates`. Empty → log `archive-no-match` and skip the rest of this step.

For each candidate, decide one action — pick the strongest signal that applies:

- **Link it** (if it has a `url` and `status` is in `article_archive.schema.published_values`): hold aside; during Step 9, link once where the topic surfaces organically. Cap 3 internal links per piece. Never force a "see also".
- **Flag repetition** (if tag overlap ≥ 2 AND title overlaps ≥ 50% of topic keywords): silent mode logs `repetition-risk: "{title}" at {path}`; interactive mode asks the user whether to continue, pivot, or stop. Never delete the draft.
- **Reusable snippet** (sibling theme: tag overlap = 1 OR title match without tag overlap): `Read` the file body (cap ~200 lines), pick up to 2 paragraph-level snippets the author can reuse. During Step 9, weave them in with explicit attribution (link if `url`, mention "covered earlier in: {title}" otherwise).

**Hard rules:**

- Read-only on the archive. Never `Write` or `Edit` inside `article_archive.path`.
- Never paste raw archive content into chat. Snippets only live inside the draft, with attribution.
- Never invent a `url`. A piece without `url` is not link-eligible.
- Snippet reuse is restricted to `article_archive`. Third-party sources from Step 8 are for citation, not quoting.

Record in the final log: `archive-consulted: {N} candidates, {L} linked, {R} repetition-flagged, {S} snippets`.

## Step 8 — Research

For each `Sources needed` item plus any categorical or numeric claim you're about to make:

1. **Reuse `--sources` if provided.** No further research needed for those URLs (still validate they resolve via the browser/WebFetch cascade below).
2. **Discover candidates via `WebSearch`.** Prefer `research_sources.trusted_blogs` and `research_sources.people_to_watch` from `.local.json`. Reject any domain in `research_sources.avoid_sources`.
3. **Verify the claim is actually present in the source — cascade per operating principle 6:**
   1. **Browser MCP first** (e.g., Claude in Chrome / Playwright if available) — uses the user's logged-in session, works for sites that block scrapers (LinkedIn, X/Twitter, paywalls). Navigate and extract the text containing the claim.
   2. **WebFetch fallback** if the browser MCP is unavailable or returns nothing usable.
   3. **Ask the user** (interactive mode) or **drop the claim** (silent mode) when both fail. Log `source-unverifiable: {claim}`.
4. **No claim without a verified primary source.** No "studies suggest" hedging.

Batch in parallel where independent (browser vs WebFetch on disjoint URLs).

## Step 9 — Write the draft

1. **Compute the draft path.** Filename preserves the working title verbatim — same capitalization, spaces, and accents as the H1. Do not slugify, do not lowercase, do not replace spaces with hyphens, **do not prepend the date or any other prefix**. Sanitize only filesystem-illegal chars (`/`, `:`, `?`, `*`, `<`, `>`, `|`, `\`, leading/trailing whitespace, trailing periods).

   Path: `{workspace}/drafts/{Title}.md`.

   Example: title `Entender antes de executar` → file `Entender antes de executar.md`. Title `Como criar cultura e estruturar uma área de produtos` → file `Como criar cultura e estruturar uma área de produtos.md`.

   The title itself must also not carry the date inside it — never bake `{YYYY-MM-DD}` into the H1 or the filename. Dates live in the frontmatter (`created`, `updated`, `date`), not in the file identity.

   If the file already exists: silent mode appends ` v2`, ` v3`, etc (with a space, preserving the title style) until a free name is found; interactive mode asks.

2. **Assemble frontmatter from the channel template.** Read the `## Frontmatter` block of `{workspace}/channel-templates/{channel}.md`. **That YAML block is the source of truth for which keys exist.** Use exactly the fields declared there, substituting placeholders (`<title>`, `<slug>`, `<YYYY-MM-DD>`, etc.) with actual values.

   **Do not invent new properties.** Never add YAML keys that are not in the template's `## Frontmatter` block. No `author`, `category`, `seo_title`, `og_image`, `summary`, `keywords`, `series`, `featured`, or any other field unless the template literally lists it. If a field feels missing, surface that in the warnings — do not silently add it. The only exception is the mandatory baseline below (always present, even when the template omits them).

   **Mandatory baseline (filled in even when the template omits them):**

   - `status: draft`
   - `published: false`
   - `created`, `updated` — today's date in `YYYY-MM-DD`.
   - `excerpt` — ≤ 200 chars.
   - `tags` — derived from topic keywords (only if the template declares `tags`; if the template has no `tags` field, do not add one).

   For any other field (`type`, `channel`, `date`, `slug`, `category`, etc.), use **exactly what the template declares** — same key, same value shape. Do not override the template's `type` value with something else, and do not add a `type` field if the template doesn't have one.

   Example shape (exact field set is whatever the channel template declares, plus the baseline above):

   ```yaml
   ---
   type: <whatever the channel template declares>
   channel: newsletter
   status: draft
   title: <title>
   slug: <slug>
   date: 2026-05-19
   created: 2026-05-19
   updated: 2026-05-19
   published: false
   excerpt: "<≤ 200 chars>"
   tags:
     - <topic tag>
   ---
   ```

3. **Write the body.** Non-negotiables:
   - **Authorial, not referential.** Honor the "Authorial stance" section at the top of this skill. The piece is the author's argument — sources are evidence and contrast, never the spine. If the user provided `--sources`, if Step 7 surfaced archive candidates, or if Step 8 verified external citations, treat all of them as raw material the author thinks *with*, not material the author explains. Never write "in this article, X argues…", "the piece by Y walks through…", "to summarize Z's framework…" as structural moves. Synthesize, take a position, and link the source inline as evidence for the author's claim.
   - **Apply `style-rules.md` in full**, not just the forbidden list. The whole file is the writing contract: voice principles, sentence patterns, one-line punches, opening/closing patterns, preferred expressions, contrast/forbidden, channel overrides. Every block is binding.
   - Anti-patterns declared in `channel-templates/{channel}.md` are also banned.
   - Use the opening technique from the outline. Recalibrate against the `## Few-shot examples` section of `voice-fingerprint.md` before writing the first sentence if you drifted.
   - Every categorical claim has a linked primary source (verified in Step 8).
   - Paragraph rhythm matches `voice-fingerprint.md` quant metrics (avg length, short-paragraph ratio).
   - Title uses the author's capitalization preference (declared in `style-rules.md`).
   - Inline links for citations. No "click here" — link the meaningful noun phrase.
   - **Output language**: the draft body is in `${OUTPUT_LANGUAGE}` resolved in Step 2.
   - **Archive integration** (only if Step 7 produced candidates):
     - For each candidate marked "link it" in Step 7, find the most natural place inside the piece where the candidate's topic surfaces and add exactly one inline link with the candidate's title (or a meaningful noun phrase) as the anchor text. Cap at 3 internal links per piece. Never force.
     - For each candidate marked "reusable snippet" in Step 7, weave it in with explicit attribution: link to the source if `url` is non-null; otherwise write a short inline mention ("covered earlier in '{title}'"). Never quote a snippet without attribution.

4. **Close with a references section.** The section title follows `${OUTPUT_LANGUAGE}` (e.g., `## Referências` in pt-BR, `## References and further reading` in en). Every link cited in the body is also listed at the bottom:

   ```markdown
   ## <localized references title>

   - [{source title}]({url}) — {one sentence on why it's relevant}
   ```

5. **Write the file.** Single `Write` call. The `style-validator` PostToolUse hook runs automatically.

## Step 9.5 — Mandatory inline self-audit

**Always runs.** Cannot be skipped. This is the cheap first line of
defense — same conversation, no sub-agent cost — and it is the reason
`--eval` defaults to `off`.

After writing the draft, re-read the file you just wrote and run an
**exhaustive** scan against the checklist below. Exhaustive means: for
each item, list **every** occurrence in the draft, not just the first
one. Do not stop at the first hit per rule. Do not delegate the count
to intuition.

### Checklist (high-risk hard rules)

For each item, count violations across the entire draft body
(excluding frontmatter and the references section):

1. **Pamphleteering inversions** — load
   `{workspace}/references/baseline-forbidden-{lang}.md` and grep the
   draft for every variant under the "Pamphleteering inversions" /
   "Inversões panfletárias" section. Also detect the generic structure
   even when wording differs: any micro-pattern of `not X[.,] {it is|é}
   Y` with parallelism. Treat each occurrence as one violation. Fix by
   asserting Y directly without the negation of X.

2. **Forbidden phrases (baseline)** — grep the draft against every
   bullet under `## Phrases` in
   `{workspace}/references/baseline-forbidden-{lang}.md`. Case-insensitive.

3. **Forbidden phrases (contrast)** — grep the draft against every
   bullet in the `CONTRAST_FORBIDDEN` / "Forbidden by contrast" block of
   `style-rules.md`.

4. **Author-specific forbidden** — same against the "Author-specific"
   block of `style-rules.md`.

5. **Channel anti-patterns** — same against the `## Anti-patterns` list
   of `channel-templates/{channel}.md`.

6. **Rhetorical questions as transitions** — flag any standalone question
   sentence ending in `?` that introduces the next paragraph instead of
   stating the claim directly. Allowed: questions that are part of the
   author's voice fingerprint signature openings/closings.

7. **Emoji policy** — if `style-rules.md` says "no emojis" / "sem
   emojis", count every emoji codepoint in the body. Each one is a
   violation.

8. **Lists vs prose** — if the style rules prefer prose, count list
   blocks. If `list_blocks / total_blocks > 0.40`, flag the longest
   list block for conversion to prose.

### Output of the self-audit

Produce an internal report (do NOT dump to chat) with this shape:

```
Self-audit:
- Pamphleteering inversions: {n} found
- Forbidden phrases (baseline): {n}
- Forbidden phrases (contrast): {n}
- Author-specific forbidden: {n}
- Channel anti-patterns: {n}
- Rhetorical-question transitions: {n}
- Emoji violations: {n}
- Lists vs prose: {ratio} (flagged: yes|no)
- Total violations: {sum}
```

### Fix

For each violation, apply one `Edit` to the draft file. Be surgical —
do not regenerate paragraphs unless the violation is structural (e.g.
list-to-prose conversion).

After fixing, re-run the checklist **once** to confirm zero residual
inversions and zero residual emoji/forbidden-phrase hits. If violations
remain after this second pass, do NOT loop further — record the
remaining count in the warnings for the Step 12 log (it will surface
as `STATUS: WARN`).

The self-audit pass counts go into the final log as
`Self-audit: {n} found, {n} fixed, {n} remaining`.

## Step 10 — Eval loop (opt-in)

If `--eval off` (the default): skip this step entirely. The mandatory
self-audit in Step 9.5 already ran. Proceed to Step 11.

Otherwise (`--eval on` or `--eval verbose`) invoke the `draft-evaluator`
agent via `Task` tool. Pass:

```
draft_path: {absolute path}
workspace_path: {absolute path}
channel: {channel}
output_language: {${OUTPUT_LANGUAGE}}
iteration: 1
previous_violations: []
```

Parse the agent's response.

### Auto-fix mode (`--eval on`)

Auto-fix loop:

1. **Verdict `pass`** → done, proceed to Step 11.
2. **Verdict `block`** → do NOT auto-fix. Record blocked violations in the final log. Proceed to Step 11 (the draft remains, but flagged for human review).
3. **Verdict `needs_revision`** → apply each violation's `Patch` via `Edit` (one Edit call per violation, in order). Do not regenerate. Then re-invoke the evaluator with `iteration: 2` and `previous_violations: [list of rule_ids from iter 1]`.
4. **Repeat up to 3 iterations.** Stop conditions:
   - Verdict becomes `pass` → done.
   - Verdict becomes `block` → done with warnings logged.
   - Iteration 3 still needs_revision → done with warnings logged ("3 iterations exhausted, {n} violations remain").
   - `Non-improvement detected: yes` → done with warnings logged ("eval-loop made no progress, stopped early").

5. **Hook alert handling.** If a `<style-validator-alert>` block appears in your context after any Edit/Write inside the loop, treat its violations as additional inputs to the next evaluator iteration (pass them as part of `previous_violations`). The hook is best-effort — the evaluator is authoritative.

### Verbose mode (`--eval verbose`)

After iteration 1, present the evaluator's full report to the user via plain text (not `AskUserQuestion`), then ask:

> "The evaluator flagged {n} violations (score: {score}/100, verdict: {verdict}). Apply all auto-patches, apply only some (tell me which Vn IDs), or skip?"

Apply selected patches via `Edit`. Re-invoke the evaluator if the user requests another pass. Do not auto-loop.

### Off mode (`--eval off`)
Skip evaluation entirely.

## Step 11 — Opinion extraction

If `--opinion-extract off`: skip.

Otherwise invoke the `opinion-extractor` agent via `Task` tool. Pass:

```
mode: single
source_paths: [{draft_path}]
workspace_path: {absolute path}
existing_opinion_map_path: {workspace}/references/opinion-map.md
output_language: {${OUTPUT_LANGUAGE}}
verbose: false
```

Parse the agent's response. The agent emits English headers (`## Hard core`, `## Forming positions`, `## Tensions and synergies between topics`, `## Neutral zones`, `## Refusals`) and content in `${OUTPUT_LANGUAGE}`. Confidence levels: `high`, `medium`, `discarded`.

### Silent mode

For each new position the agent proposes:

- **Confidence `medium`** → apply the `Apply patch` block to `opinion-map.md` via `Edit`. Append a Changelog entry (text in `${OUTPUT_LANGUAGE}`): e.g. `{YYYY-MM-DD}: {topic} — extracted automatically from draft {draft_path} (trigger: writer-create)`.
- **Confidence `high`** → the agent caps to `medium` in `single` mode (verify it did). Same apply.
- **`discarded`** → do not apply. Log silently.
- **Conflict reported** → do NOT apply. Record in the final log: `opinion-map conflict on {topic}: draft contradicts {section}. Review manually with /writer-opinion-mine.`
- **Tension/synergy reported** → apply to `## Tensions and synergies between topics` via `Edit`.

If the opinion-map uses PT headers (e.g., `## Sinergias e tensões entre temas`), apply the patch under whatever header the file currently uses. Do not rewrite the file structure.

If the opinion-map file does not exist, skip this step entirely and record: `opinion-map.md missing — extraction skipped. Run /writer-setup.`

### Verbose mode

Show the agent's report to the user (in `${OUTPUT_LANGUAGE}`), ask which proposed additions to apply, then `Edit` accordingly.

## Step 12 — Final log

Output a single compact log block. **Do not** dump draft content. The log MUST start with one of three explicit status markers so an automation parser can detect outcome without reading prose:

- `STATUS: OK` — draft written, eval passed (or skipped), opinion extraction applied.
- `STATUS: WARN` — draft written, but with non-blocking warnings (length out of range, opinion-map missing/scaffolded, eval-loop exhausted iterations on low-severity items, `Non-improvement detected: yes`, `archive-truncated`, `obsidian-cli-missing`, **self-audit violations remaining after one fix pass**, etc.).
- `STATUS: BLOCKED` — draft written but flagged by the evaluator with at least one `block`-class violation (opinion-map `## Hard core` conflict, `## Refusals` contradiction, length far off target, or any `Patch: none` high-severity item). **The draft remains on disk and must NOT be auto-published.**

The `STATUS:` line and its prefix must remain in English (it is the automation contract). The descriptive lines below it can be in `${OUTPUT_LANGUAGE}` if the user prefers, but the field labels (`Draft written`, `Title`, `Channel`, etc.) stay in English for parseability.

Format:

```
STATUS: {OK|WARN|BLOCKED}
✓ Draft written: {draft_path}
  Title: {title}
  Channel: {channel}
  Length: {n} words ({delta vs target})
  Self-audit: {n} found, {n} fixed, {n} remaining
  Eval: {verdict} (score {n}/100, {iterations} iteration(s), {fixes_applied} fixes applied) | skipped (--eval off)
  Opinion-map: {n} positions added, {n} conflicts flagged
  Archive: {N candidates, L linked, R repetition-flagged, S snippets reused} | disabled | no-match
  Warnings: {bulleted list, or "none"}
  Blocked violations (if STATUS=BLOCKED): {list each rule_id + one-line reason — these REQUIRE human review before save/publish}

Next: /writer-save to publish, or open the draft to review.
```

**Automation contract**: any pipeline that calls `/writer-create` must check the `STATUS:` prefix on the first line of the output. `BLOCKED` MUST short-circuit downstream `/writer-save` invocations until a human reviews. `WARN` is advisory — pipelines may proceed but should log the warnings.

In **interactive mode only**, after the log, ask via `AskUserQuestion` (prompts in `${OUTPUT_LANGUAGE}`):

> "Draft saved. Next step?"

Options:
- "Looks good — save to final destination" → tell the user: "Run `/writer-save {draft_path}` to move it to its final destination." Do **not** invoke `/writer-save` from inside this skill.
- "Let me read the draft first" → stop; remind them where it is.
- "Rewrite a specific part" → ask which part, apply surgical Edit.
- "Scrap and try a different angle" → confirm, delete draft, loop back to Step 6.

In **silent mode**, do NOT ask. The log is the final output.

## Failure handling

- Missing Tier 1 reference files (style-rules, voice-fingerprint, channel-templates/<channel>.md after Step 3 materialization): stop, route to `/writer-setup`.
- All sources for a claim come back from `avoid_sources` or unverifiable (browser + WebFetch both failed, user did not provide): drop the claim, record warning `source-unverifiable`.
- Disk write fails inside `{workspace_path}`: surface OS error.
- Disk write attempted outside `{workspace_path}`: refuse and log `workspace-boundary-violation`. This will become a `PreToolUse` hook in v0.7+.
- Channel template source file missing under `${CLAUDE_PLUGIN_ROOT}/...` (broken plugin install): see Step 3 fallback.
- Evaluator agent error: log the error, proceed to Step 11 (do not block on eval).
- Opinion-extractor agent error: log the error, do not block. Draft already exists on disk.

## Why this matters

Silent mode exists so this skill is safe inside automation pipelines: a cron, a hook, an external script can call `/writer-create "topic" --channel newsletter` and trust that the output is either a finished draft on disk or a clear error — never a stuck conversation waiting for input.
