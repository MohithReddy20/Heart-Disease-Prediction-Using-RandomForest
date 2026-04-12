import { Link } from "react-router-dom";

export default function NotFound() {
  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-900 via-slate-800 to-teal-950 text-white flex items-center justify-center p-6">
      <div className="text-center max-w-md">
        <p className="text-teal-400 text-sm font-semibold tracking-wide uppercase mb-2">
          404
        </p>
        <h1 className="text-3xl font-bold mb-3">Page not found</h1>
        <p className="text-gray-400 text-sm leading-relaxed mb-8">
          That route does not exist, or the link may be outdated. Use the app menu
          or start again from login.
        </p>
        <div className="flex flex-col sm:flex-row gap-3 justify-center">
          <Link
            to="/login"
            className="inline-flex justify-center rounded-xl bg-gradient-to-r from-teal-500 to-teal-600 px-5 py-2.5 text-sm font-medium hover:from-teal-400 hover:to-teal-500 transition"
          >
            Go to login
          </Link>
          <Link
            to="/dashboard"
            className="inline-flex justify-center rounded-xl border border-white/20 bg-white/5 px-5 py-2.5 text-sm font-medium hover:bg-white/10 transition"
          >
            Dashboard
          </Link>
        </div>
      </div>
    </div>
  );
}
