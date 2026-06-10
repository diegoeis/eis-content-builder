# Style Rules — {{AUTHOR_NAME}}

Authoritative voice rules. Loaded by every writer skill. Highest authority
in the voice hierarchy — wins over `voice-fingerprint.md` in any conflict.
Updated by `/writer-calibrate` (pointwise) or `/writer-setup` (rescan).

<!--
PLACEHOLDER → SOURCE MAP (used by writer-setup when populating this file):

| Placeholder                  | Source                                          |
|------------------------------|-------------------------------------------------|
| {{AUTHOR_NAME}}              | identity round (full name)                       |
| {{VOICE_PRINCIPLES}}         | voice-analyzer — prescriptive principles with example each |
| {{SENTENCE_PATTERNS}}        | voice-analyzer (sentence + paragraph metrics, prescriptive form) |
| {{ONE_LINE_PUNCHES}}         | voice-analyzer — verbatim 3-8 word standalone sentences from corpus |
| {{OPENING_PATTERNS}}         | voice-analyzer (3-5 named techniques + verbatim openings + when to use) |
| {{CLOSING_PATTERNS}}         | voice-analyzer (3-5 named techniques + verbatim closings) |
| {{PREFERRED_EXPRESSIONS}}    | voice-analyzer — grouped by function (causal, opinion, attention, conversational) |
| {{CONTRAST_FORBIDDEN}}       | voice-analyzer — forbidden-by-contrast list: clichés the author avoids + specific imported jargon |
| {{FORBIDDEN_USER}}           | initially empty placeholder; populated by /writer-calibrate over time |
| {{CAPITALIZATION}}           | static default (sentence case in headings)       |
| {{PRIMARY_LANGUAGE}}         | language.default in .local.json                  |
| {{TECH_LANGUAGE}}            | language.technical_terms_in in .local.json       |
| {{CODE_SWITCH}}              | static default (technical terms keep source lang)|
| {{BOLD_RULE}}                | static default (key terms only, not emphasis)    |
| {{LISTS_RULE}}               | static default (prose over lists by default)     |
| {{LINKS_RULE}}               | static default (inline, never raw URLs)          |
| {{EMOJIS_RULE}}              | static default (none unless author opts in)      |
| {{HEADERS_RULE}}             | static default (H2/H3 only, sentence case)       |
| {{CHANNEL_OVERRIDES}}        | voice-analyzer — per declared channel: length range + opening rule + closing rule + 1-2 channel-specific tactics |
| {{HARD_RULES}}               | static default + any explicit author rules       |

Rules for the writer-setup when populating placeholders:
- All substantive prose follows `${OUTPUT_LANGUAGE}`.
- Section headings, field labels, metric keys stay English regardless.
- Every voice principle MUST be prescriptive (rule + supporting metric +
  verbatim example), not just a metric formatted as prose.
- The CONTRAST_FORBIDDEN section MUST be populated at setup time — never
  leave as placeholder. The author can add more via /writer-calibrate.
- If a metric is `n/a`, the corresponding placeholder includes `n/a`
  plus one-line reason — never invent.
-->

## Voice Principles

{{VOICE_PRINCIPLES}}

## Sentence and Paragraph Patterns

{{SENTENCE_PATTERNS}}

## Signature one-line punches

The author drops standalone short sentences (3-8 words) as paragraph-of-its-own
after a longer argument. These are a marker of the author's rhythm —
preserve them when writing in this voice. Verbatim examples from the corpus:

{{ONE_LINE_PUNCHES}}

## Opening Patterns

{{OPENING_PATTERNS}}

## Closing Patterns

{{CLOSING_PATTERNS}}

## Preferred Expressions and Constructions

{{PREFERRED_EXPRESSIONS}}

## Forbidden Phrases and Patterns

### Baseline (always forbidden, language-specific)

The baseline list is loaded from a sibling file based on
`language.default` in `.claude/eis-content-builder.local.json`:

- pt-BR → see `references/baseline-forbidden-pt-BR.md`
- en → see `references/baseline-forbidden-en.md`
- other → no baseline file yet (contribute one if needed)

These patterns read as generic LLM output, coach-speak, or empty
corporate framing in the target language. Skills that consume voice
(`/writer-create`, `/writer-calibrate`) load the
correct baseline file together with this one.

### Forbidden by contrast (detected from corpus)

Phrases and constructions the author actively avoids — populated by
`voice-analyzer` during setup based on what *would fit the author's topic
but never appears* in the samples, plus jargon imported from external
sources that the author refused to use as-is.

{{CONTRAST_FORBIDDEN}}

### Author-specific (added by `/writer-calibrate`)

Phrases the author rejected during calibration sessions. Starts empty.

{{FORBIDDEN_USER}}

## Capitalization and Title Rules

{{CAPITALIZATION}}

## Language

- Primary: {{PRIMARY_LANGUAGE}}
- Technical terms kept in: {{TECH_LANGUAGE}}
- Code-switching rules: {{CODE_SWITCH}}

## Formatting Rules

- **Bold**: {{BOLD_RULE}}
- **Lists**: {{LISTS_RULE}}
- **Links**: {{LINKS_RULE}}
- **Emojis**: {{EMOJIS_RULE}}
- **Headers**: {{HEADERS_RULE}}

## Channel-Specific Overrides

Per-channel prescription — what changes about the voice when writing for
this channel. Goes beyond the channel-template (which describes shape
and length); this is the *voice tuning* per channel.

{{CHANNEL_OVERRIDES}}

## Hard Rules (Never Break)

> **No duplication.** Hard Rules listadas aqui são apenas regras
> autorais específicas deste autor — NÃO repetir patterns universais
> que já estejam em `baseline-forbidden-{lang}.md` nem itens de
> `CONTRAST_FORBIDDEN` acima. Cada regra mora em um único lugar.
>
> Em particular, **inversões panfletárias ("Não é X. É Y.")** moram
> exclusivamente em `baseline-forbidden-{lang}.md` na seção
> "Inversões panfletárias / Pamphleteering inversions". Não recriar
> aqui.

Todas as regras do `baseline-forbidden-{lang}.md` valem como Hard
Rules automaticamente — não precisam ser repetidas abaixo.

{{HARD_RULES}}
