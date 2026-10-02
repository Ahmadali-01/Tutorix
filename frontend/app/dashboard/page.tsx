"use client";
import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { motion, AnimatePresence } from "framer-motion";
import { Send, Sparkles, Loader2, BookOpen, Calculator, BarChart3, MessageSquare, Wrench, Zap, TrendingUp, Users, Activity } from "lucide-react";
import Sidebar from "@/components/Sidebar";
import ThemeToggle from "@/components/ThemeToggle";
import { agents, analytics, auth, courses, getToken, questions, rag, clearToken } from "@/lib/api";

type Tab = "chat" | "questions" | "curriculum" | "tools" | "analytics";

export default function Dashboard() {
  const router = useRouter();
  const [tab, setTab] = useState<Tab>("chat");
  const [user, setUser] = useState<any>(null);
  const [coursesList, setCoursesList] = useState<any[]>([]);
  const [selectedCourse, setSelectedCourse] = useState<string>("");

  useEffect(() => {
    if (!getToken()) { router.push("/"); return; }
    auth.me().then(setUser).catch(() => { clearToken(); router.push("/"); });
    courses.list().then((list) => { setCoursesList(list); if (list[0]) setSelectedCourse(list[0].id); }).catch(() => {});
  }, [router]);

  function logout() { clearToken(); router.push("/"); }

  const titles: Record<Tab, string> = {
    chat: "AI Tutor", questions: "Generate Questions", curriculum: "Curriculum Planner",
    tools: "Agent Tools", analytics: "Analytics",
  };

  return (
    <div className="min-h-screen flex bg-stone-50 dark:bg-stone-950">
      <Sidebar active={tab} onChange={setTab} email={user?.email || ""} onLogout={logout} />
      <main className="flex-1 overflow-y-auto">
        <div className="sticky top-0 z-30 glass border-b border-[#1b3a4b]/50 dark:border-stone-800/50 px-8 py-4 flex items-center justify-between">
          <div>
            <h2 className="text-2xl font-black tracking-tight">{titles[tab]}</h2>
            <p className="text-xs text-stone-500 dark:text-stone-400">Tutorix · AI Education Intelligence Platform</p>
          </div>
          <div className="flex items-center gap-3">
            <div className="hidden md:flex items-center gap-2 px-3 py-1.5 rounded-full bg-[#ff6d00]/10 dark:bg-[#ff6d00]/15 border border-[#ff6d00]/30 dark:border-[#7b2cbf]/40">
              <span className="w-2 h-2 rounded-full bg-[#ff6d00]/10 animate-pulse" />
              <span className="text-xs font-medium text-[#ff6d00] dark:text-[#ff9e00]">Live</span>
            </div>
            <ThemeToggle />
          </div>
        </div>

        <div className="max-w-6xl mx-auto p-8">
          <AnimatePresence mode="wait">
            <motion.div
              key={tab}
              initial={{ opacity: 0, y: 12 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -12 }}
              transition={{ duration: 0.25 }}
            >
              {tab === "chat" && <ChatTab courses={coursesList} selectedCourse={selectedCourse} setSelectedCourse={setSelectedCourse} />}
              {tab === "questions" && <QuestionsTab selectedCourse={selectedCourse} />}
              {tab === "curriculum" && <CurriculumTab />}
              {tab === "tools" && <ToolsTab />}
              {tab === "analytics" && <AnalyticsTab selectedCourse={selectedCourse} />}
            </motion.div>
          </AnimatePresence>
        </div>
      </main>
    </div>
  );
}

function Stat({ icon: Icon, label, value, gradient }: any) {
  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }}
      whileHover={{ y: -4 }}
      className="card card-hover p-5 shimmer-sweep stat-float"
    >
      <div className={`w-10 h-10 rounded-xl ${gradient} flex items-center justify-center text-white mb-3`}>
        <Icon size={18} />
      </div>
      <p className="text-2xl font-black">{value}</p>
      <p className="text-xs text-stone-500 dark:text-stone-400 mt-1">{label}</p>
    </motion.div>
  );
}

