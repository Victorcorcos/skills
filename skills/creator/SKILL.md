---
name: creator
description: 'Analyze the current git diff, draft a pull request title and description, generate a pull_request.md file, and open the PR on GitHub with labels. Use when asked to draft, create, or open a pull request.'
---

# 🌍 Creator

> **Purpose**: Analyze the current branch diff, draft a pull request title and description, generate a `pull_request.md` file, and open the PR on GitHub with appropriate labels.

---

## Step 1 — Diff Size Guard

Before anything else, resolve a diff base and estimate the diff size.

**Fallback chain** for the diff base, try each in order until one succeeds:
1. `upstream/main`
2. `upstream/master`
3. `origin/main`
4. `origin/master`

Store whichever works as `BASE_REF` and use it throughout.

Resolve `BASE_REF`:

```bash
BASE_REF=""
for ref in upstream/main upstream/master origin/main origin/master; do
  git rev-parse --verify --quiet "$ref" >/dev/null && BASE_REF="$ref" && break
done

test -n "$BASE_REF" && echo "$BASE_REF"
```

Then count total lines changed (insertions + deletions):

```bash
git diff "$BASE_REF" --numstat | awk '{adds+=$1; dels+=$2} END {print adds+dels}'
```

If the diff exceeds **900 lines changed**, stop and warn the user to consider running `/breaker` first.
Only proceed if the user explicitly confirms they want to continue.

---

## Step 2 — Analyze Changes

Run the diff against the resolved base:

```bash
git diff "$BASE_REF"
```

From the diff, extract:

1. **Summary**: What changed and why (infer intent from commits and code).
2. **Modules affected**: High-level areas of the codebase touched.
3. **Type of change**: bug fix, new feature, breaking change, refactor, docs, tests.
4. **Breaking changes**: API signature changes, removed endpoints, migrations, etc.
5. **Visual changes**: If UI files changed, note where screenshots/recordings should be added.

---

## Step 3 — Extract Ticket Number

Extract the ticket number from the current branch name using this regex:

```
(DIGIT|digit|DPMS|dpms)-?(\d+)
```

```bash
git rev-parse --abbrev-ref HEAD
```

Normalise the match to uppercase with a hyphen separator (e.g. `DIGIT-3131`, `DPMS-4314`).

Examples of branch names that match:
- `digit-3131` → `DIGIT-3131`
- `DIGIT3131` → `DIGIT-3131`
- `feature/dpms-4314-add-login` → `DPMS-4314`
- `DPMS1492_some_feature` → `DPMS-1492`

**If the branch name does not match**, ask the developer:

> "I couldn't find a ticket number in the branch name. Do you have one? (e.g. DIGIT-3131)"

**If the developer does not know or skips**, omit the ticket entirely:
- Do **not** add it to the PR title.
- Remove the `# Plane Ticket 🎫` section from `pull_request.md` completely — do not write any placeholder text.

Store the resolved ticket (or absence of one) as `TICKET` and use it in Steps 4 and 6.

---

## Step 4 — Draft The PR Title

Rules:

- Max 72 characters
- Imperative mood (for example "Add payment retry logic")
- Specific enough that reviewers understand scope from the title alone
- If `TICKET` was resolved, prefix the title: `TICKET Description` (e.g. `DIGIT-3131 Add payment retry logic`)
- If `TICKET` is absent, omit the prefix entirely

---

## Step 4 — Draft The PR Description

Use the PR template from the current project first:

`.github/pull_request_template.md`

If that file does not exist, fall back to the shared template that ships with this skills pack. Prefer this lookup order:

1. `$SKILLS_PATH/skills/creator/references/pull_request_template.md` (when `SKILLS_PATH` is set, common for Claude Code installs)
2. `~/.codex/skills/creator/references/pull_request_template.md` (common for Codex CLI installs)
3. `skills/creator/references/pull_request_template.md` (when working inside this skills repository)

Fill in every section of the template. Additionally, ensure the description includes:

- **Modules affected**: The areas identified in Step 2.
- **Breaking changes**: If any were detected, add a prominent warning callout.
- **Screenshot placeholders**: If visual changes were detected, add placeholders where screenshots should go.
- Enhance clarity with markdown features: code fences with language tags, tables, blockquotes, GitHub alert admonitions, mermaid diagrams, `<details>` blocks, etc.

