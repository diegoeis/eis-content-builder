---
name: writer-ideate
description: Brainstorm content ideas or discuss a specific topic before writing. Use when the user says "I'm out of ideas", "help me find what to write about", "what should I write", "estou sem ideia de tema", "me ajuda a achar um ngulo", "quero discutir esse tema antes de escrever", or runs `/writer-ideate`. Supports two modes - open ideation (no topic given, scouts trusted sources and surfaces 5-8 angles calibrated to the author's profile and preferred angles) and topic discussion (user gave a topic, maps the current conversation, then runs a Socratic loop to extract the author's unique angle). Delegates web research to the `content-scout` agent to keep the main conversation lean. When the user picks an angle, saves it to the parking lot and emits a ready-to-paste `/writer-create` command - the user (or an outer orchestrator) decides when to chain it. This skill never invokes `/writer-create` directly, keeping it a pure ideation worker.
argument-hint: "[optional topic]"
allowed-tools: Read, Glob, AskUserQuestion, Task, TodoWrite
---synopsis
Brainstorm angles or discuss a topic before writing. Two modes: open ideation (scouts trusted sources, returns 5-8 angles annotated against your opinion-map) and topic discussion (Socratic loop → locked thesis → ready-to-paste `/writer-create` command). Never invokes `/writer-create` directly.
---

# Writer Ideate

Help the user decide what to write next. You do not write the piece — you find the angle and hand off.

## Invariant rules

Inherit everything from `{workspace}/CLAUDE.md`. Key ones for this skill:

- Never cite sources listed in `avoid_sources`.
- Never propose angles matching `exclude_themes`.
- Keep the conversation lean — delegate research to `content-scout`.

## Step 1 — Load workspace config

1. `Read` `.claude/eis-content-builder.local.md`. If missing, tell the user: "Run `/writer-setup` first — I need your profile and research sources." Stop.
2. Extract `workspace_path`, `research_sources`, `ideation`, and `channels` from the config.
3. `Read` in parallel (one message, multiple Read calls):
   - `{workspace}/CLAUDE.md`
   - `{workspace}/references/author-profile.md`
   - `{workspace}/references/opinion-map.md` (optional — if absent, continue without opinion cross-referencing)

   If CLAUDE.md or author-profile.md is missing, tell the user to repair via `/writer-setup`.

4. **Build the opinion index (if opinion-map.md exists).** Extract a lean in-memory structure:
   - `firm_positions`: topics in Núcleo duro (with counter-argument).
   - `forming_positions`: topics in Em formação.
   - `neutral_zones`: topics in Zonas neutras.
   - `refusals`: topics in Não-posições.
   - `tensions`: list of topic pairs flagged with tension/synergy.
   - `authorities`: list of authors and how the user reads each.

   This index informs every mode below. Do **not** paste the map into chat.

## Step 2 — Detect mode

Parse `$ARGUMENTS` and the user's message:

- No topic mentioned → **mode: open**
- Topic given → **mode: topic**, extract the topic string

If ambiguous, ask one `AskUserQuestion`:

> "Do you already have a topic in mind, or are you fishing for ideas?"

Options: "Fishing — surprise me", "I have a topic: [I'll tell you]".

## Step 3A — Open ideation

1. **Confirm constraints.** Ask a single compact question with `AskUserQuestion`:

   > "Any constraints? Channel, deadline, mood?"

   Options:
   - "Any channel — pick what fits"
   - "Specifically for: {default_channel from CLAUDE.md}"
   - "I want to write a {blog / linkedin / newsletter / script} this week"
   - "Skip — just give me angles"

2. **Spawn the scout.** Use the `Task` tool. Pass:

   ```
   mode: "open"
   profile_path: {workspace}/references/author-profile.md
   local_config_path: .claude/eis-content-builder.local.md
   max_angles: 6
   ```

   Wait for the brief. The scout returns markdown — do not re-summarize it.

3. **Annotate the brief with the opinion-map (if available).** Before showing the brief to the user, tag each angle:
   - `🟢 posição firme` — topic matches `firm_positions`. The user has a recorded stance; the angle is ready to write.
   - `🟡 em formação` — topic matches `forming_positions`. The user has a provisional stance. Note which condition would firm it up.
   - `⚪ zona neutra` — topic matches `neutral_zones`. The angle would require the user to take a position first (offer `/writer-opinion-mine`).
   - `⛔ recusa` — topic matches `refusals`. **Drop the angle from the list entirely** and silently replace with a new one if possible. If it cannot be dropped without falling below `max_angles / 2`, list it with the ⛔ tag and a note.
   - `🔗 sinergia com X` — topic appears in `tensions`. Add a one-line suggestion: "could articulate against X from your map."
   - No tag → topic not in the map yet; angle is fresh.

   Paste the annotated brief back with the opening line: "Scouted. {N} angles, ranked by fit (tagged against your opinion-map):"

