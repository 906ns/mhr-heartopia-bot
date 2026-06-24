"""ハートピア収穫物検索 Discord Bot"""

import json
import logging
import math
import os
from pathlib import Path

import discord
from discord.ext import commands
from dotenv import load_dotenv

from weather_filter import filter_by_weather

# ログ設定
logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
logger = logging.getLogger(__name__)

load_dotenv()

# --- データ読み込み ---
DATA_PATH = Path(__file__).parent / "data" / "harvest.json"

try:
    with open(DATA_PATH, encoding="utf-8") as f:
        _raw = json.load(f)
    HARVEST_DATA: dict[str, list[dict]] = {
        "fish": _raw["fish"],
        "insect": _raw["insect"],
        "bird": _raw["bird"],
    }
    logger.info("harvest.json を読み込みました（魚%d 虫%d 鳥%d）",
                len(HARVEST_DATA["fish"]), len(HARVEST_DATA["insect"]), len(HARVEST_DATA["bird"]))
except FileNotFoundError:
    logger.error("データファイルが見つかりません: %s", DATA_PATH)
    raise SystemExit(1)
except (json.JSONDecodeError, KeyError) as e:
    logger.error("データファイルの読み込みに失敗しました: %s", e)
    raise SystemExit(1)

# メッセージ → カテゴリの対応（完全一致）
MESSAGE_TO_CATEGORY = {
    "魚": ("fish", "🐟 魚"),
    "虫": ("insect", "🦋 虫"),
    "鳥": ("bird", "🐦 鳥"),
}

# 天気定義（ボタン表示名 → フィルタキー）
WEATHERS = {
    "☀️ 晴": "晴",
    "🌧️ 雨": "雨",
    "🌈 虹": "虹",
}

# 1ページあたりの表示件数
ITEMS_PER_PAGE = 10

# ボタンのタイムアウト（秒）
VIEW_TIMEOUT = 120


# --- Embed 生成 ---

def _format_item_line(item: dict) -> str:
    """1件分の表示ブロックを生成する。"""
    return (
        f"**{item['name']}**　`Lv.{item['level']}`\n"
        f"　　⏰ {item['time']}　│　📍 {item['location']}"
    )


def build_result_embeds(
    items: list[dict],
    category_label: str,
    weather_label: str,
) -> list[discord.Embed]:
    """絞り込み結果をレベル順に並べた Embed リストとして生成する。"""
    if not items:
        embed = discord.Embed(
            title=f"{category_label}（{weather_label}）",
            description="該当する収穫物が見つかりませんでした",
            color=discord.Color.greyple(),
        )
        return [embed]

    # レベル昇順でソート
    sorted_items = sorted(items, key=lambda i: i["level"])

    # ページ分割（アイテム数ベース）
    total_pages = math.ceil(len(sorted_items) / ITEMS_PER_PAGE)
    embeds = []

    for page_idx in range(total_pages):
        start = page_idx * ITEMS_PER_PAGE
        page_items = sorted_items[start : start + ITEMS_PER_PAGE]

        # アイテム間を空行で区切って見やすくする
        blocks = [_format_item_line(item) for item in page_items]
        description = "\n\n".join(blocks)

        embed = discord.Embed(
            title=f"{category_label}（{weather_label}）",
            description=description,
            color=discord.Color.green(),
        )

        footer_parts = [f"計{len(items)}件"]
        if total_pages > 1:
            footer_parts.append(f"ページ {page_idx + 1}/{total_pages}")
        embed.set_footer(text="　".join(footer_parts))

        embeds.append(embed)

    return embeds


# --- ページング用 View ---

class PaginationView(discord.ui.View):
    """結果の Embed をページ送りするボタン付き View。"""

    def __init__(self, embeds: list[discord.Embed]):
        super().__init__(timeout=VIEW_TIMEOUT)
        self.embeds = embeds
        self.current_page = 0
        self._update_buttons()

    def _update_buttons(self):
        """現在のページに応じてボタンの有効/無効を切り替える。"""
        self.prev_button.disabled = self.current_page <= 0
        self.next_button.disabled = self.current_page >= len(self.embeds) - 1
        if len(self.embeds) <= 1:
            self.prev_button.disabled = True
            self.next_button.disabled = True

    @discord.ui.button(label="◀ 前へ", style=discord.ButtonStyle.secondary)
    async def prev_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        self.current_page = max(0, self.current_page - 1)
        self._update_buttons()
        await interaction.response.edit_message(embed=self.embeds[self.current_page], view=self)

    @discord.ui.button(label="次へ ▶", style=discord.ButtonStyle.secondary)
    async def next_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        self.current_page = min(len(self.embeds) - 1, self.current_page + 1)
        self._update_buttons()
        await interaction.response.edit_message(embed=self.embeds[self.current_page], view=self)

    async def on_timeout(self):
        """タイムアウト後、ボタンを無効化する。"""
        for child in self.children:
            if isinstance(child, discord.ui.Button):
                child.disabled = True
        if self.message:
            try:
                await self.message.edit(view=self)
            except discord.NotFound:
                pass


# --- 天気選択 View ---

class WeatherSelectView(discord.ui.View):
    """天気選択ボタンを表示する View。"""

    def __init__(self, category_key: str, category_label: str):
        super().__init__(timeout=VIEW_TIMEOUT)
        self.category_key = category_key
        self.category_label = category_label

        # 天気ボタンを動的に追加
        for label, weather_key in WEATHERS.items():
            button = discord.ui.Button(label=label, style=discord.ButtonStyle.primary)
            button.callback = self._make_callback(weather_key, label)
            self.add_item(button)

    def _make_callback(self, weather_key: str, weather_label: str):
        """天気ボタンが押されたときのコールバック。結果を表示する。"""
        async def callback(interaction: discord.Interaction):
            # 天気で絞り込み
            items = HARVEST_DATA[self.category_key]
            filtered = filter_by_weather(items, weather_key)

            # Embed 生成（レベル順でソート、各行にレベル表示あり）
            embeds = build_result_embeds(filtered, self.category_label, weather_label)

            # ページング付きで結果を表示
            view = PaginationView(embeds)
            await interaction.response.edit_message(
                content=None,
                embed=embeds[0],
                view=view,
            )
            view.message = await interaction.original_response()

        return callback

    async def on_timeout(self):
        for child in self.children:
            if isinstance(child, discord.ui.Button):
                child.disabled = True
        if self.message:
            try:
                await self.message.edit(view=self)
            except discord.NotFound:
                pass


# --- Bot 本体 ---

# メッセージ内容を読むために message_content インテントを有効化
intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)


@bot.event
async def on_ready():
    logger.info("Bot 起動完了: %s", bot.user)


@bot.event
async def on_message(message: discord.Message):
    # Bot 自身のメッセージは無視
    if message.author.bot:
        return

    # メッセージが「魚」「虫」「鳥」と完全一致したら天気選択を表示
    text = message.content.strip()
    if text in MESSAGE_TO_CATEGORY:
        category_key, category_label = MESSAGE_TO_CATEGORY[text]
        view = WeatherSelectView(category_key, category_label)
        sent = await message.channel.send(
            f"{category_label} → 天気を選んでください",
            view=view,
        )
        view.message = sent


# Bot 起動
token = os.getenv("DISCORD_TOKEN")
if not token:
    logger.error("DISCORD_TOKEN が設定されていません。.env ファイルを確認してください。")
    raise SystemExit(1)

bot.run(token)
