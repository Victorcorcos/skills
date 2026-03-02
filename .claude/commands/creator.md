# 🌍 Creator

> **Purpose**: Analyze the current branch diff, draft a pull request title and description, generate a `pull_request.md` file, and open the PR on GitHub with appropriate labels.

---

## Step 1 — Diff Size Guard

Before anything else, count the total lines changed:

```bash
git diff upstream/main --stat | tail -1
```

* If the diff exceeds **900 lines changed**, **stop** and warn the user:

> ⚠️ This diff has over 900 lines changed. Consider running `/breaker` first to split it into smaller, reviewable PRs.

* Only proceed if the user explicitly confirms they want to continue.

**Fallback chain** for the diff base — try each in order until one succeeds:
1. `upstream/main`
2. `upstream/master`
3. `origin/main`
4. `origin/master`

Store whichever works as `BASE_REF` and use it throughout.

---

## Step 2 — Analyze Changes

Run the diff against the resolved base:

```bash
git diff $BASE_REF
```

From the diff, extract:

1. **Summary** — What changed and *why* (infer intent from commit messages and code).
2. **Modules Affected** — High-level areas of the codebase touched (e.g. `auth`, `api/payments`, `frontend/dashboard`). This gives reviewers a big-picture view.
3. **Type of change** — Classify as one or more of: bug fix, new feature, breaking change, refactor, documentation, tests.
4. **Breaking changes** — If the diff includes API signature changes, renamed exports, removed endpoints, DB migrations, or anything that could break existing consumers, flag it clearly.
5. **Visual changes** — If UI files were modified, note where screenshots or recordings should be added (use placeholder markers like `<!-- screenshot: description -->`).

---

## Step 3 — Draft the PR Title

Rules:
- **Max 72 characters**
- **Imperative mood** (e.g. "Add payment retry logic", not "Added" or "Adds")
- Clear and specific — a reviewer should understand the scope from the title alone

---

## Step 4 — Draft the PR Description

Use the PR template from the **current project** first:

```
.github/pull_request_template.md
```

If that file does not exist, fall back to the shared template in this skills repository:

```
/skills/templates/pull_request_template.md
```

Fill in every section of the template. Additionally, ensure the description includes:

- **Modules Affected** — List the high-level areas identified in Step 2.
- **Breaking changes** — If any were detected, add a prominent callout:
  > [!WARNING]
  > **Breaking change**: describe what breaks and how consumers should adapt.
- **Screenshot placeholders** — If visual changes were detected, add:
  > [!TIP]
  > Add screenshots or recordings here to help reviewers verify the UI changes.
- Enhance clarity with markdown features: code fences with language tags, tables, blockquotes, GitHub alert admonitions (`[!NOTE]`, `[!TIP]`, `[!WARNING]`, `[!CAUTION]`), mermaid diagrams, collapsible `<details>` blocks — wherever they genuinely help comprehension.

---

## Step 5 — Write the Test Guidance Section

Assume a **tester** (not the developer) will validate this PR. Write step-by-step checks:

- Favor **real user scenarios** — the closer to how an actual user interacts with the system, the better.
- Each step should be concrete and actionable (e.g. "Log in as an admin user → navigate to Settings → click 'Export' → verify the CSV downloads with correct headers").
- Cover the **happy path** first, then edge cases.

---

## Step 6 — Generate `pull_request.md`

Create a file at the **repository root** called `pull_request.md` containing:

```markdown
# PR Title

<the drafted title>

# PR Description

<the full drafted description including test guidance>
```

> [!CAUTION]
> Do **NOT** commit this file. It is a disposable draft for copy-pasting or for the automated PR creation in the next step.

---

## Step 7 — Create the Pull Request

Open the PR on GitHub using `gh`:

```bash
gh pr create --title "<title>" --body-file pull_request.md
```

### Label Selection

After creating the PR, apply the **most relevant** labels from the list below. Choose labels based on the change type and status — typically 1–3 labels are appropriate.

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

> [!NOTE]
> If a label does not exist in the repository, create it first:
> ```bash
> gh label create "label name" --color "HEX" --description ""
> ```
