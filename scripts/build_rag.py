"""
핵의학Ⅰ(이론) RAG 파이프라인 구축 스크립트
추출된 청크 데이터를 LightRAG로 처리하여
지식 그래프 기반 RAG 시스템을 구축합니다.

사용법:
  export GEMINI_API_KEY="your_key"
  python scripts/build_rag.py
"""

import asyncio
import json
import os
import sys
import numpy as np

# 환경변수 설정
API_KEY = os.environ.get("GEMINI_API_KEY")
if not API_KEY:
    print("오류: GEMINI_API_KEY 환경변수를 설정해주세요.")
    sys.exit(1)

# 경로 설정
BASE_DIR = "C:/src/nuclear"
CHUNKS_PATH = os.path.join(BASE_DIR, "output/extracted/chunks.json")
RAG_STORAGE_DIR = os.path.join(BASE_DIR, "rag_storage")
os.makedirs(RAG_STORAGE_DIR, exist_ok=True)

# 임베딩 차원
EMBEDDING_DIM = 768


async def custom_gemini_embed(texts: list[str]) -> np.ndarray:
    """Gemini 임베딩 API를 직접 호출하여 벡터를 생성합니다."""
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

    # L2 정규화
    norms = np.linalg.norm(result, axis=1, keepdims=True)
    norms = np.where(norms == 0, 1, norms)
    result = result / norms

    return result


async def build_rag():
    """RAG 시스템을 구축합니다."""
    from lightrag import LightRAG, QueryParam
    from lightrag.llm.gemini import gemini_model_complete
    from lightrag.utils import EmbeddingFunc

    print("1단계: 청크 데이터 로드...")
    with open(CHUNKS_PATH, "r", encoding="utf-8") as f:
        chunks = json.load(f)
    print(f"  {len(chunks)}개 청크 로드 완료")

    # 커스텀 임베딩 함수
    embedding_func = EmbeddingFunc(
        embedding_dim=EMBEDDING_DIM,
        max_token_size=2048,
        func=custom_gemini_embed,
    )

    print("2단계: LightRAG 초기화...")
    rag = LightRAG(
        working_dir=RAG_STORAGE_DIR,
        llm_model_func=gemini_model_complete,
        llm_model_name="gemini-2.0-flash",
        llm_model_kwargs={"api_key": API_KEY},
        embedding_func=embedding_func,
        embedding_batch_num=5,
        chunk_token_size=800,
        chunk_overlap_token_size=100,
    )
    await rag.initialize_storages()
    print("  LightRAG 초기화 완료")

    # 모든 청크를 하나의 큰 문서로 합침
    print("3단계: 문서 삽입 준비...")
    full_text = ""
    for chunk in chunks:
        page_info = f"[페이지 {chunk['page_start']}"
        if chunk['page_start'] != chunk['page_end']:
            page_info += f"-{chunk['page_end']}"
        page_info += "]"
        full_text += f"\n{page_info}\n{chunk['text']}\n"

    print(f"  전체 텍스트: {len(full_text)}자")

    # 텍스트를 적당한 크기로 분할
    chunk_size = 4000
    text_parts = []
    for i in range(0, len(full_text), chunk_size):
        text_parts.append(full_text[i:i + chunk_size])

    print(f"  {len(text_parts)}개 부분으로 분할")

    print("4단계: 지식 그래프 구축 중...")
    for idx, part in enumerate(text_parts):
        try:
            await rag.ainsert(part)
            print(f"  [{idx + 1}/{len(text_parts)}] 삽입 완료")
        except Exception as e:
            err_msg = str(e)
            print(f"  [{idx + 1}/{len(text_parts)}] 오류: {err_msg[:120]}")
            if "429" in err_msg or "rate" in err_msg.lower() or "quota" in err_msg.lower():
                print("  Rate limit — 60초 대기...")
                await asyncio.sleep(60)
                try:
                    await rag.ainsert(part)
                    print(f"  [{idx + 1}/{len(text_parts)}] 재시도 성공")
                except Exception as e2:
                    print(f"  [{idx + 1}/{len(text_parts)}] 재시도 실패: {str(e2)[:120]}")

    print("  지식 그래프 구축 완료!")

    # 테스트 쿼리
    print("\n5단계: RAG 시스템 테스트...")
    test_queries = [
        "핵의학의 정의는 무엇인가?",
        "SPECT와 PET의 차이점은?",
        "방사성의약품의 체내 검사 방법은?",
    ]

    results = []
    for query in test_queries:
        print(f"\n  Q: {query}")
        try:
            result = await rag.aquery(query, param=QueryParam(mode="mix"))
            print(f"  A: {result[:250]}...")
            results.append({"query": query, "answer": result, "status": "success"})
        except Exception as e:
            print(f"  오류: {e}")
            results.append({"query": query, "error": str(e), "status": "error"})

    results_file = os.path.join(BASE_DIR, "output/rag_test_results.json")
    with open(results_file, "w", encoding="utf-8") as f:
        json.dump(results, f, ensure_ascii=False, indent=2)

    print(f"\n===== RAG 구축 완료 =====")
    print(f"저장 경로: {RAG_STORAGE_DIR}")
    print(f"총 청크: {len(chunks)}개 → {len(text_parts)}개 파트")
    print(f"테스트 결과: {results_file}")


if __name__ == "__main__":
    asyncio.run(build_rag())
