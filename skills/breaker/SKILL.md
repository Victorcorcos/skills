---
name: breaker
description: 'Open a pull request following the full PR workflow: resolve the base branch, check size limits (split into independent SRP-based branches if over the MAX limit), handle uncommitted changes, build the PR description from the template, run the pre-submit checklist, and open the PR with gh pr create. Use when asked to open a PR, create a pull request, or submit work for review.'
---

# ✂️ Breaker

> **Purpose**: Guide the full PR lifecycle — from resolving the base branch and checking size limits, through writing the PR description, to opening the PR with `gh pr create`. Splits oversized diffs into independent, SRP-based branches created directly from the resolved `BASE_REF` before doing anything else.

---

## Input

| Parameter | Required | Default |                                                  Description                                                  |
|-----------|----------|---------|---------------------------------------------------------------------------------------------------------------|
|   `MAX`   |    No    |  `1000`  | Maximum lines permitted per PR (including tests). Pass as the first argument: `/breaker 1000`, `$breaker 1000`. |

If the user provides an integer argument, use it as `MAX`. Otherwise default to **1000**.

---

## Prerequisites

Before doing anything else, verify that the required tools are installed.

### wisetree

`wisetree` is **required** to run this skill. It manages git worktrees in an organized sibling directory structure with support for copy/ignore patterns (e.g. ENV files).

Main repository: https://github.com/victorcorcos/wisetree

```bash
command -v wisetree >/dev/null 2>&1 && echo "OK" || echo "MISSING"
```

If `wisetree` is **MISSING**, stop immediately and ask the developer:

> "`wisetree` is not installed. It is required by the breaker skill to create organized worktrees for each child PR. Would you like me to install it now?"

Use the `AskUserQuestion` tool with:

1. `label: "Install wisetree"`, `description: "Run npm install -g wisetree and continue"`
2. `label: "Cancel"`, `description: "Stop the breaker skill without making any changes"`

Set `header` to `"Missing dependency"` and `multiSelect` to `false`.

- **Install wisetree**: Run `npm install -g wisetree`, then verify the installation succeeded:

```bash
command -v wisetree >/dev/null 2>&1 && echo "OK" || echo "FAILED"
```

If `OK`, restart the skill from the beginning. If `FAILED`, report the error and stop.

- **Cancel**: Stop the skill entirely.

### gh (GitHub CLI)

```bash
command -v gh >/dev/null 2>&1 && echo "OK" || echo "MISSING"
```

If `gh` is missing or not authenticated, tell the developer and stop.

---

## Resolve the base branch

Before doing anything else, fetch remote refs and resolve the base:

```bash
git fetch --all --prune

BASE_REF=""
for ref in upstream/main upstream/master origin/main origin/master; do
  git rev-parse --verify --quiet "$ref" >/dev/null && BASE_REF="$ref" && break
done
echo "$BASE_REF"   # e.g. upstream/master or upstream/main
```

Store `BASE_REF` and use it throughout (size checks, diffs, PR `--base` flag).

---

## Size limit

- Max **MAX lines per PR** (including tests) — verified by running `git diff $(git merge-base HEAD "$BASE_REF")..HEAD --numstat | awk '{a+=$1;d+=$2} END{print a+d}'`
- **Check this before doing anything else.** If the total exceeds MAX, split into independent PRs following the SRP workflow below

### SRP split workflow

> **This is the most critical part of the breaker skill. Follow it rigorously.**

When the diff exceeds MAX lines, do **not** create dependent/chained branches. Instead, split the work into **independent, self-sufficient PRs** following the Single Responsibility Principle. Every child branch must start directly from `BASE_REF`; if a proposed child needs commits from another child, the split plan is wrong and must be reorganized before any branch is created.

#### 1. Analyze the mother branch

Read every changed file in the diff. Understand the full scope of work — models, services, UI, tests, configs, migrations, etc.

#### 2. Identify semantic boundaries

Group changes by **responsibility**, not by file order or directory. Each group must represent a single, coherent purpose. Good boundaries include:

- A new model/entity + its tests
- A service/use-case + its tests
- A UI component/screen + its tests
- A refactor that enables the feature (extract, rename, restructure) + its tests
- A migration or config change + its tests
- An integration layer (API calls, state management) + its tests

#### 3. Draft a split plan and present it to the developer

Before creating any branch, compute the precise added/subtracted lines for each proposed child PR and present the plan:

