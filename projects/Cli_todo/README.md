# Simple CLI Todo App

A small command line todo manager. Tasks now carry a **status** and a **priority**, the
list can be **filtered**, and finishing a task no longer throws it away. Everything is still
stored in a plain `todo.txt` file.

## Dependencies

Requires Python 3 and [Click](https://palletsprojects.com/p/click/).

```bash
pip install click          # or: pip install -r requirements.txt
```

## How to use

Run it from your editor/IDE or from the command line:

```bash
python todo.py [COMMAND] [OPTIONS]
```

Run `python todo.py --help` to see every command, or `python todo.py [COMMAND] --help`
for the options of a single command. If you omit a required option you will simply be
prompted for it.

### Commands

| Command  | Description                                                        |
|----------|-------------------------------------------------------------------|
| `add`    | Add a task. New tasks start with status `todo`.                   |
| `tasks`  | List tasks. Can be filtered by status and/or priority.           |
| `start`  | Move a task to `in_progress`.                                     |
| `done`   | Mark a task as `done` (the task is kept in the list).            |
| `remove` | Delete a task permanently.                                        |

### Statuses and priorities

* **Status:** `todo` &rarr; `in_progress` &rarr; `done`
* **Priority:** `high`, `medium` (default), `low`

The list is shown most-urgent first (`high` before `medium` before `low`).

### Examples

```bash
# Add tasks (priority defaults to medium)
python todo.py add --add_task "Pay rent" --priority high
python todo.py add --add_task "Read a book" -p low
python todo.py add --add_task "Email boss"

# Show all tasks
python todo.py tasks

# Filter the list
python todo.py tasks --status todo
python todo.py tasks --priority high
python todo.py tasks -s in_progress          # short flags also work

# Move a task through its lifecycle
python todo.py start --task_id 2             # todo -> in_progress
python todo.py done  --fin_taskid 0          # -> done (still listed)

# Delete a task for good
python todo.py remove --task_id 1
```

Sample output of `tasks`:

```text
YOUR TASKS
**********
• [TODO] (high) Pay rent (ID: 0)
• [IN PROGRESS] (medium) Email boss (ID: 2)
• [DONE] (low) Read a book (ID: 1)
```

## Data format

Tasks live in `todo.txt` next to `todo.py`. The first line is the id counter (the next id
to hand out); every following line is one task with fields separated by ` ``` `:

```text
3
0```Pay rent```done```high
1```Read a book```todo```low
2```Email boss```in_progress```medium
```

Older `todo.txt` files that only stored `<id>```<text>` are still read correctly — missing
fields default to status `todo` and priority `medium`, and the file is rewritten in the new
format the next time it is saved.
