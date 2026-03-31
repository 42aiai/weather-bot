import os
import requests
from datetime import datetime, timedelta, timezone
from KarotterPy import Karotter

def get_weather():
    api_key = os.getenv("OWM_API_KEY")
    cities = {"東京": "Tokyo", "大阪": "Osaka", "福岡": "Fukuoka"}
    icons = {"Clear": "☀️", "Clouds": "☁️", "Rain": "☔", "Snow": "❄️", "Drizzle": "🌦️", "Thunderstorm": "⚡"}
    
    # 日本時間の現在時刻を取得
    jst = timezone(timedelta(hours=9))
    now = datetime.now(jst)
    date_str = now.strftime("%m/%d")
    week_days = ["月", "火", "水", "木", "金", "土", "日"]
    w_day = week_days[now.weekday()]
    
    target_hours = [9, 12, 15, 18, 21]
    # 案3：ヘッダー形式
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
                    
                    # 20%以上なら表示、それ以外は非表示（半角スペース+数値%）
                    pop_str = f" {pop}%" if pop >= 20 else ""
                    forecasts.append(f"{icon}{temp}{pop_str}")
            
            # 案3：📍都市名|データ1|データ2... の形式で連結
            results.append(f"📍{name}|{'|'.join(forecasts)}")
            
        return "\n".join(results)
        
    except Exception as e:
        print(f"Weather Error: {e}")
        return None

def post(text):
    if not text:
        return
    
    # 万が一200文字を超えた場合の切り捨て処理
    if len(text) > 200:
        print(f"Warning: Text too long ({len(text)} chars). Truncating.")
        text = text[:197] + "..."
        
    user_id = os.getenv("KAROTTER_ID")
    user_pw = os.getenv("KAROTTER_PW")
    
    try:
        karotter = Karotter(user_id, user_pw)
        res = karotter.post(text)
        print(f"Post Success: {res}")
    except Exception as e:
        print(f"KarotterPy Error: {e}")

if __name__ == "__main__":
    msg = get_weather()
    if msg:
        print(f"--- Sending Message (Length: {len(msg)}) ---\n{msg}")
        post(msg)
