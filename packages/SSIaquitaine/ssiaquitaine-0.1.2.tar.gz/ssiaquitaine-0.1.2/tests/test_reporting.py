import pytest
from ssiaquitaine.reporting import generate_report

def test_generate_report():
    audits = ["Audit 1", "Audit 2"]
    tasks = ["Task 1", "Task 2"]
    report = generate_report(audits, tasks)
    assert "Rapport des Audits et Tâches:" in report
    assert "Audits:" in report
    assert "- Audit 1" in report
    assert "- Audit 2" in report
    assert "Tâches:" in report
    assert "- Task 1" in report
    assert "- Task 2" in report
