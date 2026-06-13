export function formatDate(value: string): string {
  return new Intl.DateTimeFormat(undefined, {
    month: "short",
    day: "numeric",
    year: "numeric",
    hour: "numeric",
    minute: "2-digit",
  }).format(new Date(value));
}

export function averageScore(scores: number[]): number {
  if (scores.length === 0) {
    return 0;
  }

  return Math.round(scores.reduce((total, score) => total + score, 0) / scores.length);
}
