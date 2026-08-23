# auto_blog

자동 블로그 운영을 위한 파이프라인 프로젝트입니다.

## 목표

- RSS/API/웹 소스에서 콘텐츠 후보 수집
- LLM을 이용한 요약·재작성·SEO 초안 생성
- 중복/품질 필터링
- 게시물 저장 및 예약 발행
- 실행 로그와 실패 내역 추적

## 기본 구조

```text
auto_blog/
├─ src/
│  ├─ collectors/     # RSS, API, 웹 수집
│  ├─ processors/     # 요약, 재작성, SEO, 중복제거
│  ├─ publishers/     # 블로그/CMS 발행 어댑터
│  └─ core/           # 설정, 모델, 공통 로직
├─ config/            # 소스/사이트별 설정
├─ data/              # 로컬 임시 데이터 (Git 제외)
├─ logs/              # 실행 로그 (Git 제외)
├─ tests/
├─ .env.example
├─ .gitignore
└─ requirements.txt
```

## 시작

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
python -m src.main
```

## 환경 변수

`.env.example`을 복사해 `.env`를 만들고 필요한 API 키와 발행 정보를 입력합니다.

> 실제 API 키, 토큰, 비밀번호는 GitHub에 커밋하지 않습니다.
