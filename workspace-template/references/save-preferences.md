# Save Preferences

Rules that map content `type` / `channel` / `tags` to save destination + frontmatter overrides. Loaded by `/writer-save`. New rules added via `/writer-save --remember` or through the interactive save flow.

Use `*` as wildcard for any field that shouldn't match.

---

<!-- Example rule — delete or replace -->

## Rule: Blog articles

**Applies to**:
- type: article
- channel: blog
- tags: []

**Directory**: `writing/articles/`

**Filename pattern**: `{YYYY-MM-DD}-{slugified-title}.md`

**Frontmatter additions**:
```yaml
database: "[[writings.base]]"
status: draft
```

*Added: {{DATE}}*

---
