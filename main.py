import os
import requests
import hashlib

def get_weather():
    api_key = os.getenv("OWM_API_KEY")
    cities = {"東京": "Tokyo", "大阪": "Osaka", "福岡": "Fukuoka"}
    icons = {"Clear": "☀️晴れ", "Clouds": "☁️曇り", "Rain": "☔雨", "Snow": "❄️雪", "Drizzle": "🌦️", "Thunderstorm": "⚡"}
    
    results = []
    try:
        for name, city_en in cities.items():
            url = f"https://api.openweathermap.org/data/2.5/weather?q={city_en},jp&appid={api_key}&units=metric&lang=ja"
            res = requests.get(url, timeout=10).json()
            
            # 天気アイコンの取得
            weather_main = res["weather"][0]["main"]
            w = icons.get(weather_main, "☁️曇り")
            
            # 気温の取得
            t = res["main"]["temp"]
            results.append(f"{name}: {w} ({t:.1f}℃)")
            
        return "☀️【今日の天気】\n\n" + "\n".join(results)
    except Exception as e:
        print(f"Weather API Error: {e}")
        return "天気データの取得に失敗しました。"

def post(text):
    user_id = os.getenv("KAROTTER_ID")
    user_pw = os.getenv("KAROTTER_PW")
    
    if not user_id or not user_pw:
        print("Error: ID or PW not found.")
        return

    # IDとPWを直接送る方式
    url = "https://api.karotter.com/post"
    params = {
        "id": user_id,
        "password": user_pw,
        "text": text
    }
    
    try:
        res = requests.get(url, params=params, timeout=10)
        print(f"Post status: {res.status_code}")
        print(f"Response: {res.text}")
    except Exception as e:
        print(f"Post Error: {e}")

# ここが重要です！これがないとプログラムが動き出しません
if __name__ == "__main__":
    msg = get_weather()
    post(msg)
