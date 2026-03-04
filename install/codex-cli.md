# Install In Codex CLI

Codex CLI loads skills from `~/.codex/skills/<skill-name>/SKILL.md` (or `$CODEX_HOME/skills` if configured).

All install commands below assume `SKILLS_PATH` points to this repository:

```bash
export SKILLS_PATH="/abs/path/to/skills"
```

## Build (Required)

Codex skills need a small YAML frontmatter header. Install them by generating directly into your Codex skills directory:

```bash
python3 "$SKILLS_PATH/scripts/sync.py" --install --codex
```

Restart Codex CLI to pick up new skills.

# Usage

After installing and restarting Codex CLI, invoke a skill by mentioning it explicitly in your prompt.

Examples:

- `Use the creator skill to draft a PR title/description from my current git diff.`
- `Use the reviewer skill to review the changes I made in this repo.`
- `Use the breaker skill to propose how to split this PR into smaller PRs.`
