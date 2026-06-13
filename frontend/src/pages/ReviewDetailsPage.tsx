import { ArrowLeft, Download, FileCode } from "lucide-react";
import { useEffect, useState } from "react";
import { Link, useParams } from "react-router-dom";

import { getApiErrorMessage } from "../api/client";
import { exportReviewPdf, getReview } from "../api/reviews";
import { getSubmission } from "../api/submissions";
import { ErrorPanel } from "../components/ErrorPanel";
import { LoadingPanel } from "../components/LoadingPanel";
import { PageHeader } from "../components/PageHeader";
import { ReviewScoreBadge } from "../components/ReviewScoreBadge";
import type { Review, Submission } from "../types/api";
import { formatDate } from "../utils/format";

export function ReviewDetailsPage() {
  const { reviewId } = useParams();
  const [review, setReview] = useState<Review | null>(null);
  const [submission, setSubmission] = useState<Submission | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [isExporting, setIsExporting] = useState(false);
  const [error, setError] = useState("");

  useEffect(() => {
    async function loadReview() {
      if (!reviewId) {
        setError("Review id is missing.");
        setIsLoading(false);
        return;
      }

      try {
        const reviewData = await getReview(Number(reviewId));
        setReview(reviewData);
        setSubmission(await getSubmission(reviewData.submission_id));
      } catch (requestError) {
        setError(getApiErrorMessage(requestError));
      } finally {
        setIsLoading(false);
      }
    }

    void loadReview();
  }, [reviewId]);

  if (isLoading) {
    return <LoadingPanel />;
  }

  if (error || !review) {
    return <ErrorPanel message={error || "Review not found."} />;
  }

  const scores = [
    ["Security", review.security_score],
    ["Performance", review.performance_score],
    ["Maintainability", review.maintainability_score],
    ["Readability", review.readability_score],
  ] as const;
  const loadedReview = review;

  async function handleExportPdf() {
    setError("");
    setIsExporting(true);

    try {
      const pdf = await exportReviewPdf(loadedReview.id);
      const url = URL.createObjectURL(pdf);
      const link = document.createElement("a");
      link.href = url;
      link.download = `review-${loadedReview.id}.pdf`;
      document.body.appendChild(link);
      link.click();
      link.remove();
      URL.revokeObjectURL(url);
    } catch (requestError) {
      setError(getApiErrorMessage(requestError));
    } finally {
      setIsExporting(false);
    }
  }

  return (
    <>
      <PageHeader
        title={`Review #${review.id}`}
        description={`Generated ${formatDate(review.created_at)} for submission #${review.submission_id}.`}
        action={
          <div className="flex flex-wrap gap-2">
            <button
              type="button"
              onClick={handleExportPdf}
              className="primary-button"
              disabled={isExporting}
            >
              <Download size={16} />
              {isExporting ? "Exporting..." : "Export PDF"}
            </button>
            <Link to="/reviews" className="secondary-button">
              <ArrowLeft size={16} />
              Back to history
            </Link>
          </div>
        }
      />

      {error ? <ErrorPanel message={error} /> : null}

      <div className="grid gap-6 xl:grid-cols-[1fr_420px]">
        <section className="space-y-6">
          <div className="rounded-md border border-slate-200 bg-white p-5 dark:border-ink-700 dark:bg-ink-900">
            <div className="flex items-start justify-between gap-4">
              <div>
                <p className="text-sm font-medium text-slate-500 dark:text-slate-400">Overall score</p>
                <p className="mt-2 text-4xl font-semibold">{review.overall_score}</p>
              </div>
              <ReviewScoreBadge score={review.overall_score} />
            </div>
            <p className="mt-4 text-sm leading-6 text-slate-700 dark:text-slate-300">{review.summary}</p>
          </div>

          <div className="grid gap-4 sm:grid-cols-2">
            {scores.map(([label, score]) => (
              <div key={label} className="rounded-md border border-slate-200 bg-white p-4 dark:border-ink-700 dark:bg-ink-900">
                <div className="flex items-center justify-between">
                  <p className="text-sm font-semibold">{label}</p>
                  <span className="text-sm font-semibold">{score}/100</span>
                </div>
                <div className="mt-3 h-2 rounded-full bg-slate-100 dark:bg-ink-800">
                  <div className="h-2 rounded-full bg-brand-600" style={{ width: `${score}%` }} />
                </div>
              </div>
            ))}
          </div>

          <section className="rounded-md border border-slate-200 bg-white dark:border-ink-700 dark:bg-ink-900">
            <div className="border-b border-slate-200 px-5 py-4 dark:border-ink-700">
              <h2 className="text-lg font-semibold">Review comments</h2>
            </div>
            <div className="divide-y divide-slate-200 dark:divide-ink-700">
              {review.comments.map((comment) => (
                <article key={comment.id} className="p-5">
                  <div className="flex flex-wrap items-center gap-2">
                    <span className="rounded-md bg-slate-100 px-2 py-1 text-xs font-semibold text-slate-700 dark:bg-ink-800 dark:text-slate-300">
                      Line {comment.line_number}
                    </span>
                    <span className="rounded-md bg-brand-50 px-2 py-1 text-xs font-semibold text-brand-700 dark:bg-brand-500/10 dark:text-brand-400">
                      {comment.category}
                    </span>
                    <span className="rounded-md bg-amber-50 px-2 py-1 text-xs font-semibold text-amber-700 dark:bg-amber-950 dark:text-amber-300">
                      {comment.severity}
                    </span>
                  </div>
                  <p className="mt-3 text-sm leading-6 text-slate-700 dark:text-slate-300">{comment.comment}</p>
                </article>
              ))}
            </div>
          </section>
        </section>

        <aside className="rounded-md border border-slate-200 bg-white p-5 dark:border-ink-700 dark:bg-ink-900">
          <div className="mb-4 flex items-center gap-2 text-sm font-semibold">
            <FileCode size={16} className="text-brand-600 dark:text-brand-400" />
            Submitted code
          </div>
          <p className="mb-3 text-xs uppercase text-slate-500 dark:text-slate-400">
            {submission?.language ?? "unknown"}
          </p>
          <pre className="max-h-[720px] overflow-auto rounded-md bg-slate-950 p-4 text-sm leading-6 text-slate-100">
            <code>{submission?.code ?? "Code unavailable."}</code>
          </pre>
        </aside>
      </div>
    </>
  );
}
