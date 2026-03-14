---
description: Write content in your voice
allowed-tools: Read, Write, Bash, TodoWrite, AskUserQuestion, WebSearch, WebFetch
argument-hint:
  - '["topic" --channel linkedin|blog|newsletter|twitter|script]'
---

# /write — Create Content in Your Voice

Invoke using Skill tool the `eis-personal-writer-clone` skill to write content using the saved author profile.

## What this command does

Produces written content in the author's voice, calibrated to the specified channel and format.
Uses the profile saved in `$content-memory/references/` as the authoritative
guide for voice, tone, and structure.

## Steps to follow

**Step 1 — Load the author profile**

Check for `$content-memory/references/author-profile.md`.

If not found: "You don't have a writing profile yet. Run `/writer-setup` first so I can learn your voice."
Stop here.

If found: Load all four files into context before doing anything else:
- `author-profile.md`
- `style-rules.md`
- `content-structures.md`
- `style-examples.md`

**Step 2 — Understand the request**

Extract from the user's input:
- **Topic**: what the piece is about
- **Channel**: where it will be published (blog, LinkedIn, newsletter, Twitter/X thread, YouTube script, etc.)
- **Audience**: who will read or watch it (default to the author's primary audience from the profile)
- **Angle or argument**: any specific position, data point, or take the user wants included
- **Length**: if specified; otherwise use defaults from `content-structures.md`

If the channel is missing or ambiguous, ask: "Where will this be published? That affects format and tone."

Use `AskUserQuestion` for any missing critical information. Keep it to one question.

**Step 3 — Research (when needed)**

If the piece requires data, statistics, or citations:
- Use `WebSearch` and `WebFetch` to find primary sources
- Find real, verifiable information before writing
- Never write the piece with placeholder data

**Step 4 — Propose an outline** *(skip for short-form: LinkedIn, Twitter, Stories)*

Present this structure before writing:

```
## Proposed structure

**Suggested title**: {title in the author's capitalization style}

**Excerpt**: {up to 200 characters describing the piece}

**Channel**: {blog / LinkedIn / newsletter / script / etc.}

**Central thesis**: {one sentence — the position this piece defends}

**Opening**: {first sentence or paragraph approach — data, direct claim, real situation}

**Development**:
1. {First argument + example or data}
2. {Second argument — advances the narrative, doesn't repeat}
3. {Third argument or counterpoint}

**Closing**: {how it ends — direction, reflection, or synthesis}

**Sources to cite**: {links or sources to integrate}
```

Wait for the user to approve or adjust the outline before continuing.

**Step 5 — Write the content**

After outline approval:
- Follow `style-rules.md` exactly — especially the forbidden phrases list
- Use the format specified in `content-structures.md` for this channel
- Integrate verified sources with inline links
- Write the full piece or section by section if long

When the user asks to change one thing: change only that thing.
Do not regenerate the whole piece unless explicitly asked.

**Step 6 — Quality check**

Before delivering, verify against `style-examples.md` and run through:

- [ ] Opening goes straight to the thesis — no build-up or "historinha"?
- [ ] Avoided every forbidden phrase from `style-rules.md`?
- [ ] Every factual claim has a verifiable source link?
- [ ] No categorical statements without evidence?
- [ ] Thesis is clear and takes a real position?
- [ ] Arguments are progressive — each advances, none repeats?
- [ ] Examples are concrete and from real sources?
- [ ] Lists avoided where prose would be better?
- [ ] Tone matches the author's calibrated voice?
- [ ] Closing directs or reflects — doesn't just stop?
- [ ] Title follows the author's capitalization preference?

**Step 7 — Deliver with frontmatter**

Output the final piece with complete YAML frontmatter:

```markdown
---
tags:
  - {relevant topic tags}
type: {article | post | newsletter | script | thread}
status: draft
channel: {blog | linkedin | newsletter | twitter | youtube}
excerpt: "{up to 200 characters}"
created: {YYYY-MM-DD}
updated: {YYYY-MM-DD}
published: false
---

# {Title}

{content}

## References and further reading

- [{Source title}]({url}) — {one sentence on why it's relevant}
```

After delivering, tell the user: "Run `/save` when you're ready to export or publish this."

## Arguments

`$ARGUMENTS` can include:
- A topic: `/write why most product roadmaps fail`
- A channel flag: `/write --channel linkedin`
- Both: `/write quarterly planning mistakes --channel newsletter`

If no arguments are provided, ask the user what they'd like to write about.
