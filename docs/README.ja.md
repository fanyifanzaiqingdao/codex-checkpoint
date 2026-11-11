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
