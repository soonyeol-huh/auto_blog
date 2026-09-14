#!/usr/bin/env python3
"""쇼츠 슬라이드(1080x1920) HTML 생성. 사진 배경 or 브랜드 그라디언트 배경, 세이프존 고려."""

BASE_CSS = """
*{box-sizing:border-box;margin:0;padding:0}
html,body{width:1080px;height:1920px;overflow:hidden;font-family:'Apple SD Gothic Neo','Pretendard',sans-serif}
.frame{position:relative;width:1080px;height:1920px;background:#0f172a}
.bg{position:absolute;inset:0;background-size:cover;background-position:center}
.scrim{position:absolute;inset:0;background:linear-gradient(180deg,rgba(15,23,42,.15) 0%,rgba(15,23,42,.15) 40%,rgba(15,23,42,.92) 68%,rgba(15,23,42,.97) 100%)}
.brandbg{position:absolute;inset:0;background:linear-gradient(145deg,#0f172a,#1e293b)}
.wordmark{position:absolute;top:96px;left:90px;color:#e2e8f0;font-weight:900;font-size:34px;letter-spacing:-.02em;opacity:.9}
.wordmark span{font-weight:500;color:#94a3b8}
.textbox{position:absolute;left:90px;right:90px;top:1050px;bottom:420px;display:flex;align-items:flex-end}
.textbox.center{top:0;bottom:0;align-items:center;justify-content:center;text-align:center}
.textbox p{color:#fff;font-weight:800;font-size:64px;line-height:1.32;letter-spacing:-.03em}
.textbox .accent{color:#a5b4fc}
.tag{position:absolute;left:90px;top:1050px;color:#a5b4fc;font-weight:800;font-size:28px;letter-spacing:.08em}
"""

def render(bg_image=None, tag=None, html_body="", center=False):
    bg_html = f'<div class="bg" style="background-image:url(\'{bg_image}\')"></div><div class="scrim"></div>' if bg_image else '<div class="brandbg"></div>'
    tag_html = f'<div class="tag">{tag}</div>' if tag and not center else ""
    box_class = "textbox center" if center else "textbox"
    return f"""<!doctype html><html><head><meta charset="utf-8"><style>{BASE_CSS}</style></head>
<body><div class="frame">{bg_html}<div class="wordmark">VOXEN <span>INSIGHTS</span></div>{tag_html}<div class="{box_class}"><p>{html_body}</p></div></div></body></html>"""

SCENES = [
    dict(name="scene1", bg="https://images.unsplash.com/photo-1635548166842-bf67bacbefaa?auto=format&fit=crop&w=1080&h=1920&q=80",
         tag="문제", html='"예약 확인 전화드렸습니다"<br>오늘도 몇 번 하셨나요?'),
    dict(name="scene2", bg="https://images.unsplash.com/photo-1736613215617-5814eff6aae4?auto=format&fit=crop&w=1080&h=1920&q=80",
         tag="문제", html='전화·이메일 예약, 확인이 늦어지면<br><span class="accent">이중예약·노쇼</span>로 이어집니다'),
    dict(name="scene3", bg=None, center=True,
         html='AI가 문의 속<br><span class="accent">날짜·인원·요청사항</span>을<br>자동으로 정리합니다'),
    dict(name="scene4", bg="https://images.unsplash.com/photo-1642359085898-d9fde39507c9?auto=format&fit=crop&w=1080&h=1920&q=80",
         tag="해결", html='캘린더 확인부터<br>확정 알림, 노쇼 리마인드까지<br><span class="accent">자동으로 연결</span>'),
    dict(name="scene5", bg=None, center=True,
         html='<span class="accent">Voxen</span>이<br>예약 접수부터 확정까지<br>하나로 연결해드립니다'),
    dict(name="scene6", bg=None, center=True,
         html='insights.voxen.io<br><span class="accent">에서 자세히 확인하세요</span>'),
]

if __name__ == "__main__":
    for s in SCENES:
        html = render(bg_image=s.get("bg"), tag=s.get("tag"), html_body=s["html"], center=s.get("center", False))
        with open(f"{s['name']}.html", "w", encoding="utf-8") as f:
            f.write(html)
    print(f"wrote {len(SCENES)} slide html files")
