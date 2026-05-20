# Writer Workspace — {{AUTHOR_NAME}}

This file is the operational contract for the `eis-content-builder` plugin.
Any Claude Code / Cowork session that opens this workspace loads this file
automatically. Every skill in the plugin reads from this workspace and
writes back to it.

> **Synopsis.** Operational contract for this writer workspace. Declares
> reference file hierarchy, invariants, opinion-map degrade protocol, and
> the language policy. Read this first before reading any reference file.

---

## Workspace structure

```
{{WORKSPACE_PATH}}/
├── CLAUDE.md                              ← this file
├── .claude/
│   └── eis-content-builder.local.json     ← canonical config (channels, archive, language, etc.)
├── references/
│   ├── voice-fingerprint.md               ← quantitative metrics + few-shot examples (voice-analyzer)
│   ├── style-rules.md                     ← author-declared voice rules (highest authority)
│   ├── author-profile.md                  ← identity + mini-bio + expertise + audience
│   └── opinion-map.md                     ← author's recorded positions (writer-opinion-mine)
├── channel-templates/                     ← one file per channel (blog, linkedin, newsletter, ...)
├── sample-sources/                        ← original samples that trained the profile
├── drafts/                                ← pieces produced by /writer-create
└── eis-article-index.json                 ← (optional) index of the author's article archive
```

---

## Voice reference hierarchy

When writing, load these three files in this order of precedence:

1. **`references/style-rules.md`** — highest authority. Declared intent:
   rules the author consciously chose. Always wins in a conflict.
2. **`references/voice-fingerprint.md`** — measured patterns from real
   samples (quantitative metrics) + verbatim few-shot examples extracted
   from the samples. Subordinate to rules — it describes habits and
   provides concrete reference, not aspirations.
3. **`references/author-profile.md`** — identity, expertise, audience.
   Tells *who* is writing and *for whom*, not *how*.

**Conflict rule:** if `style-rules.md` prohibits something that
`voice-fingerprint.md` shows as a common pattern, follow `style-rules.md`.

`channel-templates/<channel>.md` is loaded only when writing for that
specific channel. It defines output shape (length, formatting, anti-patterns),
not voice.

**Configuration** (channels, research_sources, article_archive, save_preferences,
ideation, language) lives in `.claude/eis-content-builder.local.json`. Read
configuration from there, not from CLAUDE.md.

---

## Invariant rules (apply to every skill in this plugin)

1. **Never fabricate data, statistics, quotes, or case studies.** When a claim
   needs data, search for a primary source with `WebSearch` / `WebFetch` and
   link it inline. If no reliable source exists, do not make the claim.
2. **Voice hierarchy is authoritative.** Follow the three-file hierarchy
   above. Re-read all three when in doubt — `style-rules.md` first.
3. **Language follows the user.** Write in the language the user is
   interacting in. Default declared in `language.default` of the local config.
   Exception: `opinion-map.md` is always in Portuguese (the headings and
   structure use Portuguese terms — `Núcleo duro`, `Posições em formação`,
   etc.). The author's positions inside it may be in any language.
4. **Plugin UI is always in English.** All skill prompts, agent prompts,
   and error messages produced by this plugin remain in English regardless
   of the author's language. The *content* the plugin writes follows the
   author's language. Reference files (style-rules, author-profile,
   voice-fingerprint) are authored in the user's language.
5. **No emojis in final content** unless the user's `style-rules.md`
   explicitly allows them.
6. **Never save drafts before the user validates.** Show the piece first.
   Save to `drafts/` only after explicit approval — or write directly to
   `drafts/` when the user asked for that from the start.
7. **Surgical edits.** When the user asks to change one thing, change only
   that thing. Do not regenerate the whole piece.
8. **Efficiency matters.** Prefer writing to `drafts/` over dumping long
   content into chat. Chat cost for this workspace owner is a real constraint.
9. **Inline frontmatter.** Every piece saved to `drafts/` must have complete
   YAML frontmatter (see the appropriate `channel-templates/<channel>.md`).
10. **`sample-sources/` is input only, never read at runtime.** The
    `voice-analyzer` agent consumes it to produce `voice-fingerprint.md`.
    Other skills should never read `sample-sources/` directly — read the
    fingerprint instead.

---

## Discovery protocol (for every skill in the plugin)

Skills locate this workspace via a two-level cascade:

1. **Local discovery.** Skill checks if `cwd` is inside a workspace by
   looking for `.claude/eis-content-builder.local.json` in `cwd` or any
   parent (walk-up to `/`). First hit wins.
2. **Pointer fallback.** If no local config is found, read
   `$HOME/.claude/eis-content-builder.pointer.json` →
   extract `workspace_path` → load that workspace's
   `.claude/eis-content-builder.local.json`.
3. **Ask the user.** If neither works (pointer missing or pointing to a
   non-existent path), prompt the user for the workspace path.

When `workspace_path` from the pointer no longer exists on disk, suggest
running `/writer-setup` in repair mode.

---

## Opinion-map degrade protocol

`references/opinion-map.md` is read by `writer-ideate`, `writer-create`,
`writer-calibrate`, and the `style-validator` hook. When it is missing,
empty, or unparseable, every consuming skill MUST follow this single
protocol — do not invent local fallbacks.

1. **Treat the file as advisory, not required.** No skill aborts when
   opinion-map is missing or malformed. Proceed with the rest of the workflow.
2. **Record the degrade in the final log/output.** Use one of these literal
   markers in the warnings section so automation can detect it:
   - `opinion-map-missing` — file does not exist.
   - `opinion-map-empty` — file exists but every section is the scaffolded
     placeholder.
   - `opinion-map-corrupt` — file exists but failed to parse (broken
     markdown headings, etc.).
3. **Suggest the repair path once.** Tell the user (or include in the log):
   `Run /writer-opinion-mine to populate, or /writer-setup update mode to
   rescan samples and re-run opinion-extractor.`
4. **Never auto-create or auto-rewrite the file from a consuming skill.**
   Only `writer-setup` and `writer-opinion-mine` may create or restructure
   `opinion-map.md`. Other skills only `Edit` to append entries when the
   file already has a valid section structure.
5. **Conflict resolution is never silent.** When a consuming skill detects
   that draft content contradicts a Núcleo duro position, it must surface
   the conflict in its log and refuse to auto-apply a patch.
   `writer-opinion-mine` is the only skill allowed to rewrite Núcleo duro
   entries.

---

## Workspace metadata

- Created: `{{CREATED_DATE}}`.

The plugin version that created this workspace is recorded in
`.claude/eis-content-builder.local.json`.
