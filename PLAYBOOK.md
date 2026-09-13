# 매일 정오 자동 발행 플레이북

이 문서는 `scripts/run-daily.sh`가 headless Claude Code(`claude -p`)에게 넘기는 지침이다.
매일 이 순서대로 실행해서 글 1편을 작성·발행하고 Facebook에 포스팅한다. **사람 승인 단계 없음** —
끝까지 자동으로 완료할 것.

## 0. 준비

```
cd /Users/pass4u/VOXEN/auto_blog
git pull --ff-only origin main
```

## 1. 주제 선정

- `site/llms.txt`와 `ls site/posts`로 기존 32개+ 주제/슬러그를 확인하고 **겹치지 않는** 새 주제를 고른다.
- 반드시 아래 4개 카테고리 중 하나에 속해야 한다(기존 eyebrow 표기 참고, 조합 가능):
  - AI 자동화 — 예: `AI EASY GUIDE`, `AI OPERATIONS · RELIABILITY`, `AI · BUSINESS AUTOMATION`
  - 비즈니스 자동화 — 예: `BUSINESS AUTOMATION`, `LEAD AUTOMATION`
  - 데이터 운영 — 예: `DATA OPERATIONS · AI BUSINESS`
  - 시장 데이터 — 예: `MARKET DATA · AI BUSINESS`
- 최근 발행된 카테고리와 겹치지 않도록 균형을 맞춘다(같은 카테고리 연속 3일 이상 금지).
- 슬러그는 영문 kebab-case, 짧고 주제를 설명하는 형태(`site/posts/<slug>/`).

## 2. 글쓰기 규칙 (반드시 지킬 것)

- 한국어, B2B 실무 톤. 기존 글들의 문체(질문형 훅 → 문제 제시 → 구조적 설명 → 표/체크리스트 → FAQ → Voxen 소개 → CTA)를 따른다.
- **공개적으로 검증 가능하거나 일반적으로 통용되는 사실만 사용한다.** 없는 통계·설문·고객 사례·수치·후기를 지어내지 않는다.
- 실명 고객사, 특정 개인, 의료/법률/금융 규제 관련 단정적 조언 금지.
- 특정 경쟁 제품을 비방하지 않는다. 특정 타사 제품명을 실명 비교하지 않는다.
- `soomgo.voxen.io`, `hompy.voxen.io` 등 다른 내부 서비스 도메인을 언급하지 않는다(이 블로그는 인바운드 마케팅용).
- 분량: 기존 글과 비슷하게(본문 h2 섹션 5~7개 + FAQ 2~3문항).

## 3. 글 파일 작성 — `site/posts/<slug>/index.html`

기존 글(`site/posts/automation-vs-ai-where-to-use-ai/index.html` 등)을 정확히 참고해 아래 구조를 그대로 따른다.
**HTML은 줄바꿈 없이 한 줄로** 작성한다(기존 파일들과 동일한 포맷).

