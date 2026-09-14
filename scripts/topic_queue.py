#!/usr/bin/env python3
"""구글 시트('복센블로그 주제')를 매일 발행의 주제 큐로 쓴다.

외부 패키지 없이 동작한다 — 서비스계정 JWT를 표준 라이브러리 + cryptography 로 직접 서명하고
HTTP는 urllib 로 부른다(04.soomgo/cold_outreach/sheet-sync.py 와 같은 방식).

  python3 scripts/topic_queue.py next              # 다음 '대기' 주제 1건을 JSON 으로
  python3 scripts/topic_queue.py mark --slug <slug> [--url <url>]   # 발행됨 + 오늘 날짜 기록

종료 코드:
  0  정상
  2  설정이 없거나(키·시트ID) 큐가 비었음 → 호출 쪽에서 '알아서 주제 선정'으로 넘어갈 것
  1  실제 오류

준비(1회):
  1) Mac mini 의 ~/.config/voxen/gsheets-sa.json 을 이 기기 같은 경로로 복사 (chmod 600)
  2) '복센블로그 주제' 시트를 그 서비스계정 이메일(...iam.gserviceaccount.com)에 **편집자**로 공유
  3) ~/.config/voxen/blog-topics.env 에 시트 ID 저장:
       TOPICS_SHEET_ID=<시트 URL 의 /d/ 와 /edit 사이 문자열>
"""
import argparse
import base64
import json
import os
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from datetime import datetime, timedelta, timezone
from pathlib import Path

CFG_DIR = Path.home() / ".config/voxen"
SA_PATH = Path(os.environ.get("GSHEETS_SA", CFG_DIR / "gsheets-sa.json"))
ENV_PATH = CFG_DIR / "blog-topics.env"
SCOPE = "https://www.googleapis.com/auth/spreadsheets"
KST = timezone(timedelta(hours=9))
POSTS_DIR = Path(__file__).resolve().parent.parent / "site/posts"

# 시트 컬럼: A 번호 · B 주제 · C 카테고리 · D 대상 · E 발행여부 · F 발행일 · G 슬러그 · H URL
COL = {"주제": 1, "카테고리": 2, "대상": 3, "발행여부": 4, "발행일": 5, "슬러그": 6, "URL": 7}
DONE = "발행됨"


def load_env():
    env = {}
    if ENV_PATH.exists():
        for line in ENV_PATH.read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if line and not line.startswith("#") and "=" in line:
                k, v = line.split("=", 1)
                env[k.strip()] = v.strip().strip('"').strip("'")
    for k in ("TOPICS_SHEET_ID", "TOPICS_SHEET_TAB"):
        if os.environ.get(k):
            env[k] = os.environ[k]
    return env


def b64(data):
    return base64.urlsafe_b64encode(data).rstrip(b"=")


def access_token(sa):
    from cryptography.hazmat.primitives import hashes, serialization
    from cryptography.hazmat.primitives.asymmetric import padding

    now = int(time.time())
    header = {"alg": "RS256", "typ": "JWT"}
    claim = {"iss": sa["client_email"], "scope": SCOPE, "aud": sa["token_uri"],
             "iat": now, "exp": now + 3600}
    signing_input = b64(json.dumps(header).encode()) + b"." + b64(json.dumps(claim).encode())
    key = serialization.load_pem_private_key(sa["private_key"].encode(), password=None)
    signature = key.sign(signing_input, padding.PKCS1v15(), hashes.SHA256())
    assertion = (signing_input + b"." + b64(signature)).decode()
    body = urllib.parse.urlencode({
        "grant_type": "urn:ietf:params:oauth:grant-type:jwt-bearer", "assertion": assertion}).encode()
    req = urllib.request.Request(sa["token_uri"], data=body,
                                 headers={"Content-Type": "application/x-www-form-urlencoded"})
    with urllib.request.urlopen(req, timeout=30) as r:
        return json.load(r)["access_token"]


