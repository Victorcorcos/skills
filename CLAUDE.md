# Skills Repository

This repository contains reusable development workflow skills for Claude Code.

## Structure

- `.claude/commands/` -- Each `.md` file is a skill invokable with `/skillname`
- `templates/` -- Shared templates referenced by skills (e.g. PR template)

## Usage

Skills are templates. Customize them per project by editing the markdown files to match your team's conventions, coding standards, and tooling.

## Available Skills

| Command | Description |
|---------|-------------|
| `/creator` | PR description & title generator |
| `/breaker` | PR splitting into smaller PRs |
| `/reviewer` | Code review (Clean Code, Security, Performance) |
| `/bdder` | BDD test improvement guidance |
| `/planner` | Feature implementation planning |
| `/fixer` | PR revision feedback resolver |