```html
<!doctype html><html lang="ko"><head>
<meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>{{제목}} | Voxen Insights</title>
<meta name="description" content="{{메타 설명, 80~120자}}">
<meta name="robots" content="index,follow,max-image-preview:large,max-snippet:-1">
<link rel="canonical" href="https://insights.voxen.io/posts/{{slug}}/">
<link rel="stylesheet" href="/assets/style.css">
<meta property="og:type" content="article">
<meta property="og:title" content="{{제목}}">
<meta property="og:description" content="{{OG 설명}}">
<meta property="og:url" content="https://insights.voxen.io/posts/{{slug}}/">
<meta property="og:image" content="https://insights.voxen.io/assets/{{slug}}-og.png">
<meta property="og:image:width" content="1200"><meta property="og:image:height" content="630">
<meta property="og:image:alt" content="{{일러스트 대체텍스트}}">
<meta name="twitter:card" content="summary_large_image">
<meta name="twitter:image" content="https://insights.voxen.io/assets/{{slug}}-og.png">
<script type="application/ld+json">{"@context":"https://schema.org","@type":"Article","headline":"{{제목}}","description":"{{설명}}","datePublished":"{{YYYY-MM-DD}}T12:00:00+09:00","inLanguage":"ko-KR","image":"https://insights.voxen.io/assets/{{slug}}-og.png","author":{"@type":"Organization","name":"Voxen"},"publisher":{"@type":"Organization","name":"Voxen","url":"https://voxen.io"},"mainEntityOfPage":"https://insights.voxen.io/posts/{{slug}}/"}</script>
<script type="application/ld+json">{"@context":"https://schema.org","@type":"FAQPage","mainEntity":[{"@type":"Question","name":"{{질문1}}","acceptedAnswer":{"@type":"Answer","text":"{{답1}}"}},{"@type":"Question","name":"{{질문2}}","acceptedAnswer":{"@type":"Answer","text":"{{답2}}"}}]}</script>
</head><body><header><div class="wrap nav"><a class="brand" href="/">VOXEN <span>INSIGHTS</span></a></div></header>
<main class="wrap article">
<p class="eyebrow">{{EYEBROW}} · {{YYYY.MM.DD}}</p>
<h1>{{제목(간결한 버전)}}</h1>
<p class="lead">{{도입부, strong 태그로 핵심 문장 강조}}</p>
<figure class="visual"><img src="/assets/{{slug}}-og.svg" alt="{{일러스트 대체텍스트}}" loading="eager" style="width:100%;height:auto;border-radius:20px;display:block"><figcaption>{{캡션}}</figcaption></figure>
<h2>...</h2><p>...</p>
<!-- h2 섹션 5~7개, 필요시 <table>, <div class="callout">, <ol>/<ul> 사용 -->
<h2>FAQ</h2><h3>{{질문1}}</h3><p>{{답1}}</p><h3>{{질문2}}</h3><p>{{답2}}</p>
<h2>Voxen은 이렇게 접근합니다</h2><p>Voxen은 AI를 억지로 모든 단계에 넣기보다 현재 업무와 데이터를 먼저 살펴보고 가장 단순하고 안정적인 자동화 구조를 찾습니다. 데이터 수집·엔지니어링, AI 판단, API·대시보드, 맞춤 시스템 구축을 실제 비즈니스 프로세스에 맞게 연결합니다.</p>
<h2>이 글도 읽어보세요</h2><ul><li><a href="/posts/{{관련글1-slug}}/"><strong>{{관련글1 제목}}</strong></a> — {{한줄설명}}</li><li><a href="/posts/{{관련글2-slug}}/"><strong>{{관련글2 제목}}</strong></a> — {{한줄설명}}</li></ul>
<div class="cta"><strong>데이터와 AI를 실제 업무 시스템으로 연결하고 싶다면</strong><p>Voxen Cloud에서 데이터 수집·자동화·맞춤 시스템 구축 방향을 살펴보세요.</p><a href="https://cloud.voxen.io">cloud.voxen.io →</a></div>
<div class="contact-cta"><p>{{상담 유도 문구}}</p><a class="contact-button" href="mailto:hello@voxen.io">이메일로 상담하기</a></div>
</main><footer><div class="wrap">© 2026 Voxen</div></footer></body></html>
```

관련 글 링크는 실제 존재하는 슬러그로 2~3개 연결한다(`ls site/posts` 확인).

## 4. OG 일러스트 — `site/assets/{{slug}}-og.svg`

기존 하우스 스타일을 그대로 따른다(예: `site/assets/automation-vs-ai-where-to-use-ai-og.svg` 참고):

- `viewBox="0 0 1200 630"`, 배경 `<rect>` fill `#f8fafc`
- 선화(line art): stroke `#334155`, stroke-width `8`, round cap/join, 흰색(`#fff`) 채움 도형(둥근 사각형·원)으로 프로세스/흐름 표현
- 포인트 색상 `#c7d2fe`로 작은 원(강조점) 2~3개
- 주제에 맞게 박스 2~4개를 화살표/선으로 연결하는 미니멀 플로우 다이어그램으로 구성. 텍스트는 넣지 않는다.

## 5. 홈페이지 — `site/index.html`

`<h2>최신 인사이트</h2>` 바로 뒤에 새 `<article class="card">` 1개를 **맨 앞에 삽입**한다:

```html
<article class="card"><p class="eyebrow">{{EYEBROW}} · {{YYYY.MM.DD}}</p><h3><a href="/posts/{{slug}}/">{{제목}}</a></h3><p>{{한줄설명}}</p><a class="more" href="/posts/{{slug}}/">읽기 →</a></article>
```

그 다음 카드가 **10개를 초과하면 가장 오래된(마지막) 카드를 제거**해서 항상 10개를 유지한다.
HTML은 한 줄 포맷 그대로 유지(줄바꿈 넣지 않음).

