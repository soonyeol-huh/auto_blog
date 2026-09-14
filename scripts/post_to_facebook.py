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
import time
import urllib.request
import urllib.parse
import urllib.error

ENV_PATH = os.path.expanduser("~/.config/voxen/facebook.env")
GRAPH_VERSION = "v21.0"
DEPLOY_TIMEOUT = 300  # GitHub Pages 배포 대기 최대 5분
POLL_INTERVAL = 10


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


def wait_until_live(url: str, timeout: int = DEPLOY_TIMEOUT) -> bool:
    """글이 실제로 배포될 때까지 기다린다.

    push 직후 바로 포스팅하면 GitHub Pages 배포(보통 1~3분)가 끝나기 전이라
    Facebook 크롤러가 404를 받고 **그 404를 캐시**한다. 페이지가 나중에 살아나도
    미리보기는 "Page not found"로 굳는다. 2026-09-14에 실제로 겪은 문제다.
    """
    deadline = time.time() + timeout
    while time.time() < deadline:
        try:
            req = urllib.request.Request(url, method="HEAD")
            with urllib.request.urlopen(req, timeout=10) as resp:
                if resp.status == 200:
                    return True
        except (urllib.error.HTTPError, urllib.error.URLError, TimeoutError):
            pass
        time.sleep(POLL_INTERVAL)
    return False


def refresh_og_cache(url: str, token: str) -> None:
    """Facebook이 링크를 새로 읽게 한다(공유 디버거의 API 판). 실패해도 발송은 계속."""
    payload = urllib.parse.urlencode({"id": url, "scrape": "true", "access_token": token}).encode()
    try:
        with urllib.request.urlopen(
            urllib.request.Request(f"https://graph.facebook.com/{GRAPH_VERSION}/", data=payload), timeout=30
        ):
            pass
    except (urllib.error.HTTPError, urllib.error.URLError, TimeoutError) as e:
        print(f"[post_to_facebook] WARN: OG 캐시 갱신 실패({e}) — 그대로 진행합니다.", file=sys.stderr)


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

    if not wait_until_live(args.link):
        print(
            f"[post_to_facebook] SKIP: {args.link} 가 {DEPLOY_TIMEOUT}초 안에 배포되지 않았습니다. "
            "지금 올리면 Facebook이 404를 캐시하므로 포스팅하지 않습니다(글 발행은 유지).",
            file=sys.stderr,
        )
        return 2

    # 배포 확인 후 한 번 읽히게 해서, 포스팅 시점에 Facebook이 올바른 OG를 갖고 있게 한다
    refresh_og_cache(args.link, token)

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
