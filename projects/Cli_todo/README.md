# Simple CLI Todo App

A lightweight command-line todo manager with task statuses, priorities, and filtering.
Data is stored in a plain-text `todo.txt` file alongside the script.

## Dependencies

Requires **Python 3** and **Click**.

```bash
pip install click
```

## How to Use

Run from the project directory:

```bash
python todo.py [command] [options]
```

### Commands

| Command | Description |
|---------|-------------|
| `add` | Add a new task. Prompts for text; accepts `-p/--priority` (low/medium/high, default: medium). |
| `tasks` | List all tasks. Filter with `-s/--status` and/or `-p/--priority`. |
| `start <id>` | Mark a pending task as **in-progress**. |
| `done <id>` | Mark a task as **done** (task is kept, not deleted). |
| `remove <id>` | Permanently delete a task. |

### Task Lifecycle

```
pending  ──►  in-progress  ──►  done
```

- `add` creates a task with status **pending**.
- `start` transitions it to **in-progress**.
- `done` transitions it to **done**.
- `remove` permanently deletes a task (useful for cleaning up completed items).

### Examples

```bash
# Add a high-priority task
python todo.py add -add "Fix login bug" -p high

# Add a medium-priority task (default)
python todo.py add -add "Write unit tests"

# List all tasks
python todo.py tasks

# List only pending tasks
python todo.py tasks -s pending

# List only high-priority tasks
python todo.py tasks -p high

# Combine filters
python todo.py tasks -s in-progress -p high

# Start working on task 0
python todo.py start 0

# Mark task 0 as done
python todo.py done 0

# Remove task 0 permanently
python todo.py remove 0
```

### Sample Output

```
YOUR TASKS
**********
  [>] !!! Fix login bug  (ID: 0)
  [ ] !!  Write unit tests  (ID: 1)
  [x] !   Update README  (ID: 2)
```

Legend:
- `[ ]` pending &nbsp; `[>]` in-progress &nbsp; `[x]` done
- `!!!` high &nbsp; `!!` medium &nbsp; `!` low

## Data File Format

`todo.txt` stores tasks in a simple text format:

```
3
0```in-progress```high```Fix login bug
1```pending```medium```Write unit tests
2```done```low```Update README
```

- **Line 1:** next available ID counter.
- **Subsequent lines:** `id```status```priority```text`

> **Backward compatible:** old-format lines (`id```text`) are automatically
> read as `pending` / `medium` and upgraded to the new format on the next save.
