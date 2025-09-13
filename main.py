import os
import google.generativeai as genai
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from dotenv import load_dotenv
# 👇 1. CORS를 위한 미들웨어를 가져옵니다.
from fastapi.middleware.cors import CORSMiddleware

# .env 파일에서 환경 변수 로드
load_dotenv()

# FastAPI 앱 생성
app = FastAPI(
    title="Vibe Coding 기술 언어 번역기",
    description="기술 용어를 누구나 이해하기 쉬운 비유와 은유로 번역해줍니다.",
    version="0.3.0", # 버전 업데이트
)

# 👇 2. CORS 미들웨어 설정
# 모든 출처(origins), 모든 메서드(methods), 모든 헤더(headers)를 허용합니다.
# 개발 환경에서는 "*"로 설정하여 모든 곳에서 오는 요청을 허용하는 것이 편리합니다.
origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Gemini API 키 설정
# API 키가 코드에 직접 노출되지 않도록 .env 파일을 사용하는 것이 좋습니다.
genai.configure(api_key=os.environ.get("GOOGLE_API_KEY"))

# Gemini Pro 모델 설정
model = genai.GenerativeModel('gemini-1.5-flash-latest')

# 요청 본문(Request Body) 모델 정의
class TechTerm(BaseModel):
    term: str

# 응답 본문(Response Body) 모델 정의
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
        # Gemini 응답에서 불필요한 공백이나 마크다운을 제거합니다.
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

# api 구매
# 앱 개발 비용
# 운영 비용
# 월급