---
name: creator
description: 'Analyze the current git diff, draft a pull request title and description, generate a pull_request.md file, and open the PR on GitHub. Use when asked to draft, create, or open a pull request.'
---

# 🌍 Creator

> **Purpose**: Analyze the current branch diff, generate a `pull_request.md` file, and open the PR on GitHub.

**Requires**: `gh` (GitHub CLI) installed and authenticated. Stop if missing.

---

## Input

| Parameter  | Required | Default |                                                  Description                                                   |
|------------|----------|---------|----------------------------------------------------------------------------------------------------------------|
| `BASE_REF` |   Yes    |  —      | The base ref to diff against. Pass as the first argument: `/creator upstream/master`, `/creator origin/main`. |

If the user does not provide a base ref, stop and ask for one.

---

## Step 1 — Diff Size Guard

```bash
git diff "$BASE_REF" --numstat | awk '{adds+=$1; dels+=$2} END {print adds+dels}'
```

If the diff exceeds **1000 lines changed**, warn the user to consider `/breaker` first. Only proceed if they confirm.

---

## Step 2 — Analyze Changes

Read the diff and commit log against `BASE_REF`:

```bash
git diff "$BASE_REF"
git log "$BASE_REF"..HEAD --reverse --format="### %s%n%n%b"
```

Extract: summary, modules affected, change type, breaking changes, and visual changes.

---

## Step 3 — Extract Ticket Number

Extract ticket from the branch name using regex `(DIGIT|digit|DPMS|dpms)-?(\d+)`. Normalise to uppercase with hyphen (e.g. `DIGIT-3131`).

If not found, ask the developer. If skipped, omit the ticket from the title and remove the `# Ticket 🎫` section entirely.

---

## Step 4 — Draft The PR Title

- Max 72 characters, imperative mood
- If ticket exists, prefix: `TICKET Description` (e.g. `DIGIT-3131 Add payment retry logic`)

---

## Step 5 — Draft The PR Description

Use the project's `.github/pull_request_template.md` if it exists. Otherwise fall back to the template in this skill's `references/pull_request_template.md`.

Fill in every section. Enhance with markdown features (code fences, tables, `<details>` blocks, etc.) where helpful.

---

## Step 6 — Write The Test Guidance Section

Write numbered steps for a tester (not the developer): preconditions, concrete actions, expected results. Cover happy path first, then edge cases and regression checks.

---

## Step 7 — Generate `pull_request.md`

Create `pull_request.md` at the repository root with **only the PR body** (no title wrapper). Start with the first template section (e.g. `# Description ✍️`). Include the `# Ticket 🎫` section only if a ticket was resolved. Do not commit this file.

---

## Step 8 — Review & Confirm

Present the PR title and draft/ready mode to the user. **Wait for explicit approval** before proceeding.

---

## Step 9 — Create The Pull Request

```bash
GH_OWNER=$(gh repo view --json owner --jq '.owner.login')
GH_BRANCH=$(git rev-parse --abbrev-ref HEAD)
GH_BASE=$(gh repo view --json defaultBranchRef --jq '.defaultBranchRef.name')

# Push if needed
git push origin "$GH_BRANCH"

gh pr create \
  --title "<title>" \
  --body-file pull_request.md \
  --head "$GH_OWNER:$GH_BRANCH" \
  --base "$GH_BASE" \
  --draft  # omit if user chose "Ready for review"
```

> Always use `--head owner:branch` format to avoid `gh` aborting on uncommitted files.
