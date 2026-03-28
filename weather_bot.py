import requests
from datetime import datetime

import os  # OSの機能を使うためのライブラリ（標準で入っています）

# --- 設定エリア ---
# 直接書く代わりに、環境変数（os.getenv）から読み出す
OWM_API_KEY = os.getenv("OWM_API_KEY")
KAROTTER_ID = os.getenv("KAROTTER_ID")
KAROTTER_PW = os.getenv("KAROTTER_PW")
# 投稿したい都市のリスト（表示名もセット）
CITIES = {
    "Tokyo,jp": "東京",
    "Osaka,jp": "大阪",
    "Fukuoka,jp": "福岡"
}

def get_weather_text():
    today_str = datetime.now().strftime('%m/%d')
    report_lines = [f"【{today_str} 今日の予報】"]
    
    target_cities = {
        "Tokyo,jp": "東京",
        "Osaka,jp": "大阪",
        "Fukuoka,jp": "福岡"
    }

    # 抽出したい時間帯
    target_times = ["09:00:00", "12:00:00", "15:00:00", "18:00:00", "21:00:00"]

    for en_name, jp_name in target_cities.items():
        url = f"https://api.openweathermap.org/data/2.5/forecast?q={en_name}&appid={OWM_API_KEY}&units=metric&lang=ja"
        res = requests.get(url)
        data = res.json()
        
        city_forecasts = []
        for t in target_times:
            # 各時間帯のデータを検索
            f = next((item for item in data["list"] if t in item["dt_txt"]), None)
            if f:
                # 天気アイコンの簡易判定（3時間おきなので短く）
                main_w = f["weather"][0]["main"]
                pop = int(f.get("pop", 0) * 100)
                
                if pop >= 50: icon = "☔"
                elif pop >= 20: icon = "☁"
                else: icon = "☀"
                
                # 「アイコン+気温」のセットを作る
                temp = int(f["main"]["temp"])
                city_forecasts.append(f"{icon}{temp}℃")
        
        # 都市名と、時間を並べた予報を合体
        # 9時 | 12時 | 15時 | 18時 | 21時
        forecast_row = " | ".join(city_forecasts)
        report_lines.append(f"📍{jp_name}\n {forecast_row}")

    report_lines.append("\n(左から9時/12時/15時/18時/21時)\n#天気予報 #今日の天気")
    return "\n".join(report_lines)

def post_to_karotter(content):
    """カロッターにログインして投稿する"""
    session = requests.Session()
    
    # ① ログイン
    login_url = "https://api.karotter.com/api/auth/login"
    login_data = {"identifier": KAROTTER_ID, "password": KAROTTER_PW}
    
    login_res = session.post(login_url, json=login_data)
    if login_res.status_code != 200:
        print("ログイン失敗:", login_res.status_code)
        return

    # ② CSRFトークンの取得
    csrf_token = None
    for k, v in session.cookies.get_dict().items():
        if "csrf" in k.lower():
            csrf_token = v

    # ③ 投稿
    post_url = "https://api.karotter.com/api/posts"
    headers = {
        "Content-Type": "application/json",
        "X-CSRF-Token": csrf_token
    }
    post_data = {"content": content}
    
    res = session.post(post_url, headers=headers, json=post_data)
    print(f"投稿完了！ステータス: {res.status_code}")

# --- 実行 ---
if __name__ == "__main__":
    weather_message = get_weather_text()
    print("--- 投稿内容 ---")
    print(weather_message)
    
    # 本番投稿
    post_to_karotter(weather_message)