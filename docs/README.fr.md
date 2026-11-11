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

## Mémoire structurée

Demandez à Codex : « Pendant cette tâche, utilise task-checkpoint pour conserver les contraintes, décisions et tentatives échouées ». L’assistant enregistre les étapes importantes ; aucun processus en arrière-plan.

Les entrées sont dans .checkpoint/journal.json : ID, type, date, données immuables et historique. Champs communs : source, scope, certainty, evidence. Contraintes : text ; décisions : choice et reason ; tentatives : action, observed, conclusion, retry_when. save conserve le journal. resume affiche les historiques ; le dernier état indique la validité. Les preuves sont déclarées, pas certifiées. Réessayez en cas d’écriture simultanée.

```sh
checkpoint record constraint --file constraint.json
checkpoint record decision --file decision.json
checkpoint record attempt --file attempt.json
checkpoint records
checkpoint resolve RECORD_ID --status superseded --reason "Replaced by NEW_RECORD_ID"
```

```json
{
  "source": "user",
  "scope": "current release",
  "certainty": "explicit",
  "evidence": "User explicitly requested no database schema changes",
  "text": "Do not change the database schema"
}
```

## Tâches et historique

Placez --task avant la commande pour isoler les tâches. Sans option, la tâche historique par défaut est utilisée. Chaque sauvegarde conserve progression et journal dans history/, sans suppression automatique. Le journal passé de l’ancien format ne peut pas être reconstruit. resume affiche les entrées actives ; --full affiche tous les détails. Lire un ancien checkpoint ne restaure aucun fichier et ne remplace pas latest.

```sh
checkpoint --task login init
checkpoint --task login save --goal "Fix login" --todo "Test refresh"
checkpoint --task billing init
checkpoint tasks
checkpoint --task login history
checkpoint --task login resume
checkpoint --task login resume --full
checkpoint --task login resume --checkpoint CHECKPOINT_ID
```
