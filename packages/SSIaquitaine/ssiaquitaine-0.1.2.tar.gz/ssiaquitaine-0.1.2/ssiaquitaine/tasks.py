import os
from colorama import Fore, Style, init

init(autoreset=True)

class Task:
    def __init__(self, id, title, description, priority="medium", status="todo"):
        self.id = id
        self.title = title
        self.description = description
        self.priority = priority
        self.status = status

class TaskManager:
    def __init__(self):
        self.tasks = []
        self.next_id = 1

    def add_task(self, title, description, priority="medium"):
        task = Task(self.next_id, title, description, priority)
        self.tasks.append(task)
        self.next_id += 1

    def list_tasks(self):
        for task in self.tasks:
            status_color = {
                "todo": Fore.RED + "❌",
                "in-progress": Fore.YELLOW + "🟡",
                "done": Fore.GREEN + "✅",
            }.get(task.status, Fore.WHITE)
            print(f"{status_color} ID: {task.id} | Titre: {task.title} | Priorité: {task.priority} | Statut: {task.status}{Style.RESET_ALL}")

    def update_status(self, task_id, new_status):
        for task in self.tasks:
            if task.id == task_id:
                task.status = new_status
                break

    def export_report(self, file_path="reports/tasks_report.txt"):
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        with open(file_path, "w") as f:
            f.write("Rapport des tâches SSI\n")
            f.write("="*30 + "\n")
            for task in self.tasks:
                f.write(f"ID: {task.id}\n")
                f.write(f"Titre: {task.title}\n")
                f.write(f"Description: {task.description}\n")
                f.write(f"Priorité: {task.priority}\n")
                f.write(f"Statut: {task.status}\n")
                f.write("-"*30 + "\n")
