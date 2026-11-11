# Codex Checkpoint

## Plugin de Codex (recomendado)

Ejecute el comando siguiente desde este repositorio e instale y active el plugin en el directorio de plugins de escritorio. Abra un chat nuevo en su proyecto Git y pida “Usa task-checkpoint para guardar el progreso” o “Usa task-checkpoint para retomar la tarea”. No necesita pip; requiere Python 3.10+ y Git. No guarda automáticamente. La disponibilidad depende del cliente. La instalación e invocación dentro de la aplicación aún no se han verificado.

```sh
codex plugin marketplace add .
```

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

## Memoria estructurada

Pida a Codex: “Durante esta tarea, usa task-checkpoint para mantener restricciones, decisiones e intentos fallidos”. El asistente registra hitos; no hay ejecución en segundo plano.

Los registros viven en .checkpoint/journal.json con ID, tipo, fecha, datos inmutables e historial. Campos comunes: source, scope, certainty, evidence. Restricciones: text; decisiones: choice y reason; intentos: action, observed, conclusion, retry_when. save conserva el diario. resume muestra el historial; el último estado indica vigencia. La evidencia es declarada, no certificada. Reintente las escrituras concurrentes.

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

## Tareas e historial

Use --task antes del comando para aislar tareas. Si se omite, se usa la tarea predeterminada anterior. Cada guardado conserva progreso y diario en history/, sin limpieza automática. El diario histórico del formato anterior no se puede reconstruir. resume muestra registros activos; --full muestra todos los detalles. Consultar un checkpoint antiguo no restaura archivos ni cambia latest.

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
