# 🐱 고양이 AI 분석기 — 프로젝트 기록

## 오늘 만든 것

맥북 카메라로 얼굴/고양이를 찍으면 Gemini AI가 표정과 감정을 한국어로 분석해주는 프로그램.

- **스페이스바** → 사진 촬영 + 분석
- **q** → 종료

---

## 사용 스택

| 항목 | 내용 |
|---|---|
| 언어 | Python 3.12.10 |
| AI 모델 | Gemini 2.5 Flash (Google AI Studio 무료 API) |
| 카메라 | OpenCV |
| 이미지 처리 | Pillow |

---

## 설치한 라이브러리

```bash
python3 -m pip install google-genai opencv-python pillow
```

---

## 최종 코드

```python
import cv2
import base64
import os
from google import genai

# API 키 설정
client = genai.Client(api_key="YOUR_API_KEY")

# 카메라 켜기
cap = cv2.VideoCapture(0)
print("카메라 켜짐! 스페이스바 누르면 분석, q 누르면 종료")

while True:
    ret, frame = cap.read()
    cv2.imshow("고양이 AI 분석기", frame)
    
    key = cv2.waitKey(1)
    
    # 스페이스바 누르면 분석
    if key == 32:
        print("분석 중...")
        
        # 사진 저장
        cv2.imwrite("captured.jpg", frame)
        
        # 이미지를 base64로 변환
        with open("captured.jpg", "rb") as f:
            image_data = base64.b64encode(f.read()).decode()
        
        # Gemini한테 물어보기
        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=[
                {
                    "parts": [
                        {"text": "이 사진을 보고 피사체의 표정이나 감정을 재밌고 귀엽게 한국어로 분석해줘. 2~3문장으로 짧게."},
                        {"inline_data": {"mime_type": "image/jpeg", "data": image_data}}
                    ]
                }
            ]
        )
        
        print("\n🐱 AI 분석 결과:")
        print(response.text)
        print("-" * 40)
    
    # q 누르면 종료
    if key == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
```

---

## 트러블슈팅 기록

| 문제 | 원인 | 해결 |
|---|---|---|
| 카메라 초기화 실패 | Python 3.9 + 권한 문제 | Python 3.12로 업그레이드 |
| `gemini-2.0-flash` 404 에러 | 신규 사용자에게 구버전 모델 제공 안 함 | `gemini-2.5-flash`로 변경 |
| 라이브러리 못 찾음 | 3.9에 설치했는데 3.12로 실행 | 3.12에 재설치 |

---

## 다음 플랜

### 1단계 — 고양이 특화 (쉬움 ⭐)
프롬프트를 고양이 전용으로 바꾸기. 귀 위치, 꼬리, 눈 모양 기반으로 분석하도록 프롬프트 튜닝.

```python
"이 사진 속 고양이의 귀, 눈, 꼬리를 보고 지금 기분을 집사 입장에서 재밌게 분석해줘."
```

### 2단계 — 자동 촬영 (쉬움 ⭐⭐)
스페이스바 말고 5초마다 자동으로 찍어서 분석. 고양이가 지나갈 때 자동 감지.

### 3단계 — 텔레그램 연동 (중간 ⭐⭐⭐)
분석 결과를 폰 텔레그램으로 전송. 외출 중에도 고양이 상태 확인 가능.

```
카메라 감지 → 분석 → 텔레그램 메시지 전송
"집사님, 저 지금 배고파요 😾"
```

### 4단계 — 특정 표정 알림 (중간 ⭐⭐⭐)
"화남", "배고픔" 같은 특정 감정 감지 시에만 알림 발송.

### 5단계 — GCP 서버 상주 (어려움 ⭐⭐⭐⭐)
맥북 없이도 돌아가도록 GCP 서버에 올리기. 24시간 고양이 모니터링.

---

## 환경 정보

- **OS**: macOS (M4 MacBook Air)
- **Python**: 3.12.10
- **API**: Google Gemini 2.5 Flash (AI Studio 무료 티어)
- **프로젝트 경로**: `/Users/mok/cat-ai/`
