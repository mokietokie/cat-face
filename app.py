import streamlit as st
import base64
import os
import sys
from io import BytesIO
from dotenv import load_dotenv
from google import genai

load_dotenv()

api_key = os.getenv("GEMINI_API_KEY")
if not api_key:
    st.error("오류: GEMINI_API_KEY가 설정되지 않았습니다. .env 파일을 확인하세요.")
    sys.exit(1)

client = genai.Client(api_key=api_key)

st.title("🐱 고양이 AI 감정 분석기")

photo = st.camera_input("고양이를 카메라에 담고 촬영하세요")

if photo:
    image_data = base64.b64encode(photo.read()).decode()

    with st.spinner("분석 중..."):
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

    st.success(response.text)
