#!/usr/bin/env python3
"""새로 발행된 글을 Voxen Facebook 페이지에 링크 포스팅한다.

자격증명은 저장소 밖 ~/.config/voxen/facebook.env 에서 읽는다(git에 없음):
    FB_PAGE_ID=...
    FB_PAGE_ACCESS_TOKEN=...

사용:
    python3 scripts/post_to_facebook.py --title "..." --message "..." --link "https://insights.voxen.io/posts/<slug>/"
"""
import argparse
import os
import sys
import urllib.request
import urllib.parse
import urllib.error

ENV_PATH = os.path.expanduser("~/.config/voxen/facebook.env")
GRAPH_VERSION = "v21.0"


def load_env(path: str) -> dict:
    env = {}
    if not os.path.isfile(path):
        return env
    with open(path, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            key, value = line.split("=", 1)
            env[key.strip()] = value.strip().strip('"').strip("'")
    return env


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--title", required=True)
    parser.add_argument("--message", required=True)
    parser.add_argument("--link", required=True)
    args = parser.parse_args()

    env = load_env(ENV_PATH)
    page_id = env.get("FB_PAGE_ID") or os.environ.get("FB_PAGE_ID")
    token = env.get("FB_PAGE_ACCESS_TOKEN") or os.environ.get("FB_PAGE_ACCESS_TOKEN")

    if not page_id or not token:
        print(
            f"[post_to_facebook] SKIP: {ENV_PATH}에 FB_PAGE_ID/FB_PAGE_ACCESS_TOKEN이 없습니다. "
            "발행은 완료되었으나 Facebook 포스팅은 건너뜁니다.",
            file=sys.stderr,
        )
        return 2  # 발행 자체는 성공이므로 run-daily.sh는 이 코드를 치명적 실패로 취급하지 않는다

    url = f"https://graph.facebook.com/{GRAPH_VERSION}/{page_id}/feed"
    payload = urllib.parse.urlencode(
        {
            "message": args.message,
            "link": args.link,
            "access_token": token,
        }
    ).encode("utf-8")

    req = urllib.request.Request(url, data=payload, method="POST")
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            body = resp.read().decode("utf-8")
            print(f"[post_to_facebook] OK: {body}")
            return 0
    except urllib.error.HTTPError as e:
        body = e.read().decode("utf-8", errors="replace")
        print(f"[post_to_facebook] FAILED ({e.code}): {body}", file=sys.stderr)
        return 1
    except urllib.error.URLError as e:
        print(f"[post_to_facebook] FAILED (network): {e}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
