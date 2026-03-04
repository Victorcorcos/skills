#!/usr/bin/env python3
from __future__ import annotations

import argparse
import os
from pathlib import Path


SKILL_DESCRIPTIONS: dict[str, str] = {
    "planner": "Break down a feature request into concrete implementation steps and checklists. Use when asked to plan work, scope tasks, or produce an implementation plan.",
    "improver": "Review code for Clean Code, security, and performance issues, then apply fixes directly. Use when asked to improve code quality and implement fixes.",
    "bdder": "Improve tests using Behavior Driven Development (BDD) structure and naming conventions. Use when asked to rewrite or improve tests in a BDD style.",
    "creator": "Analyze the current git diff and draft a pull request title and description, including test guidance, and generate pull_request.md. Use when asked to draft or create a pull request description/title.",
    "breaker": "Analyze a large set of changes and propose how to split it into smaller, reviewable pull requests. Use when asked to split a PR or reduce diff size.",
    "fixer": "Address PR review feedback by proposing and implementing best-practice fixes. Use when asked to resolve review comments or follow-up changes.",
    "reviewer": "Perform a code review focused on Clean Code, security, and performance. Use when asked for a code review or risk assessment.",
}


def yaml_single_quote(value: str) -> str:
    return "'" + value.replace("'", "''") + "'"


def repo_root() -> Path:
    return Path(__file__).resolve().parents[1]


def write_text(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.is_symlink():
        path.unlink()
    if not content.endswith("\n"):
        content += "\n"
    path.write_text(content, encoding="utf-8")


def build_codex_skill(name: str, body: str) -> str:
    description = SKILL_DESCRIPTIONS.get(name)
    if not description:
        raise SystemExit(f"Missing SKILL_DESCRIPTIONS entry for: {name}")

    frontmatter = "\n".join(
        [
            "---",
            f"name: {name}",
            f"description: {yaml_single_quote(description)}",
            "---",
            "",
        ]
    )
    return frontmatter + body.lstrip("\n")


def sync(
    *,
    write: bool,
    src_dir: Path,
    claude_out_dir: Path | None,
    codex_out_dir: Path | None,
) -> None:
    root = repo_root()

    if not src_dir.exists():
        raise SystemExit(f"Missing source dir: {src_dir}")

    sources = sorted(src_dir.glob("*.md"))
    if not sources:
        raise SystemExit(f"No skills found in: {src_dir}")

    if not claude_out_dir and not codex_out_dir:
        raise SystemExit("Nothing to do: set --claude-out and/or --codex-out (or use --install).")

    for src in sources:
        name = src.stem
        body = src.read_text(encoding="utf-8")

        if write:
            if claude_out_dir:
                claude_out = claude_out_dir / f"{name}.md"
                write_text(claude_out, body)
            if codex_out_dir:
                codex_out = codex_out_dir / name / "SKILL.md"
                write_text(codex_out, build_codex_skill(name, body))
        else:
            if claude_out_dir:
                print(str(claude_out_dir / f"{name}.md"))
            if codex_out_dir:
                print(str(codex_out_dir / name / "SKILL.md"))

    pr_template_src = root / "templates" / "pull_request_template.md"
    if codex_out_dir and pr_template_src.exists():
        pr_template_out = codex_out_dir / "creator" / "assets" / "pull_request_template.md"
        if write:
            write_text(pr_template_out, pr_template_src.read_text(encoding="utf-8"))
        else:
            print(str(pr_template_out))


def main() -> None:
    parser = argparse.ArgumentParser(description="Sync canonical skill prompts to Claude and Codex formats.")
    parser.add_argument(
        "--write",
        action="store_true",
        help="Write outputs. Without this, prints the paths that would be written.",
    )
    parser.add_argument(
        "--install",
        action="store_true",
        help="Install into the current working directory's .claude/commands and your Codex skills dir. Implies --write.",
    )
    parser.add_argument(
        "--src",
        default=None,
        help="Source skills dir (default: <repo>/skills).",
    )
    parser.add_argument(
        "--claude-out",
        default=None,
        help="Claude commands output dir (default: <repo>/.claude/commands).",
    )
    parser.add_argument(
        "--codex-out",
        default=None,
        help="Codex skills output dir (default: <repo>/codex).",
    )
    parser.add_argument(
        "--claude",
        action="store_true",
        help="Write Claude outputs. If neither --claude nor --codex is given, both are written.",
    )
    parser.add_argument(
        "--codex",
        action="store_true",
        help="Write Codex outputs. If neither --claude nor --codex is given, both are written.",
    )
    args = parser.parse_args()
    root = repo_root()
    src_dir = Path(args.src).expanduser() if args.src else (root / "skills")

    write = bool(args.write or args.install)

    def default_codex_skills_dir() -> Path:
        codex_home = Path(os.environ.get("CODEX_HOME", str(Path.home() / ".codex"))).expanduser()
        return codex_home / "skills"

    if args.install:
        # Install into the *current project* for Claude, and global Codex skills dir.
        claude_default = Path.cwd() / ".claude" / "commands"
        codex_default = default_codex_skills_dir()
    else:
        # Build artifacts inside this skills repository.
        claude_default = root / ".claude" / "commands"
        codex_default = root / "codex"

    install_both = not args.claude and not args.codex
    claude_out_dir = (Path(args.claude_out).expanduser() if args.claude_out else claude_default) if (args.claude or install_both) else None
    codex_out_dir = (Path(args.codex_out).expanduser() if args.codex_out else codex_default) if (args.codex or install_both) else None

    sync(write=write, src_dir=src_dir, claude_out_dir=claude_out_dir, codex_out_dir=codex_out_dir)

    if args.install and write:
        # Make it obvious where things went; Codex installs are typically global (not in the project repo).
        if claude_out_dir:
            print(f"Installed Claude commands to: {claude_out_dir}")
        if codex_out_dir:
            print(f"Installed Codex skills to: {codex_out_dir}")


if __name__ == "__main__":
    main()
