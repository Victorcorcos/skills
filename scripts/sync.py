#!/usr/bin/env python3
"""Sync skills into Claude Code, Codex CLI, and OpenCode skill targets."""
from __future__ import annotations

import argparse
import os
from pathlib import Path
import shutil


SKILLS: tuple[str, ...] = (
    "tester",
    "bugkiller",
    "breaker",
    "coverager",
    "creator",
    "filler",
    "fixer",
    "improver",
    "planner",
    "reviewer",
)

RENAMED_SKILLS: dict[str, str] = {
    "investigator": "bugkiller",
    "bdder": "tester",
}


def repo_root() -> Path:
    return Path(__file__).resolve().parents[1]


def write_text(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.is_symlink():
        path.unlink()
    if not content.endswith("\n"):
        content += "\n"
    path.write_text(content, encoding="utf-8")


def copy_skill_dir(src: Path, dst: Path) -> None:
    if dst.is_symlink() or dst.is_file():
        dst.unlink()
    elif dst.exists():
        shutil.rmtree(dst)
    shutil.copytree(src, dst)


def cleanup_legacy_claude_commands(
    claude_out_dir: Path, write: bool
) -> None:
    """Remove stale `.claude/commands/<skill>.md` files left over from the
    pre-folder Claude install layout. Only files whose stem matches a skill in
    SKILLS are removed — anything else the user authored stays untouched."""
    legacy_dir = claude_out_dir.parent / "commands"
    if not legacy_dir.is_dir():
        return
    for name in (*SKILLS, *RENAMED_SKILLS):
        legacy_file = legacy_dir / f"{name}.md"
        if not legacy_file.is_file():
            continue
        if write:
            legacy_file.unlink()
            print(f"Removed  (Claude legacy): {legacy_file}")
        else:
            print(f"Would remove (Claude legacy): {legacy_file}")


def cleanup_renamed_skill_dirs(out_dir: Path, label: str, write: bool) -> None:
    """Remove installed skill folders left over from known renames."""
    for old_name, new_name in RENAMED_SKILLS.items():
        stale_dir = out_dir / old_name
        new_dir = out_dir / new_name
        if not stale_dir.exists() or stale_dir == new_dir:
            continue
        if write:
            if stale_dir.is_symlink() or stale_dir.is_file():
                stale_dir.unlink()
            else:
                shutil.rmtree(stale_dir)
            print(f"Removed  ({label} renamed skill): {stale_dir}")
        else:
            print(f"Would remove ({label} renamed skill): {stale_dir}")


def sync(
    *,
    write: bool,
    src_dir: Path,
    claude_out_dir: Path | None,
    codex_out_dir: Path | None,
    opencode_out_dir: Path | None,
) -> None:
    if not claude_out_dir and not codex_out_dir and not opencode_out_dir:
        raise SystemExit(
            "Nothing to do: pass --install, --claude-out, --codex-out, or --opencode-out."
        )

    for name in SKILLS:
        skill_src = src_dir / name
        src = skill_src / "SKILL.md"
        if not src.exists():
            raise SystemExit(f"Missing skill file: {src}")

        if write:
            for label, out_dir in (
                ("Claude", claude_out_dir),
                ("Codex", codex_out_dir),
                ("OpenCode", opencode_out_dir),
            ):
                if not out_dir:
                    continue
                dst = out_dir / name
                copy_skill_dir(skill_src, dst)
                print(f"Written  ({label}): {dst}")
        else:
            for out_dir in (claude_out_dir, codex_out_dir, opencode_out_dir):
                if out_dir:
                    print(str(out_dir / name / "SKILL.md"))

    if claude_out_dir:
        cleanup_legacy_claude_commands(claude_out_dir, write)
    for label, out_dir in (
        ("Claude", claude_out_dir),
        ("Codex", codex_out_dir),
        ("OpenCode", opencode_out_dir),
    ):
        if out_dir:
            cleanup_renamed_skill_dirs(out_dir, label, write)


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Sync skills into Claude Code, Codex CLI, and OpenCode."
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
            "Install into the current working directory's .claude/skills and your "
            "Codex/OpenCode skills dirs. Implies --write."
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
        help="Claude skills output dir (full skill folder copied).",
    )
    parser.add_argument(
        "--codex-out",
        default=None,
        help="Codex skills output dir.",
    )
    parser.add_argument(
        "--opencode-out",
        default=None,
        help="OpenCode skills output dir.",
    )
    parser.add_argument(
        "--claude",
        action="store_true",
        help="Install Claude commands only. If no target flags are given, all targets are installed.",
    )
    parser.add_argument(
        "--codex",
        action="store_true",
        help="Install Codex skills only. If no target flags are given, all targets are installed.",
    )
    parser.add_argument(
        "--opencode",
        action="store_true",
        help="Install OpenCode skills only. If no target flags are given, all targets are installed.",
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
        claude_default = Path.cwd() / ".claude" / "skills"
        codex_default = default_codex_skills_dir()
        opencode_default = Path.home() / ".config" / "opencode" / "skills"
    else:
        claude_default = root / ".claude" / "skills"
        codex_default = root / "codex"
        opencode_default = root / "opencode"

    install_all = not args.claude and not args.codex and not args.opencode
    claude_out_dir = (
        (Path(args.claude_out).expanduser() if args.claude_out else claude_default)
        if (args.claude or install_all)
        else None
    )
    codex_out_dir = (
        (Path(args.codex_out).expanduser() if args.codex_out else codex_default)
        if (args.codex or install_all)
        else None
    )
    opencode_out_dir = (
        (Path(args.opencode_out).expanduser() if args.opencode_out else opencode_default)
        if (args.opencode or install_all)
        else None
    )

    sync(
        write=write,
        src_dir=src_dir,
        claude_out_dir=claude_out_dir,
        codex_out_dir=codex_out_dir,
        opencode_out_dir=opencode_out_dir,
    )

    if args.install and write:
        if claude_out_dir:
            print(f"Installed Claude skills to: {claude_out_dir}")
        if codex_out_dir:
            print(f"Installed Codex skills to: {codex_out_dir}")
        if opencode_out_dir:
            print(f"Installed OpenCode skills to: {opencode_out_dir}")


if __name__ == "__main__":
    main()
