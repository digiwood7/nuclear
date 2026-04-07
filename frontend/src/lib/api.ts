const API_BASE = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

export interface QuizChoice {
  number: number;
  text: string;
}

export interface QuizQuestion {
  id: number;
  question: string;
  choices: QuizChoice[];
  answer: number;
  explanation: string;
  page_ref: string;
}

export interface QuizResponse {
  questions: QuizQuestion[];
  topic: string;
}

export interface RAGResponse {
  answer: string;
  question: string;
}

// 문제 생성 API
export async function generateQuiz(
  topic: string = "",
  count: number = 5,
  difficulty: string = "중"
): Promise<QuizResponse> {
  const res = await fetch(`${API_BASE}/api/quiz/generate`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ topic, count, difficulty }),
  });

  if (!res.ok) {
    const err = await res.json().catch(() => ({ detail: "서버 오류" }));
    throw new Error(err.detail || `HTTP ${res.status}`);
  }

  return res.json();
}

// RAG 질의 API
export async function queryRAG(question: string): Promise<RAGResponse> {
  const res = await fetch(`${API_BASE}/api/rag/query`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ question, mode: "mix" }),
  });

  if (!res.ok) {
    const err = await res.json().catch(() => ({ detail: "서버 오류" }));
    throw new Error(err.detail || `HTTP ${res.status}`);
  }

  return res.json();
}

// 서버 상태 확인
export async function checkHealth(): Promise<boolean> {
  try {
    const res = await fetch(`${API_BASE}/api/health`);
    return res.ok;
  } catch {
    return false;
  }
}
