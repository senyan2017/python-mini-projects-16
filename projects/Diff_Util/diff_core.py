"""Core comparison logic for the diff utility.

This module contains pure functions with no CLI or terminal-output
dependencies, so the comparison logic can be imported and tested
independently.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import List, Optional


class ChangeType(Enum):
    """The kind of change a DiffEntry represents."""

    EQUAL = "equal"
    CHANGED = "changed"
    ADDED = "added"
    REMOVED = "removed"


@dataclass(frozen=True)
class DiffEntry:
    """A single line-level diff result.

    Attributes:
        change_type: What happened at this line.
        line_number: 1-based position of the line in the relevant file.
            For EQUAL / CHANGED entries the line number is the same in both
            files.  For ADDED entries it is the position in the *changed*
            file; for REMOVED entries it is the position in the *original*
            file.
        original_line: The text of the line in the original file (may be
            ``None`` for ADDED entries).
        changed_line: The text of the line in the changed file (may be
            ``None`` for REMOVED and EQUAL entries).
    """

    change_type: ChangeType
    line_number: int
    original_line: Optional[str] = None
    changed_line: Optional[str] = None


# ---------------------------------------------------------------------------
# Public helpers
# ---------------------------------------------------------------------------

def read_file_lines(filepath: str) -> List[str]:
    """Read *filepath* and return its lines with trailing newlines stripped.

    Raises ``FileNotFoundError`` / ``PermissionError`` as usual so callers
    can handle them at the CLI layer.
    """
    with open(filepath, "r", encoding="utf-8") as fh:
        return [line.rstrip("\n") for line in fh]


def compute_diff(
    original_lines: List[str],
    changed_lines: List[str],
) -> List[DiffEntry]:
    """Compare two line lists and return an ordered list of `DiffEntry`.

    Algorithm (same as the original script):
      1. Walk both lists in lock-step up to the length of the shorter one.
         * Matching lines  → ``EQUAL`` entry.
         * Differing lines → ``CHANGED`` entry.
      2. Any remaining lines in the *longer* list become ``ADDED`` (if the
         changed file is longer) or ``REMOVED`` (if the original file is
         longer).
    """
    entries: List[DiffEntry] = []
    common_length = min(len(original_lines), len(changed_lines))

    # Phase 1: line-by-line comparison over the shared range.
    for index in range(common_length):
        original_line = original_lines[index]
        changed_line = changed_lines[index]

        if original_line == changed_line:
            entries.append(
                DiffEntry(
                    change_type=ChangeType.EQUAL,
                    line_number=index + 1,
                    original_line=original_line,
                )
            )
        else:
            entries.append(
                DiffEntry(
                    change_type=ChangeType.CHANGED,
                    line_number=index + 1,
                    original_line=original_line,
                    changed_line=changed_line,
                )
            )

    # Phase 2: remaining lines that exist only in one file.
    if len(original_lines) > common_length:
        for index in range(common_length, len(original_lines)):
            entries.append(
                DiffEntry(
                    change_type=ChangeType.REMOVED,
                    line_number=index + 1,
                    original_line=original_lines[index],
                )
            )
    elif len(changed_lines) > common_length:
        for index in range(common_length, len(changed_lines)):
            entries.append(
                DiffEntry(
                    change_type=ChangeType.ADDED,
                    line_number=index + 1,
                    changed_line=changed_lines[index],
                )
            )

    return entries
