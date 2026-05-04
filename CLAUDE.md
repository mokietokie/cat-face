# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

고양이 AI 감정 분석기 — 카메라로 고양이를 찍으면 Gemini 2.5 Flash가 귀, 눈, 꼬리를 보고 기분을 한국어로 분석해주는 앱. 두 가지 실행 방식이 있다.

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
# 데스크탑 (OpenCV 카메라 창)
python main.py

# 웹 (로컬 브라우저, 스마트폰 불가 — HTTP라 카메라 차단됨)
streamlit run app.py --server.address 0.0.0.0

# 웹 (스마트폰 포함 — HTTPS 터널 필요)
ngrok http 8501  # 별도 터미널에서 실행 후 https URL 사용
```

## Architecture

두 진입점이 같은 Gemini 호출 패턴을 공유한다:

- **`main.py`** — OpenCV로 맥 카메라 열기 → 스페이스바 캡처 → base64 인코딩 → Gemini API → 터미널 출력
- **`app.py`** — Streamlit `st.camera_input()` → base64 인코딩 → 동일한 Gemini API 호출 → 웹 UI 출력

Gemini 호출 구조 (두 파일 공통):
```python
client.models.generate_content(
    model="gemini-2.5-flash",
    contents=[{"parts": [{"text": "프롬프트"}, {"inline_data": {"mime_type": "image/jpeg", "data": base64_str}}]}]
)
```

## Key Constraints

- 스마트폰 카메라는 HTTPS 필수 (`getUserMedia` API 보안 정책). HTTP 로컬 IP에서는 Safari/Chrome 설정과 무관하게 차단됨.
- Gemini 모델은 `gemini-2.5-flash` 사용. `gemini-2.0-flash`는 신규 계정에서 404 발생.

## Roadmap

`cat-ai-project.md` 참고. 다음 단계: FastAPI + Render/GCP Cloud Run 배포로 HTTPS 해결 및 외부 접근 허용.