---

## Step 5 — Write The Test Guidance Section

Assume a tester (not the developer) will validate this PR. Write step-by-step checks:

- Favor real user scenarios.
- Cover the happy path first, then edge cases.

---

## Step 6 — Generate `pull_request.md`

Create a file at the repository root called `pull_request.md` containing **only the PR body** — no title, no wrapper headings.

The file must start directly with the first section from the PR template (e.g. `# Description ✍️`) and contain the full description including test guidance:

```markdown
# Description ✍️

<the drafted description>

# Overview 🔍

<overview, screenshots, etc.>

# Checks ☑️

- [ ] ...

# Test Guidance 🧪

<step-by-step tester instructions>

# Plane Ticket 🎫                          ← include ONLY if TICKET was resolved

[DIGIT-3131](https://plane.oxean.com.br/oxeanbits/browse/DIGIT-3131)
```

> **Important**:
> - Do NOT add a `# PR Title` section or a `# PR Description` wrapper. The title is passed via `--title` to `gh pr create`; this file is used as `--body-file` and is the description verbatim.
> - If no ticket was resolved, remove the `# Plane Ticket 🎫` section entirely. Do **not** write any placeholder text such as `DIGIT-XXXX` or "No ticket number provided".

Do not commit this file.

---

## Step 7 — Create The Pull Request (Optional)

### Pre-flight: resolve owner and branch

`gh pr create` will abort if it detects uncommitted files (like the freshly generated `pull_request.md`) and no `--head` flag is given. Always supply `--head` in `owner:branch` format and `--base` explicitly to avoid both issues.

Resolve the required values first:

```bash
# Remote owner (GitHub username or org that owns the repo)
GH_OWNER=$(gh repo view --json owner --jq '.owner.login')

# Current branch name
GH_BRANCH=$(git rev-parse --abbrev-ref HEAD)

# Base branch (master or main — match the repo default)
GH_BASE=$(gh repo view --json defaultBranchRef --jq '.defaultBranchRef.name')

echo "$GH_OWNER:$GH_BRANCH → $GH_BASE"
```

### Create the PR

```bash
gh pr create \
  --title "<title>" \
  --body-file pull_request.md \
  --head "$GH_OWNER:$GH_BRANCH" \
  --base "$GH_BASE"
```

> **Why `--head owner:branch`?**
> Without it, `gh` aborts when it finds any uncommitted file in the working tree (including `pull_request.md` itself).
> The bare `--head branch` form also fails with *"Head sha can't be blank"* because GitHub's API requires the fully-qualified `owner:branch` reference.

### Push the branch first if needed

If the branch has not been pushed to the remote yet, push it before creating the PR:

```bash
git push origin "$GH_BRANCH"
```

### Label Selection

After creating the PR, apply the most relevant labels (typically 1 to 3). Choose labels based on the change type and status.

| Color | Label | Apply when… |
|-------|-------|-------------|
| `#7157FF` | `user story 💬` | The PR implements a user-facing feature or story |
| `#FF0000` | `bug 🐛` | The PR fixes a bug |
| `#CC317C` | `technical debt 🛠️` | The PR addresses tech debt or cleanup |
| `#EFF714` | `WIP 🚧` | The PR is not yet complete |
| `#0075ca` | `documentation 📖` | The PR is primarily documentation |
| `#101c73` | `architecture 🏰` | The PR changes architectural patterns |
| `#0052CC` | `security 🛡️` | The PR addresses security concerns |
| `#541AE7` | `automated tests 🤖` | The PR adds or modifies tests |
| `#BFD4F2` | `enhancement ⏫` | The PR enhances existing functionality |
| `#0052CC` | `dependencies 🔗` | The PR updates dependencies |
| `#FFFF00` | `revert ⏪` | The PR reverts a previous change |
| `#D692BB` | `spike 🕸️` | The PR is exploratory / proof-of-concept |

```bash
gh pr edit --add-label "label1,label2"
```

If a label does not exist in the repository, create it first:

```bash
gh label create "label name" --color "HEX" --description ""
```
