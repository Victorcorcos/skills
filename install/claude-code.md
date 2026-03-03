# Install In Claude Code

All commands below assume `SKILLS_PATH` points to this repository:

```bash
export SKILLS_PATH="/abs/path/to/skills"
```

## Option A (Recommended): Sync Commands Into A Project

From a target repository root:

```bash
python3 "$SKILLS_PATH/scripts/sync.py" --install --no-codex
```

## Shared Templates

Some commands (notably `/creator`) may reference shared templates (for example `templates/pull_request_template.md`).

Recommended setup:

1. When a command needs the shared PR template and the project does not have `.github/pull_request_template.md`, use:

```bash
cat "$SKILLS_PATH/templates/pull_request_template.md"
```

## Option B: Copy A Single Command (No Sync)

```bash
mkdir -p .claude/commands
cp "$SKILLS_PATH/skills/creator.md" .claude/commands/
```

# Usage

Run Claude Code in that repo and invoke:

```text
/creator
/reviewer
```
