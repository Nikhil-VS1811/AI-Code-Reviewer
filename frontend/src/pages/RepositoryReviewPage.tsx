import { FormEvent, useState } from "react";
import { Github, SearchCode } from "lucide-react";

import { analyzeRepository } from "../api/repositoryReview";
import { getApiErrorMessage } from "../api/client";
import { EmptyState } from "../components/EmptyState";
import { ErrorPanel } from "../components/ErrorPanel";
import { LoadingPanel } from "../components/LoadingPanel";
import { PageHeader } from "../components/PageHeader";
import { StatCard } from "../components/StatCard";
import { exportRepositoryPdf } from "../api/repositoryPdf";
import type { RepositoryFinding, RepositoryReviewResult } from "../types/api";

const severityClasses: Record<string, string> = {
  critical: "bg-rose-500/10 text-rose-700 dark:text-rose-300",
  high: "bg-orange-500/10 text-orange-700 dark:text-orange-300",
  medium: "bg-amber-500/10 text-amber-700 dark:text-amber-300",
  low: "bg-emerald-500/10 text-emerald-700 dark:text-emerald-300",
};

function getSeverityClass(severity: string) {
  return severityClasses[severity.toLowerCase()] ?? "bg-slate-500/10 text-slate-700 dark:text-slate-300";
}

function formatSeverity(severity: string) {
  return severity.charAt(0).toUpperCase() + severity.slice(1);
}

