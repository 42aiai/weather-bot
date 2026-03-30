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
        with open(HISTORY_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}

def save_history(data):
    with open(HISTORY_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

if __name__ == "__main__":
    # 1. 実行モードの取得 (引数がなければ 'monitor' モード)
    mode = sys.argv[1] if len(sys.argv) > 1 else "monitor"
    
    # 2. 最新の警報データを取得
    current_alerts = get_jma_alerts()
    last_alerts = load_history()

    if mode == "forecast":
        # --- 【朝の定期便モード】 ---
        print("Running: Morning Forecast Mode")
        
        # 天気予報の作成と投稿
        forecast_text = weather_bot.get_weather_forecast_text()
        post_to_karotter(forecast_text)
        
        # 現在の全警報を「強制全出し(force_all=True)」で作成
        alert_msg = build_alert_message(current_alerts, last_alerts, force_all=True)
        if alert_msg:
            post_to_karotter(finalize_message(alert_msg))
            
    else:
        # --- 【15分おき監視モード】 ---
        print("Running: Alert Monitor Mode")
        
        # 変化（発令・解除）がある時だけメッセージを作成
        alert_msg = build_alert_message(current_alerts, last_alerts)
        if alert_msg:
            post_to_karotter(finalize_message(alert_msg))
        else:
            print("No changes in alerts. Skipping post.")

    # 3. 今回の状態を次回の比較用に保存
    save_history(current_alerts)
