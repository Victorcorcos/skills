---
name: fixer
description: 'Read review comments on a GitHub Pull Request, filter actionable feedback, analyze each comment, propose a solution, and walk the user through an interactive resolution flow. Use when asked to fix, address, or resolve PR review comments.'
---

# 🩹 Fixer

> **Purpose**: Fetch all review comments from a GitHub Pull Request, filter out non-actionable noise, analyze each piece of feedback, propose a concrete solution, and guide the user through resolving every comment interactively — one at a time.

Here is the desired workflow of this task in detail.

---

## Non-Negotiables

- **One comment at a time**: NEVER fix multiple comments in a single step. Each actionable comment must be presented, discussed, and resolved individually before moving to the next.
- **Always use `AskUserQuestion` tool**: When asking the user to confirm a solution, you MUST use the `AskUserQuestion` tool with structured options. Do NOT present options as plain text and wait for a freeform response.
- **No code changes before approval**: Do NOT apply any fix until the user has explicitly selected a solution via the `AskUserQuestion` tool response.
- **Group related comments**: When multiple review comments target the same file and line, merge them into a single actionable item and address them together in one round.

---

## Step 0 — Resolve the Pull Request

Determine which PR to work on. Use the following fallback chain:

1. If the user provided a PR number or URL, use that directly.
2. Otherwise, detect the current branch and look up its open PR:

```bash
gh pr view --json number,title,url,body,headRefName,baseRefName
```

If `gh` is not authenticated, tell the user:

> "GitHub CLI is not authenticated. Please run `gh auth login` in another terminal and let me know when you're ready."

Then **stop and wait** for the user's confirmation before continuing.

Store the resolved PR number as `PR_NUMBER` and use it throughout.

---

## Step 1 — Gather PR Context

Collect three pieces of context in parallel:

### 1a — PR description and metadata

```bash
gh pr view "$PR_NUMBER" --json number,title,url,body,headRefName,baseRefName,author
```

### 1b — Full diff

Fetch the diff to understand every code change in the PR:

```bash
gh pr diff "$PR_NUMBER"
```

### 1c — All review comments

Fetch every review comment (inline code comments and review-level comments):

```bash
gh api "repos/{owner}/{repo}/pulls/$PR_NUMBER/comments" --paginate
```

Also fetch top-level PR review bodies (the summary comments left when submitting a review):

```bash
gh api "repos/{owner}/{repo}/pulls/$PR_NUMBER/reviews" --paginate
```

Read the full content of every changed file referenced by comments so you understand the surrounding context — not just the diff hunks.

---

## Step 2 — Filter Actionable Comments

Not every comment requires a code change. Classify each comment into one of two buckets:

| Bucket | Examples | Action |
|--------|----------|--------|
| **Actionable** | Bug report, code improvement request, naming suggestion, security concern, performance tip, question that implies a change, request for refactor | Keep — will be processed in Step 3 |
| **Non-actionable** | "Nice!", "LGTM", "Cool", praise, acknowledgements, resolved/outdated threads, purely informational notes with no change requested | Skip — mention in the summary but do not process |

Present a quick overview to the user:

```
## PR #42 — "Add payment retry logic"

Found 8 review comments:
- 5 actionable comments to resolve
- 3 non-actionable (praise / acknowledgements) — skipped

Let's walk through the 5 actionable comments one by one.
```

If **no actionable comments** are found, report that clearly and stop:

> "I reviewed all comments on PR #42 and found no actionable feedback requiring code changes. All comments are informational or praise. Nothing to fix!"

---

## Step 3 — Analyze & Propose a Solution

For each actionable comment, prepare:

| Field | Description |
|-------|-------------|
| **#** | Sequential number (among actionable comments only) |
| **Author** | Who left the comment |
| **File** | File path and line number(s) the comment targets |
| **Comment** | The reviewer's feedback (quoted) |
| **Validity** | Is the comment valid? Brief explanation of why or why not |
| **Solution** | Proposed fix — description and code diff |

### Solution quality rules

- The solution must be **concrete**: show the actual code change as a diff, not just a description.
- The solution must **respect the existing codebase conventions** (naming, style, patterns).
- The solution must **not introduce new issues** (no security holes, no broken tests, no unrelated refactors).

---

## Step 4 — Interactive Comment-by-Comment Walkthrough

Process each actionable comment **one at a time** in the following cycle.

**CRITICAL — This is the most important step. You MUST follow it exactly.**

- Do NOT batch-apply fixes or attempt to fix multiple comments at once.
- Do NOT proceed to the next comment until the user has made a decision on the current one.
- Do NOT skip presenting the solution or the decision prompt for any actionable comment.
- Do NOT apply any code change before receiving the user's explicit choice.

For each comment, follow this exact sequence:

1. Announce: "Comment #N of M"
2. Show the reviewer's comment (quoted)
3. Show the current code in question
4. Explain whether the comment is valid and why
5. Present the proposed solution with its code diff
6. Ask the user for their decision using the `AskUserQuestion` tool (see below)
7. Wait for the user's response before doing anything else

### Decision prompt — MUST use AskUserQuestion tool

