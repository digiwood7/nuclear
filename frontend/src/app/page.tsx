"use client";

import { useState } from "react";
import QuizTab from "@/components/QuizTab";
import AskTab from "@/components/AskTab";

type Tab = "quiz" | "ask";

export default function Home() {
  const [tab, setTab] = useState<Tab>("quiz");

  return (
    <div className="flex flex-col h-dvh">
      {/* 헤더 */}
      <header className="bg-[var(--primary)] text-white px-4 py-3 flex-shrink-0">
        <h1 className="text-lg font-bold text-center tracking-tight">
          핵의학 국시 대비
        </h1>
        <p className="text-xs text-blue-200 text-center mt-0.5">
          Nuclear Medicine Board Exam Prep
        </p>
      </header>

      {/* 콘텐츠 */}
      <main className="flex-1 overflow-y-auto">
        {tab === "quiz" && <QuizTab />}
        {tab === "ask" && <AskTab />}
      </main>

      {/* 하단 탭 바 */}
      <nav className="flex-shrink-0 bg-white border-t border-gray-200 flex">
        <button
          onClick={() => setTab("quiz")}
          className={`flex-1 py-3 text-center text-sm font-medium transition-colors ${
            tab === "quiz"
              ? "text-[var(--primary)] border-t-2 border-[var(--primary)]"
              : "text-gray-500"
          }`}
        >
          <div className="text-lg mb-0.5">{tab === "quiz" ? "\u2705" : "\u2753"}</div>
          문제 풀기
        </button>
        <button
          onClick={() => setTab("ask")}
          className={`flex-1 py-3 text-center text-sm font-medium transition-colors ${
            tab === "ask"
              ? "text-[var(--primary)] border-t-2 border-[var(--primary)]"
              : "text-gray-500"
          }`}
        >
          <div className="text-lg mb-0.5">{tab === "ask" ? "\uD83D\uDCD6" : "\uD83D\uDCAC"}</div>
          질문하기
        </button>
      </nav>
    </div>
  );
}
