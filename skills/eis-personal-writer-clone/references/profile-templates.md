# Profile Templates

These are the blank templates used during `/writer-setup` to generate the author's profile files.
Fill them with information extracted from writing samples and the author's answers.

---

## Template: author-profile.md

```markdown
# Author Profile — {Author Name}

## Professional Identity

- **Name**: {name}
- **Role/Title**: {what they do}
- **Industry**: {sector or domain}
- **Experience**: {years or background}
- **Publications / presence**: {blog, LinkedIn, newsletter, YouTube, etc.}

## Areas of Expertise

{List the main topics the author has deep knowledge about and writes from a position of authority}

## Primary Audience

{Who reads this author's content — their profession, level, interests}

## Recurring Themes

{The topics that come up again and again in the author's writing}

## Philosophy and Values

{What the author believes in — principles that shape how they think and write}

## Intellectual Influences

{Thinkers, authors, sources the author respects and cites}

## Trusted Sources

{Outlets, researchers, or publications the author considers reliable for data and reference}
```

---

## Template: style-rules.md

```markdown
# Style Rules — {Author Name}

## Voice Principles

{3–5 core principles that define this author's voice — e.g., "Direct: thesis first, no warm-up", "Data-anchored: every claim needs a source", "Casual-professional: accessible without dumbing down"}

## Sentence and Paragraph Patterns

{Describe the author's structural habits — short sentences vs. long, rhythm, use of one-sentence paragraphs, etc.}

## Opening Patterns

{How this author typically opens a piece — data, direct statement, question, real situation}

## Closing Patterns

{How this author typically ends — reflection, direction, question, synthesis}

## Preferred Expressions and Constructions

{Phrases that feel natural for this author — expressions they use, transitions they prefer}

## Forbidden Phrases and Patterns

{Things this author never says — clichés, filler phrases, constructions that feel fake or artificial}

## Capitalization and Title Rules

{How they capitalize titles, section headers}

## Language

{Primary language, use of technical terms, code-switching rules if applicable}

## Formatting Rules

- **Bold**: {how they use bold — sparingly, for keywords, for entire phrases, etc.}
- **Lists**: {when to use, when to avoid}
- **Links**: {inline vs. footnotes, how to cite}
- **Emojis**: {use or avoid}
- **Headers**: {frequency and depth}

## Channel-Specific Overrides

{Any rules that apply only to specific channels — e.g., "no markdown on LinkedIn", "plain prose only for Twitter"}

## Hard Rules (Never Break)

{Absolute constraints — things that are always true regardless of channel or format}
```

---

## Template: content-structures.md

```markdown
# Content Structures — {Author Name}

Channel-by-channel format guidelines. Add or remove channels based on where the author publishes.

---

## {Channel Name} (e.g., Blog / Personal Site)

**Target length**: {word count range}

### Opening
{How to open — what works, what doesn't}

### Thesis
{Where and how the central argument appears}

### Development
{How arguments build — structure, use of examples and data}

### Closing
{How to end — what to avoid, what works}

### Metadata
{Required frontmatter or metadata fields}

### Formatting
{Specific markdown or formatting rules for this channel}

---

## {Channel Name} (e.g., LinkedIn)

{Same sections as above, adapted for this channel}

---

## {Channel Name} (e.g., Newsletter)

{Same sections as above}

---

## {Channel Name} (e.g., Twitter/X — Threads)

{Thread-specific structure}

---

## {Channel Name} (e.g., YouTube / Video Scripts)

{Script format, block structure, spoken language conventions}
```

---

## Template: save-preferences.md

```markdown
# Save Preferences

Rules that map content types, channels, or tags to specific save destinations and
frontmatter templates. Loaded automatically by the `/save` command.

Add a new rule for each combination you want to handle differently.
Use `*` as a wildcard when a field shouldn't be used for matching.

---

## Rule: {short descriptive name, e.g. "Blog articles"}

**Applies to**:
- type: {article | post | newsletter | script | thread | *}
- channel: {blog | linkedin | newsletter | twitter | youtube | *}
- tags: [{tag1}, {tag2}] *(optional — match any content with these tags)*

**Directory**: `{path/relative/to/workspace}/`
*(e.g., `writing/articles/` or `posts/blog/`)*

**Filename pattern**: `{YYYY-MM-DD}-{slugified-title}.md`
*(Available tokens: `{YYYY}`, `{MM}`, `{DD}`, `{slugified-title}`, `{type}`, `{channel}`)*

**Frontmatter additions**:
```yaml
# Fields added or overridden in the saved file's frontmatter.
# These merge with the piece's existing frontmatter — they don't replace it.
# Example:
database: "[[writings.base]]"
status: draft
```

*Added: {YYYY-MM-DD}*

---

## Rule: {another rule name}

**Applies to**:
- type: *
- channel: linkedin
- tags: []

**Directory**: `social/linkedin/`

**Filename pattern**: `{YYYY-MM-DD}-{slugified-title}.md`

**Frontmatter additions**:
```yaml
type: post
platform: linkedin
```

*Added: {YYYY-MM-DD}*

---
```

---

## Template: style-examples.md

```markdown
# Style Examples — {Author Name}

Annotated examples from the author's actual writing. Use these to calibrate tone and voice.
Add examples from writing samples provided during setup.

---

## Openings

### ✅ Works — this is the author's voice

> {Quote from their writing}

**Why it works**: {Brief explanation — what makes this feel authentic}

### ❌ Doesn't work — too generic / artificial

> {Example of a similar topic written poorly}

**Why it fails**: {What's wrong — cliché, too much setup, fake urgency, etc.}

---

## Thesis delivery

### ✅ Works

> {Quote}

**Why it works**: {Explanation}

### ❌ Doesn't work

> {Counter-example}

**Why it fails**: {Explanation}

---

## Transitions and flow

### ✅ Works

> {Quote showing natural transition between ideas}

### ❌ Doesn't work

> {Example of clunky transitions — "Another important point is...", "Moving on..."}

---

## Closings

### ✅ Works

> {Quote from an actual closing}

**Why it works**: {Explanation}

### ❌ Doesn't work

> {Generic closing example}

**Why it fails**: {Explanation}

---

## Tone — Channel-specific examples

### {Channel} example

> {Full short piece or significant excerpt}

**Notes**: {What to observe about tone, structure, formatting}
```
