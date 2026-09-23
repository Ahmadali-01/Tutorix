"use client";

import {
  BarChart3,
  BookOpen,
  GraduationCap,
  MessageSquare,
  Sparkles,
  Wrench,
  LogOut,
} from "lucide-react";

type Tab = "chat" | "questions" | "curriculum" | "tools" | "analytics";

const items: { id: Tab; label: string; icon: any }[] = [
  { id: "chat", label: "AI Tutor", icon: MessageSquare },
  { id: "questions", label: "Questions", icon: Sparkles },
  { id: "curriculum", label: "Curriculum", icon: BookOpen },
  { id: "tools", label: "Agent Tools", icon: Wrench },
  { id: "analytics", label: "Analytics", icon: BarChart3 },
];

export default function Sidebar({
  active,
  onChange,
  email,
  onLogout,
}: {
  active: Tab;
  onChange: (t: Tab) => void;
  email: string;
  onLogout: () => void;
}) {
  return (
    <aside className="w-64 bg-gradient-to-b from-slate-900 via-slate-900 to-indigo-950 text-white flex flex-col">
      <div className="p-6 border-b border-white/10">
        <div className="flex items-center gap-3">
          <div className="w-11 h-11 rounded-2xl bg-gradient-to-br from-indigo-500 to-purple-600 flex items-center justify-center shadow-lg shadow-indigo-500/30">
            <GraduationCap size={24} />
          </div>
          <div>
            <h1 className="text-lg font-bold tracking-tight">Tutorix</h1>
            <p className="text-[10px] text-indigo-300 uppercase tracking-widest">
              AI Education
            </p>
          </div>
        </div>
      </div>

      <nav className="flex-1 p-4 space-y-1">
        {items.map((it) => {
          const Icon = it.icon;
          const isActive = active === it.id;
          return (
            <button
              key={it.id}
              onClick={() => onChange(it.id)}
              className={`w-full flex items-center gap-3 px-4 py-3 rounded-xl text-sm font-medium transition-all ${
                isActive
                  ? "bg-gradient-to-r from-indigo-600 to-purple-600 shadow-lg shadow-indigo-500/30"
                  : "text-slate-300 hover:bg-white/5 hover:text-white"
              }`}
            >
              <Icon size={18} />
              {it.label}
            </button>
          );
        })}
      </nav>

      <div className="p-4 border-t border-white/10">
        <div className="px-3 py-2 mb-3">
          <p className="text-xs text-slate-400">Signed in as</p>
          <p className="text-sm font-medium truncate">{email}</p>
        </div>
        <button
          onClick={onLogout}
          className="w-full flex items-center gap-2 px-4 py-2.5 rounded-xl text-sm text-slate-300 hover:bg-white/5 hover:text-white transition"
        >
          <LogOut size={16} />
          Logout
        </button>
      </div>
    </aside>
  );
}
