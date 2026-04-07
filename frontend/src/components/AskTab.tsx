"use client";

import { useState, useRef, useEffect } from "react";
import { queryRAG } from "@/lib/api";

interface Message {
  role: "user" | "assistant";
  content: string;
  timestamp: Date;
}

const SUGGESTED = [
  "핵의학의 정의는?",
  "SPECT와 PET의 차이점",
  "99mTc의 특성",
  "유효반감기 계산법",
  "감마카메라 원리",
];

export default function AskTab() {
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);
  const bottomRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  const sendMessage = async (question?: string) => {
    const q = question || input.trim();
    if (!q || loading) return;

    const userMsg: Message = {
      role: "user",
      content: q,
      timestamp: new Date(),
    };
    setMessages((prev) => [...prev, userMsg]);
    setInput("");
    setLoading(true);

    try {
      const data = await queryRAG(q);
      const assistantMsg: Message = {
        role: "assistant",
        content: data.answer,
        timestamp: new Date(),
      };
      setMessages((prev) => [...prev, assistantMsg]);
    } catch (e) {
      const errorMsg: Message = {
        role: "assistant",
        content: `오류가 발생했습니다: ${e instanceof Error ? e.message : "알 수 없는 오류"}`,
        timestamp: new Date(),
      };
      setMessages((prev) => [...prev, errorMsg]);
    } finally {
      setLoading(false);
    }
  };

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      sendMessage();
    }
  };

  // --- 빈 화면 (추천 질문) ---
  if (messages.length === 0) {
    return (
      <div className="flex flex-col h-full">
        <div className="flex-1 p-4 flex flex-col justify-center">
          <div className="text-center mb-6">
            <div className="text-4xl mb-2">{"\uD83E\uDDE0"}</div>
            <h2 className="text-lg font-bold text-gray-800">
              무엇이든 물어보세요
            </h2>
            <p className="text-sm text-gray-500 mt-1">
              핵의학 교과서 기반 AI 학습 도우미
            </p>
          </div>
          <div className="space-y-2">
            {SUGGESTED.map((q) => (
              <button
                key={q}
                onClick={() => sendMessage(q)}
                className="w-full text-left bg-white rounded-xl p-3.5 border border-gray-200 text-sm text-gray-700 hover:border-[var(--primary)] hover:text-[var(--primary)] transition-colors"
              >
                {q}
              </button>
            ))}
          </div>
        </div>

        {/* 입력창 */}
        <div className="flex-shrink-0 p-3 bg-white border-t border-gray-200">
          <div className="flex gap-2">
            <input
              type="text"
              value={input}
              onChange={(e) => setInput(e.target.value)}
              onKeyDown={handleKeyDown}
              placeholder="질문을 입력하세요..."
              className="flex-1 bg-gray-100 rounded-xl px-4 py-2.5 text-sm outline-none focus:ring-2 focus:ring-[var(--primary)]/30"
            />
            <button
              onClick={() => sendMessage()}
              disabled={!input.trim()}
              className="bg-[var(--primary)] text-white px-4 rounded-xl font-medium text-sm disabled:opacity-40"
            >
              전송
            </button>
          </div>
        </div>
      </div>
    );
  }

  // --- 채팅 화면 ---
  return (
    <div className="flex flex-col h-full">
      <div className="flex-1 overflow-y-auto p-4 space-y-3">
        {messages.map((msg, i) => (
          <div
            key={i}
            className={`flex ${msg.role === "user" ? "justify-end" : "justify-start"}`}
          >
            <div
              className={`max-w-[85%] rounded-2xl px-4 py-3 text-sm leading-relaxed ${
                msg.role === "user"
                  ? "bg-[var(--primary)] text-white rounded-br-sm"
                  : "bg-white border border-gray-200 text-gray-800 rounded-bl-sm"
              }`}
            >
              {msg.role === "assistant" ? (
                <div className="whitespace-pre-wrap">
                  {formatAnswer(msg.content)}
                </div>
              ) : (
                msg.content
              )}
            </div>
          </div>
        ))}

        {loading && (
          <div className="flex justify-start">
            <div className="bg-white border border-gray-200 rounded-2xl rounded-bl-sm px-4 py-3">
              <div className="flex gap-1">
                <span className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" />
                <span className="w-2 h-2 bg-gray-400 rounded-full animate-bounce [animation-delay:0.1s]" />
                <span className="w-2 h-2 bg-gray-400 rounded-full animate-bounce [animation-delay:0.2s]" />
              </div>
            </div>
          </div>
        )}
        <div ref={bottomRef} />
      </div>

      {/* 입력창 */}
      <div className="flex-shrink-0 p-3 bg-white border-t border-gray-200">
        <div className="flex gap-2">
          <input
            type="text"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={handleKeyDown}
            placeholder="질문을 입력하세요..."
            className="flex-1 bg-gray-100 rounded-xl px-4 py-2.5 text-sm outline-none focus:ring-2 focus:ring-[var(--primary)]/30"
          />
          <button
            onClick={() => sendMessage()}
            disabled={!input.trim() || loading}
            className="bg-[var(--primary)] text-white px-4 rounded-xl font-medium text-sm disabled:opacity-40"
          >
            전송
          </button>
        </div>
      </div>
    </div>
  );
}

/** RAG 응답 텍스트를 간단히 포맷팅 */
function formatAnswer(text: string): string {
  return text
    .replace(/### References/g, "\n--- 참고자료 ---")
    .replace(/\*\*(.*?)\*\*/g, "$1")
    .replace(/\[reference_id:.*?\]/g, "");
}
