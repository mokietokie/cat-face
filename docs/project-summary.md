# 🐱 고양이 AI 감정 분석기 — 프로젝트 총정리

## 1. 프로젝트 개요

맥북 또는 스마트폰 카메라로 고양이를 찍으면 Google Gemini AI가 귀, 눈, 꼬리를 분석해 기분을 한국어로 설명해주는 앱.

---

## 2. 기술 스펙

| 항목 | 내용 |
|------|------|
| 언어 | Python 3.12 |
| AI 모델 | Google Gemini 2.5 Flash |
| API 클라이언트 | `google-genai` SDK |
| 이미지 전달 방식 | base64 인코딩 JPEG → Gemini `inline_data` |
| 데스크탑 버전 | OpenCV (`cv2`) 카메라 캡처 |
| 웹 버전 (배포) | FastAPI + 순수 HTML/JS (`getUserMedia`) |
| 배포 플랫폼 | Render (GitHub 자동 배포) |
| 환경변수 관리 | `.env` (로컬) / Render Environment Variables (배포) |

---

## 3. 최종 폴더 구조

```
cat-face/
├── main.py              # 데스크탑 CLI (OpenCV)
├── server.py            # FastAPI 서버 (배포용)
├── requirements.txt     # 의존성
├── render.yaml          # Render 배포 설정
├── CLAUDE.md            # Claude Code 가이드
├── static/
│   └── index.html       # 웹 카메라 UI (HTML/JS)
├── docs/
│   └── project-summary.md
└── venv/                # 로컬 전용, git 제외
```

---

## 4. 웹 프레임워크 개념 및 원리

### Streamlit

Python 코드만으로 웹 UI를 만드는 프레임워크. HTML/JS 없이 `st.camera_input()` 한 줄로 카메라 버튼이 생긴다. 내부적으로 Python 상태가 바뀔 때마다 페이지 전체를 리렌더링하는 방식이라 느리고 커스텀이 제한적이다. **빠른 프로토타입과 로컬 테스트에 최적**이지만, 배포 서버가 HTTP라 스마트폰 카메라가 차단되는 문제가 있다.

```
Python 코드 → Streamlit 엔진 → HTML/JS 자동 생성 → 브라우저
```

### FastAPI

Python으로 REST API 서버를 만드는 프레임워크. 브라우저(클라이언트)와 서버가 명확히 분리된다. 브라우저는 HTML/JS로 직접 카메라를 다루고, 사진 데이터만 서버로 전송하면 서버가 Gemini를 호출해 결과를 돌려준다. **배포 및 실서비스에 적합**하며, 타입 힌트 기반 자동 검증과 `/docs` 자동 API 문서가 특징이다.

```
브라우저(HTML/JS) ←→ FastAPI 서버(Python) ←→ Gemini API
```

이 프로젝트에서의 FastAPI 동작 흐름:

```
1. 스마트폰 브라우저 접속 (GET /)
   → server.py가 index.html 반환

2. 촬영 버튼 클릭
   → index.html이 getUserMedia로 카메라 캡처
   → 사진을 base64로 변환해 POST /analyze 전송

3. server.py가 /analyze 요청 수신
   → Gemini API 호출
   → 분석 결과 JSON으로 반환

4. 브라우저가 결과 텍스트 화면에 표시
```

### Flask

FastAPI와 동일하게 REST API 서버를 만드는 프레임워크. FastAPI보다 역사가 길고 생태계가 넓지만, 타입 검증이나 비동기 처리는 FastAPI가 더 현대적이다. 기능상 이 프로젝트에서는 Flask로도 동일하게 구현 가능하다.

### GET vs POST

| | GET | POST |
|--|-----|------|
| 용도 | 데이터 가져오기 | 데이터 보내기 |
| 이 프로젝트 | 페이지 열기 (`/`) | 사진 전송 + 분석 요청 (`/analyze`) |

### 실무에서의 활용 패턴

```
아이디어 검증 → Streamlit으로 빠르게 프로토타입
       ↓ 괜찮으면
실서비스 배포 → FastAPI로 다시 만들어서 클라우드 배포
```

이 프로젝트가 이 흐름을 그대로 경험한 케이스다.

---

