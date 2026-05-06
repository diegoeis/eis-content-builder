---
name: writer-index
description: Create or update eis-article-index.js at the root of the writer workspace by querying the Obsidian writings.base file via the Obsidian CLI. Requires Obsidian CLI to be installed. Obsidian-only for now - non-Obsidian support planned for a future version. Use when the user says "atualiza o ndice", "cria o ndice de artigos", "update article index", "refresh the index", or runs `/writer-index`.
argument-hint: "[--base <vault-relative-path-to-base-file>]"
allowed-tools: Read, Write, Bash, AskUserQuestion
---

# Writer Index

Creates or updates `eis-article-index.js` at the root of the writer workspace. The file is a JSON array snapshot of all articles tracked in the Obsidian `writings.base` database. Run this whenever you want a fresh index — after saving new drafts, after bulk status changes, or on demand.

## Invariant rules

- Never fabricate article records. The index must come entirely from the CLI output.
- Never overwrite the index with an empty array. If the query returns 0 records, stop and warn before writing.
- This skill is read-only on the vault — it queries, never modifies notes.

## Step 1 — Verify Obsidian CLI

Run:

```bash
which obsidian
```

If the command fails (exit code ≠ 0 or no path returned), stop immediately:

> "Esta skill requer o Obsidian CLI instalado. O CLI vem com o Obsidian Desktop — verifique se o app está instalado e o CLI está no PATH. Mais info: https://help.obsidian.md/cli"

Do not proceed.

## Step 2 — Load workspace config

`Read` `.claude/eis-content-builder.local.md`. If the file is missing or unreadable:

> "Workspace não configurado. Rode `/writer-setup` primeiro."

Stop.

Extract `workspace_path` from the frontmatter. This is the absolute path to the writer profile root (e.g. `/Users/diegoeis/obs-notes/eis-content-writer-profile`).

Derive `vault_root` as the parent directory of `workspace_path`:

```bash
dirname "{workspace_path}"
```

## Step 3 — Locate writings.base

Check if `$ARGUMENTS` contains `--base <path>`. If so, use that path relative to `vault_root`. Otherwise default to `writings.base` at the vault root.

Verify the base file exists:

```bash
test -f "{vault_root}/writings.base"
```

If missing, ask the user once:

> "Não encontrei `writings.base` em `{vault_root}`. Qual é o caminho relativo ao vault para o arquivo base?"

Accept a relative path answer. Validate it exists. If still not found, stop with an error.

## Step 4 — Query the base

Run:

```bash
obsidian base:query --file="{base_file_path}" --format=json
```

Capture stdout. If the command exits with a non-zero code or stderr contains an error, display the error message and stop:

> "Erro ao consultar o base: {stderr}"

If stdout is empty or is `[]` or `null`, stop before writing:

> "A query retornou 0 artigos. Verifique se o arquivo base está correto e se o vault está acessível. O índice não foi atualizado."

## Step 5 — Save the index

Parse the JSON output. Pretty-print it with 2-space indentation.

`Write` the formatted JSON to:

```
{workspace_path}/eis-article-index.js
```

The `.js` extension is intentional — the file already exists under that name in the user's vault and may be consumed by tools that expect it. The content is pure JSON (no JS wrapper, no variable assignment, no module export). Example structure:

```json
[
  {
    "path": "My Article.md",
    "file name": "My Article",
    "excerpt": "...",
    "link": null,
    "published_date": null,
    "status": "draft",
    "published_where": null,
    "tags": "#writing",
    "created time": "2026-01-01T10:00:00"
  }
]
```

## Step 6 — Confirm

Report to the user:

> "Índice atualizado: {N} artigos → `{workspace_path}/eis-article-index.js` ({ISO timestamp})"

Where `{N}` is the count of records in the array and `{ISO timestamp}` is the current date-time in ISO 8601 format.

## Failure handling

| Situation | Action |
|-----------|--------|
| Obsidian CLI not found | Stop with installation hint (Step 1) |
| workspace config missing | Stop, ask user to run `/writer-setup` |
| writings.base not found | Ask once for correct path; stop if still missing |
| CLI query error | Display stderr, stop |
| Query returns 0 records | Warn user, do NOT overwrite existing index |
| Write permission denied | Surface OS error, suggest alternative path |
