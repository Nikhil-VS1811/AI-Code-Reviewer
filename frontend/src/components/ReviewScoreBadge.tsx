interface ReviewScoreBadgeProps {
  score: number;
}

export function ReviewScoreBadge({ score }: ReviewScoreBadgeProps) {
  const tone =
    score >= 80
      ? "bg-emerald-50 text-emerald-700 dark:bg-emerald-950 dark:text-emerald-300"
      : score >= 60
        ? "bg-amber-50 text-amber-700 dark:bg-amber-950 dark:text-amber-300"
        : "bg-rose-50 text-rose-700 dark:bg-rose-950 dark:text-rose-300";

  return (
    <span className={`inline-flex min-w-14 items-center justify-center rounded-md px-2.5 py-1 text-sm font-semibold ${tone}`}>
      {score}
    </span>
  );
}
