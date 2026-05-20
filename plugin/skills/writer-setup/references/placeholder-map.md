# Placeholder → Source map for `style-rules.md`

Loaded by Step 2.7 of the parent `SKILL.md`. After `voice-analyzer` returns,
generate `style-rules.md` once using the template at
`${CLAUDE_PLUGIN_ROOT}/skills/writer-setup/assets/workspace-template/references/style-rules.md` and
substitute placeholders according to this table.

The `voice-analyzer` agent returns a section `## Style-rules content blocks`
at the end of its response, containing pre-formatted markdown blocks named
exactly after the placeholders below (`VOICE_PRINCIPLES`, `SENTENCE_PATTERNS`,
etc). For those placeholders, copy the agent's block verbatim — do not
re-summarize, do not strip examples, do not rewrite metrics.

| Placeholder                  | Source                                                                                |
|------------------------------|---------------------------------------------------------------------------------------|
| `{{AUTHOR_NAME}}`            | full name from `profile-inferencer` (or first_name)                                   |
| `{{VOICE_PRINCIPLES}}`       | voice-analyzer `VOICE_PRINCIPLES` block (prescriptive: rule + metric + example each)  |
| `{{SENTENCE_PATTERNS}}`      | voice-analyzer `SENTENCE_PATTERNS` block (paragraph + sentence metrics, prescriptive) |
| `{{ONE_LINE_PUNCHES}}`       | voice-analyzer `ONE_LINE_PUNCHES` block (3-5 verbatim short-paragraph sentences)      |
| `{{OPENING_PATTERNS}}`       | voice-analyzer `OPENING_PATTERNS` block (named techniques + verbatim + when to use)   |
| `{{CLOSING_PATTERNS}}`       | voice-analyzer `CLOSING_PATTERNS` block (same shape as openings)                      |
| `{{PREFERRED_EXPRESSIONS}}`  | voice-analyzer `PREFERRED_EXPRESSIONS` block (grouped by function, not flat list)     |
| `{{CONTRAST_FORBIDDEN}}`     | voice-analyzer `CONTRAST_FORBIDDEN` block (avoided clichés + jargon + constructions)  |
| `{{FORBIDDEN_USER}}`         | literal `_(empty — populated by /writer-calibrate over time)_`                        |
| `{{CAPITALIZATION}}`         | static default: "Headings in sentence case unless the author's samples consistently use title case (analyzer's `headers_per_1k_words` and casing patterns inform this)" |
| `{{PRIMARY_LANGUAGE}}`       | `language.default` from config (determined in 2.8)                                    |
| `{{TECH_LANGUAGE}}`          | `language.technical_terms_in` from config                                             |
| `{{CODE_SWITCH}}`            | static default: "Technical terms keep their source language unless an established translation exists" |
| `{{BOLD_RULE}}`              | static default: "Bold only for key terms or claims, not for emphasis on every other sentence" |
| `{{LISTS_RULE}}`             | static default: "Prefer prose. Use lists only when items are genuinely parallel and short" |
| `{{LINKS_RULE}}`             | static default: "Inline Markdown links. Avoid raw URLs in body text"                  |
| `{{EMOJIS_RULE}}`            | static default: "No emojis in final content. Override only if the author explicitly opts in" |
| `{{HEADERS_RULE}}`           | static default: "H2 and H3 only. Sentence case. No H1 in body — title belongs in frontmatter" |
| `{{CHANNEL_OVERRIDES}}`      | voice-analyzer `CHANNEL_OVERRIDES` block (per declared channel: length + opening + closing + tactic) |
| `{{HARD_RULES}}`             | the workspace `CLAUDE.md` invariants 1, 2, 7 (do not duplicate text; reference them)  |

If a metric from `voice-analyzer` is `n/a`, the corresponding placeholder
gets `n/a` plus a one-line reason — do not invent.

## Hard rule for the skill

The `CONTRAST_FORBIDDEN` block MUST be non-empty at setup time. If the
agent returns an empty block, retry once asking for the contrast list
explicitly (this is a known regression risk — the old v0.5 plugin had a
populated list and the new one must keep parity). If it still returns
empty on retry, surface a warning to the user and proceed.

**Language note.** The static-default English strings above are the
*source text*. When writing the file, the setup translates each
substantive value to `${OUTPUT_LANGUAGE}` (the language the user is
interacting in, refined by the analyzer's `language_detected` if
different). Keys, headings, and labels in the template stay English.
Example: with `output_language = "pt-BR"`, `{{BOLD_RULE}}` becomes
*"Negrito apenas para termos-chave ou afirmações, não para ênfase a
cada outra frase"* rather than the English source above.

Voice-analyzer's content blocks (`VOICE_PRINCIPLES`, etc.) are already
in `${OUTPUT_LANGUAGE}` because the agent received the same input — the
skill copies them verbatim, no further translation.
