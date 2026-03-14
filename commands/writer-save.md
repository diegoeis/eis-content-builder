---
description: Save or publish your content
allowed-tools: Read, Write, Bash, AskUserQuestion
argument-hint: [path | --publish | --schedule "YYYY-MM-DD HH:MM" | --remember]
---

# /writer-save — Save or Publish Content

Export the current piece as a Markdown file, or prepare it for publishing to the author's CMS.
This command is preferences-aware: it checks for saved save rules before asking where to save,
and can learn new rules when the user asks.

---

## Save Preferences

Before doing anything else, load `$content-memory/references/writer-save-preferences.md`
if it exists. This file contains rules that map content types, channels, or tags to specific
destinations and frontmatter templates.

If the file exists, read it fully and keep it in context for Steps 1–3.
If it doesn't exist, treat all preferences as undefined and proceed normally.

---

## Special mode: `--remember`

If the user runs `/writer-save --remember` or says something like "remember how to save this type of
content", "lembra como salvar artigos do blog", or "quero configurar onde salvar newsletters":

→ Jump directly to **Step R — Record a Save Preference** at the bottom of this file.
Do not proceed with saving a piece.

---

## Steps to follow

**Step 1 — Confirm what to save**

If there's active content in the session from `/writer-create`, confirm:
"I'll save the piece we just created — [title or excerpt]. Is that right?"

If it's unclear which piece to save, ask the user to specify.

**Step 2 — Match against save preferences**

Extract from the current piece:
- `type` (from frontmatter: article, post, newsletter, script, thread)
- `channel` (from frontmatter: blog, linkedin, newsletter, twitter, youtube)
- `tags` (from frontmatter)

Check `save-preferences.md` for a rule that matches this combination. A rule matches when
its `match` conditions align with the piece's type, channel, or tags.

**If a matching rule is found:**
- Show the user what rule applies: "Based on your preferences, I'll save this as [description of rule]."
- Use the rule's `directory`, `filename_pattern`, and `frontmatter` fields automatically
- Skip Step 3 and proceed to Step 4
- Still ask for confirmation if the rule triggers a publish action

**If no matching rule is found:**
- Proceed to Step 3 normally

**Step 3 — Ask for the destination** *(only when no preference matches)*

Use `AskUserQuestion`:

"Where would you like to save this?"

Options:
- "Save as Markdown file to my workspace"
- "Publish to Ghost (requires Ghost connection)"
- "Schedule for later"
- "Save as draft in my workspace"

After the user chooses, ask: "Would you like me to remember this preference for future
[type/channel] content?" If yes, go to Step R after saving.

**Step 3a — Save as Markdown file**

Determine the destination path:
- If a preference rule applies: use its `directory` and `filename_pattern`
- If no rule: suggest `{workspace}/posts/{YYYY-MM-DD}-{slugified-title}.md`
  and ask the user to confirm or change it

Check if a file already exists at that path. If it does:
"A file already exists there. Overwrite, or save with a new name?"

Build the final frontmatter by merging:
1. The frontmatter from the written piece
2. Any `frontmatter` overrides from the matched preference rule
3. Updated `updated` date (today)

Write the file and confirm: "Saved to [path]."

**Step 3b — Publish to Ghost** *(future integration)*

Check if a Ghost MCP server is connected. If not:
"Ghost publishing requires connecting your Ghost blog. This integration is coming soon.
For now, I'll save the file locally and you can import it manually."
Then fall back to Step 3a.

When Ghost is connected:
- Map frontmatter fields to Ghost API fields (tags, excerpt, published status)
- Ask for confirmation before publishing: "Ready to publish '{title}' to Ghost?
  This will be visible immediately." Wait for explicit yes.
- Call the Ghost MCP tool to create or update the post
- Return the published post URL

**Step 3c — Schedule for later**

Ask: "What date and time should this publish?"

Save the file locally with `published: false` and add `scheduled_for` to the frontmatter:

```yaml
published: false
scheduled_for: "{YYYY-MM-DD HH:MM}"
```