```
Split plan for <branch-name>

  Mother branch: +AAA -SSS (TOTAL lines)

  PR 1 — "<short description>"
         Files: ...
         +aaa -sss
  PR 2 — "<short description>"
         Files: ...
         +bbb -sss
  PR 3 — "<short description>"
         Files: ...
         +ccc -sss

  Integrity check:

           Added  Subtracted
  PR 1      +aaa        -sss
  PR 2      +bbb        -sss
  PR 3      +ccc        -sss
  ────────────────────────────
  Total     +AAA        -SSS  ← must match mother branch
```

#### Plan approval — MUST use AskUserQuestion tool

After presenting the split plan, you **MUST** use the `AskUserQuestion` tool to collect the developer's decision. Do NOT simply print the options as text and wait — you MUST invoke the tool.

Always use these two options:

1. `label: "Approve"`, `description: "The split plan looks good. Proceed with creating branches and PRs."`
2. `label: "Reject"`, `description: "The plan needs changes. I'll explain what to adjust."`

The question text must follow this format:
> `"Split plan for <branch-name> (N PRs, TOTAL lines): approve or reject?"`

Set `header` to `"Breaker Plan"` and `multiSelect` to `false`.

#### Handling each option

- **Approve**: Proceed to step 3.1 (save `BREAKER_PLAN.md`) and continue the workflow.

- **Reject** (user typed a custom response via "Other"): Read the developer's explanation of why the plan was rejected. Revise the split plan according to their feedback — adjust boundaries, move files between PRs, merge or split groups, etc. Present the updated plan and ask again with the `AskUserQuestion` tool using the same structure. **Repeat this cycle until the developer approves.**

- **Other** (user typed a custom response): Treat the same as Reject — read their input, revise, and re-present.

**CRITICAL — Do NOT create any branch or write `BREAKER_PLAN.md` until the developer explicitly selects "Approve".**

#### 3.1. Save the approved plan to `BREAKER_PLAN.md`

Once the developer approves, save the split plan to a file named `BREAKER_PLAN.md` in the repository root. This file is the source of truth for the ongoing split process. It must contain:

- The mother branch name and its total `+added -subtracted` lines
- Each child PR with its description, files, branch name, and precise `+added -subtracted` lines
- The integrity table proving the sum of children matches the mother
- A status column to track progress (`pending` / `done`)

Example:

```markdown
# Breaker Plan

Mother branch: `feature/digit-3121-offline-maps` (+512 -1000)

## Child PRs

| #  | Branch | Description | +Added | -Subtracted | Status |
|----|--------|-------------|--------|-------------|--------|
| 1  | `digit3121_offline_maps.1_add_backend` | Add backend layer with persistence, model and controller | +412 | -500 | pending |
| 2  | `digit3121_offline_maps.2_add_frontend` | Add frontend layer with design, layout and proper API requests | +100 | -250 | pending |
| 3  | `digit3121_offline_maps.3_improver_usability` | Improve the usability of related files, following Boy Scout Rule | +0 | -250 | pending |

## Integrity

|           |  Added   | Subtracted |
|-----------|----------|------------|
| Backend   |  +412    |    -500    |
| Frontend  |  +100    |    -250    |
| Usability |    +0    |    -250    |
-------------------------------------
| Total     |  +512    |    -1000   |
| Mother    |  +512    |    -1000   |
| Match     |  yes     |     yes    |
```

Use `BREAKER_PLAN.md` throughout the rest of the workflow to track which child PRs have been created and opened. Update the `Status` column to `done` as each child PR is opened.

#### 4. Create worktrees with wisetree

**Use `wisetree` to create worktrees instead of switching branches.** Each child gets its own working directory with ENV files properly copied — no `git checkout`, no stashing, no risk of cross-contamination.

> [!CAUTION]
> **EVERY child branch MUST be created from `$BASE_REF` (e.g. `upstream/main`, `origin/master`) — NEVER from another child branch, NEVER from the mother branch, NEVER from `HEAD`, and NEVER from the previous worktree's directory.**
>
> The source of every `wisetree create` call must be the resolved `$BASE_REF` itself. All children are **siblings** rooted at the same base — they are not chained, stacked, or created in sequence from each other.

##### Worktree directory structure

`wisetree` creates worktrees in a sibling directory named `{{DIRECTORY_NAME}}.worktree/`. Each worktree inside is named after its branch.

Example — if the skill is invoked inside `/status-survey` with three child branches:

