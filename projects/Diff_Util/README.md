# Diff Utility

A minimal clone of the UNIX `diff` program, written in Python.

Compares two files line by line and highlights additions, deletions, and
changes with colour-coded terminal output.

## Project Structure

```
Diff_Util/
├── diff.py          # CLI entry point (argument parsing + coloured output)
├── diff_core.py     # Core comparison logic (pure functions, no I/O side effects)
├── test_diff.py     # Unit tests for the core logic
├── requirements.txt
└── README.md
```

- **`diff_core.py`** exposes `compute_diff()` and `read_file_lines()` so the
  comparison algorithm can be imported, tested, or reused without pulling in
  any CLI or terminal-output code.
- **`diff.py`** handles argument parsing (via `argparse`), file reading, and
  rich terminal rendering.  It will not execute anything on import.

## Prerequisites

- Python 3.8 or later
- [rich](https://github.com/Textualize/rich) (see `requirements.txt`)

Install dependencies:

```bash
pip install -r requirements.txt
```

## How to Run

```bash
python diff.py <original_file> <changed_file>
```

Or on Linux / macOS (after `chmod +x diff.py`):

```bash
./diff.py <original_file> <changed_file>
```

Full help output:

```bash
python diff.py --help
```

## Usage Example

Consider two files, `v1` and `v2`:

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

Running `python diff.py v1 v2` produces:

```
[-] Line 1: Bruce
[+] Line 1: Batman

[-] Line 3: Jason
[+] Line 3: Red Hood

[+] Line 4: Joker
[+] Line 5: Ra's Al Ghul
```

Legend:

- `[-]` — line present only in the original file (deletion).
- `[+]` — line present only in the changed file (addition).
- Lines that are identical in both files are not shown.

## Running Tests

```bash
python -m unittest test_diff.py -v
```

## Screenshot

![Python Diff Utility](diff_util.jpg)

## Credits

Originally created by [KILLinefficiency](https://www.github.com/KILLinefficiency).
