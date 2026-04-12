import { useEffect, useState } from "react";
import { Navigate, Outlet } from "react-router-dom";
import api from "../services/api";

/**
 * Ensures a valid Flask session before rendering child routes.
 */
export default function ProtectedRoute() {
  const [state, setState] = useState("loading");

  useEffect(() => {
    let cancelled = false;
    (async () => {
      try {
        await api.get("/me");
        if (!cancelled) setState("ok");
      } catch {
        if (!cancelled) setState("fail");
      }
    })();
    return () => {
      cancelled = true;
    };
  }, []);

  if (state === "loading") {
    return (
      <div className="min-h-screen bg-slate-900 flex flex-col items-center justify-center gap-3 text-white">
        <div
          className="h-9 w-9 border-2 border-teal-400 border-t-transparent rounded-full animate-spin"
          aria-hidden
        />
        <p className="text-sm text-gray-400">Checking your session…</p>
      </div>
    );
  }

  if (state === "fail") {
    return <Navigate to="/login" replace />;
  }

  return <Outlet />;
}
