---
name: merger
description: 'Fetch a remote and merge its branch into the current branch, resolving conflicts without breaking code. Use when asked to merge a remote branch like `upstream/main`.'
---

# 🔀 Merger

> **Purpose**: Merge `<remote>/<branch>` into the current branch and resolve conflicts safely.

## Input

| Parameter   | Required | Description                                              |
|-------------|----------|----------------------------------------------------------|
| `MERGE_REF` |   Yes    | The ref to merge, e.g. `upstream/main`. Required. |

If missing, stop and ask.

## Steps

1. `git fetch <remote>` (the part before `/` in `MERGE_REF`)
2. `git merge <MERGE_REF>`
3. If conflicts: open each conflicted file, keep the intent of both sides, remove all `<<<<<<<` / `=======` / `>>>>>>>` markers, then `git add` and `git commit --no-edit`.

## Rules

- Never use `--ours`, `--theirs`, `--no-verify`, `reset --hard`, or `push`.
- Never drop code from either side just to clear a conflict.
- If unsure how to resolve, stop and ask.
