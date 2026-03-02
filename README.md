# Claude Code Skills

<div align="center">
  <img src="https://i.imgur.com/fzm96J1.png" alt="Skills" />
</div>

![Claude Code Skills](https://img.shields.io/badge/Claude_Code-Skills_Collection-7C3AED?style=for-the-badge&logo=data:image/svg+xml;base64,PHN2ZyB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIHZpZXdCb3g9IjAgMCAyNCAyNCIgZmlsbD0id2hpdGUiPjxwYXRoIGQ9Ik0xMiAyQzYuNDggMiAyIDYuNDggMiAxMnM0LjQ4IDEwIDEwIDEwIDEwLTQuNDggMTAtMTBTMTcuNTIgMiAxMiAyem0wIDE4Yy00LjQyIDAtOC0zLjU4LTgtOHMzLjU4LTggOC04IDggMy41OCA4IDgtMy41OCA4LTggOHoiLz48L3N2Zz4=)

A collection of reusable prompts and skills for software development workflows, designed for use with [Claude Code](https://docs.anthropic.com/en/docs/claude-code). Each skill encapsulates best practices for a specific phase of the development lifecycle -- from planning features to splitting oversized PRs.

> [!TIP]
> **Quick start** -- invoke any skill directly inside Claude Code:
> ```bash
> claude /creator    # generate a PR title & description
> claude /reviewer   # run a code review
> ```

> [!NOTE]
> Every skill is a template. Fork this repo, tweak the prompts to match your team's conventions, and commit your own version.

---

## Skills

| Skill | Command | Purpose | Status |
|-------|---------|---------|--------|
| 🗺️ Planner | `/planner` | Break down features into implementation steps | 🟡 Pending |
| ✨ Improver | `/improver` | Review code and fix all found issues directly | 🟡 Pending |
| 🧪 BDDer | `/bdder` | Improve tests using Behavior Driven Development | 🟡 Pending |
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

<details>
<summary><strong>Installation & Setup</strong></summary>

### 1. Clone the repository

```bash
git clone https://github.com/<your-user>/skills.git
```

### 2. Use the skills in any project

**Option A -- Symlink the commands directory:**

```bash
# From your target project root
ln -s /path/to/skills/.claude/commands .claude/commands
```

**Option B -- Copy individual skills:**

```bash
mkdir -p .claude/commands
cp /path/to/skills/.claude/commands/reviewer.md .claude/commands/
```

### 3. Invoke with Claude Code

```bash
claude           # start Claude Code
# then type:
/reviewer        # run the reviewer skill
/creator         # generate a PR description
```

</details>

<details>
<summary><strong>Skill Descriptions</strong></summary>

- 🗺️ **Planner** -- Takes a feature request and breaks it down into concrete implementation steps with checkmarks.
- ✨ **Improver** -- Like Reviewer, but goes further: reviews code for Clean Code, Security, and Performance issues and applies the fixes directly.
- 🧪 **BDDer** -- Examines existing tests and suggests improvements using Behavior Driven Development patterns (Given / When / Then).
- 🌍 **Creator** -- Reads the current diff / branch and produces a well-structured PR title and description following your team's template.
- ✂️ **Breaker** -- Analyzes a large PR and proposes a plan to split it into smaller, independently reviewable pull requests.
- 🩹 **Fixer** -- Reads PR review comments and produces best-practice fixes for each piece of feedback.
- 🔍 **Reviewer** -- Performs a code review focused on Clean Code principles, security vulnerabilities, and performance concerns.

</details>

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

1. A new `.md` file in `.claude/commands/`
2. An updated entry in the skills table above