function ChatTab({ courses, selectedCourse, setSelectedCourse }: any) {
  const [query, setQuery] = useState("");
  const [messages, setMessages] = useState<any[]>([]);
  const [loading, setLoading] = useState(false);

  async function send(e: React.FormEvent) {
    e.preventDefault();
    if (!query.trim()) return;
    const q = query; setQuery("");
    setMessages((m) => [...m, { role: "user", text: q }]);
    setLoading(true);
    try {
      const res: any = await rag.query(q, selectedCourse || undefined);
      setMessages((m) => [...m, { role: "ai", text: res.answer, sources: res.sources }]);
    } catch (err: any) {
      setMessages((m) => [...m, { role: "ai", text: "Error: " + err.message }]);
    } finally { setLoading(false); }
  }

  const suggestions = ["What is machine learning?", "Explain neural networks", "Give me an example of supervised learning"];

  return (
    <div className="space-y-6">
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <Stat icon={Zap} label="Powered by Gemini" value="3.6" gradient="gradient-bg" />
        <Stat icon={BookOpen} label="Grounded in your course" value="RAG" gradient="bg-gradient-to-br from-[#ff6d00] to-[#ff9e00]" />
        <Stat icon={Sparkles} label="Cited sources" value="100%" gradient="bg-gradient-to-br from-[#5a189a] to-[#9d4edd]" />
      </div>

      <div className="card p-6">
        <div className="flex items-center gap-3 mb-5">
          <div className="w-10 h-10 rounded-xl gradient-bg flex items-center justify-center text-white">
            <MessageSquare size={18} />
          </div>
          <div className="flex-1">
            <h3 className="font-bold">Ask your AI Tutor</h3>
            <p className="text-xs text-stone-500 dark:text-stone-400">Answers grounded in course materials with citations</p>
          </div>
          <select value={selectedCourse} onChange={(e) => setSelectedCourse(e.target.value)} className="input max-w-[200px]">
            <option value="">All courses</option>
            {courses.map((c: any) => <option key={c.id} value={c.id}>{c.title}</option>)}
          </select>
        </div>

        <div className="rounded-2xl border border-[#1b3a4b] dark:border-stone-800 p-4 h-96 overflow-y-auto mb-4 bg-stone-50/50 dark:bg-stone-900/40">
          {messages.length === 0 && (
            <div className="text-center mt-16">
              <div className="inline-flex w-16 h-16 rounded-2xl gradient-bg items-center justify-center text-white mb-4">
                <Sparkles size={28} />
              </div>
              <p className="font-semibold mb-1">Ask anything about your course</p>
              <p className="text-sm text-stone-500 dark:text-stone-400 mb-4">Try one of these:</p>
              <div className="flex flex-wrap justify-center gap-2">
                {suggestions.map((s) => (
                  <button key={s} onClick={() => setQuery(s)}
                    className="px-3 py-1.5 rounded-full text-xs border border-slate-300 dark:border-stone-700 hover:border-brand-500 hover:text-brand-500 transition">
                    {s}
                  </button>
                ))}
              </div>
            </div>
          )}
          {messages.map((m, i) => (
            <motion.div key={i} initial={{ opacity: 0, y: 8 }} animate={{ opacity: 1, y: 0 }}
              className={`mb-4 flex ${m.role === "user" ? "justify-end" : "justify-start"}`}>
              <div className={`max-w-2xl px-4 py-3 rounded-2xl ${
                m.role === "user"
                  ? "gradient-bg text-white shadow-lg shadow-brand-500/25"
                  : "bg-white dark:bg-stone-800 border border-[#1b3a4b] dark:border-stone-700"
              }`}>
                <p className="whitespace-pre-wrap text-sm leading-relaxed">{m.text}</p>
                {m.sources && m.sources.length > 0 && (
                  <div className="mt-3 pt-3 border-t border-[#1b3a4b] dark:border-stone-700 text-xs opacity-80">
                    <p className="font-semibold mb-1">Sources</p>
                    {m.sources.map((s: any, j: number) => (
                      <p key={j}>• score {s.score} — {s.preview?.slice(0, 70)}…</p>
                    ))}
                  </div>
                )}
              </div>
            </motion.div>
          ))}
          {loading && (
            <div className="flex items-center gap-2 text-stone-500 dark:text-stone-400">
              <Loader2 size={16} className="animate-spin" /> Tutorix is thinking…
            </div>
          )}
        </div>

        <form onSubmit={send} className="flex gap-2">
          <input value={query} onChange={(e) => setQuery(e.target.value)} placeholder="Ask anything…" className="input flex-1" />
          <motion.button whileTap={{ scale: 0.96 }} type="submit" disabled={loading} className="btn-primary px-6 flex items-center gap-2">
            <Send size={16} />
          </motion.button>
        </form>
      </div>
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
    setError(""); setLoading(true);
    try {
      const res: any = await questions.generate({ course_id: selectedCourse, topic, difficulty, count, question_type: type });
      setItems(res.questions || []);
    } catch (err: any) { setError(err.message); } finally { setLoading(false); }
  }

  return (
    <div className="space-y-6">
      <div className="card p-6">
        <div className="flex items-center gap-3 mb-5">
          <div className="w-10 h-10 rounded-xl gradient-bg flex items-center justify-center text-white"><Sparkles size={18} /></div>
          <div><h3 className="font-bold">Generate AI Questions</h3><p className="text-xs text-stone-500 dark:text-stone-400">Grounded in course materials</p></div>
        </div>
        {!selectedCourse && <p className="text-[#006466] text-sm mb-4">Select a course first (AI Tutor tab).</p>}
        <div className="grid grid-cols-1 md:grid-cols-4 gap-3 mb-4">
          <input value={topic} onChange={(e) => setTopic(e.target.value)} className="input" placeholder="Topic" />
          <select value={difficulty} onChange={(e) => setDifficulty(e.target.value)} className="input">
            <option>easy</option><option>medium</option><option>hard</option>
          </select>
          <input type="number" value={count} onChange={(e) => setCount(Number(e.target.value))} className="input" />
          <select value={type} onChange={(e) => setType(e.target.value)} className="input">
            <option value="mcq">MCQ</option><option value="short_answer">Short Answer</option><option value="true_false">True/False</option>
          </select>
        </div>
        <motion.button whileTap={{ scale: 0.97 }} onClick={generate} disabled={loading || !selectedCourse} className="btn-primary px-6 py-3 flex items-center gap-2">
          {loading ? <Loader2 size={16} className="animate-spin" /> : <Sparkles size={16} />}
          {loading ? "Generating…" : "Generate Questions"}
        </motion.button>
        {error && <p className="text-[#006466] mt-4 text-sm">{error}</p>}
      </div>

      <div className="space-y-4">
        {items.map((q, i) => (
          <motion.div key={i} initial={{ opacity: 0, y: 16 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: i * 0.05 }}
            className="card card-hover p-5 shimmer-sweep stat-float">
            <div className="flex items-start gap-3 mb-3">
              <div className="w-8 h-8 rounded-lg gradient-bg flex items-center justify-center text-white font-bold text-sm flex-shrink-0">{i + 1}</div>
              <p className="font-semibold">{q.prompt}</p>
            </div>
            {q.options && (
              <div className="space-y-2 ml-11 mb-3">
                {Object.entries(q.options).map(([k, v]: any) => (
                  <div key={k} className={`px-3 py-2 rounded-lg text-sm ${k === q.answer ? "bg-[#ff6d00]/10 dark:bg-[#ff6d00]/15 text-[#ff6d00] dark:text-[#ff9e00] border border-[#ff6d00]/30 dark:border-[#7b2cbf]/40 font-medium" : "bg-stone-50 dark:bg-stone-900/50"}`}>
                    <span className="font-semibold mr-2">{k}.</span>{v}
                  </div>
                ))}
              </div>
            )}
            <div className="ml-11 text-xs space-y-1">
              <p><span className="font-semibold text-brand-500">Answer:</span> {q.answer}</p>
              <p className="text-stone-500 dark:text-stone-400"><span className="font-semibold">Why:</span> {q.explanation}</p>
            </div>
          </motion.div>
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
    try { const res: any = await agents.curriculum(subject, grade, weeks); setData(res); } finally { setLoading(false); }
  }

  const agentIcons = [Sparkles, BookOpen, Wrench, BarChart3];

  return (
    <div className="space-y-6">
      <div className="card p-6">
        <div className="flex items-center gap-3 mb-5">
          <div className="w-10 h-10 rounded-xl gradient-bg flex items-center justify-center text-white"><BookOpen size={18} /></div>
          <div><h3 className="font-bold">Multi-Agent Curriculum Planner</h3><p className="text-xs text-stone-500 dark:text-stone-400">4 specialized agents cooperate via LangGraph</p></div>
        </div>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-3 mb-4">
          <input value={subject} onChange={(e) => setSubject(e.target.value)} className="input" placeholder="Subject" />
          <input value={grade} onChange={(e) => setGrade(e.target.value)} className="input" placeholder="Grade" />
          <input type="number" value={weeks} onChange={(e) => setWeeks(Number(e.target.value))} className="input" />
        </div>
        <motion.button whileTap={{ scale: 0.97 }} onClick={generate} disabled={loading} className="btn-primary px-6 py-3 flex items-center gap-2">
          {loading ? <Loader2 size={16} className="animate-spin" /> : <Sparkles size={16} />}
          {loading ? "Agents working…" : "Generate Curriculum"}
        </motion.button>
      </div>

      {data && (
        <div className="space-y-4">
          {data.modules.map((m: any, i: number) => {
            const obj = data.objectives.find((o: any) => o.week === m.week);
            const les = data.lessons.find((l: any) => l.week === m.week);
            const asm = data.assessments.find((a: any) => a.week === m.week);
            return (
              <motion.div key={i} initial={{ opacity: 0, y: 16 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: i * 0.08 }}
                className="card card-hover p-6">
                <div className="flex items-center gap-3 mb-3">
                  <div className="w-10 h-10 rounded-xl gradient-bg flex items-center justify-center text-white font-bold">{m.week}</div>
                  <h3 className="font-bold text-lg">{m.title}</h3>
                </div>
                <p className="text-sm text-stone-600 dark:text-stone-400 mb-4">{m.summary}</p>
                {obj && <div className="mb-3"><p className="font-semibold text-sm mb-1">Objectives</p><ul className="list-disc list-inside text-sm space-y-1 text-stone-700 dark:text-stone-300">{obj.objectives.map((o: string, j: number) => <li key={j}>{o}</li>)}</ul></div>}
                {les && <div className="mb-3"><p className="font-semibold text-sm mb-1">Lessons</p><ul className="list-disc list-inside text-sm space-y-1 text-stone-700 dark:text-stone-300">{les.topics.map((t: string, j: number) => <li key={j}>{t}</li>)}</ul><p className="text-sm mt-2"><span className="font-semibold">Activity:</span> {les.activity}</p></div>}
                {asm && <div className="text-sm bg-brand-50 dark:bg-brand-900/20 p-3 rounded-xl border border-brand-200 dark:border-brand-900"><p><span className="font-semibold">Quiz:</span> {asm.quiz_topic}</p><p><span className="font-semibold">Project:</span> {asm.project}</p></div>}
              </motion.div>
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
    const q = msg; setMsg("");
    setMessages((m) => [...m, { role: "user", text: q }]);
    setLoading(true);
    try {
      const res: any = await agents.toolChat(q);
      setMessages((m) => [...m, { role: "ai", text: res.reply, tools: res.tools_used }]);
    } catch (err: any) {
      setMessages((m) => [...m, { role: "ai", text: "Error: " + err.message }]);
    } finally { setLoading(false); }
  }

  const examples = ["What is 125 * 8?", "What time is it?", "Find questions about ML", "Stats for student a6f1f8de-c4c4-42e3-9a2e-e34c40aa7556"];

  return (
    <div className="space-y-6">
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <Stat icon={Calculator} label="Calculator" value="Math" gradient="gradient-bg" />
        <Stat icon={Activity} label="Current time" value="UTC" gradient="bg-gradient-to-br from-[#ff6d00] to-[#ff9e00]" />
        <Stat icon={Sparkles} label="Question search" value="DB" gradient="bg-gradient-to-br from-[#5a189a] to-[#9d4edd]" />
        <Stat icon={Users} label="Student stats" value="Live" gradient="bg-gradient-to-br from-[#240046] to-[#7b2cbf]" />
      </div>
      <div className="card p-6">
        <div className="flex items-center gap-3 mb-5">
          <div className="w-10 h-10 rounded-xl gradient-bg flex items-center justify-center text-white"><Wrench size={18} /></div>
          <div><h3 className="font-bold">Agentic Assistant</h3><p className="text-xs text-stone-500 dark:text-stone-400">Gemini picks the right tool automatically</p></div>
        </div>
        <div className="flex flex-wrap gap-2 mb-4">
          {examples.map((ex) => (
            <button key={ex} onClick={() => setMsg(ex)} className="px-3 py-1.5 rounded-full text-xs border border-slate-300 dark:border-stone-700 hover:border-brand-500 hover:text-brand-500 transition">{ex}</button>
          ))}
        </div>
        <div className="rounded-2xl border border-[#1b3a4b] dark:border-stone-800 p-4 h-80 overflow-y-auto mb-4 bg-stone-50/50 dark:bg-stone-900/40">
          {messages.length === 0 && <p className="text-center mt-24 text-sm text-stone-500 dark:text-stone-400">Ask something — the AI will pick the right tool.</p>}
          {messages.map((m, i) => (
            <motion.div key={i} initial={{ opacity: 0, y: 8 }} animate={{ opacity: 1, y: 0 }}
              className={`mb-4 flex ${m.role === "user" ? "justify-end" : "justify-start"}`}>
              <div className={`max-w-2xl px-4 py-3 rounded-2xl text-sm whitespace-pre-wrap ${
                m.role === "user" ? "gradient-bg text-white shadow-lg shadow-brand-500/25" : "bg-white dark:bg-stone-800 border border-[#1b3a4b] dark:border-stone-700"
              }`}>
                {m.text}
                {m.tools && m.tools.length > 0 && (
                  <div className="mt-2 pt-2 border-t border-[#1b3a4b] dark:border-stone-700 text-xs opacity-80">
                    Tools used: {m.tools.map((t: any, j: number) => (
                      <span key={j} className="font-mono bg-brand-100 dark:bg-brand-900/40 text-brand-700 dark:text-brand-300 px-1.5 py-0.5 rounded mx-0.5">{t.tool}</span>
                    ))}
                  </div>
                )}
              </div>
            </motion.div>
          ))}
          {loading && <div className="flex items-center gap-2 text-stone-500 dark:text-stone-400"><Loader2 size={16} className="animate-spin" /> Thinking…</div>}
        </div>
        <form onSubmit={send} className="flex gap-2">
          <input value={msg} onChange={(e) => setMsg(e.target.value)} className="input flex-1" />
          <motion.button whileTap={{ scale: 0.96 }} type="submit" disabled={loading} className="btn-primary px-6 flex items-center gap-2"><Send size={16} /></motion.button>
        </form>
      </div>
    </div>
  );
}

function AnalyticsTab({ selectedCourse }: any) {
  const [data, setData] = useState<any>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  useEffect(() => {
    if (!selectedCourse) return;
    setLoading(true); setError("");
    analytics.course(selectedCourse).then(setData).catch((err: any) => setError(err.message)).finally(() => setLoading(false));
  }, [selectedCourse]);

  const maxEvents = data ? Math.max(...(Object.values(data.event_breakdown || { x: 1 }) as number[])) : 1;

  return (
    <div className="space-y-6">
      {!selectedCourse && <p className="text-stone-500 dark:text-stone-400">Select a course from the AI Tutor tab.</p>}
      {loading && <div className="flex items-center gap-2"><Loader2 size={16} className="animate-spin" /> Loading…</div>}
      {error && <p className="text-[#006466]">{error}</p>}
      {data && (
        <>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <Stat icon={Activity} label="Total Events" value={data.total_events} gradient="gradient-bg" />
            <Stat icon={TrendingUp} label="Submissions" value={data.total_submissions} gradient="bg-gradient-to-br from-[#ff6d00] to-[#ff9e00]" />
            <Stat icon={BarChart3} label="Event Types" value={Object.keys(data.event_breakdown || {}).length} gradient="bg-gradient-to-br from-[#5a189a] to-[#9d4edd]" />
          </div>
          <div className="card p-6">
            <h3 className="font-bold mb-4">Event Breakdown</h3>
            <div className="space-y-3">
              {Object.entries(data.event_breakdown || {}).map(([k, v]: any) => (
                <div key={k} className="flex items-center gap-3">
                  <span className="w-40 text-sm truncate">{k}</span>
                  <div className="flex-1 bg-[#ff6d00]/10 dark:bg-stone-800 rounded-full h-3 overflow-hidden">
                    <motion.div initial={{ width: 0 }} animate={{ width: `${(v / maxEvents) * 100}%` }} transition={{ duration: 0.8, ease: "easeOut" }}
                      className="gradient-bg h-full rounded-full" />
                  </div>
                  <span className="text-sm font-semibold w-10 text-right">{v}</span>
                </div>
              ))}
            </div>
          </div>
        </>
      )}
    </div>
  );
}
