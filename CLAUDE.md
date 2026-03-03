# Skills Repository

This repository contains reusable development workflow skills for Claude Code and Codex CLI.

## Structure

- `skills/` -- Canonical source prompts (edit these). Also usable directly as Claude Code commands.
- `.claude/commands/` -- Generated Claude Code commands (same content as `skills/`)
- `codex/<skill-name>/SKILL.md` -- Generated Codex CLI skills (YAML frontmatter + skill body)
- `templates/` -- Shared templates referenced by skills (for example PR template)
- `install/` -- Installation guides

## Usage

Skills are templates. Customize them per project by editing `skills/*.md` to match your team's conventions, coding standards, and tooling, then sync:

```bash
python3 scripts/sync.py --write
```

Generated outputs:

- Do not edit `.claude/commands/*.md` or `codex/*/SKILL.md` manually.
- Edit `skills/*.md`, then re-run the sync script.

## Available Skills

| Command | Description |
|---------|-------------|
| 🗺️ `/planner` | Feature implementation planning |
| ✨ `/improver` | Review code and fix all found issues directly |
| 🧪 `/bdder` | BDD test improvement guidance |
| 🌍 `/creator` | PR description & title generator (🟢 Ready) |
| ✂️ `/breaker` | PR splitting into smaller PRs |
| 🩹 `/fixer` | PR revision feedback resolver |
| 🔍 `/reviewer` | Code review (Clean Code, Security, Performance) |
