---
description: Set up your personal writing profile
allowed-tools: Read, Write, Bash, TodoWrite, AskUserQuestion
argument-hint: [optional: path to writing samples]
---

# /writer-setup — Build Your Author Profile

Invoke using Skill tool `eis-personal-writer-clone` skill to run the author profile setup flow.

## What this command does

1. Checks if a writing profile already exists in `$content-memory/references/`
2. If it exists: asks the user whether to update it or start fresh
3. If it doesn't exist: runs the full setup flow from scratch

## Steps to follow

**Step 1 — Check for existing profile**

Use `Bash` or `Read` to check if the directory `$content-memory/references/` exists
in the current workspace. Look for `author-profile.md` specifically.

If found:
- Tell the user: "You already have a writing profile saved. Would you like to update it with new samples or review it?"
- Use `AskUserQuestion` with options: "Update with new samples", "Review current profile", "Start over"

If not found:
- Tell the user: "Let's build your writing profile. This is a one-time setup — I'll learn your voice from samples you share."
- Proceed to Step 2

**Step 2 — Collect writing samples**

Ask the user to share 2–3 pieces of their own writing. Accept:
- Text pasted directly in the chat
- File paths to `.md`, `.txt`, or `.docx` files in their workspace
- URLs to published articles or posts (use web fetch if URL provided)

Tell the user exactly this: "Share 2–3 pieces you've written and are happy with. They can be articles, posts, newsletters — anything in your voice. The more varied the better."

Read and internalize all samples before proceeding.

**Step 3 — Ask profile questions**

After reading the samples, ask targeted questions. Group them naturally — do not fire all at once.

Round 1 (identity):
- What do you do professionally? What's your main area of expertise?
- What are the main topics you write about?
- Who is your primary audience?

Round 2 (voice and style):
- How would you describe your writing style in 3 words?
- What do you never want your writing to sound like?
- Are there phrases or words you always use? Any you actively avoid?

Round 3 (channels and rules):
- Where do you publish? (Blog, LinkedIn, newsletter, YouTube, Twitter/X, etc.)
- Any hard rules for your writing? (e.g., always cite sources, never use emojis, prefer prose over lists)
- Primary language? Any technical terms you keep in another language?

**Step 4 — Analyze and write the profile**

Analyze the writing samples for:
- Sentence length and rhythm patterns
- Opening and closing structures
- Vocabulary register (formal vs. casual)
- Use of data and citations
- First vs. third person
- Use of questions, provocations, commands
- Formatting tendencies (lists, bold, headers)

Then generate all four profile files using the templates in
`skills/eis-personal-writer-clone/references/profile-templates.md`.

**Step 5 — Save the profile**

Create the directory structure and write the files:

```
$content-memory/references/
├── author-profile.md
├── style-rules.md
├── content-structures.md
└── style-examples.md
```

Each file must be complete and specific to this author — not generic placeholders.

**Step 6 — Save preferences setup**

After the writing profile files are saved, ask whether the user wants to configure
where and how their content gets saved. This is optional but recommended.

Tell the user: "One more optional step — would you like to set up save preferences?
This lets me automatically know where to save each type of content you create, with
the right filename format and frontmatter fields."

Use `AskUserQuestion`:
- "Yes, set up save preferences now"
- "Skip for now (I can run `/save --remember` later)"

If the user chooses to set up preferences now, run the preference collection loop:

**Loop — collect save rules**

For each channel or content type the user mentioned in Step 3, ask:

"For your [channel/type] content — where should I save those files?"

Collect for each rule:
1. **Directory**: path relative to their workspace (e.g., `writing/articles/`, `posts/linkedin/`)
2. **Filename format**: offer options — date + title, title only, or custom
3. **Frontmatter customization**: ask "Do you need any specific YAML fields for this type?
   For example, a database reference, a custom status field, or CMS-specific metadata."
   Accept YAML directly or a verbal description.

After each rule, ask: "Do you have another type or channel with different save settings?"
Continue until the user says no.

**Save the preferences file**

Write all collected rules to `$content-memory/references/save-preferences.md`
using the template from `./skills/eis-personal-writer-clone/references/profile-templates.md`.

**Step 7 — Confirm and summarize**

After everything is saved, tell the user:
- "Your writing profile is saved. Here's what I learned about your voice:" followed by a
  3–5 sentence summary of the key style characteristics
- A brief list of any save preferences configured: "I'll automatically save [type] to
  [directory] with [format]."
- "Use `/write` whenever you want to create content in your voice."
- "Run `/writer-setup` again any time to update your profile or preferences."

## Error handling

If the user shares fewer than 2 samples: ask for at least one more before proceeding.
If a file path can't be read: tell the user and ask them to paste the content directly.
If a URL can't be fetched: ask the user to paste the article text instead.
