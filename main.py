import os
import google.generativeai as genai
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from dotenv import load_dotenv
from fastapi.middleware.cors import CORSMiddleware

load_dotenv()

app = FastAPI(
    title="Vibe Coding 기술 언어 번역기",
    description="기술 용어를 누구나 이해하기 쉬운 비유와 은유로 번역해줍니다.",
    version="0.3.0",
)

origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

genai.configure(api_key=os.environ.get("GOOGLE_API_KEY"))

model = genai.GenerativeModel('gemini-1.5-flash-latest')

class TechTerm(BaseModel):
    term: str

class TranslationResponse(BaseModel):
    term: str
    translation: str

@app.post("/translate", response_model=TranslationResponse)
async def translate_term(tech_term: TechTerm):
    if not tech_term.term:
        raise HTTPException(status_code=400, detail="번역할 용어를 입력해주세요.")

    try:
        prompt = f"""
        당신은 기술 용어의 핵심을 '간결한 정의'와 '직관적인 비유'로 결합하는 'Vibe Coding' 전문가입니다.
        아래 기술 용어를 반드시 [핵심 정의] + [핵심 비유] 형식으로, 50자 내외의 짧은 구절로 답해주세요.
        설명하거나 긴 문장을 만들지 마세요.

        ---
        예시 1:
        - 입력: API
        - 출력: 프로그램 간의 통신 규칙. 식당의 정해진 메뉴판.

        예시 2:
        - 입력: 오픈소스 (Open Source)
        - 출력: 모두에게 공개된 소스코드. 누구나 볼 수 있는 맛집의 레시피.
        
        예시 3:
        - 입력: Git
        - 출력: 코드 버전 관리 도구. 되돌리기가 가능한 게임 세이브 파일.
        ---

        기술 용어: {tech_term.term}
        """
        response = model.generate_content(prompt)
        clean_translation = response.text.strip().replace("*", "")

        return TranslationResponse(
            term=tech_term.term,
            translation=clean_translation
        )
    except Exception as e:
        print(f"An error occurred: {e}")
        raise HTTPException(status_code=500, detail="번역 중 오류가 발생했습니다. 잠시 후 다시 시도해주세요.")

@app.get("/")
def read_root():
    return {"message": "Vibe Coding 번역기에 오신 것을 환영합니다! /docs 로 이동하여 API 문서를 확인하세요."}