# eis-content-builder

A Claude Code / Cowork plugin that works as a personal writing assistant: it learns your voice from real pieces you've written and produces content indistinguishable from your own — for blog, LinkedIn, newsletter, scripts, and any other channel you write for.

## The problem it solves

LLMs write well, but they write generic. The output reads like AI: formulaic sentences, neutral opinions, no trace of the author. This plugin fixes that by building a **writer workspace** on your machine — with a voice fingerprint (quantitative metrics + verbatim examples from your texts), style rules, an author profile, and a map of your opinions. Every piece is written through that context, and the plugin improves over time by learning from your corrections.

## How to use

1. Install the plugin via Claude Desktop. It works in both Cowork and Claude Code.
2. Open a folder (e.g. your Obsidian vault, or wherever you want to manage your writing).
3. Run `/writer-setup` — pick where the workspace lives, share 2–3 writing samples and identity links (blog, LinkedIn), and wait for the voice analysis to finish.
4. From there: `/writer-ideate` to find a topic, or `/writer-create <topic>` to start writing.

Skills also respond to natural language ("write a post about X", "I'm out of ideas").

## Skills

| Skill | What it does |
|---|---|
| `/writer-setup` | Builds the workspace from scratch: voice analysis, profile inference, opinion extraction, article-archive detection. Runs once. |
| `/writer-ideate` | Topic brainstorming (open mode, with web research over your trusted sources) or Socratic discussion of a specific topic. |
| `/writer-create` | Writes the piece in your voice and saves it to `drafts/` with complete frontmatter. Mandatory self-audit; stronger evaluation opt-in via `--eval on`. |
| `/writer-save` | Moves a draft to its final destination (folder, CMS, scheduled slot), applying saved rules (`--remember` records new ones). |
| `/writer-calibrate` | Learns from your corrections — compares your rewrite against the draft and updates the style rules. |
| `/writer-opinion-mine` | Socratic interview to map your positions, refusals, and tensions per topic (`opinion-map.md`). |
| `/writer-index` | Creates/refreshes the index of your article archive (`eis-article-index.json`), via the Obsidian CLI or a folder scan. |

## Agents (internal sub-agents)

`voice-analyzer` (voice fingerprint), `profile-inferencer` (identity from public links), `opinion-extractor` (explicit opinions in your texts), `content-scout` (web research for ideation), `draft-evaluator` (draft audit with surgical patches), `archive-detector` (LLM fallback for archive schema detection). They are invoked by the skills — never directly by the user.

There is also the deterministic script `scripts/detect-archive-schema.py`, used by `/writer-setup` to detect the YAML schema of your article archive.

## Repository structure

```
plugin/          ← the plugin itself (skills, agents, scripts) + full technical README
docs/            ← plugin PRD
```

The full documentation — workspace layout, voice hierarchy, discovery, config, external dependencies, and version history — lives in [plugin/README.md](plugin/README.md).
