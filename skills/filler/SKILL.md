---
name: filler
description: 'Analyze the current git diff, draft a pull request title and description, and generate a pull_request.md file for manual copy-paste. Stops before opening the PR on GitHub. Use when you want to fill in the PR description yourself without creating the PR.'
---

# 📋 Filler

> **Purpose**: Analyze the current branch diff and generate a `pull_request.md` file ready to copy-paste into a PR. Stops before creating the PR on GitHub.

---

## Input

| Parameter  | Required | Default |                                                  Description                                                   |
|------------|----------|---------|----------------------------------------------------------------------------------------------------------------|
| `BASE_REF` |   Yes    |  —      | The base ref to diff against. Pass as the first argument: `/filler upstream/master`, `/filler origin/main`. |

If the user does not provide a base ref, stop and ask for one.

---

## Step 1 — Analyze Changes

Read the diff and commit log against `BASE_REF`:

```bash
git diff "$BASE_REF"
git log "$BASE_REF"..HEAD --reverse --format="### %s%n%n%b"
```

Extract: summary, modules affected, change type, breaking changes, and visual changes.

---

## Step 2 — Extract Ticket Number

Extract ticket from the branch name using regex `(DIGIT|digit|DPMS|dpms)-?(\d+)`. Normalise to uppercase with hyphen (e.g. `DIGIT-3131`).

If not found, ask the developer. If skipped, omit the ticket from the title and remove the `# Ticket 🎫` section entirely.

---

## Step 3 — Draft The PR Title

- Max 72 characters, imperative mood
- If ticket exists, prefix: `TICKET Description` (e.g. `DIGIT-3131 Add payment retry logic`)

---

## Step 4 — Draft The PR Description

Use the project's `.github/pull_request_template.md` if it exists. Otherwise fall back to the template in this skill's `references/pull_request_template.md`.

Fill in every section. Enhance with markdown features (code fences, tables, `<details>` blocks, mermaid charts (horizontally is better), etc.) where helpful.

---

## Step 5 — Write The Test Guidance Section

Write numbered steps for a tester (not the developer): preconditions, concrete actions, expected results. Cover happy path first, then edge cases and regression checks.

---

## Step 6 — Generate `pull_request.md`

Create `pull_request.md` at the repository root with **the PR body** and the suggested **PR title**. Start with the first template section (e.g. `# Description ✍️`). Include the `# Ticket 🎫` section only if a ticket was resolved.

**IMPORTANT**) Do not commit this file.

After writing the file, display the PR title, PR description and the full contents of `pull_request.md` so the user can review and copy-paste them into their PR.
