#!/usr/bin/env python3
"""Command-line entry point for the diff utility.

Usage:
    python diff.py <original_file> <changed_file>

Run ``python diff.py --help`` for the full option list.
"""

import argparse
import sys
from typing import List

from rich.console import Console

from diff_core import ChangeType, DiffEntry, compute_diff, read_file_lines

console = Console()


# ---------------------------------------------------------------------------
# Argument parsing
# ---------------------------------------------------------------------------

def build_parser() -> argparse.ArgumentParser:
    """Build and return the argument parser."""
    parser = argparse.ArgumentParser(
        prog="diff.py",
        description="A minimal clone of the UNIX diff program. "
                    "Compares two files line by line and highlights additions, "
                    "deletions, and changes.",
    )
    parser.add_argument(
        "original",
        metavar="original_file",
        help="Path to the original (base) file.",
    )
    parser.add_argument(
        "changed",
        metavar="changed_file",
        help="Path to the changed (new) file.",
    )
    return parser


# ---------------------------------------------------------------------------
# Terminal output
# ---------------------------------------------------------------------------

def _format_line(tag: str, color: str, line_number: int, text: str) -> str:
    """Return a single rich-formatted output line."""
    return f"[bold {color}][{tag}] Line {line_number}:[/bold {color}] {text}"


def display_diff(entries: List[DiffEntry]) -> None:
    """Print *entries* to the terminal using rich markup.

    Only CHANGED, ADDED, and REMOVED entries produce output; EQUAL entries
    are silently skipped.
    """
    console.print()  # Leading blank line, matching original behaviour.

    for entry in entries:
        if entry.change_type == ChangeType.CHANGED:
            console.print(
                _format_line("-", "red", entry.line_number, entry.original_line or "")
            )
            console.print(
                _format_line("+", "green", entry.line_number, entry.changed_line or "")
            )

        elif entry.change_type == ChangeType.REMOVED:
            console.print(
                _format_line("-", "red", entry.line_number, entry.original_line or "")
            )

        elif entry.change_type == ChangeType.ADDED:
            console.print(
                _format_line("+", "green", entry.line_number, entry.changed_line or "")
            )

        # EQUAL entries: no output.


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main(argv: List[str] | None = None) -> int:
    """Program entry point.  Returns the process exit code."""
    parser = build_parser()
    args = parser.parse_args(argv)

    try:
        original_lines = read_file_lines(args.original)
    except FileNotFoundError:
        console.print(f"[bold red]Error:[/bold red] file not found: {args.original}")
        return 1
    except PermissionError:
        console.print(f"[bold red]Error:[/bold red] permission denied: {args.original}")
        return 1

    try:
        changed_lines = read_file_lines(args.changed)
    except FileNotFoundError:
        console.print(f"[bold red]Error:[/bold red] file not found: {args.changed}")
        return 1
    except PermissionError:
        console.print(f"[bold red]Error:[/bold red] permission denied: {args.changed}")
        return 1

    entries = compute_diff(original_lines, changed_lines)
    display_diff(entries)
    return 0


if __name__ == "__main__":
    sys.exit(main())
