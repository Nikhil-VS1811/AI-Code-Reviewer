import { ArrowRight, CheckCircle2, Code2, History, ShieldCheck } from "lucide-react";
import { Link, Navigate } from "react-router-dom";

import { useAuth } from "../contexts/AuthContext";
import { useTheme } from "../contexts/ThemeContext";

export function LandingPage() {
  const { isAuthenticated } = useAuth();
  const { theme, toggleTheme } = useTheme();

  if (isAuthenticated) {
    return <Navigate to="/dashboard" replace />;
  }

  return (
    <div className="min-h-screen bg-slate-50 text-slate-950 dark:bg-ink-950 dark:text-white">
      <header className="border-b border-slate-200 bg-white/90 backdrop-blur dark:border-ink-700 dark:bg-ink-900/90">
        <div className="mx-auto flex max-w-7xl items-center justify-between px-4 py-4 sm:px-6">
          <Link to="/" className="flex items-center gap-3 font-semibold">
            <span className="flex h-9 w-9 items-center justify-center rounded-md bg-brand-600 text-white">
              <ShieldCheck size={20} />
            </span>
            AI Code Review
          </Link>
          <div className="flex items-center gap-2">
            <button type="button" onClick={toggleTheme} className="secondary-button">
              {theme === "dark" ? "Light" : "Dark"}
            </button>
            <Link to="/login" className="secondary-button">
              Login
            </Link>
            <Link to="/signup" className="primary-button">
              Get started
            </Link>
          </div>
        </div>
      </header>

      <main>
        <section className="mx-auto grid min-h-[calc(100vh-73px)] max-w-7xl gap-8 px-4 py-10 sm:px-6 lg:grid-cols-[1fr_0.95fr] lg:items-center">
          <div>
            <div className="inline-flex items-center gap-2 rounded-md border border-slate-200 bg-white px-3 py-1 text-sm font-medium text-slate-600 dark:border-ink-700 dark:bg-ink-900 dark:text-slate-300">
              <CheckCircle2 size={16} className="text-emerald-500" />
              FastAPI, PostgreSQL, JWT, and Ollama-ready
            </div>
            <h1 className="mt-6 max-w-3xl text-4xl font-semibold tracking-normal text-slate-950 dark:text-white sm:text-5xl">
              AI-assisted code reviews with measurable engineering signals
            </h1>
            <p className="mt-5 max-w-2xl text-lg leading-8 text-slate-600 dark:text-slate-300">
              Submit code, generate structured reviews, and track quality across security,
              performance, maintainability, and readability from one focused console.
            </p>
            <div className="mt-8 flex flex-col gap-3 sm:flex-row">
              <Link to="/signup" className="primary-button justify-center">
                Start reviewing
                <ArrowRight size={18} />
              </Link>
              <Link to="/login" className="secondary-button justify-center">
                Open dashboard
              </Link>
            </div>
          </div>

          <div className="rounded-md border border-slate-200 bg-white p-4 shadow-soft dark:border-ink-700 dark:bg-ink-900">
            <div className="rounded-md bg-ink-950 p-4 text-slate-100">
              <div className="mb-4 flex items-center justify-between border-b border-white/10 pb-3">
                <div className="flex items-center gap-2">
                  <Code2 size={18} className="text-brand-400" />
                  <span className="text-sm font-semibold">Review preview</span>
                </div>
                <span className="rounded-md bg-emerald-400/10 px-2 py-1 text-xs text-emerald-300">
                  Score 86
                </span>
              </div>
              <pre className="overflow-hidden rounded-md bg-black/35 p-4 text-sm leading-6 text-slate-300">
                <code>{`def authorize(user, action):
    if not user:
        return False
    return action in user.permissions`}</code>
              </pre>
              <div className="mt-4 grid gap-3 sm:grid-cols-2">
                {[
                  ["Security", "Validate permission source before trust"],
                  ["Maintainability", "Small function, clear return path"],
                  ["Performance", "No repeated work detected"],
                  ["Readability", "Intent is easy to scan"],
                ].map(([label, text]) => (
                  <div key={label} className="rounded-md border border-white/10 p-3">
                    <p className="text-xs font-semibold text-brand-400">{label}</p>
                    <p className="mt-1 text-sm text-slate-300">{text}</p>
                  </div>
                ))}
              </div>
            </div>
            <div className="mt-4 flex items-center gap-3 text-sm text-slate-600 dark:text-slate-400">
              <History size={16} />
              Recent reviews and score trends are ready after login.
            </div>
          </div>
        </section>
      </main>
    </div>
  );
}
