# eis-content-builder

A personal writing assistant that learns your voice and produces content indistinguishable from your own — across blog, LinkedIn, newsletter, scripts, and any channel you write for.

The plugin builds a **writer workspace** on your machine (you pick where it lives — inside your Obsidian vault, a dedicated folder, anywhere). That workspace holds your author profile, voice fingerprint, style rules, opinion map, sample sources, channel templates, and drafts. Every skill reads from it. Every skill writes back to it.

---

## Skills

| Skill | Purpose |
|---|---|
| `/writer-setup` | Build the workspace from scratch. Asks where it goes, collects samples and identity links, optionally registers a folder of your already-written articles (auto-detects YAML schema), runs deep voice analysis via the `voice-analyzer` agent, infers identity via `profile-inferencer`, extracts opinions via `opinion-extractor`. v0.6.0 is first-time only; update and repair land in a later version. |
| `/writer-ideate` | Brainstorm topics (open mode) or discuss a specific topic (Socratic mode). Delegates web research to the `content-scout` agent. |
| `/writer-create` | Write a piece in your voice. Loads style-rules, voice-fingerprint, author-profile, opinion-map, and the channel template for the requested channel. Consults your article archive for internal links / repetition checks / reusable snippets. Saves to `drafts/` with complete frontmatter. |
| `/writer-save` | Move a draft from `drafts/` to its final destination. Applies saved save-preferences (stored in the local config); records new ones on demand (`--remember`). |
| `/writer-calibrate` | Refine voice rules from your corrections. Accepts a diff (plugin draft vs your rewrite) or free-text description. Updates `style-rules.md` (and re-runs `voice-analyzer` for full rescans when you ask explicitly). Flags position shifts for `/writer-opinion-mine`. |
| `/writer-opinion-mine` | Map the author's opinions on the topics they write. Socratic interview in batches of 3–5 questions. Writes to `references/opinion-map.md` — loaded by `writer-ideate` and `writer-create` so the plugin knows where the author stands, where they're still calibrating, and what they refuse to opine on. |
| `/writer-index` | Build or refresh the plugin's article index (`eis-article-index.json`) at the workspace root. Two source modes: query an Obsidian `.base` file (when the user has one and the Obsidian CLI is on PATH) or scan `article_archive.path` parsing YAML frontmatter (default fallback, no external dependencies). After writing, auto-wires `article_archive.index_file.path` in `.local.json`. |

## Agents

| Agent | Purpose |
|---|---|
| `voice-analyzer` | Deep analysis of writing samples → produces `voice-fingerprint.md` (quantitative metrics + verbatim few-shot examples) AND prescriptive content blocks the setup pastes into `style-rules.md`. Invoked by `writer-setup` and `writer-calibrate`. |
| `profile-inferencer` | Infers the author's identity (name, role, company, industry, audience, mini-bio, themes) from public links and writing samples. Uses browser tool first (Claude in Chrome, Playwright) when available, WebFetch as fallback. Writes `author-profile.md`. Invoked by `writer-setup`. |
| `archive-detector` | LLM fallback for `detect-archive-schema.py`. Detects the YAML frontmatter schema of the author's article archive when the Python script can't run. Invoked by `writer-setup` only when the script fails. |
| `content-scout` | Web research for ideation. Filters by your trusted sources, respects avoid lists, returns a compact 1.2–2KB brief. Invoked by `writer-ideate`. |
| `draft-evaluator` | Audits a draft against `style-rules.md`, `voice-fingerprint.md`, and `opinion-map.md` across multiple dimensions. Returns surgical old→new patches and a pass/needs_revision/block verdict. Read-only. Invoked by `writer-create`. |
| `opinion-extractor` | Extracts explicit opinions from writing samples and proposes structured additions to `opinion-map.md`. Two modes: `bulk` (full corpus) and `single` (one draft). Read-only. Invoked by `writer-setup`, `writer-create`, and `writer-calibrate`. |

## Scripts

| Script | Purpose |
|---|---|
| `scripts/detect-archive-schema.py` | Deterministic detector for the YAML frontmatter schema of an article archive. No external dependencies (stdlib only). Invoked by `/writer-setup` Step 2.2; falls back to the `archive-detector` agent if the script errors. |

---

> **Note on invocation:** skills in this plugin are user-invocable — they show up as `/eis-content-builder:writer-setup`, `/eis-content-builder:writer-create`, etc. Throughout this README and the skill prompts, the shorthand `/writer-setup` is used for readability. Natural language works too ("set up my writing profile", "write a blog post about X") — the skills have trigger descriptions that catch those.

## Workflow

```
/writer-setup          (once — picks workspace path, analyzes samples, infers profile)
        ↓
/writer-ideate         (optional — when you don't have a topic)
        ↓
/writer-create topic   (writes to drafts/ with mandatory self-audit; materializes channel template lazily on first use of each channel)
        ↓
/writer-save           (moves draft to its final location)
        ↓
/writer-calibrate      (when output wasn't quite your voice — learn from your fix)
        ↓
/writer-opinion-mine   (to map or sharpen your positions over time)
```

