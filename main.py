import cv2
import base64
import os
import sys
from dotenv import load_dotenv
from google import genai

load_dotenv()

api_key = os.getenv("GEMINI_API_KEY")
if not api_key:
    print("오류: GEMINI_API_KEY가 설정되지 않았습니다.")
    print(".env 파일에 GEMINI_API_KEY=발급받은키 를 입력하세요.")
    sys.exit(1)

client = genai.Client(api_key=api_key)

cap = cv2.VideoCapture(0)
if not cap.isOpened():
    print("오류: 카메라를 열 수 없습니다. 카메라 권한을 확인하세요.")
    sys.exit(1)

print("카메라 켜짐! 스페이스바 누르면 분석, q 누르면 종료")

while True:
    ret, frame = cap.read()
    if not ret:
        print("오류: 프레임을 읽을 수 없습니다.")
        break

    cv2.imshow("고양이 AI 분석기", frame)

    key = cv2.waitKey(1)

    if key == 32:
        print("분석 중...")

        cv2.imwrite("captured.jpg", frame)

        with open("captured.jpg", "rb") as f:
            image_data = base64.b64encode(f.read()).decode()

        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=[
                {
                    "parts": [
                        {"text": "이 사진 속 고양이의 귀, 눈, 꼬리를 보고 지금 기분을 집사 입장에서 재밌게 분석해줘. 2~3문장으로 짧게."},
                        {"inline_data": {"mime_type": "image/jpeg", "data": image_data}}
                    ]
                }
            ]
        )

        print("\n🐱 AI 분석 결과:")
        print(response.text)
        print("-" * 40)

    if key == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
