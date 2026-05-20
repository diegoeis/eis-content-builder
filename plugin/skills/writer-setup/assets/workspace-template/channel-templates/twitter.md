# Template: Twitter / X post

Default structure for single tweets and threads on X/Twitter.

## Target

- **Length per tweet**: ≤ 280 characters
- **Thread length**: 3–8 tweets typical; longer threads need a clear arc
- **Format**: plain text, no Markdown

## Structure (single tweet)

- **One claim, one tweet**. No setup, no preamble.
- If a number, a name, or a concrete object is the key, put it first.

## Structure (thread)

- **Tweet 1**: the thesis or the most provocative claim. Must work as a
  standalone tweet (people will see only this in the feed).
- **Tweets 2–N**: develop the argument. One idea per tweet. Number them
  if it aids readability (`1/`, `2/`).
- **Final tweet**: synthesis or call-to-action. Avoid "RT if you agree".

## Frontmatter (internal)

```yaml
title: <internal title>
slug: <slug>
date: <YYYY-MM-DD>
status: draft
type: tweet | tweet-thread
channel: twitter
thread_length: <int or null>
```

## Anti-patterns

- Hashtag spam (#thoughtleader #grindset).
- "A thread 🧵" without a real thesis in tweet 1.
- Engagement bait ("hot take incoming").
- Threads that should have been a blog post.

## Formatting rules

- Plain text, no Markdown.
- Hashtags are sparse and lowercase, or none.
- Line breaks inside a tweet are fine; whitespace helps.
