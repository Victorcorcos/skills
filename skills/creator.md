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

## Step 3 — Draft The PR Title

Rules:

- Max 72 characters
- Imperative mood (for example "Add payment retry logic")
- Specific enough that reviewers understand scope from the title alone

---

## Step 4 — Draft The PR Description

Use the PR template from the current project first:

`.github/pull_request_template.md`

If that file does not exist, fall back to the shared template that ships with this skills pack. Prefer this lookup order:

1. `$SKILLS_PATH/templates/pull_request_template.md` (when `SKILLS_PATH` is set, common for Claude Code installs)
2. `~/.codex/skills/creator/assets/pull_request_template.md` (common for Codex CLI installs)
3. `templates/pull_request_template.md` (when working inside this skills repository)

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

Create a file at the repository root called `pull_request.md` containing:

```markdown
# PR Title

<the drafted title>

# PR Description

<the full drafted description including test guidance>
```

Do not commit this file.

---

## Step 7 — Create The Pull Request (Optional)

Open the PR on GitHub using `gh`:

```bash
gh pr create --title "<title>" --body-file pull_request.md
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
