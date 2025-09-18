import json
import argparse
from pathlib import Path
from datetime import datetime

AGENDA_FILE = Path('agenda.json')

class TaskNotFound(Exception):
    def __init__(self, id_task: str):
        self.id_task = id_task
        super().__init__(f'the task with the id {id_task} does not exist.')

def get_date() -> str:
    """Generates the current date and time in human-readable format.

    Returns:
    str: String in the format 'Day, DD of Month YYYY at HH:MM AM/PM.
    """
    brand_temporal = datetime.now()
    format_date = brand_temporal.strftime("%A, %d of %b %Y at %I:%M %p.")
    return format_date

def load_agenda():
    """
    Loads the address book from the JSON file.
    - If the file exists, returns the contacts dictionary.
    - If it doesn't exist, returns an empty dictionary {}
    - If the file is corrupted (e.g., invalid content), also returns {}.
    """
    if AGENDA_FILE.exists():
        try:
            with open(AGENDA_FILE, 'r', encoding='utf-8') as f:
                return json.load(f) # -> {{}}
        except json.JSONDecodeError:
            # Corrupt or empty file: we start with an empty dictionary
            return {}
    return {}

def saved_agenda(agenda: dict):
    with open(AGENDA_FILE, 'w', encoding='utf-8') as f:
        json.dump(agenda, f, ensure_ascii=False, indent=4)

def get_id(agenda: dict) -> str:
    """ Generates a new incremental ID based on the calendar keys.
    Args:
        calendar (dict): Dictionary of tasks, where the keys are IDs in string format.
    Returns:
        str: New ID as a string.
    """
    new_id = max(map(int, agenda), default=0) + 1
    return str(new_id)

def add_task(description: str):
    """ Add a new task to the calendar.

    The function loads the calendar from the JSON file,
    generates a new ID for the task, and saves it
    with the status "todo"

    Args:
        description (str): Description of the task.

    Returns: None
    """
    createdAt = get_date()
    task = load_agenda()
    task_id = get_id(task)

    content_task = {
        'description':description,
        'status':'todo',
        'createdAt':createdAt,
        'updatedAt':None
    }

    task[task_id] = content_task

    saved_agenda(task)
    
    print(f'Task added successfully (ID: {task_id})')

def update_task(id_task: str, new_description: str):
    """ Updates a task's description.

    Args:
        id_task (str): ID of the task to update.
        new_description (str): New task description.

    Returns:
        None
    """
    updatedAt = get_date()
    
    agenda = load_agenda()

    if not agenda:
        print('the agenda is empty, first add a task.')
        return

    if id_task in agenda:
        agenda[id_task]['updatedAt'] = updatedAt
        agenda[id_task]['description'] = new_description

    else:
        raise TaskNotFound(id_task)

    saved_agenda(agenda)

def delete_task(id_task: str):
    """Elimina una tarea de la agenda.

    Args:
        id_task (str): id de la tarea a eliminar.
    
    Returns: None
    """
    agenda = load_agenda()

    if not agenda:
        print('the agenda is empty, first add a task.')
        return

    if id_task in agenda:
        del agenda[id_task]
        print(f'Task {id_task} delete')
    else:
        raise TaskNotFound(id_task)
    
    saved_agenda(agenda)

def mark_task(arg: str, id_task: str):
    """Updates the task status and its modification date.

    Args:
        arg (str): Task status.
        id_task (str): ID of the task to check.

    Returns: None
    """
    updatedAt = get_date()
    
    agenda = load_agenda()

    if not agenda:
        print('the agenda is empty, first add a task.')
        return
        
    if id_task in agenda:
        agenda[id_task]['updatedAt'] = updatedAt
        agenda[id_task]['status'] = arg
    else:
        raise TaskNotFound(id_task)
    
    saved_agenda(agenda)

def list_task(arg: str = None):
    """Lists the tasks stored in the calendar, filtering by optional status.

    Args:
        arg (str, optional): Status of the task to filter.
            Can be 'all', 'in-progress', 'done', or None to display all tasks.
    """
    agenda = load_agenda()

    if not agenda:
        print('the agenda is empty, first add a task.')
        return

    for k, v in agenda.items():

        if arg and v['status'] != arg:
            continue

        print(f'ID: {k}')
        print('-'*115)
        if v["updatedAt"]:
            print(f'Create date: {v["createdAt"]:<} {"|":^10} Update date: {v["updatedAt"]:>}')
        else:
            print(f'Creation date: {v["createdAt"]}')
        print('-'*115)
        print(f'* Description: {v["description"]}')
        print(f'* Status: {v["status"]}')
        print('='*115)
        

def main():
    parser = argparse.ArgumentParser(prog='task-cli', description='task manager')

    subparser = parser.add_subparsers(dest='command', help='available commands')

    # subcommand 'add'
    parser_add = subparser.add_parser('add', help='add a task.')
    parser_add.add_argument('description', type=str, help='task description.')

    # subcommand 'update'
    parser_update = subparser.add_parser('update', help='update a task.')
    parser_update.add_argument('id_task', type=str, help='task ID.')
    parser_update.add_argument('description', type=str, help='new task description.')

    # subcommand 'delete'
    parser_delete = subparser.add_parser('delete', help='delete a task.')
    parser_delete.add_argument('id_task', type=str, help='task ID.')

    # subcommand 'mark-in-progress'
    parser_mark_in_progress = subparser.add_parser('mark-in-progress', help='mark the task as in progress.')
    parser_mark_in_progress.add_argument('id_task', type=str, help='task ID.')

    # subcommand 'mark-done'
    parser_mark_done = subparser.add_parser('mark-done', help='mark the task as complete.')
    parser_mark_done.add_argument('id_task', type=str, help='task ID.')

    # subcommand 'list'
    parser_list = subparser.add_parser('list', help='list all task.')
    parser_list.add_argument('status', nargs='?', choices=['todo', 'in-progress', 'done'], help='Status to filter (optional). valid values: todo | in-progress | done.')

    args = parser.parse_args()

    # CLI
    if args.command == 'add':
        add_task(args.description)

    elif args.command == 'update':
        try:
            update_task(args.id_task, args.description)
        except TaskNotFound as e:
            print(e)

    elif args.command == 'delete':
        try:
            delete_task(args.id_task)
        except TaskNotFound as e:
            print(e)

    elif args.command == 'mark-in-progress':
        try:
            mark_task('in-progress', args.id_task)
        except TaskNotFound as e:
            print(e)

    elif args.command == 'mark-done':
        try:
            mark_task('done', args.id_task)
        except TaskNotFound as e:
            print(e)

    elif args.command == 'list':
        if args.status == 'in-progress':
            list_task(args.status)
        elif args.status == 'done':
            list_task(args.status)
        elif args.status == 'todo':
            list_task(args.status)
        else:
            list_task()

if __name__ == '__main__':
    main()