interface ErrorPanelProps {
  message: string;
}

export function ErrorPanel({ message }: ErrorPanelProps) {
  return (
    <div className="rounded-md border border-rose-200 bg-rose-50 p-4 text-sm text-rose-700 dark:border-rose-900 dark:bg-rose-950 dark:text-rose-200">
      {message}
    </div>
  );
}
