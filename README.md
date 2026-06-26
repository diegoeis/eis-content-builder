# eis-content-builder

A Claude Code / Cowork plugin that works as a personal writing assistant: it learns your voice from real pieces you've written and produces content indistinguishable from your own — for blog, LinkedIn, newsletter, scripts, or any channel.

## The problem it solves

LLMs write well, but they write generic. The output reads like AI and not like you. This plugin fixes that by building a local **writer workspace** with a voice fingerprint, style rules, an author profile, and an opinion map. Every piece is written through that context, and the plugin gets sharper as it learns from your corrections.

Concretely, it addresses:

- **Generic AI voice** — formulaic sentences, neutral tone, no authorial fingerprint.
- **Opinion flattening** — LLMs hedge by default; your real positions, refusals, and tensions get washed out.
- **Cold-start every time** — no memory of how you write, what you've already said, or what you refuse to claim.
- **No learning loop** — when you rewrite the output, the next draft makes the same mistakes.
- **Lost research** — sources, transcripts, and notes you'd want to ground a piece in stay disconnected from the writing.
- **Manual cross-channel adaptation** — the same idea has to be reshaped by hand for blog, LinkedIn, newsletter, etc.

## Example use cases

- `/writer-create write about this topic. search in this podcast transcript folder to enrich the content with quotes and references.`
- `/writer-ideate I've been reading a lot about agent memory lately — help me find an angle I haven't taken yet, cross-referencing my opinion-map so I don't repeat myself.`
- `/writer-calibrate here's my rewrite of yesterday's draft — learn from the diff and update the style rules so the next piece doesn't make the same mistakes.`

## How to use

1. Install the plugin (Claude Desktop, Cowork, or Claude Code).
2. Open the folder where you want to manage your writing (e.g. your Obsidian vault).
3. Run `/writer-setup` — pick where the workspace lives, share 2–3 writing samples and public links (blog, LinkedIn), and wait for the voice analysis.
4. Then: `/writer-ideate` to find a topic, or `/writer-create <topic>` to start writing.

Skills also respond to natural language ("write a post about X", "I'm out of ideas").

## Skills

| Skill | What it does |
|---|---|
| `/writer-setup` | Builds the workspace from scratch: voice analysis, profile inference, opinion extraction, article-archive detection. Runs once. |
| `/writer-ideate` | Topic brainstorm — open mode (web research over your trusted sources) or Socratic discussion of a specific topic. Hands off an angle; never writes the piece. |
| `/writer-create` | Writes the piece in your voice and saves it to `drafts/` with full frontmatter. Mandatory self-audit; stronger evaluation via `--eval on`. Silent by default; `--interactive` to ask and propose an outline. |
| `/writer-save` | Moves a draft to its final destination (folder, CMS, scheduled slot), applying saved rules. `--remember` records new rules. |
| `/writer-calibrate` | Learns from your corrections — diffs your rewrite against the draft and updates `style-rules.md` / `style-examples.md`. Never touches `voice-fingerprint.md`. |
| `/writer-opinion-mine` | Socratic interview to map positions, refusals, and tensions per topic in `opinion-map.md`. One topic per session, ~15 min. |
| `/writer-index` | Creates or refreshes the index of your published-article archive (`eis-article-index.json`), via Obsidian CLI or folder scan. |

## Sub-agents

Invoked by skills — never directly by the user:

- `voice-analyzer` — produces the voice fingerprint from samples.
- `profile-inferencer` — infers author identity from public links.
- `opinion-extractor` — extracts explicit opinions from your texts.
- `content-scout` — web research for ideation.
- `draft-evaluator` — audits drafts and proposes surgical patches.
- `archive-detector` — LLM fallback for detecting the article-archive schema.

The deterministic script `scripts/detect-archive-schema.py` runs first in `/writer-setup` to detect the YAML schema of your article archive; `archive-detector` is the fallback.

## Repository structure

```
plugin/   ← the plugin (skills, agents, scripts) + full technical README
docs/     ← plugin PRD
```

Full documentation — workspace layout, voice hierarchy, discovery, config, external dependencies, version history — in [plugin/README.md](plugin/README.md).
