"""
핵의학 RAG 백엔드 서버
- /api/quiz/generate : 문제 생성
- /api/rag/query : RAG 질의응답
- /api/health : 상태 확인
"""

import asyncio
import json
import os
import sys
import numpy as np
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

# 환경변수
API_KEY = os.environ.get("GEMINI_API_KEY", "")
BACKEND_DIR = os.path.dirname(os.path.abspath(__file__))
RAG_STORAGE_DIR = os.path.join(BACKEND_DIR, "rag_storage")
CHUNKS_PATH = os.path.join(BACKEND_DIR, "data", "chunks.json")

EMBEDDING_DIM = 768

# 전역 RAG 인스턴스
rag_instance = None
chunks_data = []


async def custom_gemini_embed(texts: list[str]) -> np.ndarray:
    """Gemini 임베딩 함수"""
    from google import genai
    from google.genai import types

    client = genai.Client(api_key=API_KEY)
    embeddings = []
    for text in texts:
        response = await client.aio.models.embed_content(
            model="gemini-embedding-001",
            contents=text,
            config=types.EmbedContentConfig(
                output_dimensionality=EMBEDDING_DIM,
            ),
        )
        embeddings.append(response.embeddings[0].values)

    result = np.array(embeddings, dtype=np.float32)
    norms = np.linalg.norm(result, axis=1, keepdims=True)
    norms = np.where(norms == 0, 1, norms)
    return result / norms


async def init_rag():
    """RAG 시스템 초기화"""
    global rag_instance, chunks_data

    from lightrag import LightRAG
    from lightrag.llm.gemini import gemini_model_complete
    from lightrag.utils import EmbeddingFunc

    # 청크 데이터 로드
    with open(CHUNKS_PATH, "r", encoding="utf-8") as f:
        chunks_data = json.load(f)

    embedding_func = EmbeddingFunc(
        embedding_dim=EMBEDDING_DIM,
        max_token_size=2048,
        func=custom_gemini_embed,
    )

    rag_instance = LightRAG(
        working_dir=RAG_STORAGE_DIR,
        llm_model_func=gemini_model_complete,
        llm_model_name="gemini-2.0-flash",
        llm_model_kwargs={"api_key": API_KEY},
        embedding_func=embedding_func,
        embedding_batch_num=5,
    )
    await rag_instance.initialize_storages()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """서버 시작/종료 시 RAG 초기화/정리"""
    print("RAG 시스템 초기화 중...")
    await init_rag()
    print(f"RAG 초기화 완료. 청크 {len(chunks_data)}개 로드됨.")
    yield
    print("서버 종료")


app = FastAPI(title="핵의학 RAG API", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# --- 요청/응답 모델 ---

class QuizRequest(BaseModel):
    topic: str = ""
    count: int = 5
    difficulty: str = "중"  # 상/중/하


class QuizChoice(BaseModel):
    number: int
    text: str


class QuizQuestion(BaseModel):
    id: int
    question: str
    choices: list[QuizChoice]
    answer: int
    explanation: str
    page_ref: str


class QuizResponse(BaseModel):
    questions: list[QuizQuestion]
    topic: str


class RAGQueryRequest(BaseModel):
    question: str
    mode: str = "mix"  # local, global, mix


class RAGQueryResponse(BaseModel):
    answer: str
    question: str


# --- API 엔드포인트 ---

@app.get("/api/health")
async def health():
    return {
        "status": "ok",
        "rag_loaded": rag_instance is not None,
        "chunks_count": len(chunks_data),
    }


@app.post("/api/rag/query", response_model=RAGQueryResponse)
async def rag_query(req: RAGQueryRequest):
    """RAG 기반 질의응답"""
    if not rag_instance:
        raise HTTPException(status_code=503, detail="RAG 시스템 미초기화")

    from lightrag import QueryParam

    try:
        result = await rag_instance.aquery(
            req.question,
            param=QueryParam(mode=req.mode),
        )
        return RAGQueryResponse(answer=result, question=req.question)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/quiz/generate", response_model=QuizResponse)
async def generate_quiz(req: QuizRequest):
    """RAG 기반 문제 생성"""
    if not rag_instance:
        raise HTTPException(status_code=503, detail="RAG 시스템 미초기화")

    from lightrag import QueryParam

    # 1단계: 주제에 관련된 내용을 RAG에서 검색
    topic = req.topic if req.topic else "핵의학 전반"
    context_query = f"{topic}에 대한 핵심 내용을 상세히 설명해주세요."

    try:
        context = await rag_instance.aquery(
            context_query,
            param=QueryParam(mode="mix"),
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"RAG 검색 오류: {e}")

    # 2단계: Gemini로 문제 생성
    from google import genai

    client = genai.Client(api_key=API_KEY)

    difficulty_map = {
        "하": "기초적인 용어와 개념을 묻는 쉬운",
        "중": "원리와 응용을 이해해야 하는 중간 난이도의",
        "상": "심화 분석과 임상 적용을 요구하는 어려운",
    }
    diff_desc = difficulty_map.get(req.difficulty, difficulty_map["중"])

    prompt = f"""다음 핵의학 교과서 내용을 기반으로 방사선사 국가고시 형태의 {diff_desc} 객관식 문제를 {req.count}개 만들어주세요.

## 교과서 내용
{context}

## 출제 규칙
1. 각 문제는 5지선다형 객관식
2. 정답은 반드시 1개
3. 오답 보기도 교과서에 나올 법한 그럴듯한 내용으로 구성
4. 해설은 왜 정답이 맞는지, 왜 오답이 틀리는지 구체적으로 설명
5. 주제: {topic}

## 반드시 아래 JSON 형식으로만 응답하세요 (다른 텍스트 없이):
```json
[
  {{
    "id": 1,
    "question": "문제 내용",
    "choices": [
      {{"number": 1, "text": "보기1"}},
      {{"number": 2, "text": "보기2"}},
      {{"number": 3, "text": "보기3"}},
      {{"number": 4, "text": "보기4"}},
      {{"number": 5, "text": "보기5"}}
    ],
    "answer": 1,
    "explanation": "해설 내용",
    "page_ref": "관련 페이지 또는 단원"
  }}
]
```"""

    try:
        response = await client.aio.models.generate_content(
            model="gemini-2.0-flash",
            contents=prompt,
        )

        raw = response.text.strip()
        # JSON 블록 추출
        if "```json" in raw:
            raw = raw.split("```json")[1].split("```")[0].strip()
        elif "```" in raw:
            raw = raw.split("```")[1].split("```")[0].strip()

        questions = json.loads(raw)

        quiz_questions = []
        for q in questions:
            quiz_questions.append(QuizQuestion(
                id=q["id"],
                question=q["question"],
                choices=[QuizChoice(**c) for c in q["choices"]],
                answer=q["answer"],
                explanation=q["explanation"],
                page_ref=q.get("page_ref", ""),
            ))

        return QuizResponse(questions=quiz_questions, topic=topic)

    except json.JSONDecodeError as e:
        raise HTTPException(
            status_code=500,
            detail=f"문제 생성 JSON 파싱 오류: {e}\nRaw: {raw[:300]}",
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"문제 생성 오류: {e}")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
