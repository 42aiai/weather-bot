import requests
import json
import os

AREA_MAP = {
    "北海道": ["北海道"],
    "東北": ["青森県", "岩手県", "宮城県", "秋田県", "山形県", "福島県"],
    "関東": ["茨城県", "栃木県", "群馬県", "埼玉県", "千葉県", "東京都", "神奈川県"],
    "中部": ["新潟県", "富山県", "石川県", "福井県", "山梨県", "長野県", "岐阜県", "静岡県", "愛知県"],
    "近畿": ["三重県", "滋賀県", "京都府", "大阪府", "兵庫県", "奈良県", "和歌山県"],
    "中国": ["鳥取県", "島根県", "岡山県", "広島県", "山口県"],
    "四国": ["徳島県", "香川県", "愛媛県", "高知県"],
    "九州": ["福岡県", "佐賀県", "長崎県", "熊本県", "大分県", "宮崎県", "鹿児島県", "沖縄県"]
}

def get_jma_alerts():
    url = "https://www.jma.go.jp/bosai/rasrf/data/rasrf.json"
    try:
        res = requests.get(url, timeout=10)
        res.raise_for_status()
        data = res.json()
        alerts = {}
        for layer in data.get("layers", []):
            name = layer.get("name")
            areas = layer.get("areas", [])
            if name and areas:
                alerts[name] = areas
        return alerts
    except Exception as e:
        print(f"Error fetching JMA data: {e}")
        return {}

def summarize_areas(area_list):
    result = []
    temp_list = list(area_list)
    for region, prefectures in AREA_MAP.items():
        if all(p in temp_list for p in prefectures):
            result.append(f"{region}の広範囲")
            for p in prefectures:
                temp_list.remove(p)
    result.extend(temp_list)
    return "、".join(result)

def build_alert_message(current, last, force_all=False):
    added_lines = []
    removed_lines = []

    for alert_type, areas in current.items():
        last_areas = last.get(alert_type, [])
        if force_all:
            if areas:
                summarized = summarize_areas(areas)
                icon = "🔴" if "特別警報" in alert_type else "🚨"
                added_lines.append(f"{icon}{alert_type}：{summarized}")
        else:
            new_areas = [a for a in areas if a not in last_areas]
            if new_areas:
                summarized = summarize_areas(new_areas)
                icon = "🔴" if "特別警報" in alert_type else "🚨"
                added_lines.append(f"{icon}{alert_type}（新規・拡大）：{summarized}")

    if not force_all:
        for alert_type, last_areas in last.items():
            current_areas = current.get(alert_type, [])
            removed = [a for a in last_areas if a not in current_areas]
            if removed:
                summarized = summarize_areas(removed)
                removed_lines.append(f"✅{alert_type}が解除されました：{summarized}")

    msg_parts = []
    if added_lines:
        msg_parts.append("\n".join(added_lines))
    if removed_lines:
        if msg_parts: msg_parts.append("\n" + "─" * 15 + "\n")
        msg_parts.append("✨【警報解除】\n" + "\n".join(removed_lines))

    return "\n".join(msg_parts) if msg_parts else None

def finalize_message(content, mode="monitor"):
    title = "🚨【気象警報：現在の状況】" if mode == "forecast" else "🚨【気象警報：更新】"
    return f"{title}\n\n{content}\n\n#気象情報 #防災"

def post_to_karotter(text):
    token = os.getenv("KAROTTER_TOKEN")
    if not token: return
    url = "https://api.karotter.com/post"
    params = {"token": token, "text": text}
    try:
        requests.get(url, params=params, timeout=10)
    except Exception as e:
        print(f"Failed to post: {e}")
