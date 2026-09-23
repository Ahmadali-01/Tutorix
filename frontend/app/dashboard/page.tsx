"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import Sidebar from "@/components/Sidebar";
import {
  agents,
  analytics,
  auth,
  courses,
  getToken,
  questions,
  rag,
  clearToken,
} from "@/lib/api";

type Tab = "chat" | "questions" | "curriculum" | "tools" | "analytics";

export default function Dashboard() {
  const router = useRouter();
  const [tab, setTab] = useState<Tab>("chat");
  const [user, setUser] = useState<any>(null);
  const [coursesList, setCoursesList] = useState<any[]>([]);
  const [selectedCourse, setSelectedCourse] = useState<string>("");

  useEffect(() => {
    if (!getToken()) {
      router.push("/");
      return;
    }
    auth.me().then(setUser).catch(() => {
      clearToken();
      router.push("/");
    });
    courses
      .list()
      .then((list) => {
        setCoursesList(list);
        if (list[0]) setSelectedCourse(list[0].id);
      })
      .catch(() => {});
  }, [router]);

  function logout() {
    clearToken();
    router.push("/");
  }

  return (
    <div className="min-h-screen flex bg-slate-100">
      <Sidebar
        active={tab}
        onChange={setTab}
        email={user?.email || ""}
        onLogout={logout}
      />
      <main className="flex-1 overflow-y-auto">
        <div className="max-w-6xl mx-auto p-8">
          <div className="bg-white rounded-2xl shadow-sm border border-slate-200 p-8">
            {tab === "chat" && (
              <ChatTab
                courses={coursesList}
                selectedCourse={selectedCourse}
                setSelectedCourse={setSelectedCourse}
              />
            )}
            {tab === "questions" && <QuestionsTab selectedCourse={selectedCourse} />}
            {tab === "curriculum" && <CurriculumTab />}
            {tab === "tools" && <ToolsTab />}
            {tab === "analytics" && <AnalyticsTab selectedCourse={selectedCourse} />}
          </div>
        </div>
      </main>
    </div>
  );
}

function ChatTab({ courses, selectedCourse, setSelectedCourse }: any) {
  const [query, setQuery] = useState("");
  const [messages, setMessages] = useState<any[]>([]);
  const [loading, setLoading] = useState(false);

  async function send(e: React.FormEvent) {
    e.preventDefault();
    if (!query.trim()) return;
    const q = query;
    setQuery("");
    setMessages((m) => [...m, { role: "user", text: q }]);
    setLoading(true);
    try {
      const res: any = await rag.query(q, selectedCourse || undefined);
      setMessages((m) => [
        ...m,
        { role: "ai", text: res.answer, sources: res.sources },
      ]);
    } catch (err: any) {
      setMessages((m) => [...m, { role: "ai", text: "Error: " + err.message }]);
    } finally {
      setLoading(false);
    }
  }

  return (
    <div>
      <h2 className="text-2xl font-bold mb-1">AI Tutor</h2>
      <p className="text-slate-500 text-sm mb-6">
        Ask questions grounded in your course materials.
      </p>

      <select
        value={selectedCourse}
        onChange={(e) => setSelectedCourse(e.target.value)}
        className="mb-4 px-3 py-2 border border-slate-300 rounded-lg"
      >
        <option value="">All courses</option>
        {courses.map((c: any) => (
          <option key={c.id} value={c.id}>
            {c.title}
          </option>
        ))}
      </select>

      <div className="border border-slate-200 rounded-xl p-4 h-96 overflow-y-auto mb-4 bg-slate-50">
        {messages.length === 0 && (
          <p className="text-slate-400 text-center mt-32">
            Ask a question to get started.
          </p>
        )}
        {messages.map((m, i) => (
          <div key={i} className={`mb-4 ${m.role === "user" ? "text-right" : "text-left"}`}>
            <div
              className={`inline-block max-w-2xl px-4 py-3 rounded-2xl ${
                m.role === "user"
                  ? "bg-gradient-to-r from-indigo-600 to-purple-600 text-white"
                  : "bg-white border border-slate-200"
              }`}
            >
              <p className="whitespace-pre-wrap">{m.text}</p>
              {m.sources && m.sources.length > 0 && (
                <div className="mt-3 pt-3 border-t border-slate-200 text-xs text-slate-500">
                  <p className="font-semibold mb-1">Sources:</p>
                  {m.sources.map((s: any, j: number) => (
                    <p key={j}>• score {s.score} — {s.preview?.slice(0, 80)}...</p>
                  ))}
                </div>
              )}
            </div>
          </div>
        ))}
        {loading && <p className="text-slate-400">Tutorix is thinking...</p>}
      </div>

      <form onSubmit={send} className="flex gap-2">
        <input
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          placeholder="Ask anything..."
          className="flex-1 px-4 py-3 border border-slate-300 rounded-lg focus:ring-2 focus:ring-indigo-500 outline-none"
        />
        <button
          type="submit"
          disabled={loading}
          className="px-6 py-3 bg-gradient-to-r from-indigo-600 to-purple-600 text-white rounded-lg font-semibold hover:opacity-90 disabled:opacity-50"
        >
          Send
        </button>
      </form>
    </div>
  );
}

