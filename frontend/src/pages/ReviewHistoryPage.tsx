import { FileCode, Search } from "lucide-react";
import { useEffect, useMemo, useState } from "react";
import { Link } from "react-router-dom";

import { getApiErrorMessage } from "../api/client";
import { listReviews } from "../api/reviews";
import { EmptyState } from "../components/EmptyState";
import { ErrorPanel } from "../components/ErrorPanel";
import { LoadingPanel } from "../components/LoadingPanel";
import { PageHeader } from "../components/PageHeader";
import { ReviewScoreBadge } from "../components/ReviewScoreBadge";
import type { Review } from "../types/api";
import { formatDate } from "../utils/format";

export function ReviewHistoryPage() {
  const [reviews, setReviews] = useState<Review[]>([]);
  const [query, setQuery] = useState("");
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    async function loadReviews() {
      try {
        setReviews(await listReviews());
      } catch (requestError) {
        setError(getApiErrorMessage(requestError));
      } finally {
        setIsLoading(false);
      }
    }

    void loadReviews();
  }, []);

  const filteredReviews = useMemo(() => {
    const normalizedQuery = query.toLowerCase().trim();
    if (!normalizedQuery) {
      return reviews;
    }

    return reviews.filter((review) =>
      [review.summary, String(review.submission_id), String(review.overall_score)]
        .join(" ")
        .toLowerCase()
        .includes(normalizedQuery),
    );
  }, [query, reviews]);

  return (
    <>
      <PageHeader title="Review history" description="Browse previous AI reviews and inspect score breakdowns." />
      {error ? <ErrorPanel message={error} /> : null}
      {isLoading ? (
        <LoadingPanel />
      ) : (
        <section className="rounded-md border border-slate-200 bg-white shadow-sm dark:border-ink-700 dark:bg-ink-900">
          <div className="border-b border-slate-200 p-4 dark:border-ink-700">
            <label className="relative block">
              <Search size={18} className="pointer-events-none absolute left-3 top-1/2 -translate-y-1/2 text-slate-400" />
              <input
                value={query}
                onChange={(event) => setQuery(event.target.value)}
                className="w-full rounded-md border border-slate-300 bg-white py-2 pl-10 pr-3 text-sm outline-none focus:border-brand-500 focus:ring-2 focus:ring-brand-500/20 dark:border-ink-700 dark:bg-ink-950"
                placeholder="Search by summary, score, or submission id"
              />
            </label>
          </div>

          {filteredReviews.length ? (
            <div className="divide-y divide-slate-200 dark:divide-ink-700">
              {filteredReviews.map((review) => (
                <Link
                  key={review.id}
                  to={`/reviews/${review.id}`}
                  className="grid gap-4 px-5 py-4 transition hover:bg-slate-50 dark:hover:bg-ink-800 md:grid-cols-[1fr_auto]"
                >
                  <div>
                    <div className="flex items-center gap-2 text-sm font-semibold">
                      <FileCode size={16} className="text-brand-600 dark:text-brand-400" />
                      Submission #{review.submission_id}
                    </div>
                    <p className="mt-1 line-clamp-2 text-sm text-slate-600 dark:text-slate-400">{review.summary}</p>
                    <p className="mt-2 text-xs text-slate-500 dark:text-slate-500">{formatDate(review.created_at)}</p>
                  </div>
                  <div className="flex items-center gap-3">
                    <ReviewScoreBadge score={review.overall_score} />
                    <span className="text-sm text-slate-500 dark:text-slate-400">{review.comments.length} comments</span>
                  </div>
                </Link>
              ))}
            </div>
          ) : (
            <div className="p-5">
              <EmptyState title="No matching reviews" description="Try a different search or create a new review." />
            </div>
          )}
        </section>
      )}
    </>
  );
}
