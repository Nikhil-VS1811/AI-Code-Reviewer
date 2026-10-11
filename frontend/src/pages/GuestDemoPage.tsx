import { useState } from "react";
import {
  AlertTriangle,
  ArrowLeft,
  ArrowRight,
  CheckCircle2,
  Code2,
  FileCode,
  Filter,
  Lightbulb,
  Lock,
  Moon,
  ShieldCheck,
  Sun,
  UserPlus,
} from "lucide-react";
import { Link } from "react-router-dom";

import { ReviewScoreBadge } from "../components/ReviewScoreBadge";
import { useTheme } from "../contexts/ThemeContext";
import { GUEST_SAMPLE_REVIEW, type GuestFinding } from "../data/guestDemoData";

const severityColors: Record<string, { badge: string; border: string }> = {
  critical: {
    badge: "bg-rose-500/10 text-rose-700 dark:bg-rose-950 dark:text-rose-300",
    border: "border-rose-300 dark:border-rose-900",
  },
  high: {
    badge: "bg-orange-500/10 text-orange-700 dark:bg-orange-950 dark:text-orange-300",
    border: "border-orange-300 dark:border-orange-900",
  },
  medium: {
    badge: "bg-amber-500/10 text-amber-700 dark:bg-amber-950 dark:text-amber-300",
    border: "border-amber-300 dark:border-amber-900",
  },
  low: {
    badge: "bg-emerald-500/10 text-emerald-700 dark:bg-emerald-950 dark:text-emerald-300",
    border: "border-emerald-300 dark:border-emerald-900",
  },
};

