def generate_report(audits, tasks):
    report = "Rapport des Audits et Tâches:\n\n"
    report += "Audits:\n"
    for audit in audits:
        report += f"- {audit}\n"
    report += "\nTâches:\n"
    for task in tasks:
        report += f"- {task}\n"
    return report
