audits = []

def add_audit(audit):
    audits.append(audit)

def list_audits():
    return audits

def remove_audit(audit):
    if audit in audits:
        audits.remove(audit)
