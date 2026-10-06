#!/usr/bin/env python3
"""明日の天気を取得して通知する。Open-Meteo (APIキー不要) を使用。"""
import json
import os
import urllib.parse
import urllib.request

API = "https://api.open-meteo.com/v1/forecast"

# WMO weather code -> 日本語
WEATHER_CODES = {
    0: "快晴", 1: "晴れ", 2: "一部曇り", 3: "曇り",
    45: "霧", 48: "霧氷",
    51: "弱い霧雨", 53: "霧雨", 55: "強い霧雨",
    56: "弱い着氷性の霧雨", 57: "強い着氷性の霧雨",
    61: "弱い雨", 63: "雨", 65: "強い雨",
    66: "弱い着氷性の雨", 67: "強い着氷性の雨",
    71: "弱い雪", 73: "雪", 75: "強い雪", 77: "霧雪",
    80: "弱いにわか雨", 81: "にわか雨", 82: "激しいにわか雨",
    85: "弱いにわか雪", 86: "強いにわか雪",
    95: "雷雨", 96: "雷雨(小さい雹)", 99: "雷雨(大きい雹)",
}


def fetch_forecast(lat, lon, tz):
    query = urllib.parse.urlencode({
        "latitude": lat,
        "longitude": lon,
        "daily": "weather_code,temperature_2m_max,temperature_2m_min,"
                 "precipitation_probability_max",
        "timezone": tz,
        "forecast_days": 2,
    })
    with urllib.request.urlopen(f"{API}?{query}", timeout=30) as res:
        return json.load(res)


def format_message(data, place):
    """daily の 2 日目(index 1)が明日。"""
    d = data["daily"]
    code = d["weather_code"][1]
    rain = d["precipitation_probability_max"][1]
    lines = [
        f"【{place}】{d['time'][1]} の天気",
        f"天気: {WEATHER_CODES.get(code, f'不明({code})')}",
        f"気温: 最高 {d['temperature_2m_max'][1]:.0f}℃ / 最低 {d['temperature_2m_min'][1]:.0f}℃",
        f"降水確率: {'-' if rain is None else f'{rain}%'}",
    ]
    if rain is not None and rain >= 50:
        lines.append("☂ 傘を忘れずに!")
    return "\n".join(lines)


def _post(url, body, headers):
    req = urllib.request.Request(url, data=body, headers=headers, method="POST")
    urllib.request.urlopen(req, timeout=30).close()


def notify(message):
    """設定されている通知先すべてに送る。1つも無ければ標準出力のみ。"""
    sent = False
    if topic := os.environ.get("NTFY_TOPIC"):
        _post(f"https://ntfy.sh/{topic}", message.encode(),
              {"Title": "Tomorrow's weather"})
        sent = True
    if url := os.environ.get("DISCORD_WEBHOOK_URL"):
        _post(url, json.dumps({"content": message}).encode(),
              {"Content-Type": "application/json", "User-Agent": "weather-notify"})
        sent = True
    if url := os.environ.get("SLACK_WEBHOOK_URL"):
        _post(url, json.dumps({"text": message}).encode(),
              {"Content-Type": "application/json"})
        sent = True
    return sent


def main():
    # Actions では未設定の vars が空文字になるため `or` でデフォルトに落とす
    place = os.environ.get("PLACE_NAME") or "東京"
    data = fetch_forecast(
        os.environ.get("LATITUDE") or "35.6895",
        os.environ.get("LONGITUDE") or "139.6917",
        os.environ.get("TIMEZONE") or "Asia/Tokyo",
    )
    message = format_message(data, place)
    print(message)
    if not notify(message):
        print("(通知先が未設定のため標準出力のみ)")


if __name__ == "__main__":
    main()
