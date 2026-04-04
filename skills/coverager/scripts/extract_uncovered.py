#!/usr/bin/env python3
"""Extract uncovered lines from a SimpleCov HTML coverage report.

Usage:
    python3 extract_uncovered.py <path-to-index.html>

Parses the SimpleCov-generated index.html and prints every file that has
missed lines, together with the line numbers and source code of those lines.
"""
from __future__ import annotations

import argparse
import re
import sys
from html.parser import HTMLParser
from pathlib import Path


class CoverageParser(HTMLParser):
    """State-machine parser that walks a SimpleCov HTML report."""

    def __init__(self) -> None:
        super().__init__()
        # Accumulated results: list of (filepath, [(line_no, code), ...])
        self.files: list[tuple[str, list[tuple[int, str]]]] = []

        # Parser state
        self._in_source_table = False
        self._current_file: str | None = None
        self._current_missed: list[tuple[int, str]] = []

        self._in_header_h3 = False
        self._header_h3_text = ""

        self._in_missed_li = False
        self._missed_line_no: int | None = None

        self._in_code = False
        self._code_text = ""

    # ----- tag open ---------------------------------------------------

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        attr = dict(attrs)

        # Detect <div class="source_table" ...>
        if tag == "div" and "source_table" in (attr.get("class") or ""):
            self._in_source_table = True
            self._current_file = None
            self._current_missed = []
            return

        if not self._in_source_table:
            return

        # <h3> inside a source_table carries the file path
        if tag == "h3":
            self._in_header_h3 = True
            self._header_h3_text = ""
            return

        # <li class="missed" data-hits="0" data-linenumber="N">
        if tag == "li" and "missed" in (attr.get("class") or ""):
            line_no_str = attr.get("data-linenumber")
            if line_no_str and line_no_str.isdigit():
                self._in_missed_li = True
                self._missed_line_no = int(line_no_str)
                self._code_text = ""
            return

        # <code class="ruby"> (or any language) inside a missed <li>
        if tag == "code" and self._in_missed_li:
            self._in_code = True
            self._code_text = ""
            return

    # ----- tag close --------------------------------------------------

    def handle_endtag(self, tag: str) -> None:
        if tag == "h3" and self._in_header_h3:
            self._in_header_h3 = False
            self._current_file = self._header_h3_text.strip()
            return

        if tag == "code" and self._in_code:
            self._in_code = False
            return

        if tag == "li" and self._in_missed_li:
            self._in_missed_li = False
            if self._missed_line_no is not None:
                self._current_missed.append(
                    (self._missed_line_no, self._code_text.strip())
                )
            self._missed_line_no = None
            return

        # End of a source_table div — flush the file
        # SimpleCov wraps each file in its own source_table div.
        # We detect the boundary when a new source_table opens or at EOF.

    # ----- text -------------------------------------------------------

    def handle_data(self, data: str) -> None:
        if self._in_header_h3:
            self._header_h3_text += data
        if self._in_code and self._in_missed_li:
            self._code_text += data

    # ----- explicit flush on new source_table or EOF ------------------

    def _flush_file(self) -> None:
        if self._current_file and self._current_missed:
            self.files.append((self._current_file, list(self._current_missed)))
        self._current_file = None
        self._current_missed = []
        self._in_source_table = False

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:  # type: ignore[override]
        attr = dict(attrs)

        # When a new source_table starts, flush the previous one
        if tag == "div" and "source_table" in (attr.get("class") or ""):
            self._flush_file()
            self._in_source_table = True
            return

        if not self._in_source_table:
            return

        if tag == "h3":
            self._in_header_h3 = True
            self._header_h3_text = ""
            return

        if tag == "li" and "missed" in (attr.get("class") or ""):
            line_no_str = attr.get("data-linenumber")
            if line_no_str and line_no_str.isdigit():
                self._in_missed_li = True
                self._missed_line_no = int(line_no_str)
                self._code_text = ""
            return

        if tag == "code" and self._in_missed_li:
            self._in_code = True
            self._code_text = ""
            return

    def close(self) -> None:
        self._flush_file()
        super().close()


def group_consecutive(lines: list[tuple[int, str]]) -> list[list[tuple[int, str]]]:
    """Group consecutive line numbers into blocks for readability."""
    if not lines:
        return []
    groups: list[list[tuple[int, str]]] = [[lines[0]]]
    for i in range(1, len(lines)):
        if lines[i][0] == lines[i - 1][0] + 1:
            groups[-1].append(lines[i])
        else:
            groups.append([lines[i]])
    return groups


def format_output(files: list[tuple[str, list[tuple[int, str]]]], html_path: str) -> str:
    """Format the uncovered lines into the expected output."""
    if not files:
        return "All files have 100% coverage!"

    total_missed = sum(len(lines) for _, lines in files)
    parts: list[str] = []
    parts.append("# Uncovered Lines")
    parts.append("")
    parts.append(f"File Path: `{html_path}`")
    parts.append("")
    parts.append(f"**{total_missed} lines** missed across **{len(files)} files**")
    parts.append("")

    for filepath, lines in files:
        parts.append(f"* {filepath}")
        groups = group_consecutive(lines)
        for group in groups:
            for line_no, code in group:
                if code:
                    parts.append(f"Line {line_no}.    {code}")
                else:
                    parts.append(f"Line {line_no}.    (empty line)")
            # Add [...] between non-consecutive groups (except the last)
            if group is not groups[-1]:
                parts.append("[...]")
        parts.append("")

    return "\n".join(parts)


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Extract uncovered lines from a SimpleCov HTML coverage report."
    )
    parser.add_argument(
        "html_path",
        help="Path to the SimpleCov index.html coverage report.",
    )
    args = parser.parse_args()

    html_path = Path(args.html_path).expanduser().resolve()
    if not html_path.exists():
        print(f"Error: file not found: {html_path}", file=sys.stderr)
        sys.exit(1)

    content = html_path.read_text(encoding="utf-8")

    cov_parser = CoverageParser()
    cov_parser.feed(content)
    cov_parser.close()

    output = format_output(cov_parser.files, str(html_path))
    print(output)


if __name__ == "__main__":
    main()
