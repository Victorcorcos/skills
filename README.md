# AI Skills

<div align="center">
  <img src="https://i.imgur.com/dlvWmZ9.png" alt="Skills" width="50%" />
</div>

![Claude Code Skills](https://img.shields.io/badge/Claude_Code-Skills_Collection-7C3AED?style=for-the-badge&logo=data:image/svg+xml;base64,PHN2ZyB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIHZpZXdCb3g9IjAgMCAyNCAyNCIgZmlsbD0id2hpdGUiPjxwYXRoIGQ9Ik0xMiAyQzYuNDggMiAyIDYuNDggMiAxMnM0LjQ4IDEwIDEwIDEwIDEwLTQuNDggMTAtMTBTMTcuNTIgMiAxMiAyem0wIDE4Yy00LjQyIDAtOC0zLjU4LTgtOHMzLjU4LTggOC04IDggMy41OCA4IDgtMy41OCA0LTggOHoiLz48L3N2Zz4=)

A collection of reusable prompts and skills for software development workflows.

This repository supports:

- **Codex CLI** — skills installed into `~/.codex/skills/<skill-name>/SKILL.md`
- **Claude Code** — compatibility command files installed into `.claude/commands/` and invoked as `/creator`, `/planner`, etc.

> [!TIP]
> Quick start:
> - Codex CLI: `python3 "$SKILLS_PATH/scripts/sync.py" --install --codex`
> - Claude Code: `cd <your-project>` then `python3 "$SKILLS_PATH/scripts/sync.py" --install --claude`

> [!NOTE]
> Every skill is a template. Fork this repo, tweak the prompts to match your team's conventions, and commit your own version.

> [!IMPORTANT]
> Pre-requisite: Add the `SKILLS_PATH` ENV to your bash profile:
> ```bash
> export SKILLS_PATH="/abs/path/to/this/repository/skills"
> ```

---

## 🧠 Skills

| Skill | Command | Purpose | Status |
|-------|---------|---------|--------|
| 🗺️ Planner | `/planner` | Plan tasks in sections, execute with approval gates | 🟢 Ready |
| ✨ Improver | `/improver` | Review code and fix all found issues directly | 🟡 Pending |
| 🧪 BDDer | `/bdder` | Improve tests using Behavior Driven Development | 🟢 Ready |
| 🌍 Creator | `/creator` | Generate PR descriptions & titles from diffs | 🟢 Ready |
| ✂️ Breaker | `/breaker` | Split large PRs into smaller, reviewable units | 🟡 Pending |
| 🩹 Fixer | `/fixer` | Resolve PR review feedback efficiently | 🟡 Pending |
| 🔍 Reviewer | `/reviewer` | Review code for Clean Code, Security & Performance | 🟡 Pending |

---

## Workflow

```mermaid
flowchart LR
    A[🗺️ planner] --> B[Coding]
    B --> C[✨ improver]
    B --> D[🧪 bdder]
    C --> E[🌍 creator]
    D --> E[🌍 creator]
    E --> F[Code Review]
    E -->|if large| G[✂️ breaker]
    G --> F
    F --> H[🩹 fixer]

    style A fill:#2563EB,color:#fff
    style C fill:#D97706,color:#fff
    style D fill:#059669,color:#fff
    style E fill:#EA580C,color:#fff
    style F fill:#1e293b,color:#fff
    style G fill:#DC2626,color:#fff
    style H fill:#DB2777,color:#fff
    style B fill:#1e293b,color:#fff
```

---

## 🔧 Installation

### 🌍 Codex CLI - Globally

```bash
python3 "$SKILLS_PATH/scripts/sync.py" --install --codex
```

This installs every skill from `skills/*` into `~/.codex/skills/<skill-name>/SKILL.md`.

Restart Codex CLI to pick up the new skill.

### 🖥️ Claude Code - Locally

From the root of any target repository:

```bash
python3 "$SKILLS_PATH/scripts/sync.py" --install --claude
```

This writes each skill into `<project>/.claude/commands/<skill>.md` with YAML frontmatter removed for Claude command compatibility.

### ⚡ Install all at once

```bash
python3 "$SKILLS_PATH/scripts/sync.py" --install
```

This installs Claude and Codex targets.

### 🔍 Dry run (print paths without writing)

```bash
python3 "$SKILLS_PATH/scripts/sync.py"
```

---

## 🚀 Usage

### 🌍 Codex CLI

```bash
cd <your-project>
codex
# then call it explicitly:
Use the planner skill to plan the implementation of the new feature
# or:
Use the creator skill to generate a PR title and description
```

### 🖥️ Claude Code

```bash
cd <your-project>
claude
# then invoke:
/planner
/creator
/bdder
```

---

## 📖 Skill Descriptions

- 🗺️ **Planner** — Investigates the codebase, plans tasks in structured checkpoint-driven sections saved as `PLAN.md`, then executes section by section with human approval gates.
- ✨ **Improver** — Like Reviewer, but goes further: reviews code for Clean Code, Security, and Performance issues and applies the fixes directly.
- 🧪 **BDDer** — Analyzes changed tests and applies Behavior Driven Development improvements directly.
- 🌍 **Creator** — Reads the current diff / branch and produces a well-structured PR title and description following your team's template.
- ✂️ **Breaker** — Analyzes a large PR and proposes a plan to split it into smaller, independently reviewable pull requests.
- 🩹 **Fixer** — Reads PR review comments and produces best-practice fixes for each piece of feedback.
- 🔍 **Reviewer** — Performs a code review focused on Clean Code principles, security vulnerabilities, and performance concerns.

---

## Example Usage

```bash
# 🗺️ Plan a new feature
claude /planner

# ✨ Review and auto-fix issues in one step
claude /improver

# 🧪 Write code, then improve tests
claude /bdder

# 🌍 Generate the PR description
claude /creator

# ✂️ If the PR is too large
claude /breaker

# 🩹 After receiving review feedback
claude /fixer

# 🔍 Review your own changes
claude /reviewer
```

---

> *"Reusable prompts turn tribal knowledge into shared infrastructure. Write the prompt once, improve it forever."*

---

## Contributing

Contributions are welcome! If you have a skill that fits the development workflow, open a PR with:

1. A new skill folder under `skills/<skill-name>/SKILL.md`
2. A corresponding `skills/<skill-name>/agents/openai.yaml`
3. An updated entry in the skills table above

Then run:

```bash
python3 scripts/sync.py --write
```
