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

1. チャンネルで「魚」「虫」「鳥」（ひらがなの「さかな」「むし」「とり」でも可）を送信
2. 天気（☀️晴 / 🌧️雨 / 🌈虹）を選択
3. 結果がレベル順に一覧表示されます（件数が多い場合はページ送り対応）

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
