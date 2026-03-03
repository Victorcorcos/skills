# Install

This repository supports two different "skills" systems:

- Claude Code commands (installed into `.claude/commands/`, invoked as `/creator`, `/reviewer`, etc.)
- Codex CLI skills (installed into `${CODEX_HOME:-~/.codex}/skills/<skill-name>/SKILL.md`, invoked inside the prompt)

Guides:

- `install/claude-code.md`
- `install/codex-cli.md`

One-command sync (run from a target project repo root):

```bash
python3 "$SKILLS_PATH/scripts/sync.py" --install
```
