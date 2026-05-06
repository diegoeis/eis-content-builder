---
name: writer-setup
description: Set up or upgrade the author's writer workspace - the folder that holds the author profile, voice fingerprint, style rules, content structures, sample sources, and drafts used by every other skill in this plugin. Use when the user says "set up my writing profile", "configure my writer workspace", "learn my tone and style", "update my writer setup", "meu perfil de escrita", or runs `/writer-setup`. Also trigger when another writer skill detects that the workspace config file is missing and asks the user to run setup first. Supports first-time setup (asks where to create the workspace, collects samples, delegates deep analysis to the voice-analyzer agent, generates all reference files) and update mode (detects existing workspace, offers to re-analyze samples or add new ones). Writes a plugin config file at `.claude/eis-content-builder.local.md` storing the chosen workspace path so subsequent sessions pick it up automatically.
argument-hint: "[optional path to writing samples]"
allowed-tools: Read, Write, Edit, Bash, Glob, AskUserQuestion, TodoWrite, WebFetch, Task
---synopsis
Create, upgrade, or repair the writer workspace. First-time: collects identity, samples, channels → runs voice-analyzer + opinion-extractor → writes all reference files. Update: re-analyzes samples or updates channels. Repair: recovers from missing or ephemeral workspace.
---

# Writer Setup

Build (or upgrade) the writer workspace. This skill is the **only** place where the workspace gets created or restructured. Every other skill reads from it.

## Invariant rules

Load and respect the invariants declared in the workspace `CLAUDE.md` once created. The most important ones:

- Never fabricate samples or metrics.
- Never write outside the workspace path the user chose.
- Plugin UI is always in English. The reference files themselves are authored in the user's language.

## Inputs

`$ARGUMENTS` may contain: a path to a samples folder, or a single sample file, or a URL. Use as first hint when collecting samples.

## Step 1 — Detect existing workspace

Check for `.claude/eis-content-builder.local.md` in the current working directory. If present, `Read` it to get `workspace_path`. Then check that `workspace_path` exists on disk and contains `CLAUDE.md` + `references/style-rules.md`.

**Ephemeral-path guard.** Before trusting the config, inspect `workspace_path`. If it starts with any of these segments, treat the config as STALE and route to branch C (repair), **without** offering to reuse the path:

- `/sessions/` (Claude Code sandbox sessions)
- `/mnt/` at the top level (sandbox mounts)
- `/tmp/`, `/private/tmp/`, `/var/folders/` (ephemeral OS locations)
- any path containing `/worktrees/` created by an agent (check via Bash `test -d`)

Warn the user: "Your config points to an ephemeral sandbox path (`{path}`) that no longer exists on disk. This happens when setup runs inside an isolated agent environment. Let's set it up again pointing to a real location."

Three branches:

- **No config file + no workspace** → branch A: **first-time setup**
- **Config file exists, workspace valid** → branch B: **update existing workspace**
- **Config file exists, workspace missing / corrupted / ephemeral** → branch C: **repair** (treat as first-time setup but warn the user, offer to reuse the same path ONLY if it is not ephemeral)

## Step 2A — First-time setup

1. **Ask where the workspace goes.** Use `AskUserQuestion`:

   > "Where should your writer workspace live? The workspace holds your author profile, voice fingerprint, style rules, sample sources, and drafts. Everything this plugin writes goes inside it."

   Options:
   - "Current folder (`./eis-content-writer-profile`)"
   - "Inside my Obsidian vault (I'll paste a path)"
   - "Custom path"

   If the user picks "Obsidian vault" or "Custom", collect the absolute path. Validate: path is absolute, parent directory exists. If invalid, re-ask once.

   **Ephemeral-path refusal.** Reject the path outright — do not fall through to "re-ask once", stop and explain — if it matches any of:
   - `/sessions/*` (Claude Code sandbox)
   - top-level `/mnt/*` (sandbox mount)
   - `/tmp/*`, `/private/tmp/*`, `/var/folders/*` (ephemeral OS locations)
   - contains `/worktrees/` and the worktree is temporary

   If the "Current folder" option resolves (via `pwd`) to one of the above, also refuse it. The workspace MUST live on durable user storage (typically under `$HOME`). Tell the user: "The path `{path}` is ephemeral — it won't survive this session. Please provide a path under your home directory or Obsidian vault."

