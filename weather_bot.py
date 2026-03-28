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

from datetime import datetime, timedelta, timezone

def get_weather_text():
    # --- 日本時間 (JST) の設定 ---
    # GitHubのサーバー(UTC)でも日本時間で計算するようにします
    jst = timezone(timedelta(hours=9))
    now_jst = datetime.now(jst)
    
    # API検索用の日付 (例: "2026-03-29")
    today_api_str = now_jst.strftime('%Y-%m-%d')
    # 投稿のタイトル用 (例: "03/29")
    today_display = now_jst.strftime('%m/%d')

    report_lines = [f"【{today_display} 今日の予報】"]
    
    # 抽出したい時間（日本時間の 9, 12, 15, 18, 21時）
    # OpenWeatherMap(UTC)では以下の時間帯に対応します
    target_times = ["00:00:00", "03:00:00", "06:00:00", "09:00:00", "12:00:00"]

    for en_name, jp_name in CITIES.items():
        url = f"https://api.openweathermap.org/data/2.5/forecast?q={en_name}&appid={OWM_API_KEY}&units=metric&lang=ja"
        res = requests.get(url)
        data = res.json()
        
        # 万が一データが取れなかった時のための安全策
        if "list" not in data:
            continue

        city_forecasts = []
        for t in target_times:
            # 「日本時間の今日の日付」かつ「指定の時間」のデータを検索
            target_str = f"{today_api_str} {t}"
            f = next((item for item in data["list"] if target_str in item["dt_txt"]), None)
            
            if f:
                # 降水確率(pop)でアイコンを決定
                pop = int(f.get("pop", 0) * 100)
                if pop >= 50: icon = "☔"
                elif pop >= 20: icon = "☁"
                else: icon = "☀"
                
                # 気温を整数にして追加
                temp = int(f["main"]["temp"])
                city_forecasts.append(f"{icon}{temp}℃")
        
        # 都市名ごとに改行を入れて見やすく整形
        forecast_row = " | ".join(city_forecasts)
        report_lines.append(f"\n📍{jp_name}\n {forecast_row}")

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
    post_to_karotter(weather_message+"　（これはテスト投稿です）")
