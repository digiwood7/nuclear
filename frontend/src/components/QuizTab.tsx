"use client";

import { useState, useCallback } from "react";
import { generateQuiz, type QuizQuestion } from "@/lib/api";

const TOPICS = [
  { label: "전체 범위", value: "" },
  { label: "핵의학 개론", value: "핵의학 정의와 개론" },
  { label: "방사성 붕괴", value: "방사성 붕괴와 반감기" },
  { label: "방사성의약품", value: "방사성의약품" },
  { label: "감마카메라/SPECT", value: "감마카메라와 SPECT" },
  { label: "PET", value: "PET 양전자방출단층촬영" },
  { label: "방사선 방호", value: "방사선 방호와 안전관리" },
];

const DIFFICULTIES = ["하", "중", "상"];

export default function QuizTab() {
  const [phase, setPhase] = useState<"setup" | "solving" | "result">("setup");
  const [topic, setTopic] = useState("");
  const [difficulty, setDifficulty] = useState("중");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [questions, setQuestions] = useState<QuizQuestion[]>([]);
  const [currentIdx, setCurrentIdx] = useState(0);
  const [selected, setSelected] = useState<number | null>(null);
  const [showExplanation, setShowExplanation] = useState(false);
  const [answers, setAnswers] = useState<Record<number, number>>({});
  const [score, setScore] = useState(0);

  const startQuiz = useCallback(async () => {
    setLoading(true);
    setError("");
    try {
      const data = await generateQuiz(topic, 5, difficulty);
      setQuestions(data.questions);
      setCurrentIdx(0);
      setSelected(null);
      setShowExplanation(false);
      setAnswers({});
      setScore(0);
      setPhase("solving");
    } catch (e) {
      setError(e instanceof Error ? e.message : "문제 생성 실패");
    } finally {
      setLoading(false);
    }
  }, [topic, difficulty]);

  const selectAnswer = (choiceNum: number) => {
    if (showExplanation) return;
    setSelected(choiceNum);
  };

  const submitAnswer = () => {
    if (selected === null) return;
    const q = questions[currentIdx];
    const isCorrect = selected === q.answer;
    if (isCorrect) setScore((s) => s + 1);
    setAnswers((prev) => ({ ...prev, [currentIdx]: selected }));
    setShowExplanation(true);
  };

  const nextQuestion = () => {
    if (currentIdx + 1 >= questions.length) {
      setPhase("result");
    } else {
      setCurrentIdx((i) => i + 1);
      setSelected(null);
      setShowExplanation(false);
    }
  };

  // --- 설정 화면 ---
  if (phase === "setup") {
    return (
      <div className="p-4 space-y-5">
        <div className="bg-white rounded-xl p-4 shadow-sm border border-gray-100">
          <h2 className="font-bold text-base mb-3">출제 주제</h2>
          <div className="flex flex-wrap gap-2">
            {TOPICS.map((t) => (
              <button
                key={t.value}
                onClick={() => setTopic(t.value)}
                className={`px-3 py-1.5 rounded-full text-sm transition-colors ${
                  topic === t.value
                    ? "bg-[var(--primary)] text-white"
                    : "bg-gray-100 text-gray-700 hover:bg-gray-200"
                }`}
              >
                {t.label}
              </button>
            ))}
          </div>
        </div>

        <div className="bg-white rounded-xl p-4 shadow-sm border border-gray-100">
          <h2 className="font-bold text-base mb-3">난이도</h2>
          <div className="flex gap-3">
            {DIFFICULTIES.map((d) => (
              <button
                key={d}
                onClick={() => setDifficulty(d)}
                className={`flex-1 py-2.5 rounded-lg text-sm font-medium transition-colors ${
                  difficulty === d
                    ? "bg-[var(--primary)] text-white"
                    : "bg-gray-100 text-gray-700 hover:bg-gray-200"
                }`}
              >
                {d === "하" ? "기초" : d === "중" ? "보통" : "심화"}
              </button>
            ))}
          </div>
        </div>

        {error && (
          <div className="bg-red-50 border border-red-200 rounded-lg p-3 text-red-700 text-sm">
            {error}
          </div>
        )}

        <button
          onClick={startQuiz}
          disabled={loading}
          className="w-full bg-[var(--primary)] text-white py-3.5 rounded-xl font-bold text-base transition-opacity disabled:opacity-50"
        >
          {loading ? (
            <span className="flex items-center justify-center gap-2">
              <span className="w-4 h-4 border-2 border-white/30 border-t-white rounded-full animate-spin" />
              문제 생성 중...
            </span>
          ) : (
            "문제 풀기 시작"
          )}
        </button>
      </div>
    );
  }

  // --- 문제 풀이 화면 ---
  if (phase === "solving") {
    const q = questions[currentIdx];
    if (!q) return null;

    return (
      <div className="p-4 space-y-4">
        {/* 진행률 바 */}
        <div className="flex items-center gap-3">
          <div className="flex-1 bg-gray-200 rounded-full h-2">
            <div
              className="bg-[var(--primary)] h-2 rounded-full transition-all"
              style={{ width: `${((currentIdx + 1) / questions.length) * 100}%` }}
            />
          </div>
          <span className="text-sm text-gray-500 font-medium">
            {currentIdx + 1}/{questions.length}
          </span>
        </div>

        {/* 문제 */}
        <div className="bg-white rounded-xl p-4 shadow-sm border border-gray-100">
          <p className="text-sm text-[var(--primary)] font-semibold mb-2">
            Q{q.id}.
          </p>
          <p className="text-[15px] leading-relaxed font-medium">{q.question}</p>
        </div>

        {/* 보기 */}
        <div className="space-y-2">
          {q.choices.map((c) => {
            let choiceStyle = "bg-white border-gray-200 text-gray-800";

            if (showExplanation) {
              if (c.number === q.answer) {
                choiceStyle = "bg-green-50 border-[var(--success)] text-green-800";
              } else if (c.number === selected && c.number !== q.answer) {
                choiceStyle = "bg-red-50 border-[var(--danger)] text-red-800";
              } else {
                choiceStyle = "bg-gray-50 border-gray-200 text-gray-400";
              }
            } else if (selected === c.number) {
              choiceStyle = "bg-blue-50 border-[var(--primary)] text-[var(--primary)]";
            }

            return (
              <button
                key={c.number}
                onClick={() => selectAnswer(c.number)}
                disabled={showExplanation}
                className={`w-full text-left p-3.5 rounded-xl border-2 transition-all text-sm leading-relaxed ${choiceStyle}`}
              >
                <span className="font-bold mr-2">{c.number}.</span>
                {c.text}
              </button>
            );
          })}
        </div>

        {/* 해설 */}
        {showExplanation && (
          <div className="bg-amber-50 border border-amber-200 rounded-xl p-4">
            <p className="text-sm font-bold text-amber-800 mb-1">해설</p>
            <p className="text-sm text-amber-900 leading-relaxed">
              {q.explanation}
            </p>
            {q.page_ref && (
              <p className="text-xs text-amber-600 mt-2">
                참조: {q.page_ref}
              </p>
            )}
          </div>
        )}

        {/* 제출 / 다음 버튼 */}
        {!showExplanation ? (
          <button
            onClick={submitAnswer}
            disabled={selected === null}
            className="w-full bg-[var(--primary)] text-white py-3 rounded-xl font-bold disabled:opacity-40"
          >
            정답 확인
          </button>
        ) : (
          <button
            onClick={nextQuestion}
            className="w-full bg-[var(--primary)] text-white py-3 rounded-xl font-bold"
          >
            {currentIdx + 1 < questions.length ? "다음 문제" : "결과 보기"}
          </button>
        )}
      </div>
    );
  }

  // --- 결과 화면 ---
  return (
    <div className="p-4 space-y-4">
      <div className="bg-white rounded-xl p-6 shadow-sm border border-gray-100 text-center">
        <div className="text-5xl mb-3">
          {score >= 4 ? "\uD83C\uDF89" : score >= 3 ? "\uD83D\uDC4D" : "\uD83D\uDCDA"}
        </div>
        <h2 className="text-2xl font-bold mb-1">
          {score} / {questions.length}
        </h2>
        <p className="text-gray-500 text-sm">
          {score === questions.length
            ? "완벽합니다!"
            : score >= 4
              ? "잘했습니다!"
              : score >= 3
                ? "조금 더 공부하면 합격!"
                : "오답 해설을 꼼꼼히 확인하세요"}
        </p>
        <div className="mt-4 flex justify-center gap-1">
          {questions.map((q, i) => (
            <div
              key={i}
              className={`w-8 h-8 rounded-full flex items-center justify-center text-xs font-bold ${
                answers[i] === q.answer
                  ? "bg-green-100 text-green-700"
                  : "bg-red-100 text-red-700"
              }`}
            >
              {i + 1}
            </div>
          ))}
        </div>
      </div>

      {/* 오답 리뷰 */}
      {questions
        .filter((q, i) => answers[i] !== q.answer)
        .map((q) => (
          <div
            key={q.id}
            className="bg-white rounded-xl p-4 shadow-sm border border-red-100"
          >
            <p className="text-sm font-bold text-red-600 mb-1">
              Q{q.id} - 오답
            </p>
            <p className="text-sm mb-2">{q.question}</p>
            <p className="text-xs text-green-700 font-medium mb-1">
              정답: {q.answer}번 -{" "}
              {q.choices.find((c) => c.number === q.answer)?.text}
            </p>
            <p className="text-xs text-gray-600">{q.explanation}</p>
          </div>
        ))}

      <button
        onClick={() => setPhase("setup")}
        className="w-full bg-[var(--primary)] text-white py-3 rounded-xl font-bold"
      >
        다시 풀기
      </button>
    </div>
  );
}