function FindingsTable({ findings }: { findings: RepositoryFinding[] }) {
  if (!findings.length) {
    return (
      <div className="p-5">
        <EmptyState title="No findings" description="The scanner did not detect security issues in this repository." />
      </div>
    );
  }

  return (
    <div className="overflow-x-auto">
      <table className="w-full min-w-[820px] text-left text-sm">
        <thead className="border-b border-slate-200 bg-slate-50 text-xs uppercase text-slate-500 dark:border-ink-700 dark:bg-ink-950 dark:text-slate-400">
          <tr>
            <th className="px-5 py-3 font-semibold">File</th>
            <th className="w-24 px-5 py-3 font-semibold">Line</th>
            <th className="w-32 px-5 py-3 font-semibold">Severity</th>
            <th className="w-36 px-5 py-3 font-semibold">Category</th>
            <th className="px-5 py-3 font-semibold">Comment</th>
          </tr>
        </thead>
        <tbody className="divide-y divide-slate-200 dark:divide-ink-700">
          {findings.map((finding, index) => (
            <tr key={`${finding.file}-${finding.line_number}-${index}`} className="align-top">
              <td className="max-w-sm px-5 py-4 font-mono text-xs text-slate-700 dark:text-slate-300">
                <span className="block truncate" title={finding.file}>
                  {finding.file}
                </span>
              </td>
              <td className="px-5 py-4 text-slate-600 dark:text-slate-400">{finding.line_number}</td>
              <td className="px-5 py-4">
                <span className={`rounded px-2 py-1 text-xs font-semibold ${getSeverityClass(finding.severity)}`}>
                  {formatSeverity(finding.severity)}
                </span>
              </td>
              <td className="px-5 py-4 text-slate-600 dark:text-slate-400">{finding.category}</td>
              <td className="px-5 py-4 text-slate-700 dark:text-slate-300">{finding.comment}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}

function SummaryList({ title, items }: { title: string; items: string[] }) {
  return (
    <div>
      <h3 className="text-sm font-semibold text-slate-900 dark:text-white">{title}</h3>
      <ul className="mt-3 space-y-2 text-sm text-slate-600 dark:text-slate-300">
        {items.map((item) => (
          <li key={item} className="flex gap-2">
            <span className="mt-2 h-1.5 w-1.5 shrink-0 rounded-full bg-brand-500" />
            <span>{item}</span>
          </li>
        ))}
      </ul>
    </div>
  );
}

function RepositoryHealthCard({ result }: { result: RepositoryReviewResult }) {
  return (
    <section className="rounded-md border border-slate-200 bg-white shadow-sm dark:border-ink-700 dark:bg-ink-900">
      <div className="flex flex-col gap-3 border-b border-slate-200 px-5 py-4 dark:border-ink-700 sm:flex-row sm:items-center sm:justify-between">
        <div>
          <h2 className="text-lg font-semibold">Repository Health</h2>
          <p className="mt-1 text-sm text-slate-500 dark:text-slate-400">
            AI-style summary generated from scanner findings and severity weighting.
          </p>
        </div>
        <div className="rounded-md bg-brand-50 px-4 py-3 text-brand-700 dark:bg-brand-500/10 dark:text-brand-300">
          <p className="text-xs font-semibold uppercase">Health Score</p>
          <p className="mt-1 text-2xl font-semibold">{result.repository_health_score}/100</p>
        </div>
      </div>

      <div className="grid gap-6 p-5 lg:grid-cols-3">
        <SummaryList title="Strengths" items={result.strengths} />
        <SummaryList title="Weaknesses" items={result.weaknesses} />
        <SummaryList title="Recommendations" items={result.recommendations} />
      </div>
    </section>
  );
}

export function RepositoryReviewPage() {
  const [repoUrl, setRepoUrl] = useState("");
  const [result, setResult] = useState<RepositoryReviewResult | null>(null);
  const [error, setError] = useState("");
  const [isScanning, setIsScanning] = useState(false);


  async function handleExportPdf() {
  if (!repoUrl.trim()) return;

  try {
    const pdfBlob = await exportRepositoryPdf(
      repoUrl.trim()
    );

    const url =
      window.URL.createObjectURL(pdfBlob);

    const link =
      document.createElement("a");

    link.href = url;
    link.download = "repository-report.pdf";

    document.body.appendChild(link);

    link.click();

    link.remove();

    window.URL.revokeObjectURL(url);

  } catch (error) {
    setError(
      getApiErrorMessage(error)
    );
  }
}




  async function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setError("");
    setResult(null);
    setIsScanning(true);

    try {
      setResult(await analyzeRepository(repoUrl.trim()));
    } catch (requestError) {
      setError(getApiErrorMessage(requestError));
    } finally {
      setIsScanning(false);
    }
  }

  return (
    <>
      <PageHeader
        title="Repository Review"
        description="Scan a GitHub repository with the static security rules and review repository-level findings."
      />

      <div className="space-y-6">
        <section className="rounded-md border border-slate-200 bg-white p-5 shadow-sm dark:border-ink-700 dark:bg-ink-900">
          <form onSubmit={handleSubmit} className="grid gap-4 lg:grid-cols-[1fr_auto] lg:items-end">
            <label className="block">
              <span className="text-sm font-medium text-slate-700 dark:text-slate-300">GitHub URL</span>
              <span className="relative mt-2 block">
                <Github
                  size={18}
                  className="pointer-events-none absolute left-3 top-1/2 -translate-y-1/2 text-slate-400"
                />
                <input
                  type="url"
                  value={repoUrl}
                  onChange={(event) => setRepoUrl(event.target.value)}
                  className="w-full rounded-md border border-slate-300 bg-white py-2.5 pl-10 pr-3 text-sm outline-none focus:border-brand-500 focus:ring-2 focus:ring-brand-500/20 dark:border-ink-700 dark:bg-ink-950"
                  placeholder="https://github.com/owner/repository"
                  disabled={isScanning}
                  required
                />
              </span>
            </label>

            <div className="flex gap-3">
  <button
    type="submit"
    className="primary-button justify-center"
    disabled={isScanning || !repoUrl.trim()}
  >
    <SearchCode size={18} />
    {isScanning
      ? "Analyzing..."
      : "Analyze Repository"}
  </button>

  <button
    type="button"
    onClick={handleExportPdf}
    className="secondary-button"
    disabled={!repoUrl.trim()}
  >
    Export PDF
  </button>
</div>
              
          </form>
        </section>

        {error ? <ErrorPanel message={error} /> : null}

        {isScanning ? <LoadingPanel /> : null}

        {result && !isScanning ? (
          <div className="space-y-6">
            <div className="grid gap-4 sm:grid-cols-2 xl:grid-cols-6">
              <StatCard label="Files Scanned" value={String(result.files_scanned)} />
              <StatCard label="Issues Found" value={String(result.issues_found)} />
              <StatCard label="Critical" value={String(result.critical)} />
              <StatCard label="High" value={String(result.high)} />
              <StatCard label="Medium" value={String(result.medium)} />
              <StatCard label="Low" value={String(result.low)} />
            </div>

            <RepositoryHealthCard result={result} />

            <section className="rounded-md border border-slate-200 bg-white shadow-sm dark:border-ink-700 dark:bg-ink-900">
              <div className="border-b border-slate-200 px-5 py-4 dark:border-ink-700">
                <h2 className="text-lg font-semibold">Findings</h2>
              </div>
              <FindingsTable findings={result.findings} />
            </section>
          </div>
        ) : null}
      </div>
    </>
  );
}
