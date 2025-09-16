import pytest
from ssiaquitaine.audit import add_audit, list_audits, remove_audit, audits

@pytest.fixture(autouse=True)
def clear_audits():
    audits.clear()

def test_add_audit():
    add_audit("New Audit")
    assert "New Audit" in list_audits()

def test_list_audits():
    assert list_audits() == []
    add_audit("Audit 1")
    add_audit("Audit 2")
    assert list_audits() == ["Audit 1", "Audit 2"]

def test_remove_audit():
    add_audit("Audit to remove")
    remove_audit("Audit to remove")
    assert "Audit to remove" not in list_audits()
