# ハートピア収穫物検索 Discord Bot

ゲーム「ハートピアスローライフ」の収穫物（魚・虫・鳥）を天気で絞り込み検索する Discord Bot です。

## セットアップ

### 1. 依存パッケージのインストール

```bash
pip install -r requirements.txt
```

### 2. Bot トークンの設定

`.env.example` をコピーして `.env` を作成し、Discord Bot のトークンを設定します。

```bash
cp .env.example .env
```

`.env` を編集して `DISCORD_TOKEN=` の後にトークンを貼り付けてください。

### 3. Discord Developer Portal での設定

1. [Discord Developer Portal](https://discord.com/developers/applications) でアプリケーションを作成
2. Bot を有効化してトークンをコピー
3. OAuth2 → URL Generator で `bot` と `applications.commands` スコープを選択
4. Bot Permissions で `Send Messages` を選択
5. 生成された URL でサーバーに招待

### 4. Bot の起動

```bash
python bot.py
```

## 使い方

- チャットに `魚`・`虫`・`鳥` のいずれかを送信する（完全一致）
- 表示されたボタンから天気（☀️ 晴 / 🌧️ 雨 / 🌈 虹）を選択する
- 条件に合う収穫物が **レベル昇順** で一覧表示される
- 結果が 11 件以上の場合は **「◀ 前へ」「次へ ▶」** ボタンでページを切り替える（1 ページあたり 10 件）

## 注意事項

- `魚`・`虫`・`鳥` は **完全一致** のみ反応する（「魚釣り」「虫探し」などは無効）
- 天気・ページングのボタンは **送信から 120 秒** で自動的に無効になる
- データには **通常収穫物（Lv.1〜上級）** のみ収録されており、**イベント限定アイテムは含まれない**
- 天気の対応は以下のとおり
  - ☀️ 晴 → 全天気・晴虹 の収穫物
  - 🌧️ 雨 → 全天気・雨雪虹 の収穫物
  - 🌈 虹 → 全天気・晴虹・虹・雨雪虹 の収穫物（全件）
- Bot が起動していない場合はメッセージに反応しない
- `DISCORD_TOKEN` が未設定の場合、Bot は起動しない（`.env` を確認すること）

## ファイル構成

```
mhr-heartopia-bot/
├── bot.py              # メイン（スラッシュコマンドとUI）
├── weather_filter.py   # 天気絞り込みロジック
├── data/
│   └── harvest.json    # 収穫物データ
├── .env.example
├── requirements.txt
└── README.md
```
