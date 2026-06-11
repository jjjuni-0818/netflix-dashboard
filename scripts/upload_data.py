"""
Netflix 데이터 → Supabase 업로드 스크립트
사용법: python scripts/upload_data.py
"""

import os, re, json, time
import urllib.request, urllib.error
from dotenv import load_dotenv

load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SERVICE_KEY  = os.getenv("SUPABASE_SERVICE_ROLE_KEY")

if not SUPABASE_URL or not SERVICE_KEY:
    raise SystemExit("❌ .env 파일에 SUPABASE_URL, SUPABASE_SERVICE_ROLE_KEY 필요")

# ── 1. HTML에서 데이터 추출 ─────────────────────────────────────
# 원본 데이터 소스: 하드코딩된 ALL_DATA가 있는 단일 파일 버전
# supabase-project와 같은 레벨의 Netflix 디렉토리에서 찾습니다
HTML_PATH = os.path.join(os.path.dirname(__file__), "..", "..", "netflix_dashboard.html")
if not os.path.exists(HTML_PATH):
    # 직접 경로 지정 (환경에 따라 수정)
    HTML_PATH = os.path.join(os.path.dirname(__file__), "..", "data", "netflix_dashboard.html")
with open(HTML_PATH, "r", encoding="utf-8") as f:
    content = f.read()

match = re.search(r"const ALL_DATA = (\[.*?\]);", content, re.DOTALL)
raw = json.loads(match.group(1))

records = [
    {
        "name":     r["Name"],
        "year":     r["Year"],
        "rating":   r["Rating"],
        "duration": r["Duration"],
        "category": r["CateAllory"],
    }
    for r in raw
]
print(f"✅ 추출 완료: {len(records)}건")

# ── 2. 기존 데이터 삭제 ──────────────────────────────────────────
def api(method, path, body=None):
    url = f"{SUPABASE_URL}/rest/v1/{path}"
    data = json.dumps(body).encode() if body else None
    req = urllib.request.Request(url, data=data, method=method)
    req.add_header("apikey", SERVICE_KEY)
    req.add_header("Authorization", f"Bearer {SERVICE_KEY}")
    req.add_header("Content-Type", "application/json")
    req.add_header("Prefer", "return=minimal")
    try:
        with urllib.request.urlopen(req) as res:
            return res.status
    except urllib.error.HTTPError as e:
        print(f"  HTTP {e.code}: {e.read().decode()}")
        return e.code

print("🗑  기존 데이터 삭제 중...")
api("DELETE", "netflix_titles?id=gte.0")

# ── 3. 배치 업로드 ───────────────────────────────────────────────
BATCH = 500
total = len(records)
for i in range(0, total, BATCH):
    batch = records[i : i + BATCH]
    status = api("POST", "netflix_titles", batch)
    print(f"  업로드 {min(i+BATCH, total)}/{total} (HTTP {status})")
    time.sleep(0.3)

print("🎉 업로드 완료!")
