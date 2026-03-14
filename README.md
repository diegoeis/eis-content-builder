# eis-content-builder

A personal writing assistant that learns your voice and produces content in it — across any channel, in any format.

## What it does

This plugin analyzes samples of your writing to build a persistent author profile: your voice, tone, style rules, preferred structures, and forbidden patterns. Once set up, it uses that profile every time you create content, so everything you write sounds like you.

---

## Commands

### `/writer-setup`
Build or update your author profile. Share 2–3 samples of your own writing and answer a few targeted questions. The plugin saves your profile to your workspace so it can reference it on every future session.

Run this once before your first `/write`. Re-run any time you want to refine your profile with new samples or correct something.

### `writer-create [topic] [--channel channel-name]`
Write content in your voice. The plugin loads your profile, asks what you need, proposes a structure for your approval, then writes the full piece.

Examples:
- `writer-create why most product roadmaps fail`
- `writer-create --channel linkedin`
- `writer-create quarterly planning mistakes --channel newsletter`

Supported channels: `blog`, `linkedin`, `newsletter`, `twitter`, `youtube` (and any custom channel you define in your profile).

### `/save [path] [--publish] [--schedule "YYYY-MM-DD HH:MM"]`
Save the content you just wrote to your workspace or prepare it for your CMS.

- Default: saves as `.md` with complete frontmatter to your workspace
- `--publish`: publishes directly to your connected CMS (Ghost integration coming soon)
- `--schedule`: saves with a scheduled publication date in frontmatter

---

## How the profile works

After running `/writer-setup`, the plugin creates a folder in your workspace:

```
{your-workspace}/
└── eis-personal-writer-clone/
    └── references/
        ├── author-profile.md       ← Who you are, expertise, themes, audience
        ├── style-rules.md          ← Voice, forbidden phrases, formatting rules
        ├── content-structures.md   ← Format guides per channel
        └── style-examples.md       ← Annotated good/bad examples from your writing
```

These are plain Markdown files. You can open and edit them directly. Claude loads them at the start of every `/write` session.

---

## Getting started

1. Install the plugin
2. Select your workspace folder in Claude Cowork
3. Run `/writer-setup` and share 2–3 samples of your writing
4. Run `writer-create` to create your first piece

---

## Setup requirements

No environment variables needed for local use.

**Ghost CMS integration** (coming in a future version) will require:
- `GHOST_API_URL` — your Ghost blog URL
- `GHOST_ADMIN_API_KEY` — your Ghost Admin API key

---

## File structure

```
eis-content-builder/
├── .claude-plugin/
│   └── plugin.json
├── commands/
│   ├── writer-setup.md        ← Build or update your author profile
│   ├── writer-create.md        ← Write content in your voice
│   └── writer-save.md         ← Save or publish your content
├── skills/
│   └── eis-personal-writer-clone/
│       ├── SKILL.md
│       └── references/
│           ├── profile-templates.md   ← Blank templates used during setup
└── README.md
```

---

## Version history

- `0.2.0` — Plugin made generic; author profile system; commands added; Ghost integration planned
- `0.1.0` — Initial version (personal configuration)
