import { useState, useRef } from "react";
import { Link, useNavigate } from "react-router-dom";
import api from "../services/api";

export default function Signup() {
  const navigate = useNavigate();
  const [form, setForm] = useState({ username: "", email: "" });
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [success, setSuccess] = useState("");
  /** Blocks a second submit before React re-renders `disabled` on the button (double-click race). */
  const submitLock = useRef(false);

  const handleChange = (e) => {
    setForm({ ...form, [e.target.name]: e.target.value });
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (submitLock.current) return;
    submitLock.current = true;
    setLoading(true);
    setError("");
    setSuccess("");

    try {
      const { data } = await api.post("/signup", {
        un: form.username,
        em: form.email,
      });
      setSuccess(
        data?.message ||
          "Account created. Check your email for your temporary password."
      );
      const pauseMs = data?.temporary_password != null ? 5000 : 1600;
      setTimeout(() => navigate("/login"), pauseMs);
    } catch (err) {
      setError(err.response?.data?.message || "Signup failed. Try again.");
    } finally {
      submitLock.current = false;
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen flex bg-gradient-to-br from-slate-900 via-teal-900 to-slate-800 text-white">
      <div className="hidden md:flex flex-1 flex-col justify-center px-16 lg:px-20 border-r border-white/5">
        <p className="text-teal-400/90 text-sm font-semibold tracking-wide uppercase mb-3">
          Get started
        </p>
        <h1 className="text-4xl lg:text-5xl font-bold leading-tight mb-6">
          Create your secure profile
        </h1>
        <p className="text-gray-300 text-lg mb-8 max-w-md leading-relaxed">
          We generate a one-time password and email it to you. After first login you can
          use the assessment tools and keep a private history tied to your username.
        </p>
        <ul className="space-y-3 text-sm text-gray-400">
          <li className="flex gap-3">
            <span className="text-teal-400 shrink-0" aria-hidden>
              ✓
            </span>
            Username must be unique (primary key in our database)
          </li>
          <li className="flex gap-3">
            <span className="text-teal-400 shrink-0" aria-hidden>
              ✓
            </span>
            Same clinical model as the original course project
          </li>
          <li className="flex gap-3">
            <span className="text-teal-400 shrink-0" aria-hidden>
              ✓
            </span>
            Educational use—not a substitute for medical care
          </li>
        </ul>
      </div>

      <div className="flex flex-1 items-center justify-center p-6">
        <div className="w-full max-w-md bg-white/10 backdrop-blur-xl border border-white/20 rounded-2xl shadow-2xl p-8">
          <p className="text-center text-teal-400/90 text-xs font-semibold uppercase tracking-wide mb-2">
            Register
          </p>
          <h2 className="text-2xl font-semibold text-center mb-6">Create account</h2>

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

          <form onSubmit={handleSubmit} className="space-y-5" aria-busy={loading}>
            <fieldset disabled={loading} className="space-y-5 border-0 p-0 m-0 min-w-0">
            <div>
              <label htmlFor="signup-username" className="text-sm text-gray-300 mb-1 block">
                Username
              </label>
              <input
                id="signup-username"
                type="text"
                name="username"
                autoComplete="username"
                value={form.username}
                onChange={handleChange}
                required
                placeholder="Choose a username"
                className="w-full h-11 px-4 rounded-lg bg-white/20 border border-white/20 text-white placeholder-gray-400 focus:outline-none focus-visible:ring-2 focus-visible:ring-teal-400"
              />
            </div>
            <div>
              <label htmlFor="signup-email" className="text-sm text-gray-300 mb-1 block">
                Email
              </label>
              <input
                id="signup-email"
                type="email"
                name="email"
                autoComplete="email"
                value={form.email}
                onChange={handleChange}
                required
                placeholder="you@example.com"
                className="w-full h-11 px-4 rounded-lg bg-white/20 border border-white/20 text-white placeholder-gray-400 focus:outline-none focus-visible:ring-2 focus-visible:ring-teal-400"
              />
            </div>
            <button
              type="submit"
              className="w-full py-3 rounded-xl bg-gradient-to-r from-teal-500 to-teal-600 text-white font-medium hover:from-teal-400 hover:to-teal-500 disabled:opacity-60 transition shadow-lg shadow-teal-900/20"
            >
              {loading ? "Creating…" : "Create account"}
            </button>
            </fieldset>
          </form>

          <p className="text-xs text-gray-400 text-center mt-4 leading-relaxed">
            A temporary password is generated on the server and emailed to you when
            delivery is configured.
          </p>
          <p className="text-sm text-center mt-4 text-gray-400">
            Already registered?{" "}
            <Link to="/login" className="text-teal-400 hover:underline font-medium">
              Sign in
            </Link>
          </p>
        </div>
      </div>
    </div>
  );
}
