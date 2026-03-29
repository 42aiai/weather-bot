import requests
import os

# 環境変数
KAROTTER_ID = os.getenv("KAROTTER_ID")
KAROTTER_PW = os.getenv("KAROTTER_PW")

# 地方区分辞書（共通で使う）
REGIONS = {
    "東北": ["青森県", "岩手県", "宮城県", "秋田県", "山形県", "福島県"],
    "関東甲信": ["茨城県", "栃木県", "群馬県", "埼玉県", "千葉県", "東京都", "神奈川県", "山梨県", "長野県"],
    "北陸": ["新潟県", "富山県", "石川県", "福井県"],
    "東海": ["岐阜県", "静岡県", "愛知県", "三重県"],
    "近畿": ["滋賀県", "京都府", "大阪府", "兵庫県", "奈良県", "和歌山県"],
    "中国": ["鳥取県", "島根県", "岡山県", "広島県", "山口県"],
    "四国": ["徳島県", "香川県", "愛媛県", "高知県"],
    "九州北部": ["福岡県", "佐賀県", "長崎県", "熊本県", "大分県"],
    "九州南部": ["宮崎県", "鹿児島県"],
    "沖縄": ["沖縄県"]
}

def post_to_karotter(content):
    if not content: return
    session = requests.Session()
    # ログイン
    login_res = session.post("https://api.karotter.com/api/auth/login", 
                             json={"identifier": KAROTTER_ID, "password": KAROTTER_PW})
    if login_res.status_code != 200:
        print("ログイン失敗")
        return
    
    # CSRF取得して投稿
    csrf = next((v for k, v in session.cookies.get_dict().items() if "csrf" in k.lower()), None)
    res = session.post("https://api.karotter.com/api/posts", 
                       headers={"X-CSRF-Token": csrf}, json={"content": content[:200]})
    print(f"投稿完了: {res.status_code}")

def summarize_areas(areas):
    remaining = list(set(areas))
    summary = []
    for reg, prefs in REGIONS.items():
        hit = [p for p in prefs if p in remaining]
        if len(hit) >= 3:
            summary.append(f"{reg}の広範囲")
            for p in hit: remaining.remove(p)
    summary.extend(remaining)
    return "、".join(summary)