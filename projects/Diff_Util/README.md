# Diff Utility

This program is a minimal clone of the UNIX ``diff`` program.

``diff.py`` takes two file names as command-line arguments and compares them
line by line, printing colored output that highlights modified, added and
removed lines.

## Project layout

| File | Purpose |
| ---- | ------- |
| ``diff_util.py`` | Core, import-safe comparison logic (reading, comparing, formatting). |
| ``diff.py`` | Thin command-line entry point (argument parsing + output). |
| ``test_diff_util.py`` | Tests for the comparison logic. |

The comparison logic lives in ``diff_util.py`` and has no side effects on
import, so it can be called directly from other code or tests.

## Prerequisites

* Python 3.7+
* Rich: ``rich>=10.11.0``

Install the dependency with:

```
pip install -r requirements.txt
```

## How to run the tool

The tool takes exactly two positional arguments: the original file followed
by the changed file.

```
python diff.py <original_file> <changed_file>
```

On Linux / macOS the script is executable and can be run directly:

```
./diff.py <original_file> <changed_file>
```

If fewer than two files are given, a usage message is printed. If a file does
not exist, a clear error is shown and the tool exits with a non-zero status.

## Usage example

Consider two files ``v1`` and ``v2``:

**v1**:
```
Bruce
Alfred
Jason
```

**v2**:
```
Batman
Alfred
Red Hood
Joker
Ra's Al Ghul
```

Running ``./diff.py v1 v2`` produces the following output (``[-]`` lines are
shown in red, ``[+]`` lines in green):

```

[-] Line 1: Bruce
[+] Line 1: Batman

[-] Line 3: Jason
[+] Line 3: Red Hood

[+] Line 4: Joker

[+] Line 5: Ra's Al Ghul

```

## Using the comparison logic directly

```python
from diff_util import compare_lines, read_lines

changes = compare_lines(read_lines("v1"), read_lines("v2"))
for change in changes:
    print(change.kind, change.line_number)
```

``compare_lines`` returns a list of ``LineChange`` records, each describing a
modified, added or removed line.

## Running the tests

With pytest:

```
pytest test_diff_util.py
```

Or, without any extra dependencies:

```
python test_diff_util.py
```

## Screenshot
![Python Diff Utility](diff_util.jpg)

# KILLinefficiency
Github Link: [KILLinefficiency](https://www.github.com/KILLinefficiency)
