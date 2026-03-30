import requests
import os

def get_weather_forecast_text():
    api_key = os.getenv("OPENWEATHER_API_KEY")
    if not api_key:
        return "⚠️ 天気予報エラー: APIキーが設定されていません。"

    cities = {"東京": "Tokyo", "大阪": "Osaka", "福岡": "Fukuoka"}
    weather_icons = {
        "Clear": "☀️晴れ", "Clouds": "☁️曇り", "Rain": "☔雨",
        "Drizzle": "🌦️霧雨", "Thunderstorm": "⚡雷雨", "Snow": "❄️雪", "Mist": "🌫️霧"
    }

    results = []
    try:
        for name, city_en in cities.items():
            url = f"https://api.openweathermap.org/data/2.5/weather?q={city_en},jp&appid={api_key}&units=metric&lang=ja"
            res = requests.get(url, timeout=10).json()
            if res.get("cod") != 200:
                results.append(f"{name}: データ取得失敗")
                continue
            
            weather_jp = weather_icons.get(res["weather"][0]["main"], "❓不明")
            temp_max = res["main"]["temp_max"]
            temp_min = res["main"]["temp_min"]
            results.append(f"{name}: {weather_jp} (最高{temp_max:.1f}℃ / 最低{temp_min:.1f}℃)")
    except Exception as e:
        return f"⚠️ 天気予報エラー: {e}"

    return "☀️【今日の天気予報】\n\n" + "\n".join(results) + "\n\n(OpenWeatherMap提供)"
