import { useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import api from "../services/api";

export default function Login() {
  const navigate = useNavigate();
  const [form, setForm] = useState({ username: "", password: "" });
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  const handleChange = (e) => {
    setForm({ ...form, [e.target.name]: e.target.value });
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError("");

    try {
      await api.post("/login", {
        un: form.username,
        pw: form.password,
      });
      navigate("/dashboard");
    } catch (err) {
      setError(err.response?.data?.message || "Invalid credentials");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen flex bg-gradient-to-br from-slate-900 via-teal-900 to-slate-800 text-white">
      <div className="hidden md:flex flex-1 flex-col justify-center px-16 lg:px-20 border-r border-white/5">
        <p className="text-teal-400/90 text-sm font-semibold tracking-wide uppercase mb-3">
          Clinical decision support
        </p>
        <h1 className="text-4xl lg:text-5xl font-bold leading-tight mb-6">
          Intelligent heart risk analysis
        </h1>
        <p className="text-gray-300 text-lg mb-8 max-w-md leading-relaxed">
          Secure access to personalized cardiovascular risk estimates, history, and
          educational context—built for awareness, not diagnosis.
        </p>
        <ul className="space-y-3 text-sm text-gray-400">
          <li className="flex gap-3">
            <span className="text-teal-400 shrink-0" aria-hidden>
              ✓
            </span>
            Track risk trends across assessments
          </li>
          <li className="flex gap-3">
            <span className="text-teal-400 shrink-0" aria-hidden>
              ✓
            </span>
            Transparent model outputs and drivers
          </li>
          <li className="flex gap-3">
            <span className="text-teal-400 shrink-0" aria-hidden>
              ✓
            </span>
            Session-based access to your saved history
          </li>
        </ul>
      </div>

      <div className="flex flex-1 items-center justify-center p-6">
        <div className="w-full max-w-md bg-white/10 backdrop-blur-xl border border-white/20 rounded-2xl shadow-2xl p-8">
          <p className="text-center text-teal-400/90 text-xs font-semibold uppercase tracking-wide mb-2">
            Sign in
          </p>
          <h2 className="text-2xl font-semibold text-center mb-6">Welcome back</h2>

          {error ? (
            <div
              className="mb-4 text-sm text-red-200 text-center bg-red-500/15 border border-red-400/30 rounded-lg py-2 px-3"
              role="alert"
            >
              {error}
            </div>
          ) : null}

          <form onSubmit={handleSubmit} className="space-y-5">
            <div>
              <label htmlFor="login-username" className="text-sm text-gray-300 mb-1 block">
                Username
              </label>
              <input
                id="login-username"
                type="text"
                name="username"
                autoComplete="username"
                value={form.username}
                onChange={handleChange}
                required
                placeholder="Enter username"
                className="w-full h-11 px-4 rounded-lg bg-white/20 border border-white/20 text-white placeholder-gray-400 focus:outline-none focus-visible:ring-2 focus-visible:ring-teal-400"
              />
            </div>
            <div>
              <label htmlFor="login-password" className="text-sm text-gray-300 mb-1 block">
                Password
              </label>
              <input
                id="login-password"
                type="password"
                name="password"
                autoComplete="current-password"
                value={form.password}
                onChange={handleChange}
                required
                placeholder="Enter password"
                className="w-full h-11 px-4 rounded-lg bg-white/20 border border-white/20 text-white placeholder-gray-400 focus:outline-none focus-visible:ring-2 focus-visible:ring-teal-400"
              />
            </div>
            <button
              type="submit"
              disabled={loading}
              className="w-full py-3 rounded-xl bg-gradient-to-r from-teal-500 to-teal-600 text-white font-medium hover:from-teal-400 hover:to-teal-500 disabled:opacity-60 transition shadow-lg shadow-teal-900/20"
            >
              {loading ? "Signing in…" : "Sign in"}
            </button>
          </form>

          <p className="text-sm text-center mt-6 text-gray-400">
            New user?{" "}
            <Link to="/signup" className="text-teal-400 hover:underline font-medium">
              Create an account
            </Link>
          </p>
          <p className="text-sm text-center mt-2">
            <Link to="/forgot" className="text-teal-400 hover:underline">
              Forgot password?
            </Link>
          </p>
        </div>
      </div>
    </div>
  );
}
