# Codex Checkpoint

## Plugin Codex (recommandé)

Exécutez la commande ci-dessous depuis ce dépôt, puis installez et activez le plugin dans le répertoire de plugins de bureau. Ouvrez une nouvelle conversation dans votre projet Git et demandez « Utilise task-checkpoint pour sauvegarder la progression » ou « Utilise task-checkpoint pour reprendre la tâche ». Pas besoin de pip ; Python 3.10+ et Git restent nécessaires. La sauvegarde n’est pas automatique. La disponibilité dépend du client. L’installation et l’appel dans l’application restent à vérifier.

```sh
codex plugin marketplace add .
```

Transmission locale de tâches pour assistants de programmation. Python 3.10+ et Git sont nécessaires.

[en](../README.md) | [zh-CN](README.zh-CN.md) | [ja](README.ja.md) | [ko](README.ko.md) | [es](README.es.md) | [fr](README.fr.md)

## Installation

```sh
python3 -m pip install .
```

## Utilisation

```sh
cd /path/to/your/git-project
checkpoint init
checkpoint save --goal "Fix login" --constraint "Keep public API" --done "Found cause" --todo "Implement fix" --verified "Existing tests passed" --unverified "Browser login flow"
checkpoint status
checkpoint resume
```

Chaque sauvegarde remplace la précédente. Répétez les options de liste pour ajouter des éléments. Les vérifications sont déclarées par l’utilisateur ; cet outil ne les exécute ni ne les certifie.

```sh
checkpoint --repo /path/to/project status
```

## Confidentialité et limites

Les données sont dans .checkpoint/latest.json, exclu localement de Git. Aucun accès aux conversations, appel réseau, changement de code ou enregistrement automatique intégré. Vérifiez les données sensibles avant tout partage. Git et SHA-256 détectent les changements des fichiers suivis et nouveaux non ignorés ; les fichiers ignorés et le contenu des sous-modules sont exclus. Sauvegardez lorsque les fichiers sont stables. resume affiche du texte à coller dans une nouvelle conversation, sans lancer Codex ni restaurer les fichiers.