## 5. 모바일 카메라 접근 — 옵션 비교

스마트폰 브라우저에서 카메라를 쓰려면 **HTTPS가 필수**. 브라우저의 `getUserMedia` API는 보안 컨텍스트(HTTPS 또는 localhost)에서만 동작한다. Safari 설정에서 카메라를 "허용"해도 HTTP 로컬 IP에서는 API 자체가 비활성화돼 있어 설정으로 우회 불가.

| 방법 | HTTPS | 난이도 | 특징 |
|------|-------|--------|------|
| 같은 WiFi + HTTP | ❌ | 쉬움 | 카메라 불가 — 처음 시도했다 실패 |
| ngrok 터널 | ✅ | 쉬움 | 임시 HTTPS URL. 맥이 켜져 있어야 함 |
| 자체 SSL 인증서 | ✅ | 중간 | 브라우저 보안 경고 뜸 |
| **클라우드 배포** | ✅ | 중간 | 항구적, 누구나 접속 가능 — 선택한 방법 |

---

## 6. 시행착오

### 6-1. Streamlit 로컬 서버로 스마트폰 접근 시도 → 실패
- `streamlit run app.py --server.address 0.0.0.0` 실행 후 스마트폰에서 `http://172.x.x.x:8501` 접속
- Safari 카메라 설정을 "허용"으로 바꿔봤으나 무효
- **원인:** HTTP 로컬 IP는 보안 컨텍스트가 아니라 브라우저 API 자체가 차단됨. 권한 설정의 문제가 아니라 프로토콜의 문제
- **결론:** `app.py` (Streamlit)는 불필요하다고 판단해 삭제

### 6-2. Gemini 503 오류
- 배포 후 첫 분석 시 "오류가 발생했습니다" 표시
- **원인:** `503 UNAVAILABLE` — Gemini 서버 일시 과부하. 유료 계정도 발생
- **대응:** 에러 핸들링 추가 → 실제 에러 메시지를 화면에 표시하도록 수정
- 잠시 후 재시도하면 정상 작동

---

## 7. 배포 플랫폼 옵션 비교

| 플랫폼 | 무료 티어 | 난이도 | 특징 |
|--------|----------|--------|------|
| **Render** | ✅ (슬립 있음) | 쉬움 | GitHub 연결 → 자동 배포. HTTPS 자동. **이번에 선택** |
| GCP Cloud Run | ✅ (요청 기반 과금) | 어려움 | Docker 기반. 트래픽 없으면 비용 0. **다음 실습 예정** |
| Railway | ✅ | 쉬움 | Render와 유사 |
| Fly.io | ✅ | 중간 | Docker 기반 |
| Vercel | ✅ | 쉬움 | 정적 사이트/서버리스 함수. Python 제한적 |
| Heroku | ❌ (유료만) | 쉬움 | 과거 대표적 무료 플랫폼이었으나 유료 전환됨 |

---

## 8. 실제 진행한 배포 — Render

### 배포 흐름

```
GitHub (mokietokie/cat-face)
  ↓ push 감지 → 자동 빌드 (pip install -r requirements.txt)
Render Web Service
  ↓ HTTPS 자동 발급
https://cat-face.onrender.com
  ↓
스마트폰 브라우저에서 카메라 접근 가능
```

### 배포 설정 (`render.yaml`)

```yaml
services:
  - type: web
    name: cat-face
    runtime: python
    buildCommand: pip install -r requirements.txt
    startCommand: uvicorn server:app --host 0.0.0.0 --port $PORT
    envVars:
      - key: GEMINI_API_KEY
        sync: false  # Render 대시보드에서 직접 입력
```

### Render 무료 플랜 특징
- 15분 비활성 시 슬립 → 첫 요청이 30~60초 느림
- GitHub push 시 자동 재배포
- HTTPS 자동 적용
- 월 750시간 무료

---

## 9. 다음 실습 예정

- **GCP Cloud Run 배포** — Docker 이미지 빌드 → Google Container Registry → Cloud Run 배포. Render보다 복잡하지만 실무에서 많이 쓰는 방식
- **재시도 로직** — Gemini 503 시 자동으로 N초 후 재시도
- **텔레그램 봇 연동** — 분석 결과를 폰으로 푸시 알림