**Step 4 — Final confirmation**

Always end with:
- The file path or CMS URL where content was saved
- The current status (draft, published, scheduled)
- Whether a preference was applied or recorded
- Next step if relevant

---

## Step R — Record a Save Preference

This step runs when the user wants to save a new rule, either explicitly via `--remember`
or after a save when they said yes to "remember this preference".

**R1 — Understand what the rule applies to**

Ask the user what types of content this rule covers. Use `AskUserQuestion`:

"What type of content should this rule apply to?"

Options:
- "A specific content type (article, post, newsletter, script...)"
- "A specific channel (blog, LinkedIn, newsletter, YouTube...)"
- "A specific tag or topic"
- "A combination of the above"

Wait for the answer. If the user says "all articles" or "blog posts", extract the
relevant `type` and/or `channel` values.

**R2 — Ask for the destination directory**

"Where should [this type of content] be saved? Provide a path relative to your workspace,
for example: `posts/blog/` or `writing/newsletters/`"

Accept a path. Do not validate it yet — the directory may not exist and will be created on
first save.

**R3 — Ask for the filename pattern**

"How should the filename be formatted?"

Options:
- "`{YYYY-MM-DD}-{slugified-title}.md` (date + title)"
- "`{slugified-title}.md` (title only)"
- "`{YYYY-MM}-{slugified-title}.md` (year-month + title)"
- "Custom pattern"

If custom: ask them to describe it. Convert to a pattern using `{YYYY}`, `{MM}`, `{DD}`,
`{slugified-title}`, `{type}`, `{channel}` as available tokens.

**R4 — Ask about frontmatter customization**

"Do you want to customize the YAML frontmatter for [this type of content]?"

If yes, ask:
"Share the frontmatter fields you want. You can paste YAML directly, or describe what you need."

Accept YAML or a description. Parse and validate the YAML structure.
If they paste fields, merge them — do not replace the base frontmatter, only add or override.

Common fields to ask about if the user seems unsure:
- `database` (e.g., for Obsidian Dataview: `"[[writings.base]]"`)
- `status` default value
- `published` default value
- Any custom fields their CMS or note system needs

**R5 — Show preview and confirm**

Show the rule before saving:

```
## New save preference

Applies to: {type} / {channel} / {tags}
Directory: {workspace}/{directory}/
Filename: {filename_pattern}
Frontmatter additions:
  {yaml preview}
```

Ask: "Save this preference?" Wait for confirmation.

**R6 — Write to save-preferences.md**

Load `$content-memory/references/save-preferences.md` if it exists,
or create it. Add the new rule following the format in the file's existing structure
(or use the base format below if the file is new).

Base format for `save-preferences.md`:

```markdown
# Save Preferences

Rules that map content types or channels to destinations and frontmatter templates.
Loaded automatically by the `/writer-save` command.

---

## Rule: {short descriptive name}

**Applies to**:
- type: {article | post | newsletter | script | thread | *}
- channel: {blog | linkedin | newsletter | twitter | youtube | *}
- tags: [{tag1}, {tag2}] *(optional — leave blank to match any tag)*

**Directory**: `{path/relative/to/workspace}/`

**Filename pattern**: `{YYYY-MM-DD}-{slugified-title}.md`

**Frontmatter additions**:
```yaml
{field}: {value}
{field}: {value}
```

*Added: {YYYY-MM-DD}*

---
```

After writing, confirm: "Preference saved. Next time you save a [{type}/{channel}] piece,
I'll apply this rule automatically."

---

## Frontmatter update on save

When saving any piece, always:
- Set `updated` to today's date
- If publishing: set `published: true` and add `published_at: {datetime}`
- If saving as draft: keep `published: false`
- Merge any frontmatter additions from the matched save preference rule

## Arguments

`$ARGUMENTS` can include:
- A specific path: `/writer-save posts/my-article.md`
- A flag: `/writer-save --publish`
- A scheduled time: `/writer-save --schedule "2026-03-15 09:00"`
- Remember mode: `/writer-save --remember`
