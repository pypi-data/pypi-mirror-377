import pytest
from ssiaquitaine.planning import add_task, list_tasks, remove_task, tasks

@pytest.fixture(autouse=True)
def clear_tasks():
    tasks.clear()

def test_add_task():
    add_task("New Task")
    assert "New Task" in list_tasks()

def test_list_tasks():
    assert list_tasks() == []
    add_task("Task 1")
    add_task("Task 2")
    assert list_tasks() == ["Task 1", "Task 2"]

def test_remove_task():
    add_task("Task to remove")
    remove_task("Task to remove")
    assert "Task to remove" not in list_tasks()
