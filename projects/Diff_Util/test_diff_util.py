"""Tests for the core diff logic in :mod:`diff_util`.

These exercise the comparison logic directly, without running the
command-line tool. Run them with ``pytest`` or, if pytest is not
installed, with ``python test_diff_util.py``.
"""

from diff_util import (
    ChangeKind,
    LineChange,
    compare_lines,
    format_changes,
)


def test_identical_files_have_no_changes():
    lines = ["alpha", "beta", "gamma"]
    assert compare_lines(lines, lines) == []


def test_modified_line_is_detected():
    original = ["alpha", "beta", "gamma"]
    changed = ["alpha", "BETA", "gamma"]
    assert compare_lines(original, changed) == [
        LineChange(
            kind=ChangeKind.MODIFIED,
            line_number=2,
            original="beta",
            changed="BETA",
        )
    ]


def test_added_trailing_lines_are_detected():
    original = ["alpha"]
    changed = ["alpha", "beta", "gamma"]
    assert compare_lines(original, changed) == [
        LineChange(kind=ChangeKind.ADDED, line_number=2, changed="beta"),
        LineChange(kind=ChangeKind.ADDED, line_number=3, changed="gamma"),
    ]


def test_removed_trailing_lines_are_detected():
    original = ["alpha", "beta", "gamma"]
    changed = ["alpha"]
    assert compare_lines(original, changed) == [
        LineChange(kind=ChangeKind.REMOVED, line_number=2, original="beta"),
        LineChange(kind=ChangeKind.REMOVED, line_number=3, original="gamma"),
    ]


def test_readme_example_scenario():
    original = ["Bruce", "Alfred", "Jason"]
    changed = ["Batman", "Alfred", "Red Hood", "Joker", "Ra's Al Ghul"]
    assert compare_lines(original, changed) == [
        LineChange(ChangeKind.MODIFIED, 1, original="Bruce", changed="Batman"),
        LineChange(ChangeKind.MODIFIED, 3, original="Jason", changed="Red Hood"),
        LineChange(ChangeKind.ADDED, 4, changed="Joker"),
        LineChange(ChangeKind.ADDED, 5, changed="Ra's Al Ghul"),
    ]


def test_format_changes_renders_expected_markup():
    changes = [
        LineChange(ChangeKind.MODIFIED, 1, original="Bruce", changed="Batman"),
        LineChange(ChangeKind.ADDED, 4, changed="Joker"),
    ]
    assert format_changes(changes) == [
        "",
        "[bold red][-] Line 1:[/bold red] Bruce",
        "[bold green][+] Line 1:[/bold green] Batman",
        "",
        "[bold green][+] Line 4:[/bold green] Joker",
        "",
    ]


def test_no_changes_still_emits_leading_blank_line():
    assert format_changes([]) == [""]


if __name__ == "__main__":
    failures = 0
    for name, test in sorted(globals().items()):
        if name.startswith("test_") and callable(test):
            try:
                test()
                print(f"PASS {name}")
            except AssertionError as error:
                failures += 1
                print(f"FAIL {name}: {error}")
    if failures:
        raise SystemExit(f"{failures} test(s) failed")
    print("All tests passed")
