# Baseline forbidden patterns — en

> Loaded by `/writer-create` and `/writer-calibrate` ONLY if the workspace
> `language.default` is `en`. These patterns read as generic LLM output,
> coach-speak, or empty corporate framing. Do not soften them, do not
> rephrase them — **go straight to the claim instead**.

> **Single registry for pamphleteering inversions.** The "Pamphleteering
> inversions" section below is the ONLY place where this pattern should
> live in this workspace. Do NOT duplicate it in `style-rules.md`
> (Hard Rules or CONTRAST_FORBIDDEN) or `voice-fingerprint.md`. If you
> are the `voice-analyzer` populating CONTRAST_FORBIDDEN, do NOT include
> inversions — they are already covered here.

## Phrases

- "In today's fast-paced world"
- "At the end of the day"
- "It's important to note"
- "As we all know"
- "Game-changer"
- "Leverage" (as a verb)
- "Unlock" (metaphorical)
- "Dive deep"
- "Journey" (metaphorical, non-travel context)
- "Holistic approach"
- "Synergy"
- "Best-in-class"
- "Cutting-edge"
- "Revolutionize"
- "Seamless"
- "Here's the truth few admit:"
- "Let's be honest:"
- "The hard truth is..."
- "What we lost along the way is..."
- "The lesson? ..."
- "Why does this matter? Because..."
- "Now for the question that really matters:"
- "The numbers speak for themselves:"

## Pamphleteering inversions (single registry — do not duplicate elsewhere)

Generic structure: "It's not {X}. It's {Y}." and variants. Reads like a
LinkedIn manifesto, political pamphlet, or motivational copy. Applies
to any negation-then-reassertion micro-structure with syntactic
parallelism — regardless of what fills X and Y.

Forbidden variants (all equivalent for detection):

- "It's not X. It's Y." (canonical)
- "It's not about X. It's about Y."
- "The problem was never X. It was Y."
- "The question is not X. It's Y."
- "This is not X. It is Y."
- "X is not the point. The point is Y."

**Detection:** any paragraph containing a short negation of one option
followed (same sentence or the immediately next one) by a short
assertion of an alternative, with syntactic parallelism. When in
doubt, count it as a violation.

**Fix:** assert Y directly, without negating X first. If the contrast
with X really matters, develop it in prose (2-3 sentences) instead of
compressing it into parallelism.

## Other constructions

- Any "setup" sentence before reaching the point (e.g. "Before we get
  into this, it's worth noting..."). Cut the setup — open with the point.
- Rhetorical questions as transitions ("Why does this matter?", "So
  what?") — state the answer directly.
- Opening with "Have you ever...".
- Closing with "So what do you think? Let me know in the comments."

**Rule of thumb:** if a sentence functions as a ramp to the real claim,
delete the ramp and start with the claim.
