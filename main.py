import os
import json
import requests
from datetime import datetime, timedelta, timezone
# tools.py から機能をインポート
from tools import post_to_karotter, summarize_areas

HISTORY_FILE = "last_alerts.json"

def get_jma_alerts():
    url = "https://www.jma.go.jp/bosai/warning/data/warning/confirm.json"
    res = requests.get(url)
    if res.status_code != 200: return {}
    data = res.json()
    current = {}
    for item in data:
        area_name = item.get("areaName")
        for status in item.get("statusList", []):
            kind_name = status.get("name")
            if "警報" in kind_name:
                if kind_name not in current: current[kind_name] = []
                if area_name not in current[kind_name]: current[kind_name].append(area_name)
    return current

def build_alert_message(current, last, force_all=False):
    added = [k for k in current if force_all or (k not in last or set(current[k]) != set(last.get(k, [])))]
    removed = [] if force_all else [k for k in last if k not in current]
    if not added and not removed: return None
    
    jst = timezone(timedelta(hours=9))
    time_str = datetime.now(jst).strftime('%m/%d %H:%M')
    lines = ["🚨【気象警報：現在の状況】" if force_all else "🚨【気象警報：更新】"]
    
    for k in added:
        icon = "🔴" if "特別警報" in k else "🚨"
        lines.append(f"{icon}{k}：\n {summarize_areas(current[k])}")
        lines.append("‼️最大級の警戒を。命を守る行動を最優先に。" if "特別警報" in k else "└ 厳重に警戒してください。")
    for k in removed:
        lines.append(f"✅{k}が解除されました")
    lines.append(f"\n({time_str} 発表)\n#気象警報")
    return "\n".join(lines)

# --- 実行部分 ---
if __name__ == "__main__":
    jst = timezone(timedelta(hours=9))
    now = datetime.now(jst)
    
    curr = get_jma_alerts()
    last = {}
    if os.path.exists(HISTORY_FILE):
        with open(HISTORY_FILE, "r") as f: last = json.load(f)

    # 朝7時の予報（別ファイルの weather_bot.py から取得する想定）
    if now.hour == 7 and now.minute < 15:
        import weather_bot # ここでインポート
        post_to_karotter(weather_bot.get_weather_forecast_text())
        msg = build_alert_message(curr, last, force_all=True)
        post_to_karotter(msg)
    else:
        # 15分おきの監視
        msg = build_alert_message(curr, last)
        post_to_karotter(msg)

    with open(HISTORY_FILE, "w") as f: json.dump(curr, f)