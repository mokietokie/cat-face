import os
import base64
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel
from dotenv import load_dotenv
from google import genai

load_dotenv()

client = genai.Client(api_key=os.environ["GEMINI_API_KEY"])

app = FastAPI()
app.mount("/static", StaticFiles(directory="static"), name="static")


@app.get("/")
def root():
    return FileResponse("static/index.html")


class ImageRequest(BaseModel):
    image: str  # base64 JPEG


@app.post("/analyze")
def analyze(req: ImageRequest):
    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=[
            {
                "parts": [
                    {"text": "이 사진 속 고양이의 귀, 눈, 꼬리를 보고 지금 기분을 집사 입장에서 재밌게 분석해줘. 2~3문장으로 짧게."},
                    {"inline_data": {"mime_type": "image/jpeg", "data": req.image}},
                ]
            }
        ],
    )
    return {"result": response.text}
