# AGENTS.md

## Repository Purpose

This repository is the source of truth for reusable AI skills.

- Author skills once under `skills/<skill-name>/`.
- Install them into Codex CLI and Claude Code with repository tooling.
- Optimize for portable skill folders first, and provider-specific metadata second.

## Canonical Skill Layout

Each skill lives in its own directory under `skills/`.

Required:

- `skills/<skill-name>/SKILL.md`
- `skills/<skill-name>/agents/openai.yaml`

Optional, only when the skill actually uses them:

- `skills/<skill-name>/scripts/`
- `skills/<skill-name>/references/`
- `skills/<skill-name>/assets/`

Do not add empty folders just to match another skill. `scripts/`, `references/`, and `assets/` exist only when the instructions explicitly depend on them.

## When To Add Support Folders

Add `scripts/` when:

- the skill must call external APIs
- the workflow needs deterministic parsing or formatting
- the task would be unsafe or fragile as prompt-only instructions
- the same command sequence would otherwise be repeated in multiple places

Add `references/` when:

- the skill needs templates
- the skill depends on long examples or fixed structured content
- the supporting text would make `SKILL.md` harder to route or maintain

Do not add either folder unless `SKILL.md` actually references it.

## Cross-Tool Source Of Truth

`SKILL.md` is the canonical source file for every skill in this repository.

Use these rules:

- Start `SKILL.md` with YAML frontmatter.
- Include at least `name` and `description`.
- Keep `name` identical to the folder name and use kebab-case.
- Write `description` as routing guidance: when to use the skill, what problem it solves, and any important trigger constraints.
- Keep shared `SKILL.md` content portable across Codex CLI and Claude Code whenever possible.
- Put OpenAI-specific UI and policy metadata in `agents/openai.yaml`, not in the shared instructions body.

## Skill Authoring Rules

Write skills so another coding agent can execute them deterministically.

- State the purpose first.
- Specify the minimum inputs the agent must collect.
- Define exact outputs the agent must return.
- Separate read-only and side-effecting modes when applicable.
- List required environment variables explicitly.
- Prefer concise numbered workflows over long narrative prose.
- Reference support files by path when needed.
- Keep `SKILL.md` focused; move bulky templates, examples, or long reference material into `references/`.
- If a workflow depends on non-trivial automation, put it in `scripts/` and have the skill call that script instead of re-implementing the logic in prompt text.
- Never require secrets to be pasted into chat; read them from environment variables.

## Provider Guidance

### Codex CLI

- The modern project-local pattern is `.agents/skills/<skill-name>/SKILL.md`.
- Global skills are commonly installed under `~/.codex/skills/<skill-name>/SKILL.md`.
- `agents/openai.yaml` is recommended in this repository for Codex-specific metadata such as display name, default prompt, invocation policy, and dependency declarations.

For `agents/openai.yaml`, prefer:

- `interface.display_name`
- `interface.short_description`
- `interface.default_prompt`
- `policy.allow_implicit_invocation`

Only declare dependencies that are real and maintained.

### Claude Code

- Prefer `.claude/skills/<skill-name>/SKILL.md` for real skills.
- Treat `.claude/commands/` as legacy slash-command compatibility, not the canonical skill model.
- Claude uses the skill `description` to decide whether to load a skill, so the description must be specific and action-oriented.
- Keep the main skill file focused and move large supporting material into adjacent files.

## Repository-Specific Maintenance

When adding, removing, or renaming a skill in this repository:

- create or update `skills/<skill-name>/SKILL.md`
- create or update `skills/<skill-name>/agents/openai.yaml`
- add `scripts/` or `references/` only if the skill uses them
- update the `SKILLS` mapping in `scripts/sync.py`
- update `README.md` so the public skill list and installation instructions stay accurate and up-to-date

If a helper script is required, prefer calling it through a stable repository-resolved path such as `SKILLS_PATH` or a path relative to the skill directory.

## Compatibility Guardrails

This repository currently includes installer logic that still targets Claude slash commands. Do not use that legacy install target as the model for new skill design.

Author new skills against the modern folder-based skill pattern:

- Codex CLI: `.agents/skills/` or `~/.codex/skills/`
- Claude Code: `.claude/skills/`

Then keep the installer and documentation aligned with that source model.

## Practical Checklist

Before finishing a skill change, verify:

- folder name, frontmatter `name`, and command name match
- `description` clearly explains when the skill should be invoked
- `SKILL.md` names every required input, output, and safety boundary
- support folders are present only when referenced
- `agents/openai.yaml` exists and matches the skill behavior
- README and installer metadata were updated if the skill catalog changed
