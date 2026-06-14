"""Unit tests for the diff utility core logic."""

import os
import tempfile
import unittest

from diff_core import ChangeType, DiffEntry, compute_diff, read_file_lines


class TestReadFileLines(unittest.TestCase):
    """Tests for ``read_file_lines``."""

    def test_reads_lines_without_trailing_newlines(self):
        with tempfile.NamedTemporaryFile(mode="w", suffix=".txt", delete=False) as fh:
            fh.write("alpha\nbeta\ngamma\n")
            path = fh.name

        try:
            lines = read_file_lines(path)
            self.assertEqual(lines, ["alpha", "beta", "gamma"])
        finally:
            os.unlink(path)

    def test_handles_file_without_trailing_newline(self):
        with tempfile.NamedTemporaryFile(mode="w", suffix=".txt", delete=False) as fh:
            fh.write("one\ntwo")
            path = fh.name

        try:
            lines = read_file_lines(path)
            self.assertEqual(lines, ["one", "two"])
        finally:
            os.unlink(path)

    def test_returns_empty_list_for_empty_file(self):
        with tempfile.NamedTemporaryFile(mode="w", suffix=".txt", delete=False) as fh:
            path = fh.name

        try:
            lines = read_file_lines(path)
            self.assertEqual(lines, [])
        finally:
            os.unlink(path)

    def test_raises_for_missing_file(self):
        with self.assertRaises(FileNotFoundError):
            read_file_lines("/nonexistent/path/that/does/not/exist.txt")


class TestComputeDiff(unittest.TestCase):
    """Tests for ``compute_diff``."""

    # -- helpers ----------------------------------------------------------

    @staticmethod
    def _types(entries):
        return [e.change_type for e in entries]

    # -- basic cases ------------------------------------------------------

    def test_identical_files(self):
        lines = ["alpha", "beta", "gamma"]
        entries = compute_diff(lines, lines)
        self.assertEqual(self._types(entries), [ChangeType.EQUAL] * 3)

    def test_completely_different_files_same_length(self):
        original = ["a", "b", "c"]
        changed = ["x", "y", "z"]
        entries = compute_diff(original, changed)
        self.assertEqual(self._types(entries), [ChangeType.CHANGED] * 3)
        # Spot-check first entry.
        self.assertEqual(entries[0].original_line, "a")
        self.assertEqual(entries[0].changed_line, "x")
        self.assertEqual(entries[0].line_number, 1)

    def test_changed_file_longer(self):
        original = ["Bruce", "Alfred", "Jason"]
        changed = ["Batman", "Alfred", "Red Hood", "Joker", "Ra's Al Ghul"]
        entries = compute_diff(original, changed)

        types = self._types(entries)
        self.assertEqual(
            types,
            [
                ChangeType.CHANGED,  # Line 1: Bruce → Batman
                ChangeType.EQUAL,    # Line 2: Alfred
                ChangeType.CHANGED,  # Line 3: Jason → Red Hood
                ChangeType.ADDED,    # Line 4: Joker
                ChangeType.ADDED,    # Line 5: Ra's Al Ghul
            ],
        )

        # Verify the added entries reference the correct line numbers.
        added = [e for e in entries if e.change_type == ChangeType.ADDED]
        self.assertEqual(added[0].line_number, 4)
        self.assertEqual(added[0].changed_line, "Joker")
        self.assertEqual(added[1].line_number, 5)
        self.assertEqual(added[1].changed_line, "Ra's Al Ghul")

    def test_original_file_longer(self):
        original = ["a", "b", "c", "d", "e"]
        changed = ["a", "b"]
        entries = compute_diff(original, changed)

        types = self._types(entries)
        self.assertEqual(
            types,
            [
                ChangeType.EQUAL,    # Line 1: a
                ChangeType.EQUAL,    # Line 2: b
                ChangeType.REMOVED,  # Line 3: c
                ChangeType.REMOVED,  # Line 4: d
                ChangeType.REMOVED,  # Line 5: e
            ],
        )

        removed = [e for e in entries if e.change_type == ChangeType.REMOVED]
        self.assertEqual(removed[0].line_number, 3)
        self.assertEqual(removed[0].original_line, "c")

    def test_both_empty(self):
        entries = compute_diff([], [])
        self.assertEqual(entries, [])

    def test_original_empty(self):
        entries = compute_diff([], ["new1", "new2"])
        types = self._types(entries)
        self.assertEqual(types, [ChangeType.ADDED, ChangeType.ADDED])
        self.assertEqual(entries[0].changed_line, "new1")
        self.assertEqual(entries[0].line_number, 1)

    def test_changed_empty(self):
        entries = compute_diff(["old1", "old2"], [])
        types = self._types(entries)
        self.assertEqual(types, [ChangeType.REMOVED, ChangeType.REMOVED])
        self.assertEqual(entries[0].original_line, "old1")
        self.assertEqual(entries[0].line_number, 1)

    def test_mixed_changes(self):
        original = ["same", "diff_old", "same2"]
        changed = ["same", "diff_new", "same2", "extra"]
        entries = compute_diff(original, changed)

        self.assertEqual(entries[0].change_type, ChangeType.EQUAL)
        self.assertEqual(entries[0].original_line, "same")

        self.assertEqual(entries[1].change_type, ChangeType.CHANGED)
        self.assertEqual(entries[1].original_line, "diff_old")
        self.assertEqual(entries[1].changed_line, "diff_new")

        self.assertEqual(entries[2].change_type, ChangeType.EQUAL)
        self.assertEqual(entries[2].original_line, "same2")

        self.assertEqual(entries[3].change_type, ChangeType.ADDED)
        self.assertEqual(entries[3].changed_line, "extra")
        self.assertEqual(entries[3].line_number, 4)


class TestDiffEntry(unittest.TestCase):
    """Tests for the ``DiffEntry`` dataclass."""

    def test_entry_is_frozen(self):
        entry = DiffEntry(
            change_type=ChangeType.EQUAL,
            line_number=1,
            original_line="hello",
        )
        with self.assertRaises(AttributeError):
            entry.line_number = 2  # type: ignore[misc]

    def test_defaults(self):
        entry = DiffEntry(change_type=ChangeType.ADDED, line_number=5)
        self.assertIsNone(entry.original_line)
        self.assertIsNone(entry.changed_line)


if __name__ == "__main__":
    unittest.main()
