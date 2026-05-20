# Opinion Map — {{AUTHOR_NAME}}

Map of the author's opinions. Loaded by `writer-ideate`, `writer-create`,
and `writer-calibrate`.

**Not a personality profile.** It's the operational record of:
- What the author thinks about the topics they write on (convictions,
  positions still forming, neutral zones)
- Where the opinions talk to each other or clash
- How the author reads the authorities of the field
- What the author refuses to opine on

Updated by the `/writer-opinion-mine` skill (Socratic interview), by
`/writer-calibrate` (when a correction signals a position shift), or
manually by the author.

> **Localization note.** Section headings, field labels, and template
> instructions are in English (they form part of the contract with the
> `opinion-extractor` agent and the consuming skills). The *content*
> filled into the placeholders below should be written in the author's
> language (`language.default` in `.claude/eis-content-builder.local.json`).
> Mixing is expected: English structure, author-language substance.

---

## Hard core (high-confidence convictions)

Topics where the opinion is firm and has already been publicly defended.
These feed the thesis directly.

Format per item:
- **Position**: one affirmative sentence, active voice, no hedging.
- **Evidence in corpus**: links to articles/posts where the position
  appears (when known).
- **Who disagrees**: public authorities who hold the opposite view.
- **My counter-argument**: one sentence answering the strongest critique
  of the position.
- **Confidence**: high.

### {{TOPIC_1}}

- **Position**: {{POSITION_1}}
- **Evidence in corpus**: {{EVIDENCE_1}}
- **Who disagrees**: {{OPPOSITION_1}}
- **Counter-argument**: {{COUNTER_1}}
- **Confidence**: high

---

## Forming positions (medium confidence, subject to revision)

Topics where there is a leaning but the author is still calibrating.
The plugin should signal in the outline that the position is
provisional.

Format per item:
- **Current position**: affirmative sentence.
- **What would change my mind**: concrete condition (data, observation,
  experience).
- **Confidence**: medium.

### {{FORMING_TOPIC_1}}

- **Current position**: {{FORMING_POSITION_1}}
- **What would change my mind**: {{FORMING_REVISE_1}}
- **Confidence**: medium

---

## Neutral zones (no firm opinion)

Topics the author writes or thinks about but does not want to sound
opinionated on yet. The plugin should avoid inventing a position —
prefer description, analysis, or open question when these topics appear.

- {{NEUTRAL_1}}
- {{NEUTRAL_2}}

---

## Refusals (explicit non-positions)

Granular. Complements `exclude_themes` in the local config.

- {{REFUSAL_1}}
- {{REFUSAL_2}}

---

## Tensions and synergies between topics

Where opinions talk to each other or clash. Useful for article
proposals that articulate two topics.

- **{{TOPIC_A}}** ↔ **{{TOPIC_B}}**: {{RELATION}}
  - Resolution (if any): {{RESOLUTION}}

---

## Reference authorities (how the author reads each one)

How the author cites each public figure in the field. Prevents the
plugin from treating every authority with the same deference.

| Authority | How the author reads | Where they agree | Where they disagree |
|---|---|---|---|
| {{AUTHORITY_1}} | {{READ_1}} | {{AGREE_1}} | {{DISAGREE_1}} |

---

## Operator profile (Graham-minimal, only what helps the writing)

Three fields — not a full Graham.

- **Infinite game the author plays (and that guides what they write)**: {{GAME}}
- **Writing elephant (what triggers a post, what irritates enough to publish)**: {{ELEPHANT}}
- **Strength → shadow in writing (how strength becomes weakness under pressure)**: {{STRENGTH_SHADOW}}

---

## Changelog

Records position shifts over time. Each entry: date, topic, change in
one line, trigger.

- {{DATE}}: {{TOPIC}} — {{CHANGE}} (trigger: {{TRIGGER}})
