import { Code2, GitBranch, History, LayoutDashboard, LogOut, Moon, Plus, ShieldCheck, Sun } from "lucide-react";
import { NavLink, Outlet, useNavigate } from "react-router-dom";

import { useAuth } from "../contexts/AuthContext";
import { useTheme } from "../contexts/ThemeContext";

const navItems = [
  { to: "/dashboard", label: "Dashboard", icon: LayoutDashboard },
  { to: "/submit", label: "Submit", icon: Plus },
  { to: "/reviews", label: "Reviews", icon: History },
  { to: "/repository-review", label: "Repository Review", icon: GitBranch },
];

export function AppShell() {
  const { logout, user } = useAuth();
  const { theme, toggleTheme } = useTheme();
  const navigate = useNavigate();

  function handleLogout() {
    logout();
    navigate("/");
  }

  return (
    <div className="min-h-screen bg-slate-50 text-slate-950 dark:bg-ink-950 dark:text-slate-100">
      <aside className="fixed inset-y-0 left-0 z-20 hidden w-72 border-r border-slate-200 bg-white px-5 py-6 dark:border-ink-700 dark:bg-ink-900 lg:block">
        <NavLink to="/dashboard" className="flex items-center gap-3">
          <span className="flex h-10 w-10 items-center justify-center rounded-md bg-brand-600 text-white">
            <ShieldCheck size={22} />
          </span>
          <span>
            <span className="block text-sm font-semibold uppercase text-brand-600 dark:text-brand-400">
              AI Review
            </span>
            <span className="block text-lg font-semibold">Code Console</span>
          </span>
        </NavLink>

        <nav className="mt-10 space-y-2">
          {navItems.map((item) => (
            <NavLink
              key={item.to}
              to={item.to}
              className={({ isActive }) =>
                [
                  "flex items-center gap-3 rounded-md px-3 py-2.5 text-sm font-medium transition",
                  isActive
                    ? "bg-brand-600 text-white"
                    : "text-slate-600 hover:bg-slate-100 dark:text-slate-300 dark:hover:bg-ink-800",
                ].join(" ")
              }
            >
              <item.icon size={18} />
              {item.label}
            </NavLink>
          ))}
        </nav>

        <div className="absolute bottom-6 left-5 right-5">
          <div className="rounded-md border border-slate-200 p-3 dark:border-ink-700">
            <p className="truncate text-sm font-semibold">{user?.username}</p>
            <p className="truncate text-xs text-slate-500 dark:text-slate-400">{user?.email}</p>
          </div>
        </div>
      </aside>

      <div className="lg:pl-72">
        <header className="sticky top-0 z-10 border-b border-slate-200 bg-white/95 px-4 py-3 backdrop-blur dark:border-ink-700 dark:bg-ink-900/95 sm:px-6">
          <div className="mx-auto flex max-w-7xl items-center justify-between gap-3">
            <NavLink to="/dashboard" className="flex items-center gap-2 font-semibold lg:hidden">
              <Code2 size={22} className="text-brand-600" />
              AI Review
            </NavLink>
            <nav className="hidden items-center gap-2 lg:flex">
              <span className="text-sm text-slate-500 dark:text-slate-400">Backend</span>
              <span className="rounded-md bg-emerald-50 px-2 py-1 text-xs font-semibold text-emerald-700 dark:bg-emerald-950 dark:text-emerald-300">
                Connected
              </span>
            </nav>
            <div className="flex items-center gap-2">
              <button
                type="button"
                onClick={toggleTheme}
                className="icon-button"
                aria-label="Toggle dark mode"
                title="Toggle dark mode"
              >
                {theme === "dark" ? <Sun size={18} /> : <Moon size={18} />}
              </button>
              <button
                type="button"
                onClick={handleLogout}
                className="icon-button"
                aria-label="Log out"
                title="Log out"
              >
                <LogOut size={18} />
              </button>
            </div>
          </div>
          <nav className="mt-3 flex gap-2 overflow-x-auto lg:hidden">
            {navItems.map((item) => (
              <NavLink
                key={item.to}
                to={item.to}
                className={({ isActive }) =>
                  [
                    "flex shrink-0 items-center gap-2 rounded-md px-3 py-2 text-sm font-medium",
                    isActive
                      ? "bg-brand-600 text-white"
                      : "bg-slate-100 text-slate-700 dark:bg-ink-800 dark:text-slate-200",
                  ].join(" ")
                }
              >
                <item.icon size={16} />
                {item.label}
              </NavLink>
            ))}
          </nav>
        </header>

        <main className="mx-auto max-w-7xl px-4 py-6 sm:px-6 lg:py-8">
          <Outlet />
        </main>
      </div>
    </div>
  );
}
