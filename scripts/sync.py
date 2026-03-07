#!/usr/bin/env python3
"""Sync skills into Claude Code and Codex CLI skill targets."""
from __future__ import annotations

import argparse
import os
from pathlib import Path


SKILLS: tuple[str, ...] = (
    "bdder",
    "breaker",
    "creator",
    "fixer",
    "improver",
    "planner",
    "reviewer",
)


def repo_root() -> Path:
    return Path(__file__).resolve().parents[1]


def write_text(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.is_symlink():
        path.unlink()
    if not content.endswith("\n"):
        content += "\n"
    path.write_text(content, encoding="utf-8")


def strip_frontmatter(markdown: str) -> str:
    """Remove YAML frontmatter from SKILL.md before installing as a Claude command."""
    lines = markdown.splitlines(keepends=True)
    if not lines:
        return markdown
    if lines[0].strip() != "---":
        return markdown

    for index in range(1, len(lines)):
        if lines[index].strip() == "---":
            return "".join(lines[index + 1 :]).lstrip("\n")
    return markdown


def sync(
    *,
    write: bool,
    src_dir: Path,
    claude_out_dir: Path | None,
    codex_out_dir: Path | None,
) -> None:
    if not claude_out_dir and not codex_out_dir:
        raise SystemExit(
            "Nothing to do: pass --install, --claude-out, or --codex-out."
        )

    for name in SKILLS:
        src = src_dir / name / "SKILL.md"
        if not src.exists():
            raise SystemExit(f"Missing skill file: {src}")
        body = src.read_text(encoding="utf-8")

        if write:
            if claude_out_dir:
                # Claude Code commands: write a frontmatter-stripped view of the skill.
                dst = claude_out_dir / f"{name}.md"
                write_text(dst, strip_frontmatter(body))
                print(f"Written  (Claude): {dst}")
            if codex_out_dir:
                # Codex CLI: write the canonical source skill as-is.
                dst = codex_out_dir / name / "SKILL.md"
                write_text(dst, body)
                print(f"Written  (Codex):  {dst}")
        else:
            if claude_out_dir:
                print(str(claude_out_dir / f"{name}.md"))
            if codex_out_dir:
                print(str(codex_out_dir / name / "SKILL.md"))


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Sync skills into Claude Code and Codex CLI."
    )
    parser.add_argument(
        "--write",
        action="store_true",
        help="Write synced skill files. Without this, prints the paths that would be written.",
    )
    parser.add_argument(
        "--install",
        action="store_true",
        help=(
            "Install into the current working directory's .claude/commands and your "
            "Codex skills dir. Implies --write."
        ),
    )
    parser.add_argument(
        "--src",
        default=None,
        help="Source skills dir (default: <repo>/skills).",
    )
    parser.add_argument(
        "--claude-out",
        default=None,
        help="Claude commands output dir (frontmatter removed).",
    )
    parser.add_argument(
        "--codex-out",
        default=None,
        help="Codex skills output dir.",
    )
    parser.add_argument(
        "--claude",
        action="store_true",
        help="Install Claude commands only. If neither --claude nor --codex is given, both are installed.",
    )
    parser.add_argument(
        "--codex",
        action="store_true",
        help="Install Codex skills only. If neither --claude nor --codex is given, both are installed.",
    )
    args = parser.parse_args()

    root = repo_root()
    src_dir = Path(args.src).expanduser() if args.src else (root / "skills")
    write = bool(args.write or args.install)

    def default_codex_skills_dir() -> Path:
        codex_home = Path(
            os.environ.get("CODEX_HOME", str(Path.home() / ".codex"))
        ).expanduser()
        return codex_home / "skills"

    if args.install:
        claude_default = Path.cwd() / ".claude" / "commands"
        codex_default = default_codex_skills_dir()
    else:
        claude_default = root / ".claude" / "commands"
        codex_default = root / "codex"

    install_both = not args.claude and not args.codex
    claude_out_dir = (
        (Path(args.claude_out).expanduser() if args.claude_out else claude_default)
        if (args.claude or install_both)
        else None
    )
    codex_out_dir = (
        (Path(args.codex_out).expanduser() if args.codex_out else codex_default)
        if (args.codex or install_both)
        else None
    )

    sync(
        write=write,
        src_dir=src_dir,
        claude_out_dir=claude_out_dir,
        codex_out_dir=codex_out_dir,
    )

    if args.install and write:
        if claude_out_dir:
            print(f"Installed Claude commands to: {claude_out_dir}")
        if codex_out_dir:
            print(f"Installed Codex skills to: {codex_out_dir}")


if __name__ == "__main__":
    main()
