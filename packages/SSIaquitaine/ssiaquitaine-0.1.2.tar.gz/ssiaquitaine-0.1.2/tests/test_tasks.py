import pytest
from ssiaquitaine.tasks import TaskManager

@pytest.fixture
def task_manager():
    return TaskManager()

def test_add_task(task_manager):
    task_manager.add_task("Test Task", "Test Description")
    assert len(task_manager.tasks) == 1
    assert task_manager.tasks[0].title == "Test Task"

def test_update_status(task_manager):
    task_manager.add_task("Test Task", "Test Description")
    task_manager.update_status(1, "done")
    assert task_manager.tasks[0].status == "done"

def test_export_report(task_manager, tmp_path):
    task_manager.add_task("Test Task", "Test Description")
    file_path = tmp_path / "report.txt"
    task_manager.export_report(file_path)
    assert file_path.read_text() != ""
