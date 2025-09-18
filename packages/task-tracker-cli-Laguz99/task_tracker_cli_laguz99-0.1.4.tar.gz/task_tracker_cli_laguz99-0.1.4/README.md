# Task Tracker CLI app

This is a light app for the administration of tasks from the Command-Line Interface (CLI).

## Features

* Add a new task with your description.
* Update the description of an existing task.
* Change the status of a task such as: "todo", "in-progress" or "done".
* Eliminate a task for your ID.
* List all tasks or list for your status.

## Installation

```bash
pip install task-tracker-cli-Laguz99
```


## Usage

**Add a task**
```bash
# Adding a new task
taskcli add "Buy groceries"
# ouput: Task added successfully (ID: 1)
```

**Update a task**
```bash
# Updating a task
taskcli update 1 "Buy groceries an cook dinner"
```

**Mark task status**
```bash
# Marking a task as in progress or done
taskcli mark-in-progress 1
taskcli mark-done 1
```
**Delete a task**
```bash
# deleting a task
taskcli delete 1
# ouput: Task 1 delete
```

**List tasks**
```bash
# list all tasks
taskcli list

# list tasks by status:
# todo
taskcli list todo

# in progress
taskcli list in-progress

# done
taskcli list done
```

**Help**
```bash
taskcli -h
taskcli --help
```
