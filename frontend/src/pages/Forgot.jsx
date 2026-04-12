import { useState } from "react";
import { Link } from "react-router-dom";
import api from "../services/api";

export default function Forgot() {
  const [form, setForm] = useState({ username: "", email: "" });
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [success, setSuccess] = useState("");

  const handleChange = (e) => {
    setForm({ ...form, [e.target.name]: e.target.value });
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError("");
    setSuccess("");

    try {
      const res = await api.post("/forgot", {
        un: form.username,
        em: form.email,
      });
      setSuccess(res.data?.message || "A new temporary password has been sent to your email.");
    } catch (err) {
      setError(err.response?.data?.message || "Could not reset. Check username and email.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen flex bg-gradient-to-br from-slate-900 via-teal-900 to-slate-800 text-white">
      <div className="hidden md:flex flex-1 flex-col justify-center px-16 lg:px-20 border-r border-white/5">
        <p className="text-teal-400/90 text-sm font-semibold tracking-wide uppercase mb-3">
          Account recovery
        </p>
        <h1 className="text-4xl font-bold leading-tight mb-6">Reset access safely</h1>
        <p className="text-gray-300 text-lg mb-6 max-w-md leading-relaxed">
          We verify your username and registered email match, then issue a new temporary
          password the same way as initial signup.
        </p>
        <p className="text-sm text-gray-500 max-w-md">
          If email delivery is not configured on the server, check the terminal for a
          fallback password line from Flask.
        </p>
      </div>

      <div className="flex flex-1 items-center justify-center p-6">
        <div className="w-full max-w-md bg-white/10 backdrop-blur-xl border border-white/20 rounded-2xl shadow-2xl p-8">
          <p className="text-center text-teal-400/90 text-xs font-semibold uppercase tracking-wide mb-2">
            Password reset
          </p>
          <h2 className="text-2xl font-semibold text-center mb-2">Forgot password</h2>
          <p className="text-sm text-gray-400 text-center mb-6">
            Enter the details you used at registration.
          </p>

          {error ? (
            <div
              className="mb-4 text-sm text-red-200 text-center bg-red-500/15 border border-red-400/30 rounded-lg py-2 px-3"
              role="alert"
            >
              {error}
            </div>
          ) : null}
          {success ? (
            <div
              className="mb-4 text-sm text-emerald-200 text-center bg-emerald-500/15 border border-emerald-400/30 rounded-lg py-2 px-3"
              role="status"
            >
              {success}
            </div>
          ) : null}

          <form onSubmit={handleSubmit} className="space-y-5">
            <div>
              <label htmlFor="forgot-username" className="text-sm text-gray-300 mb-1 block">
                Username
              </label>
              <input
                id="forgot-username"
                type="text"
                name="username"
                autoComplete="username"
                value={form.username}
                onChange={handleChange}
                required
                placeholder="Your username"
                className="w-full h-11 px-4 rounded-lg bg-white/20 border border-white/20 text-white placeholder-gray-400 focus:outline-none focus-visible:ring-2 focus-visible:ring-teal-400"
              />
            </div>
            <div>
              <label htmlFor="forgot-email" className="text-sm text-gray-300 mb-1 block">
                Email
              </label>
              <input
                id="forgot-email"
                type="email"
                name="email"
                autoComplete="email"
                value={form.email}
                onChange={handleChange}
                required
                placeholder="Registered email"
                className="w-full h-11 px-4 rounded-lg bg-white/20 border border-white/20 text-white placeholder-gray-400 focus:outline-none focus-visible:ring-2 focus-visible:ring-teal-400"
              />
            </div>
            <button
              type="submit"
              disabled={loading}
              className="w-full py-3 rounded-xl bg-gradient-to-r from-teal-500 to-teal-600 text-white font-medium hover:from-teal-400 hover:to-teal-500 disabled:opacity-60 transition"
            >
              {loading ? "Processing…" : "Send new password"}
            </button>
          </form>

          <p className="text-sm text-center mt-6">
            <Link to="/login" className="text-teal-400 hover:underline">
              ← Back to sign in
            </Link>
          </p>
        </div>
      </div>
    </div>
  );
}
