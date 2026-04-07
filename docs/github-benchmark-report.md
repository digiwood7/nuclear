# 방사선사 국가고시 RAG 학습 플랫폼 - GitHub 벤치마킹 리포트

> 작성일: 2026-04-07
> 목적: 핵의학 방사선사 국가고시 대비 문제은행 + RAG 기반 학습 플랫폼 구축을 위한 오픈소스 프로젝트 조사

---

## 목차

1. [프로젝트 개요](#1-프로젝트-개요)
2. [RAG 엔진 (핵심 인프라)](#2-rag-엔진-핵심-인프라)
3. [PDF 교과서 → RAG 파이프라인](#3-pdf-교과서--rag-파이프라인)
4. [Next.js + PWA 퀴즈 앱](#4-nextjs--pwa-퀴즈-앱)
5. [AI 문제 생성 + RAG 결합](#5-ai-문제-생성--rag-결합)
6. [의료 도메인 특화 RAG](#6-의료-도메인-특화-rag)
7. [추천 아키텍처 조합](#7-추천-아키텍처-조합)
8. [교과서 RAG화 프로세스](#8-교과서-raghua-프로세스)
9. [종합 비교표](#9-종합-비교표)

---

## 1. 프로젝트 개요

### 구현 목표

- **문제은행 시스템**: 국가고시 기출문제 형태 분석 → 유사 문제 자동 출제 → 해설 제공
- **RAG Q&A 시스템**: 수험자가 모르는 부분을 키워드로 질문 → 교과서 기반 해설 제공
- **교재 RAG화**: 핵의학 방사선사 교과서 자료를 벡터 데이터베이스로 변환

### 기술 스택

- **프론트엔드**: Next.js, TypeScript, Tailwind CSS, PWA (모바일 앱처럼 보이도록)
- **백엔드**: Next.js API Routes 또는 FastAPI
- **AI/RAG**: LangChain, 벡터 DB, LLM (Claude API)

---

## 2. RAG 엔진 (핵심 인프라)

### 2.1 RAGFlow

- **GitHub**: https://github.com/infiniflow/ragflow
- **Stars**: 77,200+
- **기술 스택**: Python, Go (백엔드) / React (프론트엔드) / Docker / MySQL / Redis
- **벡터 DB**: Elasticsearch (기본) 또는 Infinity
- **임베딩 모델**: 설정 가능 (다양한 모델 지원)
- **문서 수집**: 자체 개발 DeepDoc 엔진 — 딥러닝 기반 PDF 파싱 → 템플릿 기반 청킹 → 임베딩 생성
- **핵심 기능**:
  - 딥 문서 이해 (PDF/Word/이미지/엑셀)
  - 템플릿 기반 지능형 청킹 (Naive, Manual, **Book**, Laws, Paper 등)
  - 인용 근거 시각화 (환각 감소)
  - 에이전틱 워크플로우
  - 크로스 언어 검색
  - 멀티모달 처리
- **아키텍처**: 마이크로서비스 구조, 5,664+ 커밋으로 매우 활발히 유지보수
- **평가**: 가장 성숙한 RAG 엔진. **Book 청킹 모드**가 있어 교과서 처리에 특화. 문서 파싱/검색 백엔드로 가장 적합

### 2.2 Kotaemon

- **GitHub**: https://github.com/Cinnamon/kotaemon
- **Stars**: 25,300+
- **기술 스택**: Python / Gradio (UI) / Docker
- **벡터 DB**: ChromaDB, LanceDB, Milvus, Qdrant, InMemory (선택 가능)
- **임베딩 모델**: 다양한 LLM 제공자 지원 (OpenAI, Ollama, llama-cpp 등)
- **문서 수집**: Azure Document Intelligence, Adobe PDF Extract, Docling, Unstructured
- **핵심 기능**:
  - 멀티 유저 로그인
  - 하이브리드 RAG (전문검색 + 벡터검색)
  - 리랭킹
  - 멀티모달 QA (표/그림 지원)
  - PDF 뷰어 내 인용 표시
  - GraphRAG 지원
  - ReAct/ReWOO 추론 에이전트
- **아키텍처**: Apache 2.0 라이선스, 3단계 사용자 계층
- **평가**: 문서 기반 Q&A에 특화. 벡터 DB 선택 자유도 높고 UI 깔끔. 의료 교재 기반 질의응답에 직접 활용 가능

### 2.3 Quivr

- **GitHub**: https://github.com/QuivrHQ/quivr
- **Stars**: 39,100+
- **기술 스택**: Python / React / TypeScript / Docker / PostgreSQL
- **벡터 DB**: PGVector, FAISS (또는 임의의 벡터스토어)
- **임베딩 모델**: 설정 가능 (OpenAI, Anthropic, Mistral, Groq, Ollama 지원)
- **문서 수집**: Megaparse (자체 오픈소스 도구)로 PDF/TXT/Markdown 등 처리
- **핵심 기능**:
  - 의견화된(opinionated) RAG 프레임워크
  - 커스텀 워크플로우 (filter_history → rewrite → retrieve → generate_rag)
  - 인터넷 검색 통합
  - 리랭커 설정
  - Le Juge 평가 프레임워크
- **아키텍처**: Apache 2.0 라이선스, 모듈형 RAG 파이프라인
- **평가**: "두 번째 뇌" 컨셉. 학생이 교재를 업로드하고 질의하는 개인화 학습 도구로 전용 가능

### 2.4 PrivateGPT

- **GitHub**: https://github.com/zylon-ai/private-gpt
- **Stars**: 57,200+
- **기술 스택**: Python / LlamaIndex
- **벡터 DB**: Qdrant, Chroma 등
- **임베딩 모델**: 로컬 HuggingFace 또는 OpenAI
- **핵심 기능**:
  - **100% 오프라인 실행** 가능
  - Ollama를 통한 로컬 LLM 지원
  - PDF, DOCX 등 다양한 포맷 지원
- **평가**: 완전한 데이터 프라이버시가 필요한 교육 기관에 적합. 인터넷 없이도 동작

### 2.5 Verba

- **GitHub**: https://github.com/weaviate/Verba
- **Stars**: 7,600+
- **기술 스택**: Python / Weaviate
- **벡터 DB**: Weaviate (자체 벡터 DB)
- **핵심 기능**:
  - `pip install goldenverba` 한 줄 설치
  - Ollama, HuggingFace, Anthropic, OpenAI 지원
  - 데이터 교차 참조 및 인사이트 도출
- **평가**: 빠른 프로토타이핑에 적합

---

## 3. PDF 교과서 → RAG 파이프라인

핵의학 교과서(수식, 테이블, 방사선 도표 포함)를 처리하려면 PDF 파싱이 핵심.

### 3.1 MinerU

- **GitHub**: https://github.com/opendatalab/MinerU
- **Stars**: 58,300+
- **기술 스택**: Python
- **PDF 처리**: VLM + OCR 듀얼 엔진, **109개 언어** 지원
- **테이블/이미지/수식 처리**:
  - 수식: LaTeX 형식으로 자동 변환
  - 테이블: HTML 형식으로 자동 변환
  - 이미지: 자동 감지 및 추출
  - 스캔 PDF 자동 감지 후 OCR 활성화
- **출력 형식**: Markdown, JSON
- **인터페이스**: CLI, FastAPI 서버(mineru-api), Gradio UI, Python SDK
- **평가**: **교과서의 복잡한 레이아웃(수식, 테이블, 다단 구성) 처리에 가장 강력**. CJK(한중일) 콘텐츠 처리에 특히 뛰어남. Shanghai AI Lab 개발

### 3.2 Docling

- **GitHub**: https://github.com/docling-project/docling
- **Stars**: 57,100+
- **기술 스택**: Python (IBM Research Zurich 개발)
- **PDF 처리**: 페이지 레이아웃, 읽기 순서, 테이블 구조, 코드, 수식, 이미지 분류 등 고급 PDF 이해
- **청킹 전략**: **HybridChunker** — 문서 구조를 존중하면서 토큰 예산을 준수하는 계층적 청킹
- **테이블/이미지/수식 처리**:
  - 테이블: table-structure 모델이 행/열/병합 셀 재조립 → Pandas DataFrame/CSV 출력
  - 수식/코드: DocTags 포맷으로 복잡한 요소 캡처
  - 이미지: SmolDocling VLM 활용 그림 캡셔닝
- **프레임워크 통합**: LangChain, LlamaIndex, CrewAI, Haystack 플러그앤플레이
- **출력 형식**: Markdown, JSON, DocTags
- **평가**: **교과서의 구조적 의미(heading, paragraph, list)를 정확히 보존**. IBM Research 개발로 학술/기술 문서 품질 높음

### 3.3 Marker

- **GitHub**: https://github.com/datalab-to/marker
- **Stars**: 33,400+
- **기술 스택**: Python (Surya OCR 엔진 기반)
- **PDF 처리**: PDF, DOCX, PPTX, 이미지 → Markdown/JSON 변환
- **테이블/이미지/수식**: 테이블, 수학 수식, 코드 블록, 링크, 참조 모두 포맷팅
- **출력 형식**: Markdown, JSON, HTML, chunks
- **성능**: GPT-4o, Deepseek OCR, Mistral OCR을 모두 능가
- **라이센스**: 코드 GPL / 모델 가중치는 연구/개인 사용 무료
- **평가**: 빠른 변환 속도와 높은 정확도로 대량 교과서 PDF 일괄 처리에 적합

### 3.4 RAG-Anything

- **GitHub**: https://github.com/HKUDS/RAG-Anything
- **Stars**: 15,300+
- **기술 스택**: Python (LightRAG 위에 구축)
- **PDF 처리**: **MinerU를 내장**하여 고충실도 문서 구조 추출
- **멀티모달 처리 (핵심 차별점)**:
  - **ImageModalProcessor**: 시각적 콘텐츠와 맥락적 의미 해석
  - **TableModalProcessor**: 테이블 구조 파싱, 논리적/수치적 관계 디코딩
  - **EquationModalProcessor**: 수학 기호와 수식의 의미론 이해
- **아키텍처**: 듀얼 그래프 구축 — 크로스 모달 지식 그래프 + 텍스트 기반 지식 그래프 병합
- **평가**: **학술 연구, 기술 문서, 수식이 많은 교과서에 가장 특화**. EMNLP 2025 논문 기반 학술적 검증

---

## 4. Next.js + PWA 퀴즈 앱

### 4.1 mlynch/nextjs-tailwind-ionic-capacitor-starter

- **GitHub**: https://github.com/mlynch/nextjs-tailwind-ionic-capacitor-starter
- **Stars**: 1,900+
- **기술 스택**: Next.js 14, TypeScript, Tailwind CSS, Ionic Framework, Capacitor
- **핵심 기능**:
  - iOS/Android/PWA 단일 코드베이스
  - Ionic이 네이티브 수준 UI 컨트롤 제공 (navigation, transitions, tabs)
  - Capacitor가 네이티브 SDK 전체 접근 제공
  - Card, Notifications, Settings, Tabs 등 예제 컴포넌트
- **평가**: **Stars 가장 많은 PWA 스타터**. 이 템플릿 위에 퀴즈 기능 구축이 가장 현실적

### 4.2 tib0/next-pwa-template

- **GitHub**: https://github.com/tib0/next-pwa-template
- **기술 스택**: Next.js 14, TypeScript, Serwist(Service Worker), DaisyUI, Tailwind CSS, Dexie(IndexedDB)
- **핵심 기능**:
  - Serwist로 Service Worker 구현
  - Dexie로 IndexedDB 활용한 **오프라인 데이터 저장**
  - DaisyUI 기반 반응형 UI
  - 완전한 PWA 지원 (설치 가능, 오프라인 지원)
- **평가**: **오프라인 기능 가장 잘 구현된 PWA 템플릿**. 오프라인 문제풀이 구현 시 핵심 참고

### 4.3 SharjeelSafdar/quiz-app-pwa

- **GitHub**: https://github.com/SharjeelSafdar/project7a2-quiz-app-pwa
- **기술 스택**: React, TypeScript, Styled Components, Service Worker, FCM
- **핵심 기능**:
  - **PWA 퀴즈 앱의 직접적인 구현체**
  - 모든 OS에 설치 가능
  - 30개+ 카테고리, 객관식 및 O/X 문제
  - 3단계 난이도 선택
  - 결과 화면 정답/오답 하이라이트
  - React Suspense + Render-as-You-Fetch 패턴
- **평가**: **PWA + 퀴즈의 가장 직접적인 조합**. 기능 설계와 오프라인 전략 참고에 최적

### 4.4 Hamed-Hasan/Quiz-management

- **GitHub**: https://github.com/Hamed-Hasan/Quiz-management-backend (백엔드) / https://github.com/Hamed-Hasan/Quiz-management-frontend (프론트엔드)
- **기술 스택**: Next.js, TypeScript, Redux, Express.js, PostgreSQL, Prisma
- **핵심 기능**:
  - Admin/Performer 역할 기반 인증
  - 퀴즈 CRUD + 카테고리 분류
  - 단일 선택 및 다중 선택(MCQ) 문제
  - 카테고리별 10문제 랜덤 출제, 즉시 피드백, 실시간 점수 계산
  - 리더보드 및 상위 퍼포머 표시
- **DB 스키마**: Prisma로 PostgreSQL 스키마 정의
- **평가**: 가장 완성도 높은 퀴즈 관리 시스템. 문제은행(Question Bank) 관리, 사용자 역할, 점수 관리 모두 포함

### 4.5 quentin-mckay/AI-Quiz-Generator

- **GitHub**: https://github.com/quentin-mckay/AI-Quiz-Generator
- **Stars**: 92
- **기술 스택**: Next.js, OpenAI ChatGPT API
- **핵심 기능**:
  - 사용자 지정 언어, 주제, 난이도 MCQ 생성
  - 실시간 응답 스트리밍 로딩 화면
  - 점수 기반 결과 화면 (GIF, 축하 효과)
  - Kahoot 스타일 오디오 플레이어
- **평가**: **UI/UX 관점에서 가장 세련된 프로젝트**. 게이미피케이션 요소 참고에 탁월

### 4.6 기타 참고 프로젝트

| 프로젝트 | 기술 스택 | 핵심 참고 포인트 |
|---------|----------|----------------|
| [ECarry/quiz-online-nextjs](https://github.com/ECarry/quiz-online-nextjs) | Next.js, Prisma, MongoDB, AuthJS v5, Shadcn UI, Tailwind | Shadcn UI + Tailwind 모바일 반응형 |
| [web-slate/test-mate](https://github.com/web-slate/test-mate) | Next.js | 시험 UX 플로우 참고 |
| [arBishal/OEMS](https://github.com/arBishal/OEMS-Online-Exam-Management-System) | Next.js | 시험 관리 시스템 (공지, 토론 기능) |
| [meleongg/flashcard-frontend](https://github.com/meleongg/flashcard-frontend) | Next.js 14, Tailwind, PWA | Next.js + PWA + 학습 앱 세 가지 결합 |

---

## 5. AI 문제 생성 + RAG 결합

### 5.1 AI-Quiz-Generator (OussamaBenSlama)

- **GitHub**: https://github.com/OussamaBenSlama/AI-Quiz-generator
- **Stars**: 4
- **기술 스택**: FastAPI (백엔드) / Next.js + TypeScript (프론트엔드)
- **벡터 DB**: ChromaDB
- **임베딩 모델**: Ollama (Llama3)
- **문서 수집**: Unstructured.io → LangChain 텍스트 청킹 → Ollama 임베딩 → ChromaDB
- **핵심 기능**:
  - PDF 업로드 → 문서당 8개 퀴즈 자동 생성
  - Yes/No + 객관식 + 단답형 지원
  - 답변 제출 및 피드백
- **평가**: **교육/시험 플랫폼에 가장 가까운 기술 스택** (Next.js + FastAPI). 아키텍처 참고용으로 매우 유용

### 5.2 GenQuest-RAG

- **GitHub**: https://github.com/MohammedAly22/GenQuest-RAG
- **Stars**: 17
- **기술 스택**: Python / PyTorch / HuggingFace / Streamlit
- **벡터 DB**: Weaviate
- **임베딩 모델**: T5-small (SQuAD 파인튜닝)
- **핵심 기능**:
  - 답변 인식 질문 생성 (Answer-Aware QG)
  - **Bloom's Taxonomy 수준별 질문** (지식/이해/적용/분석/평가/창조)
  - Diverse Beam Search로 다양한 질문 생성
  - BERTScore 91.82 달성
- **평가**: **교육학 이론 기반 질문 생성**. 시험 문제 자동 생성의 학술적 접근법 참고에 적합

### 5.3 QuizGen-RAG

- **GitHub**: https://github.com/gkuling/QuizGen-RAG
- **Stars**: 4
- **기술 스택**: Python / LlamaIndex / Azure OpenAI
- **핵심 기능**:
  - Bloom's Taxonomy 6단계별 단답형 문제 생성
  - **주차별 맞춤 문제 생성** (교과 과정 연동)
  - JSON/CSV 출력 지원
- **평가**: 대학 강의 커리큘럼 기반 문제 생성에 특화. 교육 과정 연동 로직 참고

### 5.4 Medha AI (RAG-Powered Fullstack Learning Platform)

- **GitHub**: https://github.com/SHubhamanjk/rag-powered-fullstack-learning-platform
- **기술 스택**: React 18 + TypeScript + Vite / FastAPI + Python 3.11 / MongoDB / Docker
- **벡터 DB**: FAISS
- **임베딩 모델**: all-MiniLM-L6-v2 (SentenceTransformers)
- **핵심 기능**:
  - RAG 기반 학습자료 분석
  - MCQ/서술형 퀴즈 시스템
  - AI 의심 해결 도우미 (음성 I/O)
  - **마인드맵 자동 생성** (Graphviz)
  - YouTube 튜토리얼 연동
  - 학습 분석 대시보드
  - JWT 인증
- **평가**: **기능 면에서 교육 플랫폼에 가장 가까운 풀스택 프로젝트**. 아키텍처 참고 가치 매우 높음

### 5.5 tripathirakeshofficial/quizmify

- **GitHub**: https://github.com/tripathirakeshofficial/quizmify
- **기술 스택**: Next.js 13, TailwindCSS, OpenAI API, NextAuth, Prisma
- **핵심 기능**:
  - AI(OpenAI)로 퀴즈 자동 생성
  - NextAuth 인증
  - Prisma DB 연동
- **평가**: AI 문제 동적 생성 패턴 참고. Prisma 퀴즈/문제/답변 모델 구조 확인 가능

---

## 6. 의료 도메인 특화 RAG

### 6.1 MedRAG ★ 핵심 참고

- **GitHub**: https://github.com/Teddy-XiongGZ/MedRAG
- **Stars**: 534
- **기술 스택**: Python / PyTorch / Transformers / FAISS / Java (BM25용)
- **벡터 DB**: FAISS (HNSW 가속 옵션)
- **임베딩 모델**: Contriever (110M), **MedCPT (109M, 바이오메디컬 특화)**, SPECTER (110M), BM25
- **의료 코퍼스**:
  - PubMed: 2,390만건
  - StatPearls: 9,300건 / 30만 스니펫
  - 의학 교과서: 18권 / 12.5만 스니펫
  - Wikipedia: 650만건
  - **총 MedCorp: 5,420만 스니펫**
- **핵심 기능**:
  - Standard RAG, Chain-of-Thought, i-MedRAG (반복 검색)
  - 사전 지정 스니펫
  - 코퍼스 캐싱
  - 다중 코퍼스 교차 검색
  - 6종 LLM 대비 **정확도 최대 18% 향상**
- **아키텍처**: 3개 컴포넌트 (Corpora / Retrievers / LLMs)
- **평가**: **의료 시험 준비에 가장 직접적으로 관련된 프로젝트**. MMLU 의학 질문에서 검증됨. 의학 교과서 RAG의 핵심 레퍼런스

### 6.2 Medical-RAG-LLM

- **GitHub**: https://github.com/AquibPy/Medical-RAG-LLM
- **Stars**: 38
- **기술 스택**: Python / FastAPI / HTML
- **벡터 DB**: Qdrant (Docker, localhost:6333)
- **임베딩 모델**: **PubMedBERT** (바이오메디컬 텍스트 특화)
- **LLM**: BioMistral 7B (GGUF 양자화)
- **핵심 기능**:
  - **완전 로컬 실행** (클라우드 의존성 없음)
  - 의학 요약, Q&A, 임상 의사결정, 문헌 분석, 환자 교육
- **평가**: 프라이버시 중요한 의료 데이터 처리에 적합. **Qdrant + PubMedBERT** 조합이 의료 도메인 RAG의 좋은 레퍼런스

### 6.3 PaperQA2

- **GitHub**: https://github.com/Future-House/paper-qa
- **Stars**: 8,300+
- **기술 스택**: Python 3.11+ / LiteLLM / Pydantic / tantivy
- **임베딩 모델**: OpenAI text-embedding-3-small (기본), 로컬 SentenceTransformer 지원
- **핵심 기능**:
  - 에이전틱 RAG (검색 → 증거 수집 → 답변 생성)
  - 인텍스트 인용 근거
  - Semantic Scholar/Crossref 메타데이터 자동 조회
  - 전문검색 + 벡터검색 하이브리드
- **평가**: 학술 논문/교과서 기반 Q&A에 최적화. 의학 논문 검색 시스템 백엔드로 활용 가능

---

## 7. 추천 아키텍처 조합

### 시스템 아키텍처 다이어그램

```
┌──────────────────────────────────────────────────────────┐
│                   프론트엔드 (PWA)                          │
│   Next.js 14 + TypeScript + Tailwind CSS + Ionic          │
│   참고: mlynch/starter + next-pwa-template                │
│                                                           │
│   ┌─────────────┐  ┌──────────────┐  ┌────────────────┐  │
│   │  문제풀이 UI  │  │  RAG 질의 UI  │  │  학습현황 대시보드│  │
│   └─────────────┘  └──────────────┘  └────────────────┘  │
├──────────────────────────────────────────────────────────┤
│                   백엔드 API 레이어                         │
│   Next.js API Routes 또는 FastAPI                         │
│   참고: AI-Quiz-Generator (OussamaBenSlama)               │
│                                                           │
│   ┌──────────────────┐  ┌───────────────────────────┐    │
│   │  문제은행 시스템     │  │  RAG Q&A 시스템             │    │
│   │  - 기출문제 DB      │  │  - 교과서 벡터 검색          │    │
│   │  - AI 문제 생성     │  │  - 키워드 질의응답           │    │
│   │  - 해설 제공        │  │  - 인용 근거 표시            │    │
│   │  참고: Quiz-mgmt   │  │  참고: MedRAG + Kotaemon   │    │
│   └──────────────────┘  └───────────────────────────┘    │
├──────────────────────────────────────────────────────────┤
│              PDF 교과서 파싱 파이프라인                       │
│   MinerU (한글 교과서) → 청킹 → 임베딩                      │
│   참고: RAG-Anything (수식/테이블 프로세서)                  │
├──────────────────────────────────────────────────────────┤
│                데이터 저장소                                 │
│   ┌──────────────────┐  ┌───────────────────────────┐    │
│   │  관계형 DB          │  │  벡터 DB                    │    │
│   │  PostgreSQL        │  │  pgvector                  │    │
│   │  + Prisma ORM     │  │  (하이브리드 검색)             │    │
│   │  참고: Quiz-mgmt   │  │  참고: Quivr               │    │
│   └──────────────────┘  └───────────────────────────┘    │
└──────────────────────────────────────────────────────────┘
```

### 레이어별 참고 프로젝트 매핑

| 레이어 | 참고 프로젝트 | 가져올 것 |
|--------|-------------|----------|
| **모바일 PWA 기반** | mlynch/nextjs-tailwind-ionic-capacitor-starter (1.9k stars) | Ionic + Capacitor + Next.js 앱 셸 구조 |
| **오프라인/SW** | tib0/next-pwa-template | Serwist Service Worker + Dexie IndexedDB 오프라인 전략 |
| **퀴즈 도메인 로직 + DB** | Hamed-Hasan/Quiz-management | Prisma 스키마, 문제 CRUD, 카테고리, 점수, 리더보드 |
| **퀴즈 PWA UX** | SharjeelSafdar/quiz-app-pwa | 카테고리 선택, 난이도, 결과 화면, 오프라인 플로우 |
| **UI 게이미피케이션** | quentin-mckay/AI-Quiz-Generator (92 stars) | 진행바, 점수 기반 피드백, 애니메이션 |
| **AI 문제 생성 + RAG** | OussamaBenSlama/AI-Quiz-generator | Next.js + FastAPI + ChromaDB + LangChain 풀스택 |
| **의료 RAG** | MedRAG | MedCPT 임베딩, 의학 코퍼스 구조, i-MedRAG 반복 검색 |
| **교과서 PDF 파싱** | MinerU + RAG-Anything | 한글 PDF 파싱, 수식/테이블 전용 프로세서 |

---

## 8. 교과서 RAG화 프로세스

핵의학 교과서를 RAG로 변환하는 6단계 프로세스:

### Step 1: PDF 파싱

```
교과서 PDF → MinerU → Markdown + 메타데이터
```

- MinerU로 교과서 PDF를 Markdown으로 변환
- 수식 → LaTeX, 테이블 → HTML, 이미지 → 별도 파일로 추출
- 한글 콘텐츠에 대한 CJK 지원 활용

### Step 2: 의미 기반 청킹

```
Markdown → Docling HybridChunker → 512~1024 토큰 청크
```

- 챕터/섹션 단위로 의미 기반 분할
- Docling의 HybridChunker 참고 (문서 구조 존중 + 토큰 예산 준수)
- 각 청크에 메타데이터 부착 (챕터, 섹션, 페이지, 주제)

### Step 3: 임베딩 생성

```
청크 → MedCPT 또는 PubMedBERT → 벡터 임베딩
```

- 의료 도메인 특화 임베딩 모델 사용
- MedCPT (MedRAG 검증) 또는 PubMedBERT (Medical-RAG-LLM 검증)
- 일반 모델 대비 의료 용어 검색 정확도 대폭 향상

### Step 4: 벡터 저장

```
임베딩 + 메타데이터 → pgvector (PostgreSQL)
```

- pgvector에 임베딩 + 메타데이터 저장
- 하이브리드 인덱스 생성 (HNSW + GIN)
- 메타데이터 필터링 지원 (과목별, 챕터별 검색)

### Step 5: 하이브리드 검색

```
사용자 질문 → BM25 키워드 검색 + 벡터 유사도 검색 → 리랭킹
```

- BM25 (키워드 매칭) + 벡터 검색 (의미 유사도) 병합
- Cohere Reranker 또는 Cross-Encoder로 리랭킹
- 상위 5~10개 청크 선택

### Step 6: LLM 답변 생성

```
검색 결과 + 질문 → Claude API → 해설/답변 생성
```

- 검색된 컨텍스트를 Claude API에 전달
- 인용 근거와 함께 답변 생성
- 교과서 페이지/섹션 참조 정보 포함

---

## 9. 종합 비교표

### RAG 엔진 비교

| 프로젝트 | Stars | 벡터 DB | 퀴즈 생성 | 의료 특화 | 프론트엔드 | 핵심 강점 |
|---------|-------|---------|-----------|-----------|-----------|-----------|
| RAGFlow | 77.2K | Elasticsearch | X | X | React | 최고 수준 문서 파싱/청킹 |
| PrivateGPT | 57.2K | Qdrant/Chroma | X | X | - | 완전 오프라인 실행 |
| Quivr | 39.1K | PGVector/FAISS | X | X | React | 모듈형 RAG 프레임워크 |
| Kotaemon | 25.3K | 다양 (선택) | X | X | Gradio | 하이브리드 RAG + GraphRAG |
| PaperQA2 | 8.3K | Numpy/외부 | X | 학술 | CLI/API | 학술 논문 특화 에이전틱 RAG |
| Verba | 7.6K | Weaviate | X | X | 내장 | 간편 설치, 교차 참조 |
| MedRAG | 534 | FAISS | X | **O** | CLI | 의학 4대 코퍼스 통합 검색 |
| Medical-RAG-LLM | 38 | Qdrant | X | **O** | HTML | 완전 로컬 의료 RAG |

### PDF 파싱 도구 비교

| 도구 | Stars | 수식 처리 | 테이블 처리 | 한글 지원 | 출력 형식 | 프레임워크 통합 |
|------|-------|----------|-----------|----------|----------|--------------|
| MinerU | 58.3K | LaTeX 변환 | HTML 변환 | **우수** (CJK) | MD, JSON | API/CLI |
| Docling | 57.1K | DocTags | DataFrame | 지원 | MD, JSON, DocTags | LangChain, LlamaIndex |
| Marker | 33.4K | 포맷팅 | 포맷팅 | 지원 | MD, JSON, HTML | CLI |
| RAG-Anything | 15.3K | **전용 프로세서** | **전용 프로세서** | MinerU 내장 | GraphRAG | API |

### 퀴즈/문제 생성 비교

| 프로젝트 | AI 문제 생성 | RAG 기반 | Next.js | PWA | DB 스키마 |
|---------|------------|---------|---------|-----|----------|
| AI-Quiz-Generator (Oussama) | O | O | **O** | X | ChromaDB |
| GenQuest-RAG | O | O | X | X | Weaviate |
| QuizGen-RAG | O | O | X | X | LlamaIndex |
| Medha AI | O | O | X | X | MongoDB |
| quizmify | O | X | **O** | X | Prisma |
| Quiz-management | X | X | **O** | X | **Prisma+PostgreSQL** |
| quiz-app-pwa | X | X | X | **O** | - |
| next-pwa-template | X | X | **O** | **O** | IndexedDB |

---

## 부록: 핵심 참고 리소스

- [RAG Techniques](https://github.com/NirDiamant/RAG_Techniques) (26.5K stars) — RAG 기법 종합 레퍼런스
- [OpenClaw Medical Skills](https://github.com/FreedomIntelligence/OpenClaw-Medical-Skills) (1.9K stars) — USMLE 스킬 포함
- [Top 10 RAG Frameworks on GitHub (2026)](https://florinelchis.medium.com/top-10-rag-frameworks-on-github-by-stars-january-2026-e6edff1e0d91)
- [Best Open-Source PDF-to-Markdown Tools (2026)](https://themenonlab.blog/blog/best-open-source-pdf-to-markdown-tools-2026)
