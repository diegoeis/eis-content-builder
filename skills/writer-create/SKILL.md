---
name: writer-create
description: Write a piece of content in the author's voice, grounded in their profile, voice fingerprint, style rules, content structures and recorded opinions. Use when the user says "write an article about", "create a LinkedIn post", "draft a newsletter", "escreve um post sobre", "quero um ensaio sobre", or runs `/writer-create`. Default mode is silent - suitable for automation. Loads full workspace context, researches sources, writes to `drafts/` with complete YAML frontmatter, runs the `draft-evaluator` agent in a fix loop (max 3 iterations), then updates `references/opinion-map.md` via `opinion-extractor`. With `--interactive`, asks clarifying questions and proposes outlines. Never writes draft content into chat - always saves to `drafts/`.
argument-hint: "<topic> [--channel newsletter|blog|linkedin|twitter|youtube|script] [--thesis \"...\"] [--length N] [--sources url1,url2] [--interactive] [--eval silent|verbose|off] [--opinion-extract on|off]"
allowed-tools: Read, Write, Edit, Bash, Glob, AskUserQuestion, WebSearch, WebFetch, TodoWrite, Task
---synopsis
Write a piece in the author's voice. Silent by default (zero questions, auto eval-loop, saves to `drafts/`). Add `--interactive` for outline approval and step-by-step control. Outputs `STATUS: OK|WARN|BLOCKED` on the first line for automation pipelines.
---

# Writer Create

Produce content indistinguishable from the author's own writing. The piece lives in `drafts/`, not in chat.

This skill has **two modes**:

- **Silent / non-interactive (default)**: zero questions, zero outline approvals, eval-loop auto-applies fixes, opinion-extractor runs automatically. Designed to be safe to run from a cron, hook, or external automation.
- **Interactive (`--interactive`)**: asks for missing inputs, proposes outline for approval, surfaces eval violations for user decision.

## Defaults (silent mode)

| Argument | Default |
|---|---|
| `--channel` | `newsletter` |
| `--eval` | `silent` (auto-fix loop, max 3 iterations) |
| `--opinion-extract` | `on` |
| `--interactive` | off |

## Invariant rules

Inherit from `{workspace}/CLAUDE.md`. Critical ones for this skill:

- Never fabricate data, statistics, quotes, or case studies.
- Every factual claim links to a verifiable primary source.
- Write in the user's conversation language (unless they ask otherwise).
- Never dump the full piece into chat. Save to `drafts/`, show the path, log a short summary.
- Surgical edits only when the user asks for changes. Do not regenerate.

## Step 1 — Parse arguments

Parse `$ARGUMENTS`. Treat the first non-flag token (and any trailing free text up to the first flag) as the **topic**.

- `--channel <c>` → channel. Default: `newsletter`.
- `--thesis "..."` → user-supplied thesis. If absent, you derive one in Step 4 from opinion-map (Núcleo duro) or the topic itself.
- `--length N` → word target override. If absent, use channel default from `content-structures.md`.
- `--sources url1,url2` → seed sources. Reuse first; supplement with WebSearch as needed.
- `--interactive` → enables the interactive mode. Without it, silent mode is active.
- `--eval silent|verbose|off` → default `silent`. `verbose` surfaces violations to user. `off` skips evaluation.
- `--opinion-extract on|off` → default `on`. Skips opinion-extractor when `off`.

**Topic missing AND silent mode → fail fast.** Output: `error: --writer-create requires a <topic>. Pass it as the first argument or run with --interactive.` Stop. Do not proceed.

**Topic missing AND interactive mode → ask once via `AskUserQuestion`.**

## Step 2 — Load workspace

1. `Read` `.claude/eis-content-builder.local.md`. Missing → silent mode: output `error: workspace not configured. Run /writer-setup first.` and stop. Interactive: same message but as a friendly prompt.
2. Extract `workspace_path`. **Validate before using it:**
   - `Bash: test -d "{workspace_path}" && test -f "{workspace_path}/CLAUDE.md"` — if either fails, stop with `error: workspace at {workspace_path} is missing or incomplete. Run /writer-setup to repair.`
   - Reject ephemeral roots (`/sessions/`, top-level `/mnt/`, `/tmp/`, `/private/tmp/`, `/var/folders/`) even if they exist right now. Same stop + repair message.
3. `Read` all reference files in parallel (one message, multiple Read calls):
   - `{workspace}/CLAUDE.md`
   - `{workspace}/references/voice-fingerprint.md`
   - `{workspace}/references/author-profile.md`
   - `{workspace}/references/style-rules.md`
   - `{workspace}/references/content-structures.md`
   - `{workspace}/references/style-examples.md`
   - `{workspace}/references/opinion-map.md` (if absent, proceed without it but record in the final log: `opinion-map missing — thesis derived from topic only`)

   Any **required** file missing (first 6) → silent mode: emit `error: required file {path} missing. Run /writer-setup update mode.` and stop. Interactive: same message as a prompt.

