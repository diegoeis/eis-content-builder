# Template: LinkedIn post

Default structure for LinkedIn posts. LinkedIn truncates at ~210 characters
on feed display — the hook must land in the first 1–2 lines.

## Target

- **Length**: 800–1300 characters (LinkedIn hard limit: 3000)
- **Format**: plain text. No Markdown. Line breaks separate paragraphs.
- **Hashtags**: 3–5 at the end, lowercase

## Structure

- **Hook (lines 1–2)**: a claim, a number, or a counterintuitive observation.
  Must stand alone — most readers see only this before "see more".
- **Development (3–6 short paragraphs)**: one idea per paragraph.
  1–3 sentences each. Whitespace between paragraphs is the formatting tool.
- **Closing**: a single sentence that lands the thesis or asks one specific
  question (not "thoughts?").
- **Hashtags**: at the end, on a single line.

## Frontmatter (internal, not published)

```yaml
title: <internal title for the draft>
slug: <slug>
date: <YYYY-MM-DD>
status: draft
type: linkedin-post
channel: linkedin
hashtags: []
```

## Anti-patterns

- Markdown syntax (`**bold**`, headers, lists).
- Bullet points as primary structure (LinkedIn renders them poorly).
- More than 1–2 emojis.
- "Engagement bait" closings ("agree?", "thoughts?", "what would you do?").
- More than 5 hashtags.

## Formatting rules

- Plain text only. Use UPPERCASE sparingly for emphasis where you'd use bold.
- Whitespace is the formatting tool — short paragraphs, line breaks between them.
- Numbers and specifics over adjectives.
