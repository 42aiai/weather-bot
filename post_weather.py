import os
import requests
from datetime import datetime, timezone, timedelta
from karotterpy import KarotterDevClient

# --- 設定 ---
OWM_API_KEY = os.environ["OWM_API_KEY"]
KAROTTER_API_KEY = os.environ["KAROTTER_API_KEY"]

CITIES = [
    {"name": "東京", "lat": 35.6895, "lon": 139.6917},
    {"name": "大阪", "lat": 34.6937, "lon": 135.5023},
    {"name": "福岡", "lat": 33.5904, "lon": 130.4017},
]

TARGET_HOURS = [9, 12, 15, 18, 21]

JST = timezone(timedelta(hours=9))

WEATHER_EMOJI = {
    "Clear": "☀️",
    "Clouds": "☁️",
    "Rain": "☔",
    "Drizzle": "🌧️",
    "Thunderstorm": "⛈️",
    "Snow": "❄️",
    "Mist": "🌫️",
    "Fog": "🌫️",
    "Haze": "🌫️",
}

def get_emoji(main: str) -> str:
    return WEATHER_EMOJI.get(main, "🌡️")

def fetch_forecast(lat: float, lon: float) -> dict:
    """OpenWeatherMap 3時間予報を取得し {unix_timestamp: {...}} の辞書で返す"""
    url = "https://api.openweathermap.org/data/2.5/forecast"
    params = {
        "lat": lat,
        "lon": lon,
        "appid": OWM_API_KEY,
        "units": "metric",
        "lang": "ja",
    }
    resp = requests.get(url, params=params, timeout=10)
    resp.raise_for_status()
    data = resp.json()

    result = {}
    for item in data["list"]:
        result[item["dt"]] = {
            "main": item["weather"][0]["main"],
            "temp": round(item["main"]["temp"]),
            "pop": round(item.get("pop", 0) * 100),  # 0.0〜1.0 → %
        }
    return result

def find_forecast_for_hour(forecast: dict, target_dt: datetime) -> dict | None:
    """target_dt に最も近い予報エントリを返す（±90分以内）"""
    target_ts = int(target_dt.timestamp())
    best = None
    best_diff = 91 * 60  # 91分

    for ts, data in forecast.items():
        diff = abs(ts - target_ts)
        if diff < best_diff:
            best_diff = diff
            best = data

    return best

def build_city_line(city_name: str, forecasts_for_hours: list[dict | None]) -> str:
    parts = []
    for f in forecasts_for_hours:
        if f is None:
            parts.append("？")
            continue
        emoji = get_emoji(f["main"])
        temp = f["temp"]
        pop = f["pop"]
        if pop > 0:
            parts.append(f"{emoji}{temp} {pop}%")
        else:
            parts.append(f"{emoji}{temp}")

    return f"📍{city_name}｜" + "｜".join(parts)

def main():
    now_jst = datetime.now(JST)
    # 投稿対象日（翌日 or 当日）
    # 6:30実行 → 当日の9〜21時を対象
    target_date = now_jst.date()

    # ヘッダー行
    weekday_ja = ["月", "火", "水", "木", "金", "土", "日"][target_date.weekday()]
    header = f"【{target_date.strftime('%m/%d')}({weekday_ja}) {'/'.join(str(h) for h in TARGET_HOURS)}時】"

    lines = [header]

    for city in CITIES:
        forecast = fetch_forecast(city["lat"], city["lon"])

        forecasts_for_hours = []
        for hour in TARGET_HOURS:
            target_dt = datetime(
                target_date.year, target_date.month, target_date.day,
                hour, 0, 0, tzinfo=JST
            )
            f = find_forecast_for_hour(forecast, target_dt)
            forecasts_for_hours.append(f)

        line = build_city_line(city["name"], forecasts_for_hours)
        lines.append(line)

    post_text = "\n".join(lines)
    print("投稿内容:\n", post_text)

    client = KarotterDevClient(KAROTTER_API_KEY)
    client.tweets.create(post_text)
    print("投稿完了！")

if __name__ == "__main__":
    main()
