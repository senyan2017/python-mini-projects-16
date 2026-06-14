import os
import click

# Keep todo.txt next to this script so the app works no matter where it is run from.
TODO_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'todo.txt')

# Field separator used in todo.txt. Kept identical to the original format so that
# old data files (which used "<id>```<text>") can still be read.
SEP = '```'

STATUSES = ['todo', 'in_progress', 'done']
PRIORITIES = ['high', 'medium', 'low']

# Human friendly labels shown in the task list.
STATUS_LABELS = {
    'todo': 'TODO',
    'in_progress': 'IN PROGRESS',
    'done': 'DONE',
}

# Sort weight so the most urgent tasks are listed first.
PRIORITY_ORDER = {'high': 0, 'medium': 1, 'low': 2}


def load_data():
    '''Read todo.txt and return (next_id, tasks).

    The first line holds the next id to assign. Every following line is one task.

    Two on-disk formats are accepted so upgrading never breaks an existing file:
      * old: "<id>```<text>"                         -> status=todo, priority=medium
      * new: "<id>```<text>```<status>```<priority>"
    '''
    if not os.path.exists(TODO_FILE):
        return 0, {}
    with open(TODO_FILE) as f:
        content = f.readlines()
    if not content:
        return 0, {}
    try:
        next_id = int(content[0].strip())
    except ValueError:
        next_id = 0
    tasks = {}
    for line in content[1:]:
        line = line.rstrip('\n')
        if not line:
            continue
        parts = line.split(SEP)
        task_id = parts[0]
        text = parts[1] if len(parts) > 1 else ''
        status = parts[2] if len(parts) > 2 and parts[2] in STATUSES else 'todo'
        priority = parts[3] if len(parts) > 3 and parts[3] in PRIORITIES else 'medium'
        tasks[task_id] = {'text': text, 'status': status, 'priority': priority}
    return next_id, tasks


def save_data(next_id, tasks):
    '''Persist the id counter and every task back to todo.txt in the new format.'''
    lines = [str(next_id)]
    for task_id, task in tasks.items():
        lines.append(SEP.join([str(task_id), task['text'], task['status'], task['priority']]))
    with open(TODO_FILE, 'w') as f:
        f.writelines('%s\n' % line for line in lines)


def format_task(task_id, task):
    '''Build the single-line representation of a task for display.'''
    label = STATUS_LABELS.get(task['status'], task['status'].upper())
    return '\u2022 [%s] (%s) %s (ID: %s)' % (label, task['priority'], task['text'], task_id)


def _set_status(ctx, task_id, new_status, message):
    '''Shared helper for the status-transition commands (start / done).'''
    key = str(task_id)
    tasks = ctx.obj['TASKS']
    if key in tasks:
        tasks[key]['status'] = new_status
        click.echo(message % (tasks[key]['text'], key))
        save_data(ctx.obj['NEXT_ID'], tasks)
    else:
        click.echo('Error: no task with id ' + key)


@click.group()
@click.pass_context
def todo(ctx):
    '''Simple CLI Todo App'''
    ctx.ensure_object(dict)
    next_id, tasks = load_data()
    ctx.obj['NEXT_ID'] = next_id
    ctx.obj['TASKS'] = tasks


@todo.command()
@click.option('-s', '--status', 'status_filter', type=click.Choice(STATUSES),
              default=None, help='Only show tasks with this status.')
@click.option('-p', '--priority', 'priority_filter', type=click.Choice(PRIORITIES),
              default=None, help='Only show tasks with this priority.')
@click.pass_context
def tasks(ctx, status_filter, priority_filter):
    '''Display tasks, optionally filtered by status or priority'''
    all_tasks = ctx.obj['TASKS']
    items = [
        (i, t) for i, t in all_tasks.items()
        if (status_filter is None or t['status'] == status_filter)
        and (priority_filter is None or t['priority'] == priority_filter)
    ]
    if not items:
        if all_tasks:
            click.echo('No tasks match the given filters.\n')
        else:
            click.echo('No tasks yet! Use ADD to add one.\n')
        return
    # Most urgent first, then by id for a stable order.
    items.sort(key=lambda kv: (
        PRIORITY_ORDER.get(kv[1]['priority'], 99),
        int(kv[0]) if kv[0].isdigit() else kv[0],
    ))
    click.echo('YOUR TASKS\n**********')
    for i, t in items:
        click.echo(format_task(i, t))
    click.echo('')


@todo.command()
@click.option('-add', '--add_task', prompt='Enter task to add')
@click.option('-p', '--priority', type=click.Choice(PRIORITIES), default='medium',
              help='Task priority (default: medium).')
@click.pass_context
def add(ctx, add_task, priority):
    '''Add a task'''
    if add_task:
        new_id = str(ctx.obj['NEXT_ID'])
        ctx.obj['TASKS'][new_id] = {'text': add_task, 'status': 'todo', 'priority': priority}
        click.echo('Added task "%s" with ID %s (priority: %s)' % (add_task, new_id, priority))
        save_data(ctx.obj['NEXT_ID'] + 1, ctx.obj['TASKS'])


@todo.command()
@click.option('-id', '--task_id', 'task_id', prompt='Enter ID of task to start', type=int)
@click.pass_context
def start(ctx, task_id):
    '''Mark a task as in progress'''
    _set_status(ctx, task_id, 'in_progress', 'Task "%s" (ID %s) is now in progress')


@todo.command()
@click.option('-fin', '--fin_taskid', 'fin_taskid', prompt='Enter ID of task to finish', type=int)
@click.pass_context
def done(ctx, fin_taskid):
    '''Mark a task as done (the task stays in the list)'''
    _set_status(ctx, fin_taskid, 'done', 'Marked task "%s" (ID %s) as done')


@todo.command()
@click.option('-id', '--task_id', 'task_id', prompt='Enter ID of task to remove', type=int)
@click.pass_context
def remove(ctx, task_id):
    '''Delete a task by ID'''
    key = str(task_id)
    tasks = ctx.obj['TASKS']
    if key in tasks:
        task = tasks.pop(key)
        click.echo('Removed task "%s" (ID %s)' % (task['text'], key))
        # Reset the id counter once the list is empty so ids stay tidy.
        save_data(ctx.obj['NEXT_ID'] if tasks else 0, tasks)
    else:
        click.echo('Error: no task with id ' + key)


if __name__ == '__main__':
    todo()
