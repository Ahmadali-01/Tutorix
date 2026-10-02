"use client";
import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { motion } from "framer-motion";
import { Sparkles, ArrowRight, Loader2, Mail, Lock } from "lucide-react";
import { auth, setToken, getToken } from "@/lib/api";
import Logo from "@/components/Logo";
import ThemeToggle from "@/components/ThemeToggle";

export default function Home() {
  const router = useRouter();
  const [email, setEmail] = useState("admin@tutorix.com");
  const [password, setPassword] = useState("admin123");
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    if (getToken()) router.push("/dashboard");
  }, [router]);

  async function handleLogin(e: React.FormEvent) {
    e.preventDefault();
    setError("");
    setLoading(true);
    try {
      const res = await auth.login(email, password);
      setToken(res.access_token);
      router.push("/dashboard");
    } catch {
      setError("Login failed. Check your credentials.");
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="min-h-screen relative flex items-center justify-center p-4 overflow-hidden gradient-bg-soft">
      <div className="absolute top-0 -left-20 w-96 h-96 rounded-full bg-brand-500/20 blur-3xl animate-float" />
      <div className="absolute bottom-0 -right-20 w-96 h-96 rounded-full bg-[#0b525b]/20 blur-3xl animate-float" style={{ animationDelay: "1.5s" }} />
      <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[700px] h-[700px] rounded-full border border-brand-500/10 animate-spin-slow" />

      <div className="absolute top-6 right-6 z-20">
        <ThemeToggle />
      </div>

      <motion.div
        initial={{ opacity: 0, y: 24, scale: 0.96 }}
        animate={{ opacity: 1, y: 0, scale: 1 }}
        transition={{ duration: 0.5, ease: "easeOut" }}
        className="w-full max-w-md glass rounded-3xl shadow-2xl p-8 relative z-10 border border-white/20"
      >
        <div className="text-center mb-8">
          <motion.div
            initial={{ scale: 0, rotate: -180 }}
            animate={{ scale: 1, rotate: 0 }}
            transition={{ type: "spring", stiffness: 180, damping: 15, delay: 0.1 }}
            className="inline-flex mb-4 relative"
          >
            <Logo size={64} />
            <div className="absolute inset-0 blur-2xl bg-brand-500/50 -z-10" />
          </motion.div>
          <h1 className="text-4xl font-black tracking-tight gradient-text">Tutorix</h1>
          <p className="text-stone-600 dark:text-stone-400 text-sm mt-2 flex items-center justify-center gap-1.5">
            <Sparkles size={14} className="text-brand-500" />
            AI Education Intelligence Platform
          </p>
        </div>

        <form onSubmit={handleLogin} className="space-y-4">
          <div>
            <label className="block text-xs font-semibold text-stone-600 dark:text-stone-400 mb-2 uppercase tracking-wider">Email</label>
            <div className="relative">
              <Mail size={16} className="absolute left-3.5 top-1/2 -translate-y-1/2 text-stone-400" />
              <input
                type="email" value={email} onChange={(e) => setEmail(e.target.value)}
                className="input pl-10" required
              />
            </div>
          </div>
          <div>
            <label className="block text-xs font-semibold text-stone-600 dark:text-stone-400 mb-2 uppercase tracking-wider">Password</label>
            <div className="relative">
              <Lock size={16} className="absolute left-3.5 top-1/2 -translate-y-1/2 text-stone-400" />
              <input
                type="password" value={password} onChange={(e) => setPassword(e.target.value)}
                className="input pl-10" required
              />
            </div>
          </div>

          {error && (
            <motion.div
              initial={{ opacity: 0, y: -8 }} animate={{ opacity: 1, y: 0 }}
              className="text-[#006466] dark:text-[#006466] text-sm bg-[#006466] dark:bg-[#006466]/40 p-3 rounded-xl border border-[#1b3a4b] dark:border-[#1b3a4b]"
            >
              {error}
            </motion.div>
          )}

          <motion.button
            whileHover={{ scale: 1.02 }} whileTap={{ scale: 0.98 }}
            type="submit" disabled={loading}
            className="btn-primary w-full py-3.5 flex items-center justify-center gap-2"
          >
            {loading ? <Loader2 size={18} className="animate-spin" /> : <>Sign In <ArrowRight size={16} /></>}
          </motion.button>
        </form>

        <div className="mt-6 pt-4 border-t border-slate-300/50 dark:border-stone-700/50">
          <p className="text-[11px] text-center text-stone-500 dark:text-stone-500">
            Default admin · <span className="font-mono">admin@tutorix.com / admin123</span>
          </p>
        </div>
      </motion.div>
    </div>
  );
}
