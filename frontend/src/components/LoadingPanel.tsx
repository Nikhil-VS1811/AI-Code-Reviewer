export function LoadingPanel() {
  return (
    <div className="flex min-h-64 items-center justify-center rounded-md border border-slate-200 bg-white dark:border-ink-700 dark:bg-ink-900">
      <div className="h-9 w-9 animate-spin rounded-full border-2 border-slate-300 border-t-brand-500" />
    </div>
  );
}
