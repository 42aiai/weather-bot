import os
import requests

def get_weather():
    api_key = os.getenv("OPENWEATHER_API_KEY")
    cities = {"東京": "Tokyo", "大阪": "Osaka", "福岡": "Fukuoka"}
    icons = {"Clear": "☀️晴れ", "Clouds": "☁️曇り", "Rain": "☔雨", "Snow": "❄️雪"}
    
    results = []
    try:
        for name, city_en in cities.items():
            url = f"https://api.openweathermap.org/data/2.5/weather?q={city_en},jp&appid={api_key}&units=metric&lang=ja"
            res = requests.get(url).json()
            w = icons.get(res["weather"][0]["main"], "☁️曇り")
            t = res["main"]["temp"]
            results.append(f"{name}: {w} ({t:.1f}℃)")
        return "☀️【今日の天気】\n\n" + "\n".join(results)
    except:
        return "天気データの取得に失敗しました。"

def post(text):
    token = os.getenv("KAROTTER_TOKEN")
    requests.get(f"https://api.karotter.com/post?token={token}&text={requests.utils.quote(text)}")

if __name__ == "__main__":
    msg = get_weather()
    post(msg)
