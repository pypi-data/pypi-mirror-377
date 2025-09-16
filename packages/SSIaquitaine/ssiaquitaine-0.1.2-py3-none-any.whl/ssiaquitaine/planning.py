tasks = []

def add_task(task):
    tasks.append(task)

def list_tasks():
    return tasks

def remove_task(task):
    if task in tasks:
        tasks.remove(task)
