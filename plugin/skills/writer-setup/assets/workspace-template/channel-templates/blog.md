# Template: Blog post

Default structure for full-length articles published on the author's blog.
Adjust target length, structure, and anti-patterns based on the author's
actual blog posts (the `profile-inferencer` agent tunes these from samples
during setup; tune manually afterwards as needed).

## Target

- **Length**: 800–1500 words (adjust to the author's typical post)
- **Format**: Markdown with H2/H3 sections
- **Reading time**: 4–8 min

## Structure

- **Opening**: 1–2 paragraphs. Lead with the claim, a concrete observation,
  or a data point. Avoid setup/ramps.
- **Thesis**: stated explicitly in the first third of the piece.
- **Development**: 3–5 sections, each with a clear sub-claim and evidence
  (data, example, or argument).
- **Closing**: synthesis, direction, or contrast with the opening. Avoid
  "what do you think? let me know in the comments."

## Frontmatter (YAML, required at top of file)

```yaml
title: <title>
slug: <slug>
date: <YYYY-MM-DD>
tags: []
status: draft
excerpt: <one-sentence max 180 chars summary>
type: article
channel: blog
```

## Anti-patterns

- Setup sentences before reaching the point.
- Rhetorical questions as transitions.
- "In today's fast-paced world" / "no fim do dia, tudo se resume a" type openings.
- Emojis (unless `style-rules.md` allows).
- Heavy list usage when prose would do.

## Formatting rules

- Bold only for key terms or claims, not for emphasis on every other sentence.
- Inline links over footnotes.
- One H1 max (the title; usually rendered from frontmatter, not in body).
- Code blocks for technical content; quote blocks for citations.
