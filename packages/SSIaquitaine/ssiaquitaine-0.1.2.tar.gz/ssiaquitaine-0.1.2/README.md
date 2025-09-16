# SSIaquitaine

Un outil de gestion de projet pour un SSI (Système de Sécurité Informatique).

## Fonctionnalités

- **Core**: Fonctions de base pour l'accueil des utilisateurs SSI.
- **Planning**: Gestion simple des tâches (ajouter, lister, supprimer).
- **Audit**: Module pour ajouter et suivre des audits de sécurité.
- **Reporting**: Génération d'un rapport texte de l'état des projets SSI.
- **Gestion des tâches**: Un module complet pour gérer les tâches avec des statuts, des priorités et des descriptions.

## Améliorations de la version 0.1.1

- **Nouveau module de gestion des tâches**: `ssiaquitaine.tasks` avec `TaskManager` pour une gestion avancée.
- **Affichage coloré**: Utilisation de `colorama` pour améliorer la lisibilité des statuts de tâches.
- **Export de rapports**: Fonctionnalité pour exporter des rapports de tâches au format texte.
- **Configuration centralisée**: Passage à `pyproject.toml` pour une gestion moderne du packaging.

## Architecture

```
SSIaquitaine
├── Core       → Fonctions de base (welcome)
├── Planning   → Gestion des tâches SSI
├── Audit      → Suivi des audits de sécurité
├── Reporting  → Génération de rapports
└── Tasks      → Gestion avancée des tâches
```

## Exemple d'utilisation

### Utilisation en Python

```python
from ssiaquitaine.tasks import TaskManager

tm = TaskManager()
tm.add_task("Analyser logs firewall", "Audit sécurité hebdomadaire", "high")
tm.add_task("Former équipe", "Session de sensibilisation SSI", "medium")
tm.update_status(1, "in-progress")
tm.list_tasks()
tm.export_report()
```

### Utilisation en ligne de commande (CLI)

```bash
ssiaquitaine-welcome Mohamed
```

## Installation

1. Clonez le dépôt :
   ```bash
   git clone https://github.com/tuteur1/SSIaquitaine.git
   cd SSIaquitaine
   ```
2. Créez et activez un environnement virtuel :
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   ```
3. Installez le package :
   ```bash
   pip install .
   ```

## Contribution

Les contributions sont les bienvenues ! Veuillez suivre les étapes suivantes :
1. Fork le dépôt.
2. Créez une nouvelle branche (`git checkout -b feature/AwesomeFeature`).
3. Effectuez vos modifications et commitez-les (`git commit -m 'Add some AwesomeFeature'`).
4. Poussez vers la branche (`git push origin feature/AwesomeFeature`).
5. Ouvrez une Pull Request.

## Licence

Ce projet est sous licence MIT. Voir le fichier [LICENSE](LICENSE) pour plus de détails.
