# Codex Checkpoint

Relevo local de tareas para asistentes de programación. Requiere Python 3.10+ y Git.

[en](../README.md) | [zh-CN](README.zh-CN.md) | [ja](README.ja.md) | [ko](README.ko.md) | [es](README.es.md) | [fr](README.fr.md)

## Instalación

```sh
python3 -m pip install .
```

## Uso

```sh
cd /path/to/your/git-project
checkpoint init
checkpoint save --goal "Fix login" --constraint "Keep public API" --done "Found cause" --todo "Implement fix" --verified "Existing tests passed" --unverified "Browser login flow"
checkpoint status
checkpoint resume
```

Cada guardado sustituye al anterior. Repita las opciones de lista para añadir elementos. Las verificaciones las declara el usuario; la herramienta no las ejecuta ni certifica.

```sh
checkpoint --repo /path/to/project status
```

## Privacidad y límites

Los datos se guardan en .checkpoint/latest.json, excluido localmente de Git. No hay acceso a chats, red, cambios de código ni guardado automático integrado. Revise los datos sensibles antes de compartir. El estado de Git y SHA-256 detectan cambios en archivos versionados y nuevos no ignorados; se excluyen los ignorados y el contenido de submódulos. Guarde con los archivos estables. resume imprime texto para un nuevo chat; no inicia Codex ni restaura archivos.
