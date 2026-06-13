import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  Tooltip,
  ResponsiveContainer,
  CartesianGrid,
} from "recharts";

type Props = {
  reviews: {
    id: number;
    overall_score: number;
  }[];
};

export function ReviewScoreTrend({ reviews }: Props) {
  const data = reviews.map((review) => ({
    review: `#${review.id}`,
    score: review.overall_score,
  }));

  return (
    <div className="rounded-md border border-slate-200 bg-white p-5 shadow-sm dark:border-ink-700 dark:bg-ink-900">
      <h2 className="mb-4 text-lg font-semibold">
        Review Score Trend
      </h2>

      <div className="h-80">
        <ResponsiveContainer width="100%" height="100%">
          <LineChart data={data}>
            <CartesianGrid strokeDasharray="3 3" />
            <XAxis dataKey="review" />
            <YAxis domain={[0, 100]} />
            <Tooltip />
            <Line
              type="monotone"
              dataKey="score"
              strokeWidth={3}
            />
          </LineChart>
        </ResponsiveContainer>
      </div>
    </div>
  );
}