import { ArrowRight, FileCode, History, Plus } from "lucide-react";
import { ReviewScoreTrend } from "../components/charts/ReviewScoreTrend";
import { useEffect, useMemo, useState } from "react";
import { Link } from "react-router-dom";

import { listReviews } from "../api/reviews";
import { listSubmissions } from "../api/submissions";
import { getApiErrorMessage } from "../api/client";
import { EmptyState } from "../components/EmptyState";
import { ErrorPanel } from "../components/ErrorPanel";
import { LoadingPanel } from "../components/LoadingPanel";
import { PageHeader } from "../components/PageHeader";
import { ReviewScoreBadge } from "../components/ReviewScoreBadge";
import { StatCard } from "../components/StatCard";
import type { Review, Submission } from "../types/api";
import { averageScore, formatDate } from "../utils/format";

export function DashboardPage() {
  const [submissions, setSubmissions] = useState<Submission[]>([]);
  const [reviews, setReviews] = useState<Review[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    async function loadDashboard() {
      try {
        const [submissionData, reviewData] = await Promise.all([
          listSubmissions(),
          listReviews(),
        ]);
        setSubmissions(submissionData);
        setReviews(reviewData);
      } catch (requestError) {
        setError(getApiErrorMessage(requestError));
      } finally {
        setIsLoading(false);
      }
    }

    void loadDashboard();
  }, []);

  const average = useMemo(
    () => averageScore(reviews.map((review) => review.overall_score)),
    [reviews],
  );
  const averageSecurity = useMemo(() => {
  if (!reviews.length) return 0;

  return Math.round(
    reviews.reduce(
      (sum, review) => sum + review.security_score,
      0
    ) / reviews.length
  );
}, [reviews]);

const severityStats = useMemo(() => {
  return reviews
    .flatMap((review) => review.comments)
    .reduce(
      (acc, comment) => {
        const severity = comment.severity.toLowerCase();

        if (severity === "critical") acc.critical++;
        else if (severity === "high") acc.high++;
        else if (severity === "medium") acc.medium++;
        else if (severity === "low") acc.low++;

        return acc;
      },
      {
        critical: 0,
        high: 0,
        medium: 0,
        low: 0,
      }
    );
}, [reviews]);

const topIssues = useMemo(() => {
  const issueCounts: Record<string, number> = {};

  reviews
    .flatMap((review) => review.comments)
    .forEach((comment) => {
      issueCounts[comment.comment] =
        (issueCounts[comment.comment] || 0) + 1;
    });

  return Object.entries(issueCounts)
    .sort((a, b) => b[1] - a[1])
    .slice(0, 5);
}, [reviews]);


  const recentReviews = reviews.slice(0, 5);

  return (
    <>
      <PageHeader
        title="Dashboard"
        description="Track submission volume, review coverage, and quality signals from AI-generated reviews."
        action={
          <Link to="/submit" className="primary-button">
            <Plus size={18} />
            New submission
          </Link>
        }
      />

      {error ? <ErrorPanel message={error} /> : null}
      {isLoading ? (
        <LoadingPanel />
      ) : (
        <div className="space-y-6">
          <div className="grid gap-4 sm:grid-cols-2 xl:grid-cols-4">
            <StatCard label="Total submissions" value={String(submissions.length)} helper="Code snippets submitted" />
            <StatCard label="Total reviews" value={String(reviews.length)} helper="AI reviews generated" />
            <StatCard
  label="Critical Issues"
  value={String(severityStats.critical)}
  helper="Critical vulnerabilities"
/>

<StatCard
  label="High Issues"
  value={String(severityStats.high)}
  helper="High severity findings"
/>
          </div>
          <div className="grid gap-4 sm:grid-cols-2 xl:grid-cols-4">
  <StatCard
    label="Medium Issues"
    value={String(severityStats.medium)}
    helper="Medium severity findings"
  />

  <StatCard
    label="Low Issues"
    value={String(severityStats.low)}
    helper="Low severity findings"
  />

  <StatCard
    label="Average Score"
    value={reviews.length ? String(average) : "N/A"}
    helper="Overall review score"
  />

  <StatCard
    label="Security Average"
    value={String(averageSecurity)}
    helper="Average security score"
  />
</div>

          <div className="grid gap-6">
  <ReviewScoreTrend reviews={reviews} />
</div>

<section className="rounded-md border border-slate-200 bg-white shadow-sm dark:border-ink-700 dark:bg-ink-900">
  <div className="border-b border-slate-200 px-5 py-4 dark:border-ink-700">
    <h2 className="text-lg font-semibold">
      Top Security Problems
    </h2>
  </div>

  <div className="p-5">
    {topIssues.length ? (
      <div className="space-y-3">
        {topIssues.map(([issue, count]) => (
          <div
            key={issue}
            className="flex items-center justify-between"
          >
            <span className="text-sm">{issue}</span>

            <span className="rounded bg-red-500/10 px-2 py-1 text-xs font-semibold text-red-400">
              {count}
            </span>
          </div>
        ))}
      </div>
    ) : (
      <p className="text-sm text-slate-500">
        No issues detected yet.
      </p>
    )}
  </div>
</section>

<section className="rounded-md border border-slate-200 bg-white shadow-sm dark:border-ink-700 dark:bg-ink-900">
            <div className="flex items-center justify-between border-b border-slate-200 px-5 py-4 dark:border-ink-700">
              <div>
                <h2 className="text-lg font-semibold">Recent reviews</h2>
                <p className="text-sm text-slate-500 dark:text-slate-400">Latest generated code review results</p>
              </div>
              <Link to="/reviews" className="secondary-button">
                View all
                <ArrowRight size={16} />
              </Link>
            </div>
            {recentReviews.length ? (
              <div className="divide-y divide-slate-200 dark:divide-ink-700">
                {recentReviews.map((review) => (
                  <Link
                    key={review.id}
                    to={`/reviews/${review.id}`}
                    className="flex flex-col gap-3 px-5 py-4 transition hover:bg-slate-50 dark:hover:bg-ink-800 sm:flex-row sm:items-center sm:justify-between"
                  >
                    <div className="min-w-0">
                      <div className="flex items-center gap-2 text-sm font-semibold">
                        <FileCode size={16} className="text-brand-600 dark:text-brand-400" />
                        Submission #{review.submission_id}
                      </div>
                      <p className="mt-1 line-clamp-2 text-sm text-slate-600 dark:text-slate-400">{review.summary}</p>
                      <p className="mt-2 flex items-center gap-2 text-xs text-slate-500 dark:text-slate-500">
                        <History size={14} />
                        {formatDate(review.created_at)}
                      </p>
                    </div>
                    <ReviewScoreBadge score={review.overall_score} />
                  </Link>
                ))}
              </div>
            ) : (
              <div className="p-5">
                <EmptyState
                  title="No reviews yet"
                  description="Submit code and generate a review to populate your dashboard metrics."
                  action={<Link to="/submit" className="primary-button">Create first review</Link>}
                />
              </div>
            )}
          </section>
        </div>
      )}
    </>
  );
}
