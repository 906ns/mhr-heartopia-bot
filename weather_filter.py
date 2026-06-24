"""天気による収穫物の絞り込みロジック"""

# ユーザーが選んだ天気 → マッチする weather 値の対応表
# 「虹」はすべての天気値にマッチする（全件返す）
WEATHER_MATCH = {
    "晴": {"全天気", "晴虹"},
    "雨": {"全天気", "雨雪虹"},
    "虹": {"全天気", "晴虹", "虹", "雨雪虹"},
}


def filter_by_weather(items: list[dict], weather_choice: str) -> list[dict]:
    """収穫物リストを天気で絞り込む。weather_choice は "晴" / "雨" / "虹" のいずれか。"""
    allowed = WEATHER_MATCH.get(weather_choice)
    if allowed is None:
        return []
    return [item for item in items if item.get("weather") in allowed]