2. **Confirm and create.** Show the final path. Ask a short yes/no confirmation. Then `Bash`: `mkdir -p "{workspace}/references" "{workspace}/sample-sources" "{workspace}/drafts"`.

   After `mkdir`, verify the directory resolves to a durable location: `Bash: realpath "{workspace}"` and re-check against the ephemeral-path list. If it resolves into an ephemeral location (symlink trap), abort and ask again.

3. **Write the plugin config file.** `Write` `.claude/eis-content-builder.local.md` with the full config schema (collected in Step 5 — write this file after collecting identity + channels + language, not before):

   ```yaml
   ---
   workspace_path: {absolute workspace path}
   initialized_at: {YYYY-MM-DD}
   version: 0.4.1

   channels:
     blog:
       url: "{blog url or empty}"
       cms: "{ghost | wordpress | obsidian | custom | none}"
       publish_via: "{api | manual}"
     linkedin:
       profile_url: "{url or empty}"
       posting_tool: "{manual | buffer | other}"
     newsletter:
       platform: "{substack | buttondown | beehiiv | other | none}"
       url: "{url or empty}"
     # Add or remove channels as the author publishes in new places.

   research_sources:
     trusted_blogs: []        # e.g. https://lennysnewsletter.com
     rss_feeds: []            # { url, tag }
     people_to_watch: []      # { name, platform, url }
     avoid_sources: []        # domains the author refuses to cite

   ideation:
     exclude_themes: []       # themes the author refuses to write about
     preferred_angles: []     # e.g. counterintuitive, data-driven, personal-experience
     default_channel: "{default channel}"

   language:
     default: "{pt-BR | en | es | etc.}"
     technical_terms_in: "{language kept for technical terms}"
   ---

   Plugin config for eis-content-builder. Tracks workspace location and all mutable settings.
   Gitignored by the plugin. Delete to force re-setup.
   ```

   Ensure `.claude/` exists first (`mkdir -p .claude`). Ensure it's gitignored locally.

4. **Copy the workspace CLAUDE.md template.** Read `${CLAUDE_PLUGIN_ROOT}/workspace-template/CLAUDE.md`. Substitute `{{AUTHOR_NAME}}` and `{{WORKSPACE_PATH}}` placeholders. Write the result to `{workspace}/CLAUDE.md`. The template no longer contains channel/language/research_sources blocks — those live in `.local.md`.

5. **Collect author identity + channels + language.** Ask in short rounds, not all at once. Use `AskUserQuestion` when choices are discrete; free-text otherwise.

   Round 1 — identity:
   - Name (if not obvious from workspace)
   - Role / title
   - Industry / domain
   - Years of experience
   - Main expertise areas (free text)
   - Primary audience

   Round 2 — channels (for each one the user mentions, capture URL + CMS + how they publish):
   - Blog?
   - LinkedIn?
   - Newsletter?
   - Any others (YouTube, Twitter/X, Substack, personal site)?

   Round 3 — language + preferences:
   - Default writing language
   - Technical terms kept in which language
   - Any exclude-themes (things they refuse to write about)
   - Preferred angles (counterintuitive, data-driven, personal-experience, etc.)

   Populate the `.claude/eis-content-builder.local.md` fields with these answers. Do NOT write channels/language/research_sources into `CLAUDE.md`.

6. **Collect writing samples.** Tell the user:

   > "Now I need 2–3 samples of your actual writing — the more varied, the better. Share them as file paths, pasted text, or URLs."

   For each sample:
   - If a file path → read it, copy cleaned content to `{workspace}/sample-sources/{slug}.md`.
   - If pasted text → save it directly to `{workspace}/sample-sources/sample-{n}.md` with a short header.
   - If a URL → `WebFetch` it, strip nav/boilerplate, save to `{workspace}/sample-sources/{slug}.md`.

   Minimum 2 samples. If fewer than 2, ask for more. Hard stop.

7. **Run deep analysis.** Spawn the `voice-analyzer` agent. Pass:
   - `sample_paths`: absolute paths to each file you saved in `sample-sources/`
   - `fingerprint_path`: `{workspace}/references/voice-fingerprint.md`
   - `examples_path`: `{workspace}/references/style-examples.md`
   - `sample_sources_dir`: `{workspace}/sample-sources`
   - `author_name`: from identity collection

   Wait for the agent to return. If it errors, surface the error and offer retry with more samples.

