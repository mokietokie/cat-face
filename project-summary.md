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
| 웹 버전 (로컬) | Streamlit `st.camera_input()` |
| 웹 버전 (배포) | FastAPI + 순수 HTML/JS (`getUserMedia`) |
| 배포 플랫폼 | Render (GitHub 자동 배포) |
| 환경변수 관리 | `.env` (로컬) / Render Environment Variables (배포) |

---

## 3. 앱 구조 (현재)

```
cat-face/
├── main.py           # 데스크탑 CLI (OpenCV)
├── app.py            # Streamlit 웹앱 (로컬 전용)
├── server.py         # FastAPI 서버 (배포용)
├── static/
│   └── index.html    # 카메라 UI (HTML/JS)
├── render.yaml       # Render 배포 설정
├── requirements.txt
└── .env              # API 키 (git 제외)
```

---

## 4. 모바일 카메라 접근 — 옵션 비교

스마트폰 브라우저에서 카메라를 쓰려면 **HTTPS가 필수**. 브라우저의 `getUserMedia` API는 보안 컨텍스트(HTTPS 또는 localhost)에서만 동작하며, Safari 설정에서 카메라를 허용해도 HTTP 로컬 IP에서는 API 자체가 비활성화됨.

| 방법 | HTTPS | 난이도 | 비용 | 특징 |
|------|-------|--------|------|------|
| 같은 WiFi + HTTP | ❌ | 쉬움 | 무료 | 카메라 불가 (처음 시도, 실패) |
| ngrok 터널 | ✅ | 쉬움 | 무료 | 임시 URL, 맥 켜져 있어야 함 |
| 자체 SSL 인증서 | ✅ | 중간 | 무료 | 브라우저 보안 경고 뜸 |
| **클라우드 배포** | ✅ | 중간 | 무료~유료 | **항구적, 누구나 접속 가능** ← 선택 |

---

## 5. 시행착오

### 5-1. Streamlit 로컬 서버로 스마트폰 접근 시도 → 실패
- `streamlit run app.py --server.address 0.0.0.0` 으로 실행
- 스마트폰에서 `http://172.x.x.x:8501` 접속
- Safari 카메라 설정 "허용"으로 변경해봤으나 무효
- **원인:** HTTP 로컬 IP는 보안 컨텍스트가 아니라 브라우저 API 자체가 차단됨
- **교훈:** 카메라 권한은 설정의 문제가 아니라 프로토콜(HTTP/HTTPS)의 문제

### 5-2. Gemini 503 오류
- 배포 후 첫 분석 시 "오류가 발생했습니다" 표시
- **원인:** `503 UNAVAILABLE` — Gemini 서버 일시 과부하 (유료 계정도 발생)
- **대응:** 프론트엔드 에러 처리 개선 → 실제 에러 메시지 표시하도록 수정
- 잠시 후 재시도하면 정상 작동

---

## 6. 프레임워크 옵션 비교

### 웹 프레임워크

| 프레임워크 | 언어 | 난이도 | 특징 |
|-----------|------|--------|------|
| **Streamlit** | Python만 | 쉬움 | `st.camera_input()` 기본 제공. 로컬/ngrok 용도엔 최적. 배포 시 HTTP 문제 있음 |
| **FastAPI** | Python + HTML/JS | 중간 | REST API + 정적 파일 서빙. 배포에 적합. 선택한 방식 |
| Flask | Python + HTML/JS | 중간 | FastAPI와 유사. 더 오래된 생태계 |
| Node.js (Express) | JavaScript | 중간 | Python AI 코드와 언어 분리 필요 |

### 배포 플랫폼 옵션

| 플랫폼 | 무료 티어 | 난이도 | 특징 |
|--------|----------|--------|------|
| **Render** | ✅ (슬립 있음) | 쉬움 | GitHub 연결 → 자동 배포. HTTPS 자동. **이번에 선택** |
| GCP Cloud Run | ✅ (요청 기반 과금) | 어려움 | Docker 기반. 트래픽 없으면 비용 0. 다음 실습 예정 |
| Railway | ✅ | 쉬움 | Render와 유사 |
| Fly.io | ✅ | 중간 | Docker 기반 |
| Vercel | ✅ | 쉬움 | 정적 사이트/서버리스 함수. Python 제한적 |
| Heroku | ❌ (유료만) | 쉬움 | 과거 대표적 무료 플랫폼이었으나 유료 전환 |

---

## 7. 실제 진행한 배포 — Render

### 구조
```
GitHub (mokietokie/cat-face)
  ↓ push 감지 → 자동 빌드
Render Web Service
  ↓ HTTPS 자동 발급
https://cat-face.onrender.com
  ↓
스마트폰 브라우저 카메라 접근 가능
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

## 8. 다음 실습 예정

- **GCP Cloud Run 배포** — Docker 이미지 빌드 → Google Container Registry → Cloud Run 배포. Render보다 복잡하지만 실무에서 많이 쓰는 방식.
- **재시도 로직** — Gemini 503 시 자동으로 N초 후 재시도
- **텔레그램 봇 연동** — 분석 결과를 폰으로 푸시 알림