---

## Workspace structure

After `/writer-setup`, the path you chose contains:

```
<your-workspace>/
├── CLAUDE.md                              ← operational rules + voice hierarchy + protocols
├── .claude/
│   └── eis-content-builder.local.json     ← canonical config (channels, archive, research, save_preferences, language, ideation)
├── references/
│   ├── voice-fingerprint.md               ← quantitative metrics + few-shot examples (one consolidated file)
│   ├── author-profile.md                  ← identity, mini-bio, expertise, audience, themes
│   ├── style-rules.md                     ← highest authority for voice (wins over fingerprint)
│   ├── opinion-map.md                     ← author's recorded positions
│   └── baseline-forbidden-<lang>.md       ← language-specific list of forbidden phrases
├── channel-templates/                     ← one file per channel, materialized lazily by /writer-create
├── sample-sources/                        ← original samples that trained the profile
├── drafts/                                ← pieces written by the plugin
└── eis-article-index.json                 ← (optional) index of the author's article archive

$HOME/.claude/
└── eis-content-builder.pointer.json       ← discovery anchor when skills run outside the workspace folder
```

The workspace has its own `CLAUDE.md` — any Claude Code / Cowork session opening that folder picks it up automatically. That means the invariants (never fabricate data, voice hierarchy, etc.) apply even outside this plugin's skills.

### Voice reference hierarchy

When writing, the plugin loads three files in this order of precedence:

1. `references/style-rules.md` — declared intent, always wins in a conflict.
2. `references/voice-fingerprint.md` — measured patterns from real samples (quantitative metrics) plus verbatim few-shot examples extracted from the corpus. Subordinate to rules — it describes habits and provides concrete reference, not aspirations.
3. `references/author-profile.md` — identity, expertise, audience. Tells *who* is writing and *for whom*, not *how*.

`channel-templates/<channel>.md` is loaded only when writing for that specific channel. It defines output shape (length, formatting, anti-patterns), not voice.

### Discovery

Every skill in the plugin locates the workspace via a two-level cascade:

1. **Local discovery.** Skill checks if `cwd` is inside a workspace by looking for `.claude/eis-content-builder.local.json` in `cwd` or any parent (walk-up to `/`). First hit wins.
2. **Pointer fallback.** If no local config is found, read `$HOME/.claude/eis-content-builder.pointer.json` → extract `workspace_path` → load that workspace's `.claude/eis-content-builder.local.json`.

If neither works (pointer missing or pointing to a non-existent path), the skill prompts the user to run `/writer-setup`.

---

## Plugin config

On first setup, the plugin writes `.claude/eis-content-builder.local.json` inside the workspace and `$HOME/.claude/eis-content-builder.pointer.json` for discovery. The local file is the single source of truth for all mutable settings:

```json
{
  "workspace_path": "/absolute/path/to/your/workspace",
  "initialized_at": "YYYY-MM-DD",
  "version": "0.6.0",

  "author": {
    "first_name": "diego",
    "full_name": "Diego Eis"
  },

  "language": {
    "default": "pt-BR",
    "technical_terms_in": "en"
  },

  "channels": {
    "blog": {
      "url": "https://yoursite.com",
      "cms": "ghost",
      "publish_via": "manual",
      "has_template": true,
      "materialized": false,
      "template_customizations": null
    },
    "newsletter": {
      "shares_url_with": "blog",
      "platform": "ghost",
      "has_template": true,
      "materialized": false,
      "template_customizations": null
    },
    "linkedin": {
      "profile_url": "https://linkedin.com/in/you",
      "posting_tool": "manual",
      "has_template": true,
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
    "enabled": false,
    "path": "",
    "file_pattern": "**/*.md",
    "toolchain": "generic",
    "schema": {
      "title_property": null,
      "tags_property": null,
      "status_property": null,
      "published_values": [],
      "date_property": null,
      "url_property": null,
      "excerpt_property": null
    },
    "index_file": { "path": null, "format": null }
  },

  "save_preferences": [],

  "ideation": {
    "exclude_themes": [],
    "preferred_angles": [],
    "default_channel": "blog"
  }
}
```

This file is gitignored by the plugin. Delete it (and the pointer) to force re-setup. Edit it directly to update channels, research preferences, or save rules — no need to re-run `/writer-setup`.

### Lazy channel-template materialization

Channel templates (`blog.md`, `newsletter.md`, `linkedin.md`, `twitter.md`) are **not** created during setup. `/writer-create` materializes a channel's template on its first use of that channel: it reads the source template from the plugin, applies any `template_customizations` recorded in the config (proposed by `profile-inferencer` during setup), and writes the customized version to `{workspace}/channel-templates/<channel>.md`. Subsequent runs use the materialized file directly.

This means setup is faster, and users only pay materialization cost for channels they actually write for.

---

## External dependencies