def api(token, path, method="GET", payload=None, params=""):
    url = f"https://sheets.googleapis.com/v4/spreadsheets/{path}{params}"
    data = json.dumps(payload).encode() if payload is not None else None
    req = urllib.request.Request(url, data=data, method=method,
                                 headers={"Authorization": f"Bearer {token}",
                                          "Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=60) as r:
        return json.load(r)


def connect():
    """(token, sheet_id, tab) 또는 설정이 없으면 None."""
    env = load_env()
    sheet_id = env.get("TOPICS_SHEET_ID")
    if not SA_PATH.exists() or not sheet_id:
        return None
    sa = json.loads(SA_PATH.read_text(encoding="utf-8"))
    token = access_token(sa)
    tab = env.get("TOPICS_SHEET_TAB")
    if not tab:  # 탭 이름을 안 줬으면 첫 번째 시트를 쓴다
        meta = api(token, sheet_id, params="?fields=sheets.properties.title")
        tab = meta["sheets"][0]["properties"]["title"]
    return token, sheet_id, tab


def read_rows(token, sheet_id, tab):
    rng = urllib.parse.quote(f"{tab}!A1:H1000")
    got = api(token, sheet_id, params=f"/values/{rng}")
    return got.get("values", [])


def cell(row, key):
    i = COL[key]
    return row[i].strip() if len(row) > i and row[i] else ""


def cmd_next(args):
    conn = connect()
    if conn is None:
        print(f"[topic_queue] SKIP: 설정 없음({SA_PATH} 또는 {ENV_PATH}의 TOPICS_SHEET_ID). "
              "주제를 직접 선정하세요.", file=sys.stderr)
        return 2
    token, sheet_id, tab = conn
    rows = read_rows(token, sheet_id, tab)

    for n, row in enumerate(rows[1:], start=2):  # 1행은 헤더
        topic, slug = cell(row, "주제"), cell(row, "슬러그")
        if not topic or cell(row, "발행여부") == DONE:
            continue
        if slug and (POSTS_DIR / slug).exists():
            continue  # 시트가 아직 '대기'여도 이미 글이 있으면 건너뛴다
        print(json.dumps({
            "row": n,
            "주제": topic,
            "카테고리": cell(row, "카테고리"),
            "대상": cell(row, "대상"),
            "슬러그": slug,
        }, ensure_ascii=False))
        return 0

    print("[topic_queue] SKIP: 큐에 남은 '대기' 주제가 없습니다. 주제를 직접 선정하세요.", file=sys.stderr)
    return 2


def cmd_mark(args):
    conn = connect()
    if conn is None:
        print("[topic_queue] SKIP: 설정 없음 — 시트 기록을 건너뜁니다.", file=sys.stderr)
        return 2
    token, sheet_id, tab = conn
    rows = read_rows(token, sheet_id, tab)

    for n, row in enumerate(rows[1:], start=2):
        if cell(row, "슬러그") != args.slug:
            continue
        today = datetime.now(KST).strftime("%Y-%m-%d")
        url = args.url or f"https://insights.voxen.io/posts/{args.slug}/"
        data = [
            {"range": f"{tab}!E{n}:F{n}", "values": [[DONE, today]]},
            {"range": f"{tab}!H{n}", "values": [[url]]},
        ]
        api(token, f"{sheet_id}/values:batchUpdate", method="POST",
            payload={"valueInputOption": "USER_ENTERED", "data": data})
        print(f"[topic_queue] OK: {n}행 '{cell(row, '주제')}' → {DONE} {today}")
        return 0

    print(f"[topic_queue] WARN: 시트에서 슬러그 '{args.slug}' 를 찾지 못했습니다.", file=sys.stderr)
    return 2


def main() -> int:
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest="cmd", required=True)
    sub.add_parser("next")
    m = sub.add_parser("mark")
    m.add_argument("--slug", required=True)
    m.add_argument("--url")
    args = ap.parse_args()

    try:
        return cmd_next(args) if args.cmd == "next" else cmd_mark(args)
    except urllib.error.HTTPError as e:
        print(f"[topic_queue] Sheets API {e.code}: {e.read().decode()[:300]}", file=sys.stderr)
        return 1
    except urllib.error.URLError as e:
        print(f"[topic_queue] 네트워크 오류: {e}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
