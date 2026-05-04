# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

고양이 AI 감정 분석기 — 카메라로 고양이를 찍으면 Gemini 2.5 Flash가 귀, 눈, 꼬리를 보고 기분을 한국어로 분석해주는 앱. 데스크탑(OpenCV)과 웹(FastAPI + Render 배포) 두 가지 방식으로 동작한다.

## Setup

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

`.env` 파일에 API 키 필요:
```
GEMINI_API_KEY=발급받은키
```

## Running

```bash
# 데스크탑 (OpenCV 카메라 창, 스페이스바로 캡처)
python main.py

# 웹 로컬 테스트 (브라우저에서만 — 스마트폰 카메라는 HTTP라 차단됨)
uvicorn server:app --reload

# 웹 배포 (Render에서 자동 실행)
uvicorn server:app --host 0.0.0.0 --port $PORT
```

## Architecture

```
main.py      → OpenCV 카메라 → 스페이스바 캡처 → Gemini API → 터미널 출력
server.py    → FastAPI 서버  → static/index.html 서빙
               index.html    → getUserMedia 카메라 → POST /analyze → Gemini API → 결과 표시
```

Gemini 호출 구조 (두 파일 공통):
```python
client.models.generate_content(
    model="gemini-2.5-flash",
    contents=[{"parts": [{"text": "프롬프트"}, {"inline_data": {"mime_type": "image/jpeg", "data": base64_str}}]}]
)
```

## Deployment

Render에 배포 중 (GitHub push 시 자동 재배포):
- 설정 파일: `render.yaml`
- 환경변수 `GEMINI_API_KEY`는 Render 대시보드에서 관리
- HTTPS 자동 적용 → 스마트폰 카메라 사용 가능

## Key Constraints

- 스마트폰 카메라는 HTTPS 필수 (`getUserMedia` 보안 정책). HTTP 로컬 IP에서는 Safari/Chrome 설정과 무관하게 차단됨.
- Gemini 모델은 `gemini-2.5-flash` 사용. `gemini-2.0-flash`는 신규 계정에서 404 발생.
- Gemini 503 오류는 서버 일시 과부하로 유료 계정도 발생. 재시도하면 해결됨.

## Roadmap

`docs/project-summary.md` 참고. 다음 단계: GCP Cloud Run 배포 실습.
