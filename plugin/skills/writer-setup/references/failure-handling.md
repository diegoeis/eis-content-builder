# Failure handling reference for `/writer-setup`

Loaded by the parent `SKILL.md` final section. Each row describes a
failure mode the skill expects to encounter and how to react.

| Where | What | Action |
|---|---|---|
| Step 1.2 | ephemeral parent_path | Refuse, re-ask. After 1 retry, abort. |
| Step 1.6 | realpath resolves to ephemeral (symlink trap) | Abort. Do not write anything. |
| Step 1.7 | < 2 readable samples | Ask once for more, then abort if still < 2. |
| Step 2.3 | voice-analyzer fails twice | Abort. Preserve workspace, do not write pointer. |
| Step 2.3 | profile-inferencer fails twice | Degrade — collect identity inline in Step 3.0. |
| Step 2.3 | opinion-extractor fails twice | Degrade — opinion-map stays scaffolded. |
| Step 2.3 | archive script + agent both fail | Degrade — archive disabled. |
| Step 4.1 | a critical reference file is missing | Abort. Preserve workspace, do not write pointer. |
| Step 4.2/4.3 | filesystem error writing config or pointer | Retry once silently, then surface the OS error. |
| Step 4.4 | /writer-index fails | Non-blocking. Report in final message. |

## Retry policy summary

For each of the three agents (`voice-analyzer`, `profile-inferencer`,
`opinion-extractor`), if the first call returns an error, silently
re-dispatch the same agent once. Do not tell the user about the first
failure. If the second call also fails, surface the error to the user
in the confirmation screen.

## Terminal-failure messages

- **voice-analyzer fails twice**: `"Voice analysis failed twice.
  Reason: {error}. Your workspace files are preserved at
  {workspace_path} but the pointer was not written. Inspect the
  samples (make sure they're text, ≥300 words each) and re-run
  /writer-setup with corrected samples."`

- **profile-inferencer fails twice**: degrade. Step 3.0 asks the
  user inline for identity fields before showing the confirmation
  screen.

- **opinion-extractor fails twice**: degrade. The opinion-map stays
  scaffolded. The confirmation screen marks it as pending and
  recommends `/writer-opinion-mine`.

- **Archive script + agent both fail**: degrade. Archive
  `enabled: false`. Confirmation screen explains the failure.