Most skills require no external tools — only Claude-native tools and filesystem access. Browser-tool MCPs (Claude in Chrome, Playwright) are used opportunistically by `profile-inferencer` when available, but the plugin works without them (falls back to WebFetch).

| Skill / agent | External dependency |
|---|---|
| `/writer-setup` (archive detection) | Python 3 on `$PATH` for `scripts/detect-archive-schema.py`. If Python is missing, falls back to the `archive-detector` LLM agent. |
| `/writer-index` (Mode A only) | **Obsidian CLI** — must be on `$PATH` when sourcing from an Obsidian `.base` file. Ships with Obsidian Desktop. If the CLI is missing, the skill silently falls back to Mode B (folder scan + YAML parsing), which has no external dependencies. |
| `profile-inferencer` (best path for social URLs) | A browser-tool MCP (Claude in Chrome, Playwright). Optional — used when present, falls back to WebFetch when absent. WebFetch tends to fail on LinkedIn / Twitter / Instagram / Facebook / TikTok / Threads. |

---

## Getting started

1. Install the plugin.
2. Open a folder in Claude Code or Cowork (recommended: your Obsidian vault, or any folder where you want to manage your writing).
3. Run `/writer-setup`.
   - Pick where the workspace lives.
   - Share 1–3 identity links (blog, newsletter, LinkedIn, etc.) and 2–3 writing samples (file paths, pasted text, or URLs).
   - Optionally point the plugin at a folder of articles you've already written — Obsidian is auto-detected, schema is inferred.
   - Wait for the agents to finish (voice analysis, profile inference, opinion extraction in parallel).
   - Confirm or correct the inferred profile.
4. Run `/writer-ideate` to brainstorm or `/writer-create <topic>` to start writing.

---

## Why drafts live in files, not in chat

Every piece `/writer-create` produces is written to `drafts/`. The plugin shows you the path and a short preview — never the full body. This is deliberate: dumping long content into chat is expensive in tokens, and you'd rather read the draft in your editor anyway. When you want edits, point to the draft; the plugin patches it with surgical `Edit` calls.

---

## Language

The skill prose and agent prompts in this plugin are in English (for portability across Claude Code / Cowork). The text the user reads in the UI — questions, error messages, confirmation screens — and the substantive content written to reference files follows the user's language (detected from the conversation, refined by sample analysis). Section headings, field labels, and metric keys inside reference files stay English because they are part of the contract between agents and skills.

---

## Version history

- `0.6.0` — Major refactor of `/writer-setup`. New architecture:
  - Setup reduced from 10 steps + 6 sub-rounds to 4 macro steps with one concentrated input form and one confirmation screen.
  - Reference files consolidated from 7 to 4: `voice-fingerprint.md` now includes the few-shot examples section; `content-structures.md` was replaced by the `channel-templates/` folder; `save-preferences.md` moved into the local config.
  - Config switched from YAML (`.local.md`) to JSON (`.local.json`).
  - Discovery cascade simplified from 4 levels to 2 (local walk-up → pointer fallback).
  - Channel templates are lazy-materialized by `/writer-create` on first use of each channel.
  - New agents: `profile-inferencer` (identity inference with browser-tool support), `archive-detector` (LLM fallback for the Python script).
  - New deterministic script: `scripts/detect-archive-schema.py`.
  - LinkedIn and social URLs now attempt fetching via browser-tool MCP (Claude in Chrome, Playwright) when available, fall back to WebFetch.
  - Headers in `opinion-map.md` migrated from PT to EN (part of the agent ↔ skill contract); content inside follows the user's language.
  - Opinion-extractor runs in setup as a third parallel agent — first `/writer-create` has populated opinion-map from the start.
- `0.5.0` — Article archive support: `/writer-setup` Round 4 + Step 5b ask whether the author maintains a folder of past pieces, auto-detect the YAML frontmatter schema (leaving any field the author does not have as `null`), and persist to a new `article_archive` block in `.local.md`. Obsidian is auto-detected via a `.obsidian/` walk-up — no question asked. `/writer-create` consults the archive for internal-link candidates, repetition risk, and reusable snippets. `/writer-index` was reworked as the plugin's index builder.
- `0.4.1` — Quality improvements: synopsis blocks added to all skills and agents for progressive disclosure; style-validator hook fast-exit path made explicit; `writer-ideate` agent invocation unified to `Task` tool; `writer-create` interactive mode no longer invokes `/writer-save` directly.
- `0.4.0` — `voice-fingerprint.md` moved to `references/`; explicit voice hierarchy (style-rules > style-examples > fingerprint); all mutable config moved from `CLAUDE.md` into `.claude/eis-content-builder.local.md`; `/writer-index` skill for Obsidian article index.
- `0.3.0` — Workspace made portable (lives anywhere); `voice-fingerprint.md` with quantitative metrics; `voice-analyzer` + `content-scout` agents; `/writer-ideate` + `/writer-calibrate` skills; style-validator hook; commands consolidated into skills.
- `0.2.0` — Author profile system; generic commands; Ghost integration planned.
- `0.1.0` — Initial personal version.
</content>
</invoke>