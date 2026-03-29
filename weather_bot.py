import requests
import os
from datetime import datetime, timedelta, timezone

OWM_API_KEY = os.getenv("OWM_API_KEY")
CITIES = {"Tokyo,jp": "東京", "Osaka,jp": "大阪", "Fukuoka,jp": "福岡"}

def get_weather_forecast_text():
    jst = timezone(timedelta(hours=9))
    now = datetime.now(jst)
    today_api_str = now.strftime('%Y-%m-%d')
    report = [f"【{now.strftime('%m/%d')} 今日の予報】"]
    target_times = ["00:00:00", "03:00:00", "06:00:00", "09:00:00", "12:00:00"]

    for en, jp in CITIES.items():
        url = f"https://api.openweathermap.org/data/2.5/forecast?q={en}&appid={OWM_API_KEY}&units=metric&lang=ja"
        data = requests.get(url).json()
        if "list" not in data: continue
        
        city_f = []
        for t in target_times:
            target = f"{today_api_str} {t}"
            f = next((item for item in data["list"] if target in item["dt_txt"]), None)
            if f:
                pop = int(f.get("pop", 0) * 100)
                icon = "☔" if pop >= 50 else ("☁" if pop >= 20 else "☀")
                city_f.append(f"{icon}{int(f['main']['temp'])}℃")
        report.append(f"\n📍{jp}\n {' | '.join(city_f)}")
    
    report.append("\n(左から9時/12時/15時/18時/21時)\n#天気予報")
    return "\n".join(report)