8. **Generate the remaining reference files.** After the agent returns:
   - `{workspace}/references/author-profile.md` — fill from the identity/expertise answers + any themes surfaced by the analyzer.
   - `{workspace}/references/style-rules.md` — fill from the analyzer's fingerprint (forbidden patterns, voice principles derived from metrics) + the user's explicit rules (emoji policy, list preference, etc.).
   - `{workspace}/references/content-structures.md` — one block per channel the user declared, pre-filled with reasonable defaults, flagged for the user to refine.
   - `{workspace}/references/save-preferences.md` — start as empty template. Tell the user they can populate it via `/writer-save --remember` as they save pieces.
   - `{workspace}/references/opinion-map.md` — copy the template as a scaffolded file. Keep section headers, replace `{{AUTHOR_NAME}}` with the user's name, remove all other `{{placeholder}}` tokens leaving the sections empty. Step 8b below will populate the sections from the samples — do not write positions manually here.

   Use the templates at `${CLAUDE_PLUGIN_ROOT}/workspace-template/references/*.md` as the shape.

8b. **Extract opinions from the samples.** Spawn the `opinion-extractor` agent in `bulk` mode. Pass:
   - `mode`: `bulk`
   - `source_paths`: absolute paths of every file in `{workspace}/sample-sources/`
   - `workspace_path`: `{workspace}`
   - `existing_opinion_map_path`: `{workspace}/references/opinion-map.md`
   - `verbose`: false

   When the agent returns:
   - For each `New positions` entry, apply the `Apply patch` block to `opinion-map.md` via `Edit` (insert into the named section after the named anchor). Append the corresponding line to `## Changelog` with trigger `writer-setup`.
   - For each `Promotions` entry, move the block between sections via `Edit` and append the changelog line.
   - For each `Tensions and synergies` entry, append to `## Sinergias e tensões entre temas`.
   - For each `Conflicts` entry: do nothing structurally, but append to the user-facing summary in step 9 so the author can resolve manually.

   If the agent errors, surface the error but do not block setup completion — leave the opinion-map as scaffolded.

9. **Show a summary, ask for corrections.** Summarize in 5–8 lines: workspace path, samples analyzed, key voice signatures extracted, channels configured. Ask:

   > "Anything in the profile I should adjust before we finish?"

   Handle at most one round of corrections (edit the relevant file inline). Do not loop.

10. **Close.** Tell the user:

    > "Workspace ready at `{workspace}`. You can now use `/writer-ideate` to brainstorm topics, `/writer-create` to write, `/writer-save` to save or publish, `/writer-calibrate` to refine my voice match, and `/writer-opinion-mine` to start mapping your opinions on the topics you write about — the opinion-map makes every future piece sharper because the plugin stops asking 'what's your take' and already knows."

## Step 2B — Update existing workspace

1. `Read` `{workspace}/CLAUDE.md`. Check the `Workspace version:` value vs plugin v0.4.1.

2. Ask the user what they want:

   - "Add new samples and re-run analysis"
   - "Update channels or language preferences"
   - "Upgrade workspace format (if version is older)"
   - "Start over" (treat as first-time setup but keep `sample-sources/`)

3. For each option, run only the relevant substeps from 2A. Do not rerun the whole flow.

4. When re-analyzing: pass all files in `sample-sources/` (existing + newly added) to the `voice-analyzer` agent. Overwrite `references/voice-fingerprint.md` and `references/style-examples.md`. Then re-run the `opinion-extractor` agent in `bulk` mode (same call shape as Step 8b in 2A). Apply only the patches whose extracted positions do not conflict with existing entries — surface conflicts to the user.

5. For upgrade: diff the template's `CLAUDE.md` against the workspace's. Add new top-level sections that are missing. Preserve user-authored values. If the workspace config has channels/research_sources/language in `CLAUDE.md` (v0.3 format), migrate those values into `.claude/eis-content-builder.local.md` and remove them from `CLAUDE.md`.

6. Update `version:` in `.claude/eis-content-builder.local.md`.

## Step 2C — Repair

Tell the user: "Your plugin config points to `{old_path}` but that folder doesn't exist. Do you want to create it fresh at that path, pick a new path, or skip repair?" Then proceed as 2A or 2B based on their answer.

## TodoWrite usage

Use `TodoWrite` for Step 2A items 5, 6, 7, 8 — those are the four heaviest chunks. Mark each done as you finish. Do not create todos for trivial single-call steps.

## Failure handling

- Missing absolute path → ask once more, then abort with a clear message.
- Fewer than 2 readable samples → abort before calling the analyzer.
- Analyzer returns error → surface verbatim, offer retry.
- Write permission denied on workspace path → tell the user the OS-level error, ask for a different path.
