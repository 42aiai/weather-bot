import requests
import os

def get_weather_forecast_text():
    """OpenWeatherMapから3都市の予報を取得してテキストにする"""
    # GitHubのSecretsに保存したAPIキーを取得
    # ※もしSecrets名が違う場合は、ここを合わせるかGitHub側を修正してください
    api_key = os.getenv("OWM_API_KEY")
    
    if not api_key:
        return "⚠️ 天気予報エラー: APIキーが設定されていません。"

    cities = {
        "東京": "Tokyo",
        "大阪": "Osaka",
        "福岡": "Fukuoka"
    }
    
    # お天気コードを日本語に変換するマッピング（簡易版）
    weather_icons = {
        "Clear": "☀️晴れ",
        "Clouds": "☁️曇り",
        "Rain": "☔雨",
        "Drizzle": "🌦️霧雨",
        "Thunderstorm": "⚡雷雨",
        "Snow": "❄️雪",
        "Mist": "🌫️霧"
    }

    results = []
    try:
        for name, city_en in cities.items():
            # Current Weather API または 5 Day Forecast API を使用
            url = f"https://api.openweathermap.org/data/2.5/weather?q={city_en},jp&appid={api_key}&units=metric&lang=ja"
            res = requests.get(url, timeout=10).json()

            if res.get("cod") != 200:
                results.append(f"{name}: データ取得失敗")
                continue

            # 天気と気温を取得
            main_weather = res["weather"][0]["main"]
            weather_jp = weather_icons.get(main_weather, "❓不明")
            temp_max = res["main"]["temp_max"]
            temp_min = res["main"]["temp_min"]

            results.append(f"{name}: {weather_jp} (最高{temp_max:.1f}℃ / 最低{temp_min:.1f}℃)")
            
    except Exception as e:
        return f"⚠️ 天気予報エラー: {e}"

    header = "☀️【今日の天気予報】\n\n"
    footer = "\n\n(OpenWeatherMap提供)"
    return header + "\n".join(results) + footer