## Step 3 — Cross-reference opinion-map

Scan `opinion-map.md` for the topic. Apply these decisions:

- **Topic in `## Núcleo duro`** → use the recorded position as thesis; embed the recorded counter-argument inside the piece.
- **Topic in `## Posições em formação`** → use the recorded position but apply hedging from author's register. Record in final log: `thesis based on forming position — review before publishing`.
- **Topic in `## Zonas neutras`** → propose analytical/descriptive framing. Do not fabricate a position. Record in final log: `topic is neutral — piece is descriptive, not opinionated`.
- **Topic in `## Não-posições`** →
  - Silent mode: stop. Output `error: topic "{topic}" is in opinion-map.md ## Não-posições. Refusing to write. Remove the refusal first or pick another topic.` Do not write anything.
  - Interactive mode: ask user before proceeding.
- **Topic appears in `## Sinergias e tensões`** → record as a candidate angle in your internal outline.

## Step 4 — Build internal outline

Always build an outline. In **silent mode** the outline is internal — you proceed directly to writing. In **interactive mode** present it via `AskUserQuestion` and wait for approval (skip the approval step for short-form: LinkedIn, tweets, posts ≤ 250 words).

The outline captures:

- **Working title** (using the author's capitalization preference from style-rules.md)
- **Channel** + **target length** (from `content-structures.md`)
- **Central thesis** (one sentence — from opinion-map if Núcleo, from `--thesis` arg if passed, otherwise inferred from topic)
- **Opening technique** (pick one from `voice-fingerprint.md` signature openings)
- **Development beats** (3–5 numbered, each: claim + data/example, no repetition)
- **Closing technique** (pick one from `voice-fingerprint.md` signature closings)
- **Sources needed** (claims that require verification)
- **Excerpt** (≤200 chars for frontmatter)

For multi-beat pieces (blog + newsletter + script combos, or pieces with ≥4 beats), use `TodoWrite` to track each beat. Skip for short-form.

## Step 5 — Research

For each `Sources needed` item plus any categorical or numeric claim you're about to make:

1. Reuse `--sources` if provided.
2. `WebSearch` for primary sources. Prefer `research_sources.trusted_blogs` from `.claude/eis-content-builder.local.md`.
3. `WebFetch` top candidates to confirm the claim is actually in the source.
4. Reject any hit from `avoid_sources` (in `.claude/eis-content-builder.local.md`).
5. If no reliable source exists for a claim → drop the claim. No "studies suggest" hedging.

Batch in parallel where independent.

## Step 6 — Write the draft

1. **Compute the draft path.** Filename preserves sentence case of the working title exactly as it will appear as H1 — do not slugify, do not lowercase, do not replace spaces with hyphens. Sanitize only filesystem-illegal chars (`/`, `:`, `?`, `*`, `<`, `>`, `|`, `\`, leading/trailing whitespace, trailing periods). Keep spaces, accents, capitalization.

   Path: `{workspace}/drafts/{YYYY-MM-DD} - {Title in sentence case}.md`.

   Example: title `Como criar cultura e estruturar uma área de produtos` → file `2026-04-18 - Como criar cultura e estruturar uma área de produtos.md`.

   If the file already exists: silent mode appends `-v2`, `-v3`, etc until a free name is found; interactive mode asks.

2. **Assemble frontmatter.** Pull required fields from `content-structures.md` for this channel. Base fields always present:

   ```yaml
   ---
   type: {article | post | newsletter | script | thread}
   channel: {blog | linkedin | newsletter | twitter | youtube}
   status: draft
   created: {YYYY-MM-DD}
   updated: {YYYY-MM-DD}
   published: false
   excerpt: "{≤ 200 chars}"
   tags:
     - {topic tag}
     - {...}
   ---
   ```

3. **Write the body.** Non-negotiables:
   - Use the opening technique from the outline. Recalibrate against `style-examples.md` before writing the first sentence if you drifted.
   - Every forbidden phrase from `style-rules.md` is banned.
   - Every categorical claim has a linked primary source.
   - Paragraph rhythm matches `voice-fingerprint.md` quant metrics (avg length, short-paragraph ratio).
   - Lists only when content is genuinely enumerable. Prose otherwise if style-rules says so.
   - Title uses the author's capitalization preference.
   - Inline links for citations. No "click here" — link the meaningful noun phrase.

4. **Close with a references section.** Every link cited in the body is also listed at the bottom:

   ```markdown
   ## References and further reading

   - [{source title}]({url}) — {one sentence on why it's relevant}
   ```

5. **Write the file.** Single `Write` call. The `style-validator` PostToolUse hook runs automatically.

## Step 7 — Eval loop

If `--eval off`: skip this step entirely.

Otherwise invoke the `draft-evaluator` agent via `Task` tool. Pass:

```
draft_path: {absolute path}
workspace_path: {absolute path}
channel: {channel}
iteration: 1
previous_violations: []
```

Parse the agent's response.

### Silent mode (`--eval silent`, default)

Auto-fix loop:

1. **Verdict `pass`** → done, proceed to Step 8.
2. **Verdict `block`** → do NOT auto-fix. Record blocked violations in the final log. Proceed to Step 8 (the draft remains, but flagged for human review).
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

## Step 8 — Opinion extraction

If `--opinion-extract off`: skip.

Otherwise invoke the `opinion-extractor` agent via `Task` tool. Pass:

```
mode: single
source_paths: [{draft_path}]
workspace_path: {absolute path}
existing_opinion_map_path: {workspace}/references/opinion-map.md
verbose: false
```

Parse the agent's response.

### Silent mode

For each new position the agent proposes:

- **Confidence média** → apply the `Apply patch` block to `opinion-map.md` via `Edit`. Append a Changelog entry: `{YYYY-MM-DD}: {topic} — extraído automaticamente do draft {draft_path} (gatilho: writer-create)`.
- **Confidence alta** → cap to média when the agent comes from `single` mode (the agent already enforces this, but verify). Same apply.
- **Conflict reported** → do NOT apply. Record in the final log: `opinion-map conflict on {topic}: draft contradicts {section}. Review manually with /writer-opinion-mine.`
- **Tension/synergy reported** → apply to `## Sinergias e tensões entre temas` via `Edit`.

If the opinion-map file does not exist, skip this step entirely and record: `opinion-map.md missing — extraction skipped. Run /writer-setup.`

### Verbose mode

Show the agent's report to the user, ask which proposed additions to apply, then `Edit` accordingly.

## Step 9 — Final log

Output a single compact log block. **Do not** dump draft content. The log MUST start with one of three explicit status markers so an automation parser can detect outcome without reading prose:

- `STATUS: OK` — draft written, eval passed (or skipped), opinion extraction applied.
- `STATUS: WARN` — draft written, but with non-blocking warnings (length out of range, opinion-map missing, eval-loop exhausted iterations on low-severity items, `Non-improvement detected: yes`, etc.).
- `STATUS: BLOCKED` — draft written but flagged by the evaluator with at least one `block`-class violation (opinion-map Núcleo conflict, Não-posições contradiction, length far off target, or any `Patch: none` high-severity item). **The draft remains on disk and must NOT be auto-published.**

Format:

```
STATUS: {OK|WARN|BLOCKED}
✓ Draft written: {draft_path}
  Title: {title}
  Channel: {channel}
  Length: {n} words ({delta vs target})
  Eval: {verdict} (score {n}/100, {iterations} iteration(s), {fixes_applied} fixes applied)
  Opinion-map: {n} positions added, {n} conflicts flagged
  Warnings: {bulleted list, or "none"}
  Blocked violations (if STATUS=BLOCKED): {list each rule_id + one-line reason — these REQUIRE human review before save/publish}

Next: /writer-save to publish, or open the draft to review.
```

**Automation contract**: any pipeline that calls `/writer-create` must check the `STATUS:` prefix on the first line of the output. `BLOCKED` MUST short-circuit downstream `/writer-save` invocations until a human reviews. `WARN` is advisory — pipelines may proceed but should log the warnings.

In **interactive mode only**, after the log, ask via `AskUserQuestion`:

> "Draft saved. Next step?"

Options:
- "Looks good — save to final destination" → tell the user: "Run `/writer-save {draft_path}` to move it to its final destination." Do **not** invoke `/writer-save` from inside this skill.
- "Let me read the draft first" → stop; remind them where it is.
- "Rewrite a specific part" → ask which part, apply surgical Edit.
- "Scrap and try a different angle" → confirm, delete draft, loop back to Step 4.

In **silent mode**, do NOT ask. The log is the final output.

## Failure handling

- Missing reference files: stop, route to `/writer-setup`.
- All sources for a claim come back from `avoid_sources` or unverifiable: drop the claim, record warning.
- Disk write fails: surface OS error.
- Evaluator agent error: log the error, proceed to Step 8 (do not block on eval).
- Opinion-extractor agent error: log the error, do not block.

## Why this matters

Silent mode exists so this skill is safe inside automation pipelines: a cron, a hook, an external script can call `/writer-create "topic" --channel newsletter` and trust that the output is either a finished draft on disk or a clear error — never a stuck conversation waiting for input.
