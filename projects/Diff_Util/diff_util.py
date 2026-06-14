"""Core diff logic for a minimal clone of the UNIX ``diff`` program.

This module is import-safe: it has no side effects on import, so the
comparison logic can be called directly from tests or other code without
running the command-line tool. The command-line entry point lives in
``diff.py``.

The pipeline is split into three independent stages:

* :func:`read_lines`      - read a file into a list of lines.
* :func:`compare_lines`   - compare two line lists into a list of changes.
* :func:`format_changes`  - turn changes into colored, printable lines.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import List, Optional


class ChangeKind(Enum):
    """The kind of change detected on a single line."""

    MODIFIED = "modified"  # line exists in both files but differs
    ADDED = "added"        # line only exists in the changed file
    REMOVED = "removed"    # line only exists in the original file


@dataclass(frozen=True)
class LineChange:
    """A single line-level difference between two files.

    ``original`` is ``None`` for added lines and ``changed`` is ``None``
    for removed lines; both are present for modified lines.
    """

    kind: ChangeKind
    line_number: int
    original: Optional[str] = None
    changed: Optional[str] = None


def read_lines(path: str) -> List[str]:
    """Read ``path`` and return its contents as a list of lines.

    Trailing newlines are stripped so callers and tests can work with
    clean strings.
    """
    with open(path, "r", encoding="utf-8") as handle:
        return handle.read().splitlines()


def compare_lines(original: List[str], changed: List[str]) -> List[LineChange]:
    """Compare two lists of lines and return the ordered list of changes.

    Lines are compared one-by-one up to the length of the shorter file.
    Any extra lines in the longer file are reported as additions (when the
    changed file is longer) or removals (when the original file is longer).
    """
    changes: List[LineChange] = []
    common_length = min(len(original), len(changed))

    for index in range(common_length):
        if original[index] != changed[index]:
            changes.append(
                LineChange(
                    kind=ChangeKind.MODIFIED,
                    line_number=index + 1,
                    original=original[index],
                    changed=changed[index],
                )
            )

    for index in range(common_length, len(changed)):
        changes.append(
            LineChange(
                kind=ChangeKind.ADDED,
                line_number=index + 1,
                changed=changed[index],
            )
        )

    for index in range(common_length, len(original)):
        changes.append(
            LineChange(
                kind=ChangeKind.REMOVED,
                line_number=index + 1,
                original=original[index],
            )
        )

    return changes


def _format_removed(line_number: int, text: str) -> str:
    return f"[bold red][-] Line {line_number}:[/bold red] {text}"


def _format_added(line_number: int, text: str) -> str:
    return f"[bold green][+] Line {line_number}:[/bold green] {text}"


def format_changes(changes: List[LineChange]) -> List[str]:
    """Render ``changes`` into a flat list of printable, colored lines.

    The output preserves the original tool's style: a leading blank line,
    each change group rendered with red ``[-]`` / green ``[+]`` markers and
    followed by a blank separator line. Markup uses ``rich`` tags and is
    only interpreted when printed through ``rich``.
    """
    lines: List[str] = [""]

    for change in changes:
        if change.kind is ChangeKind.MODIFIED:
            lines.append(_format_removed(change.line_number, change.original))
            lines.append(_format_added(change.line_number, change.changed))
        elif change.kind is ChangeKind.ADDED:
            lines.append(_format_added(change.line_number, change.changed))
        elif change.kind is ChangeKind.REMOVED:
            lines.append(_format_removed(change.line_number, change.original))
        lines.append("")

    return lines
