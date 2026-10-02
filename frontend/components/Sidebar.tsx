"use client";
import { motion, AnimatePresence } from "framer-motion";
import { useTheme } from "next-themes";
import { useEffect, useState } from "react";
import {
  BarChart3, BookOpen, MessageSquare, Moon, Sparkles, Sun,
  Wrench, LogOut, ChevronLeft, ChevronRight,
} from "lucide-react";
import Logo from "./Logo";

type Tab = "chat" | "questions" | "curriculum" | "tools" | "analytics";

const items: { id: Tab; label: string; icon: any; desc: string }[] = [
  { id: "chat", label: "AI Tutor", icon: MessageSquare, desc: "Ask anything" },
  { id: "questions", label: "Questions", icon: Sparkles, desc: "Generate MCQs" },
  { id: "curriculum", label: "Curriculum", icon: BookOpen, desc: "Multi-agent planning" },
  { id: "tools", label: "Agent Tools", icon: Wrench, desc: "Function calling" },
  { id: "analytics", label: "Analytics", icon: BarChart3, desc: "Live insights" },
];

export default function Sidebar({
  active, onChange, email, onLogout,
}: {
  active: Tab;
  onChange: (t: Tab) => void;
  email: string;
  onLogout: () => void;
}) {
  const { theme, setTheme } = useTheme();
  const [mounted, setMounted] = useState(false);
  const [collapsed, setCollapsed] = useState(false);

  useEffect(() => {
    setMounted(true);
    const c = localStorage.getItem("tutorix_sidebar_collapsed");
    if (c === "1") setCollapsed(true);
  }, []);

  function toggle() {
    setCollapsed((v) => {
      const next = !v;
      localStorage.setItem("tutorix_sidebar_collapsed", next ? "1" : "0");
      return next;
    });
  }

  function refresh() {
    window.location.reload();
  }

  return (
    <motion.aside
      animate={{ width: collapsed ? 84 : 288 }}
      transition={{ type: "spring", stiffness: 320, damping: 32 }}
      className="flex-shrink-0 bg-slate-950 text-white flex flex-col relative overflow-hidden"
    >
      <div className="absolute -top-24 -right-24 w-64 h-64 rounded-full bg-[#ff6d00]/15 blur-3xl pointer-events-none" />
      <div className="absolute -bottom-24 -left-24 w-64 h-64 rounded-full bg-[#9d4edd]/15 blur-3xl pointer-events-none" />

      <div className="p-4 border-b border-white/10 relative z-10">
        <div className="flex items-center gap-3">
          <button
            onClick={refresh}
            className="relative flex-shrink-0 hover:opacity-80 active:scale-95 transition"
            title="Refresh page"
            aria-label="Refresh page"
          >
            <Logo size={44} />
            <div className="absolute inset-0 blur-xl bg-[#ff6d00]/40 -z-10 pointer-events-none" />
          </button>
          <AnimatePresence>
            {!collapsed && (
              <motion.button
                onClick={refresh}
                initial={{ opacity: 0, x: -10 }}
                animate={{ opacity: 1, x: 0 }}
                exit={{ opacity: 0, x: -10 }}
                className="text-left hover:opacity-80 transition"
                title="Refresh page"
              >
                <h1 className="text-xl font-black tracking-tight gradient-text">Tutorix</h1>
                <p className="text-[10px] text-[#ff9e00] uppercase tracking-[0.2em] font-semibold">AI Education</p>
              </motion.button>
            )}
          </AnimatePresence>
        </div>
      </div>

      <button
        onClick={toggle}
        className="absolute top-20 right-3 w-7 h-7 rounded-full bg-[#ff6d00] text-white flex items-center justify-center shadow-lg hover:bg-[#ff9e00] z-30 border-2 border-white/20 cursor-default"
        title={collapsed ? "Expand" : "Collapse"}
      >
        {collapsed ? <ChevronRight size={16} /> : <ChevronLeft size={16} />}
      </button>

      <nav className="flex-1 p-3 space-y-1 relative z-10 overflow-y-auto">
        {items.map((it, idx) => {
          const Icon = it.icon;
          const isActive = active === it.id;
          return (
            <motion.button
              key={it.id}
              initial={{ opacity: 0, x: -20 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ delay: idx * 0.05 }}
              onClick={() => onChange(it.id)}
              className={`w-full flex items-center gap-3 px-3 py-3 rounded-xl text-sm font-medium transition-all group relative ${
                isActive ? "text-white" : "text-slate-400 hover:text-white hover:bg-white/5"
              }`}
              title={collapsed ? it.label : undefined}
            >
              {isActive && (
                <motion.div
                  layoutId="activeTab"
                  className="absolute inset-0 gradient-bg rounded-xl shadow-lg shadow-[#ff6d00]/40"
                  transition={{ type: "spring", stiffness: 400, damping: 30 }}
                />
              )}
              <Icon size={20} className="relative z-10 flex-shrink-0" />
              <AnimatePresence>
                {!collapsed && (
                  <motion.div
                    initial={{ opacity: 0, x: -10 }}
                    animate={{ opacity: 1, x: 0 }}
                    exit={{ opacity: 0, x: -10 }}
                    className="relative z-10 text-left flex-1"
                  >
                    <div>{it.label}</div>
                    <div className={`text-[10px] ${isActive ? "text-white/70" : "text-slate-500"}`}>{it.desc}</div>
                  </motion.div>
                )}
              </AnimatePresence>
            </motion.button>
          );
        })}
      </nav>

      <div className="p-3 border-t border-white/10 relative z-10 space-y-2">
        <button
          onClick={() => setTheme(theme === "dark" ? "light" : "dark")}
          className="w-full flex items-center gap-3 px-3 py-2.5 rounded-xl text-sm text-slate-300 hover:bg-white/5 hover:text-white transition"
          title={collapsed ? "Toggle theme" : undefined}
        >
          {mounted && theme === "dark" ? <Sun size={18} /> : <Moon size={18} />}
          {!collapsed && <span>{mounted && theme === "dark" ? "Light mode" : "Dark mode"}</span>}
        </button>
        {!collapsed && (
          <div className="px-3 py-2 rounded-xl bg-white/5">
            <p className="text-[10px] text-slate-500 uppercase tracking-wider">Signed in</p>
            <p className="text-xs font-medium truncate">{email || "—"}</p>
          </div>
        )}
        <button
          onClick={onLogout}
          className="w-full flex items-center gap-3 px-3 py-2.5 rounded-xl text-sm text-slate-300 hover:bg-red-500/10 hover:text-red-300 transition"
          title={collapsed ? "Logout" : undefined}
        >
          <LogOut size={18} />
          {!collapsed && <span>Logout</span>}
        </button>
      </div>
    </motion.aside>
  );
}
