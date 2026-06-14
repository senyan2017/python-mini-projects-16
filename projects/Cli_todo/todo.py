import click
import os

TODO_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'todo.txt')

STATUSES = ['pending', 'in-progress', 'done']
PRIORITIES = ['low', 'medium', 'high']


def load_tasks():
    """Load tasks from todo.txt.

    Supports two formats for backward compatibility:
      - Old format:  id```task_text          (defaults: status=pending, priority=medium)
      - New format:  id```status```priority```task_text

    Returns:
        tuple: (latest_id: int, tasks: dict)
    """
    latest_id = 0
    tasks = {}

    if not os.path.exists(TODO_FILE):
        return latest_id, tasks

    with open(TODO_FILE, 'r', encoding='utf-8') as f:
        lines = f.readlines()

    if not lines:
        return latest_id, tasks

    # First line is always the next-ID counter
    try:
        latest_id = int(lines[0].strip())
    except ValueError:
        latest_id = 0

    for line in lines[1:]:
        line = line.rstrip('\n')
        if not line:
            continue

        parts = line.split('```')

        if len(parts) == 2:
            # Old format: id```text
            task_id, text = parts
            tasks[task_id] = {
                'status': 'pending',
                'priority': 'medium',
                'text': text,
            }
        elif len(parts) >= 4:
            # New format: id```status```priority```text
            # Text may itself contain "```", so rejoin everything after index 3
            task_id = parts[0]
            status = parts[1] if parts[1] in STATUSES else 'pending'
            priority = parts[2] if parts[2] in PRIORITIES else 'medium'
            text = '```'.join(parts[3:])
            tasks[task_id] = {
                'status': status,
                'priority': priority,
                'text': text,
            }
        # Lines with 3 parts are malformed – skip them

    return latest_id, tasks


def save_tasks(latest_id, tasks):
    """Persist tasks to todo.txt in the new format."""
    lines = [str(latest_id) + '\n']
    for task_id, task in tasks.items():
        line = (
            f"{task_id}```{task['status']}```{task['priority']}```{task['text']}\n"
        )
        lines.append(line)

    with open(TODO_FILE, 'w', encoding='utf-8') as f:
        f.writelines(lines)


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

@click.group()
@click.pass_context
def todo(ctx):
    '''Simple CLI Todo App'''
    ctx.ensure_object(dict)
    latest_id, tasks = load_tasks()
    ctx.obj['LATEST'] = latest_id
    ctx.obj['TASKS'] = tasks


# ---- tasks ----------------------------------------------------------------

@todo.command()
@click.pass_context
@click.option(
    '--status', '-s',
    type=click.Choice(STATUSES, case_sensitive=False),
    default=None,
    help='Filter by status (pending / in-progress / done)',
)
@click.option(
    '--priority', '-p',
    type=click.Choice(PRIORITIES, case_sensitive=False),
    default=None,
    help='Filter by priority (low / medium / high)',
)
def tasks(ctx, status, priority):
    '''Display tasks, optionally filtered by status or priority.'''
    filtered = dict(ctx.obj['TASKS'])

    if status:
        filtered = {k: v for k, v in filtered.items() if v['status'] == status}
    if priority:
        filtered = {k: v for k, v in filtered.items() if v['priority'] == priority}

    if not filtered:
        if status or priority:
            click.echo('No matching tasks found.\n')
        else:
            click.echo('No tasks yet! Use ADD to add one.\n')
        return

    # Sort: high priority first, then by ascending ID
    priority_order = {'high': 0, 'medium': 1, 'low': 2}
    sorted_items = sorted(
        filtered.items(),
        key=lambda item: (priority_order.get(item[1]['priority'], 1), int(item[0])),
    )

    status_icons = {'pending': '[ ]', 'in-progress': '[>]', 'done': '[x]'}
    priority_tags = {'high': '!!!', 'medium': '!! ', 'low': '!  '}

    click.echo('YOUR TASKS')
    click.echo('**********')
    for task_id, task in sorted_items:
        icon = status_icons.get(task['status'], '[ ]')
        ptag = priority_tags.get(task['priority'], '!! ')
        click.echo(f"  {icon} {ptag} {task['text']}  (ID: {task_id})")
    click.echo('')


# ---- add ------------------------------------------------------------------

@todo.command()
@click.pass_context
@click.option('-add', '--add_task', prompt='Enter task to add', help='Task description')
@click.option(
    '-p', '--priority',
    type=click.Choice(PRIORITIES, case_sensitive=False),
    default='medium',
    show_default=True,
    help='Task priority',
)
def add(ctx, add_task, priority):
    '''Add a task with an optional priority (default: medium).'''
    if not add_task:
        return

    task_id = str(ctx.obj['LATEST'])
    ctx.obj['TASKS'][task_id] = {
        'status': 'pending',
        'priority': priority,
        'text': add_task,
    }
    ctx.obj['LATEST'] += 1

    click.echo(
        f'Added task "{add_task}"  (ID: {task_id}, priority: {priority}, status: pending)'
    )
    save_tasks(ctx.obj['LATEST'], ctx.obj['TASKS'])


# ---- start ----------------------------------------------------------------

@todo.command()
@click.pass_context
@click.argument('task_id', type=int)
def start(ctx, task_id):
    '''Mark a pending task as in-progress.'''
    tid = str(task_id)
    if tid not in ctx.obj['TASKS']:
        click.echo(f'Error: no task with ID {task_id}')
        return

    task = ctx.obj['TASKS'][tid]
    if task['status'] == 'in-progress':
        click.echo(f'Task "{task["text"]}" is already in progress.')
    elif task['status'] == 'done':
        click.echo(f'Task "{task["text"]}" is already done.')
    else:
        task['status'] = 'in-progress'
        click.echo(f'Started task "{task["text"]}"  (ID: {tid})')
        save_tasks(ctx.obj['LATEST'], ctx.obj['TASKS'])


# ---- done -----------------------------------------------------------------

@todo.command()
@click.pass_context
@click.argument('task_id', type=int)
def done(ctx, task_id):
    '''Mark a task as done.'''
    tid = str(task_id)
    if tid not in ctx.obj['TASKS']:
        click.echo(f'Error: no task with ID {task_id}')
        return

    task = ctx.obj['TASKS'][tid]
    if task['status'] == 'done':
        click.echo(f'Task "{task["text"]}" is already done.')
    else:
        task['status'] = 'done'
        click.echo(f'Completed task "{task["text"]}"  (ID: {tid})')
        save_tasks(ctx.obj['LATEST'], ctx.obj['TASKS'])


# ---- remove ---------------------------------------------------------------

@todo.command()
@click.pass_context
@click.argument('task_id', type=int)
def remove(ctx, task_id):
    '''Permanently delete a task.'''
    tid = str(task_id)
    if tid not in ctx.obj['TASKS']:
        click.echo(f'Error: no task with ID {task_id}')
        return

    task = ctx.obj['TASKS'].pop(tid)
    click.echo(f'Removed task "{task["text"]}"  (ID: {tid})')
    save_tasks(ctx.obj['LATEST'], ctx.obj['TASKS'])


if __name__ == '__main__':
    todo()
