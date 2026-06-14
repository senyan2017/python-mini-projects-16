#!/usr/bin/env python3
"""Command-line entry point for the minimal ``diff`` clone.

This module only handles argument parsing and output; all comparison
logic lives in :mod:`diff_util` so it can be imported and tested on its
own. Importing this file does not run the tool - call :func:`main` or run
it as a script.

Usage:
    python diff.py <original_file> <changed_file>
"""

import sys
from typing import List, Optional

from rich import print

from diff_util import compare_lines, format_changes, read_lines

USAGE = (
    "Usage:\n"
    "\tMust provide two file names as command-line arguments.\n"
    "\tdiff.py <original_file> <changed_file>"
)


def main(argv: Optional[List[str]] = None) -> int:
    """Run the diff tool. Returns a process exit code."""
    args = sys.argv[1:] if argv is None else argv

    if len(args) < 2:
        print(USAGE)
        return 1

    original_path, changed_path = args[0], args[1]

    try:
        original_contents = read_lines(original_path)
        changed_contents = read_lines(changed_path)
    except FileNotFoundError as error:
        print(f"[bold red]Error:[/bold red] file not found: {error.filename}")
        return 1

    changes = compare_lines(original_contents, changed_contents)
    for line in format_changes(changes):
        print(line)

    return 0


if __name__ == "__main__":
    sys.exit(main())
