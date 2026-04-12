import { Link, useNavigate } from "react-router-dom";
import api from "../services/api";

export function AppTopNav({ title, subtitle, extra }) {
  const navigate = useNavigate();

  return (
    <header className="max-w-6xl mx-auto w-full flex flex-col gap-4 sm:flex-row sm:items-start sm:justify-between text-white border-b border-white/10 pb-6 mb-8">
      <div>
        <p className="text-teal-400/90 text-xs font-semibold uppercase tracking-wide mb-1">
          Heart Risk AI
        </p>
        <h1 className="text-2xl font-bold tracking-tight">{title}</h1>
        {subtitle ? (
          <p className="text-sm text-gray-300 mt-1 max-w-xl">{subtitle}</p>
        ) : null}
      </div>
      <nav className="flex flex-wrap items-center gap-2 shrink-0" aria-label="App">
        <Link
          to="/dashboard"
          className="text-sm px-3 py-1.5 rounded-lg bg-white/10 hover:bg-white/15 border border-white/10 transition"
        >
          Dashboard
        </Link>
        <Link
          to="/prediction"
          className="text-sm px-3 py-1.5 rounded-lg bg-white/10 hover:bg-white/15 border border-white/10 transition"
        >
          Assessment
        </Link>
        <Link
          to="/history"
          className="text-sm px-3 py-1.5 rounded-lg bg-white/10 hover:bg-white/15 border border-white/10 transition"
        >
          History
        </Link>
        {extra}
        <button
          type="button"
          onClick={async () => {
            try {
              await api.post("/logout");
            } finally {
              navigate("/login");
            }
          }}
          className="text-sm px-3 py-1.5 rounded-lg text-red-200 bg-red-500/15 hover:bg-red-500/25 border border-red-400/30 transition"
        >
          Logout
        </button>
      </nav>
    </header>
  );
}
