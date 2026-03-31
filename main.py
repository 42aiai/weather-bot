import os
import requests
from datetime import datetime, timedelta, timezone
from karotterpy import KarotterDevClient

def get_weather():
    api_key = os.getenv("OWM_API_KEY")
    cities = {"東京": "Tokyo", "大阪": "Osaka", "福岡": "Fukuoka"}
    icons = {"Clear": "☀️", "Clouds": "☁️", "Rain": "☔", "Snow": "❄️", "Drizzle": "🌦️", "Thunderstorm": "⚡"}
    
    jst = timezone(timedelta(hours=9))
    now = datetime.now(jst)
    date_str = now.strftime("%m/%d")
    week_days = ["月", "火", "水", "木", "金", "土", "日"]
    w_day = week_days[now.weekday()]
    
    target_hours = [9, 12, 15, 18, 21]
    results = [f"【{date_str}({w_day}) 9/12/15/18/21時】"]

    try:
        for name, city_en in cities.items():
            url = f"https://api.openweathermap.org/data/2.5/forecast?q={city_en},jp&appid={api_key}&units=metric&lang=ja"
            res = requests.get(url, timeout=10)
            res.raise_for_status()
            data = res.json()
            
            forecasts = []
            today = now.date()
            for item in data["list"]:
                dt_jst = datetime.fromtimestamp(item["dt"], jst)
                if dt_jst.date() == today and dt_jst.hour in target_hours:
                    w_key = item["weather"][0]["main"]
                    icon = icons.get(w_key, "☁️")
                    temp = int(item["main"]["temp"])
                    pop = int(item.get("pop", 0) * 100)
                    pop_str = f" {pop}%" if pop >= 20 else ""
                    forecasts.append(f"{icon}{temp}{pop_str}")
            
            results.append(f"📍{name}|{'|'.join(forecasts)}")
        return "\n".join(results)
    except Exception as e:
        print(f"Weather Error: {e}")
        return None

def post(text):
    if not text: return
    api_key = os.getenv("KAROTTER_API_KEY")
    try:
        # クイックスタート通りの初期化
        client = KarotterDevClient(api_key)
        # 投稿
        client.tweets.create(text)
        print("Post Success!")
    except Exception as e:
        print(f"KarotterPy Error: {e}")

if __name__ == "__main__":
    msg = get_weather()
    if msg:
        if len(msg) > 200:
            msg = msg[:197] + "..."
        post(msg)