## 6. sitemap.xml

- 첫 줄(루트 `https://insights.voxen.io/`)의 `lastmod`를 오늘 날짜로 갱신.
- 그 바로 뒤에 새 URL을 삽입:
  `<url><loc>https://insights.voxen.io/posts/{{slug}}/</loc><lastmod>{{YYYY-MM-DD}}</lastmod><changefreq>weekly</changefreq><priority>0.9</priority></url>`
- 기존 글 URL은 **삭제하지 않는다**(sitemap은 전체 아카이브 보관, 개수 제한 없음).

## 7. feed.xml (RSS)

`<language>ko-KR</language>` 바로 뒤, 기존 첫 `<item>` 앞에 새 `<item>`을 삽입:

```html
<item><title>{{제목}}</title><link>https://insights.voxen.io/posts/{{slug}}/</link><guid>https://insights.voxen.io/posts/{{slug}}/</guid><pubDate>{{RFC822, 오늘 03:00 GMT = 한국시간 정오}}</pubDate><description>{{한줄설명}}</description></item>
```

`<item>`이 **10개를 초과하면 가장 오래된(마지막) item을 제거**해서 항상 10개를 유지.

## 8. llms.txt

`## Latest Articles` 섹션 맨 위에 새 줄 삽입:

```
- [{{제목}}]({{URL}}): {{영문 한줄 요약}}
```

이 섹션 항목이 **10개를 초과하면 가장 오래된(마지막) 줄을 제거**해서 항상 10개를 유지.

## 9. 커밋 & 푸시

```
git add -A
git commit -m "Publish {{짧은 제목}}

Co-Authored-By: Claude Sonnet 5 <noreply@anthropic.com>"
git push origin main
```

한 커밋으로 처리한다(과거처럼 파일별로 5개 커밋 나누지 않음 — 동일 결과, 더 단순).
push하면 GitHub Actions(`pages.yml`)가 자동으로 `insights.voxen.io`에 배포한다.

## 10. Facebook 포스팅

**`--message`의 첫 줄이 가장 중요하다.** Facebook 피드에서는 게시글이 길면 자동으로 접히고 첫 줄(또는 첫 1~2문장)만
보인 채 "더 보기"로 잘리기 때문에, 첫 줄만 읽고도 클릭하고 싶게 만드는 후킹 문장이어야 한다.
- 첫 줄에 제목을 그대로 반복하지 말 것 — 질문형·문제 제기·의외성 있는 한 문장으로 시작한다.
  (예: "매출 보고서 숫자랑 대시보드 숫자가 왜 다르죠?" 같은 실제 상황을 던지는 문장)
- 첫 줄만으로 "이거 우리 얘기인데" 싶게 만들고, 그다음 줄부터 핵심 요약과 해시태그를 붙인다.
- 제목이나 요약을 그대로 복붙하지 않는다 — 접힌 상태에서 보이는 한 줄은 별도로 다시 쓴다.

```
python3 scripts/post_to_facebook.py \
  --title "{{제목}}" \
  --message "{{Facebook 게시글 본문 — 후킹 문장 1~2줄 + 핵심 요약, 해시태그 2~3개}}" \
  --link "https://insights.voxen.io/posts/{{slug}}/"
```

`~/.config/voxen/facebook.env`에 `FB_PAGE_ID`/`FB_PAGE_ACCESS_TOKEN`이 없으면 스크립트가 에러 메시지를 내고 종료한다 —
이 경우 **글 발행은 그대로 유지**하고 Facebook 포스팅만 건너뛴 뒤 로그에 사유를 남긴다(재시도하지 않음, 다음날 처리).

## 11. 로그

`logs/YYYY-MM-DD.log`에 다음을 한 줄씩 기록:
- 선정한 주제/슬러그
- 발행 URL
- git push 결과(커밋 해시)
- Facebook 포스팅 결과(성공/실패 사유)

## 실패 시 처리

- 중간에 실패하면(예: git push 충돌) 절대 `--force` push하지 않는다. `git pull --rebase`로 한 번 재시도하고,
  그래도 실패하면 변경사항을 그대로 두고 로그에 실패 사유를 남긴 뒤 종료한다(다음날 사람이 확인).
- 이미 오늘 날짜로 발행된 글이 있으면(로그 확인) 중복 발행하지 않고 종료한다.
