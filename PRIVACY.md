# Privacy — Codex Checkpoint

Codex Checkpoint is an independent, free, local task-memory plugin. Contact: commit39@qq.com. Support: https://github.com/fanyifanzaiqingdao/codex-checkpoint/issues.

The bundled Python tool makes no network requests and includes no analytics or payment processing. It reads Git metadata and tracked/nonignored project files to compute fingerprints. It stores task goals, constraints, decision reasons, attempts, validation descriptions and repository metadata in your project’s `.checkpoint/` directory. These records can contain sensitive information if you or your assistant put it there; do not include credentials.

When your coding assistant reads these records, their contents become available to that assistant and may be processed according to the host application's settings and policies. This plugin does not control the host application's processing or GitHub's handling of support reports.

Records remain on your device until you delete them. Saving replaces latest.json; journal.json retains lifecycle history. To delete task memory, remove the project's .checkpoint directory after stopping writers. Your backups or exported copies may retain data. Git's local ignore rule is not encryption and does not prevent you from sharing records manually.

Do not post private records or credentials in public GitHub issues. The maintainer receives information you voluntarily submit through email or GitHub; those services apply their own policies. No guaranteed support-response or deletion deadline is promised by this document.