export function GuestDemoPage() {
  const { theme, toggleTheme } = useTheme();
  const [selectedSeverity, setSelectedSeverity] = useState<string>("all");
  const [selectedCategory, setSelectedCategory] = useState<string>("all");
  const [activeFindingId, setActiveFindingId] = useState<number | null>(1);

  const filteredFindings = GUEST_SAMPLE_REVIEW.findings.filter((finding) => {
    const matchesSeverity =
      selectedSeverity === "all" || finding.severity === selectedSeverity;
    const matchesCategory =
      selectedCategory === "all" || finding.category === selectedCategory;
    return matchesSeverity && matchesCategory;
  });

  const scores = [
    { label: "Security", score: GUEST_SAMPLE_REVIEW.security_score },
    { label: "Performance", score: GUEST_SAMPLE_REVIEW.performance_score },
    { label: "Maintainability", score: GUEST_SAMPLE_REVIEW.maintainability_score },
    { label: "Readability", score: GUEST_SAMPLE_REVIEW.readability_score },
  ];

  const codeLines = GUEST_SAMPLE_REVIEW.code.trim().split("\n");

  return (
    <div className="min-h-screen bg-slate-50 text-slate-950 dark:bg-ink-950 dark:text-slate-100">
      {/* Top Header */}
      <header className="sticky top-0 z-20 border-b border-slate-200 bg-white/95 backdrop-blur dark:border-ink-700 dark:bg-ink-900/95">
        <div className="mx-auto flex max-w-7xl items-center justify-between px-4 py-3 sm:px-6">
          <div className="flex items-center gap-3">
            <Link to="/" className="flex items-center gap-2.5 font-semibold text-slate-950 dark:text-white">
              <span className="flex h-9 w-9 items-center justify-center rounded-md bg-brand-600 text-white">
                <ShieldCheck size={20} />
              </span>
              <span className="hidden sm:inline">AI Code Review</span>
            </Link>
            <span className="inline-flex items-center gap-1.5 rounded-full border border-amber-300 bg-amber-50 px-2.5 py-0.5 text-xs font-semibold text-amber-800 dark:border-amber-700/60 dark:bg-amber-950/50 dark:text-amber-300">
              <span className="h-1.5 w-1.5 rounded-full bg-amber-500 animate-pulse" />
              Demo Mode
            </span>
          </div>

          <div className="flex items-center gap-2">
            <button
              type="button"
              onClick={toggleTheme}
              className="icon-button"
              aria-label="Toggle theme"
            >
              {theme === "dark" ? <Sun size={18} /> : <Moon size={18} />}
            </button>
            <Link to="/login" className="secondary-button text-xs sm:text-sm">
              Sign In
            </Link>
            <Link to="/signup" className="primary-button text-xs sm:text-sm">
              <UserPlus size={16} />
              <span className="hidden sm:inline">Create Free Account</span>
              <span className="sm:hidden">Sign Up</span>
            </Link>
          </div>
        </div>
      </header>

      <main className="mx-auto max-w-7xl px-4 py-6 sm:px-6 sm:py-8">
        {/* Prominent Demo Disclaimer Banner */}
        <section
          aria-label="Demo disclaimer"
          className="mb-6 flex flex-col gap-3 rounded-lg border border-amber-300 bg-amber-50 p-4 text-amber-900 dark:border-amber-800/60 dark:bg-amber-950/40 dark:text-amber-200 sm:flex-row sm:items-center sm:justify-between"
        >
          <div className="flex items-start gap-3">
            <AlertTriangle className="mt-0.5 h-5 w-5 shrink-0 text-amber-600 dark:text-amber-400" />
            <div>
              <p className="font-semibold text-sm sm:text-base">
                Demo Data — Not a Live AI Analysis
              </p>
              <p className="mt-0.5 text-xs text-amber-800 dark:text-amber-300 sm:text-sm">
                This is an interactive demonstration with fixed sample findings. No live AI requests,
                Git clones, or database writes were executed. Create an account to review your own code.
              </p>
            </div>
          </div>
          <div className="flex shrink-0 items-center gap-2">
            <Link to="/signup" className="primary-button text-xs bg-amber-600 hover:bg-amber-500">
              Run Live Review
              <ArrowRight size={14} />
            </Link>
          </div>
        </section>

        {/* Overview Header & Actions */}
        <div className="mb-6 flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
          <div>
            <div className="flex items-center gap-2">
              <Link to="/" className="inline-flex items-center gap-1 text-xs text-slate-500 hover:text-brand-600 dark:text-slate-400">
                <ArrowLeft size={14} />
                Return to Home
              </Link>
            </div>
            <h1 className="mt-1 text-2xl font-bold tracking-tight text-slate-950 dark:text-white sm:text-3xl">
              Sample Code Review
            </h1>
            <p className="mt-1 text-sm text-slate-600 dark:text-slate-300">
              Preloaded analysis for a session validation and telemetry module ({GUEST_SAMPLE_REVIEW.language}).
            </p>
          </div>

          <div className="flex flex-wrap items-center gap-2">
            <Link to="/signup" className="primary-button">
              <UserPlus size={16} />
              Review Your Own Code
            </Link>
          </div>
        </div>

        {/* Quality Score & Dimension Cards */}
        <section aria-label="Review scores" className="mb-8 grid gap-4 lg:grid-cols-[340px_1fr]">
          <div className="rounded-lg border border-slate-200 bg-white p-5 shadow-sm dark:border-ink-700 dark:bg-ink-900">
            <div className="flex items-start justify-between">
              <div>
                <p className="text-xs font-semibold uppercase tracking-wider text-slate-500 dark:text-slate-400">
                  Overall Quality Score
                </p>
                <div className="mt-2 flex items-baseline gap-2">
                  <span className="text-4xl font-extrabold text-slate-900 dark:text-white">
                    {GUEST_SAMPLE_REVIEW.overall_score}
                  </span>
                  <span className="text-sm font-medium text-slate-500">/ 100</span>
                </div>
              </div>
              <ReviewScoreBadge score={GUEST_SAMPLE_REVIEW.overall_score} />
            </div>
            <p className="mt-4 text-xs leading-5 text-slate-600 dark:text-slate-300">
              {GUEST_SAMPLE_REVIEW.summary}
            </p>
          </div>

          <div className="grid gap-3 sm:grid-cols-2">
            {scores.map(({ label, score }) => (
              <div
                key={label}
                className="flex flex-col justify-between rounded-lg border border-slate-200 bg-white p-4 shadow-sm dark:border-ink-700 dark:bg-ink-900"
              >
                <div className="flex items-center justify-between">
                  <span className="text-sm font-semibold text-slate-800 dark:text-slate-200">{label}</span>
                  <span className="text-sm font-bold text-slate-900 dark:text-white">{score}/100</span>
                </div>
                <div className="mt-3 h-2 w-full overflow-hidden rounded-full bg-slate-100 dark:bg-ink-800">
                  <div
                    className={`h-full rounded-full transition-all duration-500 ${
                      score >= 80 ? "bg-emerald-500" : score >= 60 ? "bg-amber-500" : "bg-rose-500"
                    }`}
                    style={{ width: `${score}%` }}
                  />
                </div>
              </div>
            ))}
          </div>
        </section>

        {/* Main Interactive Grid: Findings & Code Inspection */}
        <div className="grid gap-6 xl:grid-cols-[1.1fr_1fr]">
          {/* Findings Column */}
          <section aria-label="Review findings" className="space-y-4">
            <div className="rounded-lg border border-slate-200 bg-white p-4 shadow-sm dark:border-ink-700 dark:bg-ink-900">
              <div className="flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
                <div className="flex items-center gap-2">
                  <Filter size={16} className="text-brand-600 dark:text-brand-400" />
                  <h2 className="text-base font-semibold text-slate-900 dark:text-white">
                    Findings ({filteredFindings.length})
                  </h2>
                </div>

                {/* Severity Filter Chips */}
                <div className="flex flex-wrap items-center gap-1.5">
                  {(["all", "critical", "high", "medium", "low"] as const).map((sev) => (
                    <button
                      key={sev}
                      type="button"
                      onClick={() => setSelectedSeverity(sev)}
                      className={`rounded px-2.5 py-1 text-xs font-medium capitalize transition ${
                        selectedSeverity === sev
                          ? "bg-brand-600 text-white"
                          : "bg-slate-100 text-slate-600 hover:bg-slate-200 dark:bg-ink-800 dark:text-slate-300 dark:hover:bg-ink-700"
                      }`}
                    >
                      {sev}
                    </button>
                  ))}
                </div>
              </div>

              {/* Category Filter Chips */}
              <div className="mt-3 flex flex-wrap items-center gap-1.5 border-t border-slate-100 pt-3 dark:border-ink-800">
                <span className="text-xs text-slate-500 dark:text-slate-400">Category:</span>
                {(["all", "security", "performance", "maintainability"] as const).map((cat) => (
                  <button
                    key={cat}
                    type="button"
                    onClick={() => setSelectedCategory(cat)}
                    className={`rounded px-2 py-0.5 text-xs font-medium capitalize transition ${
                      selectedCategory === cat
                        ? "bg-slate-800 text-white dark:bg-slate-200 dark:text-slate-900"
                        : "text-slate-600 hover:bg-slate-100 dark:text-slate-400 dark:hover:bg-ink-800"
                    }`}
                  >
                    {cat}
                  </button>
                ))}
              </div>
            </div>

            {/* Findings List */}
            <div className="space-y-3">
              {filteredFindings.length === 0 ? (
                <div className="rounded-lg border border-dashed border-slate-300 p-8 text-center text-sm text-slate-500 dark:border-ink-700 dark:text-slate-400">
                  No findings match the selected filters.
                </div>
              ) : (
                filteredFindings.map((finding: GuestFinding) => {
                  const isActive = activeFindingId === finding.id;
                  const colors = severityColors[finding.severity] ?? severityColors.low;

                  return (
                    <article
                      key={finding.id}
                      onClick={() => setActiveFindingId(finding.id)}
                      className={`cursor-pointer rounded-lg border bg-white p-5 transition shadow-sm hover:shadow dark:bg-ink-900 ${
                        isActive
                          ? `ring-2 ring-brand-500 ${colors.border}`
                          : "border-slate-200 dark:border-ink-700"
                      }`}
                    >
                      <div className="flex flex-wrap items-center justify-between gap-2">
                        <div className="flex items-center gap-2">
                          <span className="font-mono text-xs font-semibold rounded bg-slate-100 px-2 py-1 text-slate-700 dark:bg-ink-800 dark:text-slate-300">
                            Line {finding.line_number}
                          </span>
                          <span className={`rounded px-2 py-1 text-xs font-semibold capitalize ${colors.badge}`}>
                            {finding.severity}
                          </span>
                          <span className="rounded bg-brand-50 px-2 py-1 text-xs font-semibold capitalize text-brand-700 dark:bg-brand-950 dark:text-brand-300">
                            {finding.category}
                          </span>
                        </div>
                        {isActive ? (
                          <span className="text-xs font-medium text-brand-600 dark:text-brand-400">
                            Inspecting Line {finding.line_number}
                          </span>
                        ) : null}
                      </div>

                      <p className="mt-3 text-sm font-medium leading-relaxed text-slate-800 dark:text-slate-200">
                        {finding.comment}
                      </p>

                      <div className="mt-3 rounded-md border border-slate-100 bg-slate-50/80 p-3 dark:border-ink-800 dark:bg-ink-950/60">
                        <div className="flex items-center gap-1.5 text-xs font-semibold text-slate-700 dark:text-slate-300">
                          <Lightbulb size={14} className="text-amber-500" />
                          Remediation Recommendation
                        </div>
                        <p className="mt-1 text-xs leading-5 text-slate-600 dark:text-slate-400">
                          {finding.remediation}
                        </p>
                      </div>
                    </article>
                  );
                })
              )}
            </div>
          </section>

          {/* Interactive Source Code Viewer */}
          <aside aria-label="Sample source code" className="space-y-4">
            <div className="overflow-hidden rounded-lg border border-slate-200 bg-white shadow-sm dark:border-ink-700 dark:bg-ink-900">
              <div className="flex items-center justify-between border-b border-slate-200 bg-slate-50 px-4 py-3 dark:border-ink-700 dark:bg-ink-950">
                <div className="flex items-center gap-2">
                  <FileCode size={16} className="text-brand-600 dark:text-brand-400" />
                  <span className="text-xs font-semibold uppercase tracking-wider text-slate-700 dark:text-slate-300">
                    Source: session_validator.py
                  </span>
                </div>
                <span className="font-mono text-xs text-slate-500 dark:text-slate-400">
                  {codeLines.length} lines • Python
                </span>
              </div>

              {/* Code with Interactive Line Highlighting */}
              <div className="max-h-[640px] overflow-auto bg-slate-950 p-4 font-mono text-xs leading-6 text-slate-200">
                {codeLines.map((lineText, idx) => {
                  const lineNum = idx + 1;
                  const matchingFinding = GUEST_SAMPLE_REVIEW.findings.find(
                    (f) => f.line_number === lineNum
                  );
                  const isHighlighted = matchingFinding?.id === activeFindingId;

                  return (
                    <div
                      key={lineNum}
                      onClick={() => {
                        if (matchingFinding) {
                          setActiveFindingId(matchingFinding.id);
                        }
                      }}
                      className={`flex items-start transition-colors ${
                        isHighlighted
                          ? "bg-brand-500/25 text-white ring-1 ring-brand-400"
                          : matchingFinding
                          ? "bg-rose-500/15 hover:bg-rose-500/25 cursor-pointer"
                          : "hover:bg-white/5"
                      }`}
                    >
                      <span className="w-10 shrink-0 select-none text-right pr-3 text-slate-600">
                        {lineNum}
                      </span>
                      <span className="whitespace-pre overflow-x-auto flex-1">
                        {lineText || " "}
                      </span>
                      {matchingFinding ? (
                        <span className="ml-2 select-none shrink-0 rounded px-1.5 py-0.2 text-[10px] font-bold uppercase tracking-wider text-rose-400">
                          [{matchingFinding.severity}]
                        </span>
                      ) : null}
                    </div>
                  );
                })}
              </div>
            </div>

            <div className="rounded-lg border border-slate-200 bg-white p-4 text-xs text-slate-600 shadow-sm dark:border-ink-700 dark:bg-ink-900 dark:text-slate-400">
              <p className="flex items-center gap-1.5 font-medium text-slate-700 dark:text-slate-300">
                <Code2 size={14} className="text-brand-500" />
                Line inspection tip
              </p>
              <p className="mt-1">
                Lines with security and performance warnings are highlighted in the source viewer.
                Click on any flagged line to see detailed vulnerability explanations and fixes.
              </p>
            </div>
          </aside>
        </div>

        {/* Clear Conversion Path Callout */}
        <section
          aria-label="Account registration callout"
          className="mt-12 rounded-xl border border-brand-200 bg-gradient-to-r from-brand-50 via-white to-slate-50 p-6 shadow-sm dark:border-brand-900/50 dark:from-ink-900 dark:via-ink-900 dark:to-ink-950 sm:p-8"
        >
          <div className="flex flex-col gap-6 lg:flex-row lg:items-center lg:justify-between">
            <div className="max-w-2xl">
              <div className="inline-flex items-center gap-1.5 rounded-md bg-brand-100 px-2.5 py-1 text-xs font-semibold text-brand-800 dark:bg-brand-950 dark:text-brand-300">
                <Lock size={12} />
                Full Platform Capabilities
              </div>
              <h2 className="mt-3 text-xl font-bold text-slate-950 dark:text-white sm:text-2xl">
                Ready to review your real repositories and pull requests?
              </h2>
              <p className="mt-2 text-sm text-slate-600 dark:text-slate-300">
                Create a free account to unlock automated GitHub repository scans, AI-assisted multi-file audits,
                historical score trends, and downloadable PDF compliance reports.
              </p>
              <div className="mt-4 flex flex-wrap gap-4 text-xs font-medium text-slate-600 dark:text-slate-400">
                <span className="flex items-center gap-1">
                  <CheckCircle2 size={14} className="text-emerald-500" /> No credit card required
                </span>
                <span className="flex items-center gap-1">
                  <CheckCircle2 size={14} className="text-emerald-500" /> Instant repository scanning
                </span>
                <span className="flex items-center gap-1">
                  <CheckCircle2 size={14} className="text-emerald-500" /> Exportable audit PDFs
                </span>
              </div>
            </div>

            <div className="flex flex-col gap-3 sm:flex-row sm:items-center">
              <Link to="/signup" className="primary-button justify-center text-sm py-2.5 px-5">
                Create Free Account
                <ArrowRight size={16} />
              </Link>
              <Link to="/login" className="secondary-button justify-center text-sm py-2.5 px-5">
                Sign In
              </Link>
            </div>
          </div>
        </section>
      </main>
    </div>
  );
}