4. **Let the user pick.** Use `AskUserQuestion`:

   > "Which angle calls to you?"

   Options: `Angle 1`, `Angle 2`, ..., `None — try again with different constraints`, `Park all of these for later`.

5. **On pick:**
   - Confirm the angle: show title + one-line summary.
   - If the angle is tagged `⚪ zona neutra`, ask: "Esse tema está como zona neutra no seu opinion-map. Quer mapear sua posição primeiro (`/writer-opinion-mine {topic}`) ou seguir direto pro rascunho sem posição firmada?"
   - Save the chosen angle to `{workspace}/drafts/_ideas-parking-lot.md` (prepend to the top; create file if missing). This is always saved, regardless of whether the user wants to write now.
   - Suggest the next command verbatim so the user can copy-paste or invoke it directly:

     > "Angle saved to the parking lot. To write it now, run:
     > `/writer-create \"{angle title}\" --channel {scout's suggested channel} --sources {anchor_url_1},{anchor_url_2}`"

   - Do **not** invoke `writer-create` from inside this skill. Keep ideate as a pure worker that produces an angle artifact; the user (or an outer orchestrator) chains the next skill.

6. **On "None":** loosen one filter (ask which: channel? themes? timeframe?) and rerun the scout with adjusted input. Max 2 reruns before suggesting the user switch to topic mode.

7. **On "Park all":** append all angles from the brief to `{workspace}/drafts/_ideas-parking-lot.md` with today's date as a section header. Tell the user where they're parked.

## Step 3B — Topic discussion

1. **Scout the landscape.** Use the `Task` tool to invoke `content-scout`. Pass:

   ```
   mode: "topic"
   topic: "{user's topic}"
   profile_path: {workspace}/references/author-profile.md
   local_config_path: .claude/eis-content-builder.local.md
   max_angles: 5
   ```

   The scout will return what the current conversation about this topic looks like, what's overdone, what's missing. Paste the brief back with one-line intro: "Here's the landscape on {topic}:"

2. **Socratic loop.** Ask the user, one question at a time:

   a. "What do you think about {topic} that most people writing about it disagree with?"

   b. "What specific data, story, or experience do you have that isn't in the current conversation?"

   c. "If a reader finishes your piece and remembers only one sentence, what should that sentence be?"

   After each answer, reflect back what's emerging. Do not summarize until the user has answered all three. Keep each of your turns under 60 words — this is discussion, not writing.

3. **Converge to a thesis.** Propose one candidate thesis in one sentence:

   > "Working thesis: {...}. Does this nail it, or is it off?"

   Iterate max 2 times. If still off after 2 iterations, ask: "Want me to generate 3 alternate thesis framings?" — generate them, let the user pick.

4. **Outline handoff.** Once thesis is locked:

   - Propose a compact outline: opening approach, 3 development beats, closing technique. Use the `voice-fingerprint.md` signature techniques as a menu for opening/closing choices.
   - Save the thesis + outline + topic + scout sources to the parking lot entry for this angle (one block, structured).
   - Suggest the next command verbatim:

     > "Thesis locked. To write it now, run:
     > `/writer-create \"{topic}\" --channel {channel} --thesis \"{one-line thesis}\" --sources {urls}`"

   - Do **not** invoke `/writer-create` from inside this skill. The user chains it.

## Parking lot file format

`{workspace}/drafts/_ideas-parking-lot.md`:

```markdown
# Ideas Parking Lot

Angles considered but not written yet. Prepend newest at top.

---

## {YYYY-MM-DD} — {context, e.g. "Open ideation, PM + LLMs"}

### {Angle title}
- Why now: {...}
- Unique angle: {...}
- Sources: {link}, {link}

### {Next angle}
...

---
```

Do not delete entries automatically. The user clears this file manually.

## TodoWrite usage

Only use for topic mode, Step 3B items 2 and 3 (Socratic loop + thesis convergence). One todo per substep. Open-ideation mode does not need todos.

## Failure handling

- Scout returns empty / no angles: tell the user, offer to switch modes or loosen filters.
- Missing `research_sources` in `.local.md`: scout already warns; relay that warning.
- User rejects every angle in topic mode: stop gracefully, suggest `/writer-setup` to refine themes/preferred_angles.