```
/status-survey/                                                      ← mother branch (untouched)
/status-survey.worktree/digit3121_offline_maps.1_add_backend/        ← child worktree 1  (forked from BASE_REF)
/status-survey.worktree/digit3121_offline_maps.2_add_frontend/       ← child worktree 2  (forked from BASE_REF)
/status-survey.worktree/digit3121_offline_maps.3_improver_usability/ ← child worktree 3  (forked from BASE_REF)
```

All three children share the **same starting commit** — the tip of `$BASE_REF`. None of them is a descendant of another.

##### Create each worktree

For each child PR in `BREAKER_PLAN.md`, run these 4 steps from inside the mother repository directory (`$REPO_DIR`) for every child — never from inside another child's worktree:

```bash
REPO_DIR="$(pwd)"                                 # mother repository directory — anchor for the whole loop
REPO_NAME="$(basename "$REPO_DIR")"
BASE_SHA="$(git -C "$REPO_DIR" rev-parse "$BASE_REF")"  # every child must start from exactly this commit
CHILD_BRANCH="digit3121_offline_maps.1_add_backend"  # example — child branches MUST follow `<mother>.<N>_<description>` where N is the 1-based child index
CHILD_DIR="../$REPO_NAME.worktree/$CHILD_BRANCH"

# 0. Sanity-check: you MUST be in the mother repo directory, not inside a previously-created child worktree.
[ "$(pwd)" = "$REPO_DIR" ] || { echo "ERROR: not in mother repo dir"; exit 1; }

# 1. Create the worktree from $BASE_REF only — never from another child branch, the mother branch, or HEAD.
#    -s "$BASE_REF" is mandatory. Do not replace it with a short branch name, HEAD, or a previous child branch.
wisetree create -n "$CHILD_BRANCH" -s "$BASE_REF" -b "$CHILD_BRANCH"

# 2. Verify the new child branch starts at the exact $BASE_REF commit and has zero commits ahead before any work is applied.
[ "$(git -C "$CHILD_DIR" rev-parse HEAD)" = "$BASE_SHA" ] || { echo "ERROR: child does not start at $BASE_REF"; exit 1; }
[ "$(git -C "$CHILD_DIR" rev-list --count "$BASE_REF..HEAD")" = "0" ] || { echo "ERROR: child has commits before population"; exit 1; }

# 3. Enter the worktree to populate it (next sub-section).
cd "$CHILD_DIR"

# 4. Return to the mother directory before starting the next child.
cd "$REPO_DIR"
```

These 4 steps are **mandatory for every child worktree**. The `cd "$REPO_DIR"` at the end is non-negotiable — the next iteration of the loop must always start from the mother repo directory so the next `wisetree create -s "$BASE_REF"` cannot accidentally resolve against a child's git context.

##### Populate each worktree

For each child, copy only the files assigned to that PR from the mother branch into the corresponding worktree directory. Never copy commits, patches, or file state from another child worktree. Then commit inside the worktree:

```bash
cd "../$REPO_NAME.worktree/$CHILD_BRANCH"
# copy/apply the relevant changes from the mother branch
git add -A
git commit -m "PREFIX-XXXX <short description of this child PR>"
cd "$REPO_DIR"
```

**CRITICAL — The mother branch directory must remain untouched.** Never modify files in the mother directory during the split. All changes happen inside worktree directories.

##### Keep worktrees alive

Do **not** remove worktrees after opening PRs. The developer will continue working in these worktree directories to address review feedback, push fixes, and iterate until the PRs are merged. Each worktree is the active working directory for its child PR throughout the entire PR lifecycle.

#### 5. Rules for each child PR

- **Independent**: every PR must build, pass tests, and be mergeable on its own — no PR depends on another PR in the split
- **Self-sufficient**: each PR contains both the implementation **and** all related automated tests for that implementation
- **Single responsibility**: each PR has one clear purpose described in its title
- **All forked from `$BASE_REF`**: every child branch is created directly from `$BASE_REF` (the resolved upstream trunk, e.g. `upstream/main`) and its PR targets `$BASE_REF`. Never fork a child from another child, from the mother branch, from `HEAD`, or from a short branch name that could resolve to the wrong ref — children are siblings of each other, never a chain
- **Within MAX**: every child PR must be ≤ MAX lines
- **Isolated worktree**: each child lives in its own worktree directory — never switch branches in the mother directory, and always run `wisetree create -s "$BASE_REF"` from the mother repo directory (`$REPO_DIR`), never from inside another child's worktree