function QuestionsTab({ selectedCourse }: any) {
  const [topic, setTopic] = useState("machine learning basics");
  const [difficulty, setDifficulty] = useState("easy");
  const [count, setCount] = useState(3);
  const [type, setType] = useState("mcq");
  const [items, setItems] = useState<any[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  async function generate() {
    setError("");
    setLoading(true);
    try {
      const res: any = await questions.generate({
        course_id: selectedCourse,
        topic,
        difficulty,
        count,
        question_type: type,
      });
      setItems(res.questions || []);
    } catch (err: any) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  }

  return (
    <div>
      <h2 className="text-2xl font-bold mb-1">Generate Questions</h2>
      <p className="text-slate-500 text-sm mb-6">
        Create MCQs, short answers, and more — grounded in your materials.
      </p>

      {!selectedCourse && (
        <p className="text-red-600 mb-4">Select a course first (AI Tutor tab).</p>
      )}

      <div className="grid grid-cols-1 md:grid-cols-4 gap-3 mb-4">
        <input
          value={topic}
          onChange={(e) => setTopic(e.target.value)}
          placeholder="Topic"
          className="px-3 py-2 border border-slate-300 rounded-lg"
        />
        <select
          value={difficulty}
          onChange={(e) => setDifficulty(e.target.value)}
          className="px-3 py-2 border border-slate-300 rounded-lg"
        >
          <option>easy</option>
          <option>medium</option>
          <option>hard</option>
        </select>
        <input
          type="number"
          value={count}
          onChange={(e) => setCount(Number(e.target.value))}
          className="px-3 py-2 border border-slate-300 rounded-lg"
        />
        <select
          value={type}
          onChange={(e) => setType(e.target.value)}
          className="px-3 py-2 border border-slate-300 rounded-lg"
        >
          <option value="mcq">MCQ</option>
          <option value="short_answer">Short Answer</option>
          <option value="true_false">True/False</option>
        </select>
      </div>

      <button
        onClick={generate}
        disabled={loading || !selectedCourse}
        className="mb-6 px-6 py-3 bg-gradient-to-r from-indigo-600 to-purple-600 text-white rounded-lg font-semibold hover:opacity-90 disabled:opacity-50"
      >
        {loading ? "Generating..." : "Generate"}
      </button>

      {error && <p className="text-red-600 mb-4">{error}</p>}

      <div className="space-y-4">
        {items.map((q, i) => (
          <div key={i} className="border border-slate-200 rounded-xl p-4">
            <p className="font-semibold mb-2">
              {i + 1}. {q.prompt}
            </p>
            {q.options && (
              <div className="space-y-1 mb-2">
                {Object.entries(q.options).map(([k, v]: any) => (
                  <p key={k} className={k === q.answer ? "text-green-600 font-medium" : ""}>
                    {k}. {v}
                  </p>
                ))}
              </div>
            )}
            <p className="text-sm text-slate-500">
              <span className="font-semibold">Answer:</span> {q.answer}
            </p>
            <p className="text-sm text-slate-500 mt-1">
              <span className="font-semibold">Why:</span> {q.explanation}
            </p>
          </div>
        ))}
      </div>
    </div>
  );
}

function CurriculumTab() {
  const [subject, setSubject] = useState("Introduction to Python Programming");
  const [grade, setGrade] = useState("Grade 10");
  const [weeks, setWeeks] = useState(3);
  const [data, setData] = useState<any>(null);
  const [loading, setLoading] = useState(false);

  async function generate() {
    setLoading(true);
    try {
      const res: any = await agents.curriculum(subject, grade, weeks);
      setData(res);
    } finally {
      setLoading(false);
    }
  }

  return (
    <div>
      <h2 className="text-2xl font-bold mb-1">Curriculum Planner</h2>
      <p className="text-slate-500 text-sm mb-6">
        Four AI agents plan modules, objectives, lessons, and assessments.
      </p>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-3 mb-4">
        <input
          value={subject}
          onChange={(e) => setSubject(e.target.value)}
          className="px-3 py-2 border border-slate-300 rounded-lg"
          placeholder="Subject"
        />
        <input
          value={grade}
          onChange={(e) => setGrade(e.target.value)}
          className="px-3 py-2 border border-slate-300 rounded-lg"
          placeholder="Grade level"
        />
        <input
          type="number"
          value={weeks}
          onChange={(e) => setWeeks(Number(e.target.value))}
          className="px-3 py-2 border border-slate-300 rounded-lg"
        />
      </div>

      <button
        onClick={generate}
        disabled={loading}
        className="mb-6 px-6 py-3 bg-gradient-to-r from-indigo-600 to-purple-600 text-white rounded-lg font-semibold hover:opacity-90 disabled:opacity-50"
      >
        {loading ? "Agents working..." : "Generate Curriculum"}
      </button>

      {data && (
        <div className="space-y-4">
          {data.modules.map((m: any, i: number) => {
            const obj = data.objectives.find((o: any) => o.week === m.week);
            const les = data.lessons.find((l: any) => l.week === m.week);
            const asm = data.assessments.find((a: any) => a.week === m.week);
            return (
              <div key={i} className="border border-slate-200 rounded-xl p-5">
                <h3 className="font-bold text-lg mb-1">
                  Week {m.week}: {m.title}
                </h3>
                <p className="text-slate-600 text-sm mb-3">{m.summary}</p>

                {obj && (
                  <div className="mb-3">
                    <p className="font-semibold text-sm">Objectives:</p>
                    <ul className="list-disc list-inside text-sm text-slate-700">
                      {obj.objectives.map((o: string, j: number) => (
                        <li key={j}>{o}</li>
                      ))}
                    </ul>
                  </div>
                )}

                {les && (
                  <div className="mb-3">
                    <p className="font-semibold text-sm">Lesson topics:</p>
                    <ul className="list-disc list-inside text-sm text-slate-700">
                      {les.topics.map((t: string, j: number) => (
                        <li key={j}>{t}</li>
                      ))}
                    </ul>
                    <p className="text-sm text-slate-600 mt-1">
                      <span className="font-semibold">Activity:</span> {les.activity}
                    </p>
                  </div>
                )}

                {asm && (
                  <div className="text-sm bg-indigo-50 p-3 rounded-lg">
                    <p>
                      <span className="font-semibold">Quiz:</span> {asm.quiz_topic}
                    </p>
                    <p>
                      <span className="font-semibold">Project:</span> {asm.project}
                    </p>
                  </div>
                )}
              </div>
            );
          })}
        </div>
      )}
    </div>
  );
}

function ToolsTab() {
  const [msg, setMsg] = useState("What is 42 * 17?");
  const [messages, setMessages] = useState<any[]>([]);
  const [loading, setLoading] = useState(false);

  async function send(e: React.FormEvent) {
    e.preventDefault();
    const q = msg;
    setMsg("");
    setMessages((m) => [...m, { role: "user", text: q }]);
    setLoading(true);
    try {
      const res: any = await agents.toolChat(q);
      setMessages((m) => [
        ...m,
        { role: "ai", text: res.reply, tools: res.tools_used },
      ]);
    } catch (err: any) {
      setMessages((m) => [...m, { role: "ai", text: "Error: " + err.message }]);
    } finally {
      setLoading(false);
    }
  }

  return (
    <div>
      <h2 className="text-2xl font-bold mb-1">Agent Tools</h2>
      <p className="text-slate-500 text-sm mb-6">
        The AI picks the right tool automatically — calculator, time, question search, or student stats.
      </p>

      <div className="border border-slate-200 rounded-xl p-4 h-80 overflow-y-auto mb-4 bg-slate-50">
        {messages.length === 0 && (
          <p className="text-slate-400 text-center mt-32">
            Ask something like "What is 25 * 4?"
          </p>
        )}
        {messages.map((m, i) => (
          <div key={i} className={`mb-4 ${m.role === "user" ? "text-right" : "text-left"}`}>
            <div
              className={`inline-block max-w-2xl px-4 py-3 rounded-2xl whitespace-pre-wrap ${
                m.role === "user"
                  ? "bg-gradient-to-r from-indigo-600 to-purple-600 text-white"
                  : "bg-white border border-slate-200"
              }`}
            >
              {m.text}
              {m.tools && m.tools.length > 0 && (
                <div className="mt-2 pt-2 border-t border-slate-200 text-xs text-slate-500">
                  Tools used:{" "}
                  {m.tools.map((t: any, j: number) => (
                    <span key={j} className="font-mono bg-slate-100 px-1 rounded">
                      {t.tool}
                    </span>
                  ))}
                </div>
              )}
            </div>
          </div>
        ))}
        {loading && <p className="text-slate-400">Thinking...</p>}
      </div>

      <form onSubmit={send} className="flex gap-2">
        <input
          value={msg}
          onChange={(e) => setMsg(e.target.value)}
          className="flex-1 px-4 py-3 border border-slate-300 rounded-lg focus:ring-2 focus:ring-indigo-500 outline-none"
        />
        <button
          type="submit"
          disabled={loading}
          className="px-6 py-3 bg-gradient-to-r from-indigo-600 to-purple-600 text-white rounded-lg font-semibold hover:opacity-90 disabled:opacity-50"
        >
          Ask
        </button>
      </form>
    </div>
  );
}

function AnalyticsTab({ selectedCourse }: any) {
  const [data, setData] = useState<any>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  async function load() {
    if (!selectedCourse) return;
    setLoading(true);
    setError("");
    try {
      const res = await analytics.course(selectedCourse);
      setData(res);
    } catch (err: any) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    load();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [selectedCourse]);

  return (
    <div>
      <h2 className="text-2xl font-bold mb-1">Analytics</h2>
      <p className="text-slate-500 text-sm mb-6">
        Live learning analytics for the selected course.
      </p>

      {!selectedCourse && (
        <p className="text-slate-500">Select a course from the AI Tutor tab.</p>
      )}
      {loading && <p>Loading...</p>}
      {error && <p className="text-red-600">{error}</p>}

      {data && (
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <div className="bg-gradient-to-br from-indigo-500 to-purple-600 text-white rounded-xl p-6">
            <p className="text-sm opacity-80">Total Events</p>
            <p className="text-4xl font-bold">{data.total_events}</p>
          </div>
          <div className="bg-gradient-to-br from-emerald-500 to-teal-600 text-white rounded-xl p-6">
            <p className="text-sm opacity-80">Submissions</p>
            <p className="text-4xl font-bold">{data.total_submissions}</p>
          </div>
          <div className="bg-gradient-to-br from-amber-500 to-orange-600 text-white rounded-xl p-6">
            <p className="text-sm opacity-80">Event Types</p>
            <p className="text-4xl font-bold">
              {Object.keys(data.event_breakdown || {}).length}
            </p>
          </div>

          <div className="md:col-span-3 border border-slate-200 rounded-xl p-5">
            <h3 className="font-bold mb-3">Event Breakdown</h3>
            {Object.entries(data.event_breakdown || {}).map(([k, v]: any) => (
              <div key={k} className="flex items-center gap-3 mb-2">
                <span className="w-40 text-sm">{k}</span>
                <div className="flex-1 bg-slate-100 rounded-full h-3 overflow-hidden">
                  <div
                    className="bg-gradient-to-r from-indigo-600 to-purple-600 h-full"
                    style={{
                      width: `${
                        (v / Math.max(...(Object.values(data.event_breakdown) as number[]))) * 100
                      }%`,
                    }}
                  />
                </div>
                <span className="text-sm font-semibold w-10 text-right">{v}</span>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}
