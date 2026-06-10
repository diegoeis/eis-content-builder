# Template: Newsletter issue

Default structure for newsletter editions. Tune to the author's typical
edition length and rhythm.

## Target

- **Length**: 600–1200 words (typical newsletter sweet spot)
- **Format**: Markdown; minimal headers; one clear thesis per issue
- **Reading time**: 3–6 min

## Structure

- **Subject line**: 6–10 words. Concrete, specific, no clickbait. Should
  preview the issue's claim, not tease it.
- **Opening hook**: 1 short paragraph that frames why this issue exists today.
- **Body**: single thesis developed in 3–5 short sections. Direct prose;
  no listicles unless the author's voice favors them.
- **Closing**: one actionable takeaway or open question that ties back to
  the opening.
- **PS / footer**: optional. Used sparingly for related links, archive
  pointer, or author mini-bio (see `author-profile.md`).

## Frontmatter

```yaml
title: <title>
slug: <slug>
date: <YYYY-MM-DD>
tags: []
status: draft
excerpt: <one-sentence max 180 chars summary>
type: article
channel: newsletter
```

## Anti-patterns

- Multiple unrelated topics in one issue.
- Over-formatted with too many headers/lists.
- "Hey friends" / "Olá pessoal" type openings unless the author actually
  writes that way.
- Emojis as section dividers.

## Formatting rules

- Bold only for terms being defined or quoted phrases.
- Inline links — never raw URLs.
- Short paragraphs (2–4 sentences); newsletters read on mobile.