#### 6. Integrity verification (mandatory)

After populating all worktrees, verify both **lineage** (children must be forked from `$BASE_REF`, not from each other) and **line counts** (children must perfectly partition the mother).

##### 6a. Lineage check — no child may contain another child's commits

For each child worktree, verify two things:

1. The merge-base with `$BASE_REF` equals the tip of `$BASE_REF` itself.
2. No other child branch tip is an ancestor of this child branch.

The first check alone is **not enough**: a child incorrectly created from another child can still have `$BASE_REF` as its merge-base with trunk. The second check catches stacked child branches.

```bash
BASE_SHA="$(git -C "$REPO_DIR" rev-parse "$BASE_REF")"
FAIL=0

for CHILD_BRANCH in <list every child branch from BREAKER_PLAN.md>; do
  CHILD_DIR="../$REPO_NAME.worktree/$CHILD_BRANCH"
  MB="$(git -C "$CHILD_DIR" merge-base HEAD "$BASE_REF")"
  if [ "$MB" = "$BASE_SHA" ]; then
    echo "OK   $CHILD_BRANCH  forked from $BASE_REF"
  else
    echo "FAIL $CHILD_BRANCH  forked from $MB (expected $BASE_SHA)"
    FAIL=1
  fi

  for OTHER_BRANCH in <list every child branch from BREAKER_PLAN.md>; do
    [ "$OTHER_BRANCH" = "$CHILD_BRANCH" ] && continue
    OTHER_SHA="$(git -C "$REPO_DIR" rev-parse "$OTHER_BRANCH")"
    [ "$OTHER_SHA" = "$BASE_SHA" ] && continue

    if git -C "$CHILD_DIR" merge-base --is-ancestor "$OTHER_BRANCH" HEAD; then
      echo "FAIL $CHILD_BRANCH  contains commits from sibling $OTHER_BRANCH"
      FAIL=1
    fi
  done
done

[ "$FAIL" = "0" ] || exit 1
```

Every child must print only `OK` lines and no `FAIL` lines. If any child prints `FAIL`, stop immediately. **Delete that child's worktree and branch, recreate it from `$BASE_REF`, repopulate it only from the mother diff, and rerun the full lineage check** before continuing:

```bash
wisetree remove -n "$CHILD_BRANCH"
git -C "$REPO_DIR" branch -D "$CHILD_BRANCH"
# then re-run the step 4 worktree-creation block for this child with -s "$BASE_REF", ensuring you are in $REPO_DIR
```

##### 6b. Line-count check — children must partition the mother

For each child worktree, run:

```bash
cd "../$REPO_NAME.worktree/$CHILD_BRANCH"
git diff $(git merge-base HEAD "$BASE_REF")..HEAD --numstat | awk '{a+=$1;d+=$2} END{print "+"a, "-"d}'
cd "$REPO_DIR"
```

Then verify:

1. Each child's actual `+added -subtracted` matches the value in `BREAKER_PLAN.md`
2. The sum of all children's `+added` equals the mother's `+added`
3. The sum of all children's `-subtracted` equals the mother's `-subtracted`

- If both sums match → the split is correct
- If they differ → the split is **wrong**. Investigate which changes were lost or duplicated and fix before opening any PR
- **No changes may be added or removed during the split** — the children must be a perfect partition of the mother

Update `BREAKER_PLAN.md` with the actual verified counts if they differ from the estimates.

#### 7. Branch naming

Child branches **must** follow the pattern `<mother-branch>.<N>_<description>`, where `N` is the 1-based index of the child within the split plan and `<description>` is a short snake_case summary of that PR's responsibility. The branch name doubles as the worktree directory name.

For example, if the mother branch is `digit3347_create_mention_sidepanel`, the children must be named:

```
digit3347_create_mention_sidepanel.1_child1_description
digit3347_create_mention_sidepanel.2_child2_description
digit3347_create_mention_sidepanel.3_child3_description
digit3347_create_mention_sidepanel.4_child4_description
```

Concrete naming examples mapped to their worktree paths:

```
<original-branch>.1_add_backend        → worktree at <repo>.worktree/<original-branch>.1_add_backend/
<original-branch>.2_add_frontend       → worktree at <repo>.worktree/<original-branch>.2_add_frontend/
<original-branch>.3_improver_usability → worktree at <repo>.worktree/<original-branch>.3_improver_usability/
```