After presenting the solution in text, you **MUST** use the `AskUserQuestion` tool to collect the user's decision. Do NOT simply print the options as text and wait — you MUST invoke the tool.

Always use these two options:

1. `label: "Apply solution"`, `description: "[one-line description of the solution]"`
2. `label: "Skip"`, `description: "Move to the next comment without changes"`

The question text must follow this format:
> `"Comment #N — [Short summary]: how to proceed?"`

Set `header` to `"Comment #N"` and `multiSelect` to `false`.

The user can always select "Other" (automatically provided by the tool) to explain what they want instead.

### Handling each option

- **Apply solution**: Apply the fix to the code immediately. Confirm the change was applied and show the final state of the modified code. Then commit the change and reply to the reviewer (see "Committing and replying after each fix" below). Then move to the next comment.

- **Other** (user typed a custom response): Read the user's explanation. Propose a revised solution based on their feedback. Show the updated diff. Ask again with the `AskUserQuestion` tool using the same structure. Repeat until the user picks a solution or skips.

- **Skip**: Acknowledge the skip. Do not apply any change. Move to the next comment.

### Committing and replying after each fix

After every fix is applied, immediately commit **only that change** and then reply to the reviewer comment on GitHub. This is **mandatory** — every applied fix must follow the full cycle: **fix → commit → reply**.

1. Stage only the files modified by this fix.
2. Build the commit title in this format:
   > `fix (review): [short imperative description of what was changed]`
3. Build the commit body with:
   - `PR #<PR_NUMBER>, comment #<N> — <reviewer's feedback quoted briefly>`
   - A one-sentence explanation of the solution that was applied.
4. Create the commit.
5. **Immediately reply** to the reviewer's comment on GitHub using the commit hash from step 4:

```bash
gh api "repos/{owner}/{repo}/pulls/$PR_NUMBER/comments/{comment_id}/replies" \
  -f body="Addressed in [SHORT_HASH](COMMIT_URL) — [brief description of the fix]. Thanks for the feedback!"
```

Build the reply values as follows:
- `SHORT_HASH`: the short commit hash (use `git rev-parse --short HEAD`).
- `COMMIT_URL`: construct from the PR URL — `https://github.com/{owner}/{repo}/pull/$PR_NUMBER/commits/FULL_HASH` (use `git rev-parse HEAD` for the full hash).
- `{comment_id}`: the numeric ID of the review comment being addressed.

The commit hash in the reply **must** be a clickable markdown link so reviewers can jump straight to the code changes. Keep the reply concise and professional.

**Example commit:**

```
fix (review): extract retry delay into a named constant

PR #42, comment #2 — "Magic number 3000 is unclear"
Replaced the inline 3000 ms literal with a RETRY_DELAY_MS constant to improve readability.
```

**Example reply posted to GitHub:**

> Addressed in [a1b2c3d](https://github.com/acme/repo/pull/42/commits/a1b2c3d4e5f6a7b8c9d0e1f2a3b4c5d6e7f8a9b0) — Extracted magic number into RETRY_DELAY_MS constant. Thanks for the feedback!

Do NOT squash multiple fixes into one commit. Each resolved comment gets its own commit and its own reply. Do NOT defer replies to a later step — reply immediately after each commit.

### Between comments

After resolving or skipping a comment, transition:

> "Moving to comment #[N+1] of [M]..."

---

## Step 5 — Final Summary

After all comments have been addressed, present a summary:

```
## Fixer Complete — PR #42

### Resolved
- ✅ #1 — [Short description] (solution applied)
- ✅ #3 — [Short description] (solution applied)
- ✅ #4 — [Short description] (custom solution applied)

### Skipped
- ⏭️ #2 — [Short description] (user chose to skip)
- ⏭️ #5 — [Short description] (user chose to skip)

### Non-Actionable (not processed)
- 💬 @reviewer1: "Looks great!" (praise)
- 💬 @reviewer2: "Nice refactor" (praise)

### Stats
- Total review comments: [T]
- Actionable: [A]
- Fixes applied: [X]
- Skipped: [Y]
- Non-actionable: [Z]
```

---

## Step 6 — Push Commits To Remote

After Step 5, run this command as a mandatory final step:

```bash
git push origin HEAD
```

This ensures every commit hash referenced in reviewer replies exists on the PR branch remote and all commit links are valid.

If push fails, report the exact error and stop to let the user decide how to proceed.

---

## Quality Principles

These principles apply throughout the workflow:

- **Faithful to feedback**: Understand what the reviewer actually asked for. Do not misinterpret or over-extend their comment.
- **Evidence-based**: Only propose fixes grounded in the actual code and the reviewer's feedback. Never fabricate issues.
- **Concrete solution**: Every proposed fix must include a real code diff — not just a description of what to change.
- **One at a time**: Never batch-apply fixes. Each comment needs explicit user approval.
- **Minimal changes**: Fix only what the reviewer asked about — do not refactor surrounding code unless the user requests it.
- **Context-aware**: Respect existing codebase conventions. Propose fixes that match the project's style and patterns.
- **No silent changes**: Never modify code without showing the user what will change first.
- **Reviewer respect**: Treat every comment as worth considering, even if the proposed fix differs from what the reviewer suggested.
