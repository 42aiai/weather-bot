import sys
import json
import os
from datetime import datetime
import requests

# 自作モジュールのインポート
import weather_bot
from tools import get_jma_alerts, build_alert_message, finalize_message, post_to_karotter

# 履歴ファイルの保存先
HISTORY_FILE = "last_alerts.json"

def load_history():
    if os.path.exists(HISTORY_FILE):
        try:
            with open(HISTORY_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception as e:
            print(f"Error loading history: {e}")
            return {}
    return {}

def save_history(data):
    try:
        with open(HISTORY_FILE, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=4)
    except Exception as e:
        print(f"Error saving history: {e}")

if __name__ == "__main__":
    mode = sys.argv[1] if len(sys.argv) > 1 else "monitor"
    
    current_alerts = get_jma_alerts()
    last_alerts = load_history()

    if mode == "forecast":
        print("Running: Morning Forecast Mode")
        # ① 天気予報の投稿
        forecast_text = weather_bot.get_weather_forecast_text()
        post_to_karotter(forecast_text)
        
        # ② 警報の投稿（全出しモード）
        alert_msg = build_alert_message(current_alerts, last_alerts, force_all=True)
        if alert_msg:
            post_to_karotter(finalize_message(alert_msg, mode=mode))
        else:
            no_alert_msg = "現在、全国の自治体に発表されている気象警報はありません。"
            post_to_karotter(finalize_message(no_alert_msg, mode=mode))
            
    else:
        print("Running: Alert Monitor Mode")
        # 変化（差分）がある時だけ投稿
        alert_msg = build_alert_message(current_alerts, last_alerts, force_all=False)
        if alert_msg:
            post_to_karotter(finalize_message(alert_msg, mode=mode))
        else:
            print("No changes in alerts. Skipping post.")

    save_history(current_alerts)