The numeric prefix after the `.` is mandatory — it preserves the order of the split and makes child PRs easy to scan against `BREAKER_PLAN.md`.

---

## Uncommitted changes

Before writing the PR title and description, check for uncommitted work:

1. Run `git status` to detect staged, unstaged, or untracked changes
2. If any exist, **ask the developer only**: which files should be included in this commit?
3. Wait for confirmation before staging anything
4. Generate the commit message from the diff following the PR title format defined in this doc — do not ask the developer for it
5. Only then proceed to writing the PR title and description

Never assume all uncommitted changes belong to the current PR — the developer may have unrelated work in progress.

---

## PR Title

- Format: `PREFIX-XXXX <plain-language summary>` — e.g. `DIGIT-3121 Add offline support for map view` or `DPMS-42 Fix session timeout`
- Extract the ticket number from the branch name (see **Ticket number** section below) before writing the title
- Title must be a short, plain-language summary of the change (no conventional commits style required)
- **For split PRs only**: append `(N/TOTAL)` at the end of the title to indicate which child this is — e.g. `DIGIT-3121 Add backend layer (1/3)`, `DIGIT-3121 Add frontend layer (2/3)`, `DIGIT-3121 Improve usability (3/3)`

## PR Description

- Write for **non-technical stakeholders** (QA, PO): explain *what* changed and *why*, not *how*
- Avoid deep technical jargon; a QA engineer or Product Owner must understand the purpose without reading code

## Ticket number

1. Extract from the branch name using the case-insensitive regex `([A-Z]+)-?(\d+)` (matches `DIGIT-3023`, `digit3023`, `digit-3023`, `DPMS-42`, `dpms42`, `DUV-100`, `duv-100`, `duv100`, `ETC-7`, `etc7`, etc.) — normalise to `UPPERCASE-NUMBER` in the PR title (e.g. `dpms42` → `DPMS-42`, `duv100` → `DUV-100`)
2. If the branch name does not match, ask the developer for the ticket number
3. If the developer does not know the ticket number, omit it from both the PR title and the Plane Ticket section — **do not write any placeholder text** such as "No ticket number provided"; remove the section entirely

---

## Opening the PR

Always write the PR body to a temp file and use `--body-file`. Never pass the body inline with `--body "..."` because PR descriptions contain markdown backticks that trigger the backtick-command-substitution hook.

### Single PR (diff within MAX)

Run from the current working directory:

```sh
cat > /tmp/pr_body.md << 'ENDBODY'
# Description ✍️
...
ENDBODY

GH_USER=$(gh api user --jq '.login')
REPO=$(gh repo view --json nameWithOwner --jq '.nameWithOwner')
BRANCH=$(git branch --show-current)

git push origin "$BRANCH"

gh pr create \
  --repo "$REPO" \
  --base "$(echo "$BASE_REF" | sed 's|.*/||')" \
  --head "$GH_USER:$BRANCH" \
  --title "PREFIX-XXXX Summary" \
  --body-file /tmp/pr_body.md
```

### Split PRs (one per child)

Each child PR gets its **own independent PR title and description**, written separately according to its responsibility. Repeat the following block for every child in `BREAKER_PLAN.md`, substituting that child's branch name, title, and body:

```sh
cd "../$REPO_NAME.worktree/$CHILD_BRANCH"

cat > /tmp/pr_body.md << 'ENDBODY'
# Description ✍️
...
ENDBODY

GH_USER=$(gh api user --jq '.login')
REPO=$(gh repo view --json nameWithOwner --jq '.nameWithOwner')
BRANCH=$(git branch --show-current)

git push origin "$BRANCH"

gh pr create \
  --repo "$REPO" \
  --base "$(echo "$BASE_REF" | sed 's|.*/||')" \
  --head "$GH_USER:$BRANCH" \
  --title "PREFIX-XXXX Child summary (N/TOTAL)" \
  --body-file /tmp/pr_body.md

cd "$REPO_DIR"
```

After each child PR is created, update the `Status` column in `BREAKER_PLAN.md` to `done`.

---

## PR Template

Use the PR template from the current project first:

`.github/pull_request_template.md`

If that file does not exist, fall back to the shared template that ships with this skills pack. Prefer this lookup order:

1. `$SKILLS_PATH/skills/breaker/references/pull_request_template.md` (when `SKILLS_PATH` is set, common for Claude Code installs)
2. `~/.codex/skills/breaker/references/pull_request_template.md` (common for Codex CLI installs)
3. `skills/breaker/references/pull_request_template.md` (when working inside this skills repository)

Fill in every section of the template. The Ticket section is always the **last** section — omit it entirely when no ticket number is available.

### Description ✍️

- Plain language, no jargon — written for QA and PO
- Use a `> [!NOTE]` alert to highlight the core task being done (the user story being implemented, or the problem being solved, or the refactor being implemented, etc)
- Also explain why this step is required and what it brings to the system (the pull request value)
- If the change has a visible user impact, state it in one sentence

### Overview 🔍

- If the feature has an UI change in the system, leave a `<details>` collapsible placeholder for screenshots/GIFs with a `| Before | After |` table — the developer fills these in, the agent cannot capture UI
- If the feature does not have a UI change, **generate** a `mermaid` diagram inside a `<details>` block derived from the code that illustrates the flow of the feature being implemented or the architecture changes:

```mermaid
flowchart LR
    A[User taps button] --> B[Action dispatched] --> C[State updated] --> D[UI re-renders]

    style A fill:#dbeafe,stroke:#2563eb,stroke-width:2px,color:#1e3a8a
    style B fill:#e9d5ff,stroke:#7c3aed,stroke-width:2px,color:#4c1d95
    style C fill:#dcfce7,stroke:#16a34a,stroke-width:2px,color:#14532d
    style D fill:#fef3c7,stroke:#d97706,stroke-width:2px,color:#92400e
```

- Another possibility is to make a markdown table for the feature, displaying what the PR is implemented in an easier way to understand
- Use `> [!WARNING]` for known limitations or risks reviewers must be aware of
- Enhance clarity with markdown features: code fences with language tags, tables, blockquotes, GitHub alert admonitions, mermaid diagrams, `<details>` blocks, etc.

### Test Guidance 🦮

Assume a tester (not the developer) will validate this PR. Write numbered step-by-step checks that include:

- **Preconditions**: Setup, test data, or permissions required before testing
- **Concrete actions**: Reference specific pages, endpoints, buttons, or CLI commands the tester should interact with
- **Expected results**: State what the tester should observe after each action (e.g. "The toast shows 'Payment saved'", "The API returns 200 with `{ status: 'ok' }`")
- **Happy path first**, then edge cases (e.g. invalid input, empty state, unauthorized access)
- **Regression checks**: If the change touches shared code, note areas that should still work as before

### Ticket 🎫

- If `TICKET` was resolved, add a link: `[TICKET](link/to/TICKET)` (following the `pull_request_template.md` ticket guidance and the extract ticket title and code)
- If no ticket was resolved, remove this section entirely — do **not** write any placeholder text

## Pre-submit checklist

**Do not open the PR until every item below passes.**

### Size gate

```sh
git diff $(git merge-base HEAD "$BASE_REF")..HEAD --numstat | awk '{a+=$1;d+=$2} END{print a+d}'
```

**Single PR** — verify before opening:

- Total lines are within MAX. If not, stop and run the SRP split workflow first.
- No uncommitted changes remain that belong to this PR.

**Split PRs** — run the size gate from inside each child worktree and also verify:

- Every child PR is within MAX lines.
- The sum of all child PR lines equals the mother branch total. If not, changes were lost or duplicated during the split — fix before opening any PR.
- Every child PR is independent and self-sufficient.

When all checks pass, proceed to **Opening the PR**.

---

## Final Summary

After all PRs have been opened, print a summary to the terminal.

### Split PRs

```
## Breaker Complete

### PRs Opened

| # |    Branch    |   PR URL   |          Worktree Path          |
|---|--------------|------------|---------------------------------|
| 1 | `<branch-1>` | <pr-url-1> | `<absolute-path-to-worktree-1>` |
| 2 | `<branch-2>` | <pr-url-2> | `<absolute-path-to-worktree-2>` |
| 3 | `<branch-3>` | <pr-url-3> | `<absolute-path-to-worktree-3>` |

### Stats
- Total PRs opened: N
- Mother branch: <branch-name> (+AAA -SSS lines)
- Each worktree is still live — continue work there to address review feedback.
```

### Single PR

```
## Breaker Complete

### PR Opened

|   Branch   |  PR URL  |
|------------|----------|
| `<branch>` | <pr-url> |
```
