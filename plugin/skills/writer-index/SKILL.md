---
name: writer-index
description: Create or update the plugin's article index file (`eis-article-index.json`) at the workspace root. Two source modes — (a) query an Obsidian `.base` file via the Obsidian CLI when the user has one, (b) scan the folder declared in `article_archive` and parse YAML frontmatter when they don't. After writing, auto-wires `article_archive.index_file.path` in `.local.json` if it was null. Output is always JSON. Use when the user says "atualiza o índice", "cria o índice de artigos", "update article index", "refresh the index", or runs `/writer-index`.
argument-hint: "[--base <vault-relative-path-to-base-file>] [--out <output-filename>]"
allowed-tools: Read, Write, Edit, Bash, AskUserQuestion
---

# SKILL

> **Synopsis.** Builds `eis-article-index.json` at the workspace root. Source is Obsidian `.base` (if user has one and Obsidian CLI is on PATH) or a scan of `article_archive.path` parsing YAML frontmatter (fallback, no external dependencies). After writing, auto-wires `article_archive.index_file.path` in `.local.json` if empty, so `/writer-create` picks it up automatically. Never writes an empty index.


# Writer Index

Build or refresh **the plugin's own article index** at the root of the writer workspace. The output file is always `eis-article-index.json` (JSON, not JS — `.js` was a legacy convention that's been retired). Run this whenever you want a fresh snapshot — after saving new drafts, after bulk status changes, or on demand.

This skill is the **builder**, not the consumer. `/writer-create` reads `article_archive.index_file.path` from `.local.json`; this skill writes that file and points the config at it.

## Invariant rules

- Never fabricate records. Every entry must come from the source (base query or YAML scan).
- Never overwrite the index with an empty array. Zero records → stop and warn.
- Read-only on the vault and on the archive folder. This skill only writes its own index file (and `.local.json`).

## Step 1 — Load workspace config

Locate the plugin config using the canonical probe in `../writer-setup/references/load-config.md` (pointer → env var → walk-up, all targeting `.local.json`). Empty → tell the user "Workspace não configurado. Rode `/writer-setup` primeiro." Stop. Otherwise `Read "$CONFIG_PATH"`, parse as JSON, and extract `workspace_path`, `article_archive.path`, `article_archive.toolchain`, `article_archive.file_pattern`, `article_archive.schema`, and any existing `article_archive.index_file`.

If `article_archive.enabled` is false or `article_archive.path` is empty, stop with: "Sem `article_archive` configurado em `.local.json`. Rode `/writer-setup` (modo update) e escolha registrar a pasta de artigos antes."

## Step 2 — Pick source mode

Pick one of two modes. Do NOT prompt the user unless the data is ambiguous.

- **Mode A — Obsidian base** when ALL of:
  - `article_archive.toolchain == "obsidian"`
  - `obsidian` CLI is on PATH (`which obsidian`)
  - The user either passed `--base <path>` or the existing `article_archive.index_file.format == "obsidian-base"` (use the path already recorded), **or** the user explicitly mentions a base file in their message.

- **Mode B — Folder scan** (default fallback): for every other case. Uses `Glob` + `Read` to walk `article_archive.path` matching `article_archive.file_pattern` and parses YAML frontmatter from each file.

If the user is on Obsidian but has no base file, run Mode B silently — Mode A is purely a convenience for Obsidian users who curate base files. Never force-create a base file.

## Step 3 — Build the records

### Mode A — Obsidian base

1. Resolve the base file path: `--base <path>` arg → use directly; else read `article_archive.index_file.path`. Validate the file exists.
2. Run:

   ```bash
   obsidian base:query --file="{base_file_path}" --format=json
   ```

3. Capture stdout. Non-zero exit → display stderr and stop. Empty / `[]` / `null` → stop with: "A query retornou 0 artigos. Índice não foi atualizado."
4. The result is your `records` array. Continue to Step 4.

### Mode B — Folder scan

1. `Glob "{article_archive.path}/{article_archive.file_pattern}"`. Zero results → stop with: "Nenhum arquivo encontrado em `{path}` com pattern `{file_pattern}`. Índice não foi atualizado."
2. For each path, read the first ~120 lines (frontmatter is near the top) and parse the top YAML block. Build one record per file:

   ```json
   {
     "path": "<absolute path>",
     "title": "<value of schema.title_property or null>",
     "tags": "<value of schema.tags_property or null>",
     "status": "<value of schema.status_property or null>",
     "date": "<value of schema.date_property or null>",
     "url": "<value of schema.url_property or null>",
     "excerpt": "<value of schema.excerpt_property or null>"
   }
   ```

   For any schema property that is `null` in the config, leave the corresponding record field `null` — never guess. If `title` would be null and the body starts with an H1, you may use the H1 text as `title` (it's a body-derived fallback, not invention). Otherwise leave it null.

3. Cap at 5000 records — if more, warn the user and take the most recent 5000 by `date` field (or by file mtime if `date` is null).

## Step 4 — Write the index

Output path: `{workspace_path}/eis-article-index.json`. If `--out <filename>` was supplied, use that filename instead (still inside `{workspace_path}`).

`Write` the records as pretty-printed JSON (2-space indent). Sample shape:

```json
[
  {
    "path": "/abs/path/My Article.md",
    "title": "My Article",
    "tags": ["product", "writing"],
    "status": "published",
    "date": "2026-01-01",
    "url": "https://example.com/my-article",
    "excerpt": "..."
  }
]
```

## Step 5 — Auto-wire `index_file` in `.local.json`

If `article_archive.index_file.path` is `null` (or pointed somewhere that no longer exists), `Edit` `.local.json` to set:

```yaml
index_file:
  path: {absolute path of the file you just wrote}
  format: json
```

If `index_file.path` was already set and points to a different file (e.g. a user-maintained `.base` or CSV), do **not** overwrite — print a note: "Você já tem `index_file.path` apontando para `{old path}`. Mantive como está. Se quiser usar o índice que acabei de gerar, edite `.local.json` manualmente ou rode `/writer-setup` em modo update."

## Step 6 — Confirm

Report:

> "Índice atualizado: {N} artigos → `{output path}` (modo {A|B}, {ISO timestamp})"

If Step 5 auto-wired the config, add: "Apontei `article_archive.index_file.path` para esse arquivo. `/writer-create` vai usar automaticamente."

## Failure handling

| Situation | Action |
|---|---|
| workspace config missing | Stop, ask user to run `/writer-setup` |
| `article_archive` disabled / no path | Stop, ask user to register the archive first |
| Mode A: Obsidian CLI not found | Silently downgrade to Mode B (do NOT block) |
| Mode A: base file not found | Stop, ask once for the correct path |
| Mode A: query error | Display stderr, stop |
| Mode B: zero files | Stop, do NOT overwrite |
| Write permission denied | Surface OS error |
