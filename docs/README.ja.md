# Codex Checkpoint

## Codex プラグイン（推奨）

このリポジトリで次のコマンドを実行し、デスクトップのプラグイン一覧からインストールして有効にしてください。対象の Git プロジェクトで新しいチャットを開き、「task-checkpoint で進捗を保存」または「task-checkpoint で前の作業を再開」と伝えます。pip は不要ですが Python 3.10+ と Git が必要です。自動保存ではありません。画面や対応状況はバージョンによって異なります。アプリ内のインストールと呼び出しは未検証です。

```sh
codex plugin marketplace add .
```

コーディング助手向けのローカル作業引き継ぎ。Python 3.10 以上と Git が必要です。

[en](../README.md) | [zh-CN](README.zh-CN.md) | [ja](README.ja.md) | [ko](README.ko.md) | [es](README.es.md) | [fr](README.fr.md)

## インストール

```sh
python3 -m pip install .
```

## 使い方

```sh
cd /path/to/your/git-project
checkpoint init
checkpoint save --goal "Fix login" --constraint "Keep public API" --done "Found cause" --todo "Implement fix" --verified "Existing tests passed" --unverified "Browser login flow"
checkpoint status
checkpoint resume
```

保存するたびに前の記録を上書きします。リスト用のオプションは繰り返せます。検証結果は利用者が記入し、ツールは検証を実行しません。

```sh
checkpoint --repo /path/to/project status
```

## プライバシーと制限

記録は .checkpoint/latest.json に保存され、Git のローカル除外設定で無視されます。通信、チャットの読み取り、コード変更、自動保存連携はありません。共有前に機密情報を確認してください。Git 状態と SHA-256 は追跡済みファイルと無視されていない新規ファイルを確認します。無視対象とサブモジュール内部は対象外です。ファイルが安定した状態で保存してください。resume は新しいチャットに貼る文章だけを出力し、Codex の起動やファイルの復元は行いません。

## 構造化タスク記憶

Codex に「この作業中、task-checkpoint でユーザーの制約、判断理由、失敗した試行を継続して記録してください」と伝えます。バックグラウンド処理ではなく、助手が重要な節目で呼び出します。

記録は .checkpoint/journal.json に保存され、ID、種類、作成時刻、不変の内容、状態履歴を持ちます。共通項目は source、scope、certainty、evidence。制約は text、判断は choice と reason、試行は action、observed、conclusion、retry_when が必須です。save は記録を消しません。resume は全履歴を表示し、最後の状態で有効性を判断します。証拠は自己申告です。並行書き込みは再試行してください。

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

## タスクと履歴

コマンドの前に --task を指定して分離します。省略時は旧形式の既定タスクです。保存ごとに history/ に進捗と記録を保持します。自動削除しません。古い形式の過去の記録は復元できません。通常は有効な記録のみ表示し、--full で全履歴を表示します。履歴の参照はコードや最新状態を変更しません。

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

## v0.5.0

復元時に追加・削除・変更ファイルと検証の古さを表示します。旧記録は個別比較できません。制約、判断、試行の順で、同種ではユーザー由来を優先します。--supersedes は原子的に記録を置換し、replacement_id で関連付けます。

```sh
checkpoint --task login record constraint --file new-rule.json --supersedes OLD_RECORD_ID
checkpoint --task login resume
```
