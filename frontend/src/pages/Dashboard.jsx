import { Link, useNavigate } from "react-router-dom";
import { useEffect, useState } from "react";
import api from "../services/api";
import heroIllustration from "../assets/dashboard-hero.svg";
import insightIllustration from "../assets/dashboard-insight.svg";

export default function Dashboard() {
  const navigate = useNavigate();

  const [username, setUsername] = useState("");
  const [risk, setRisk] = useState(null);

  useEffect(() => {
    const fetchUser = async () => {
      try {
        const res = await api.get("/me");
        setUsername(res.data.username);
      } catch {
        navigate("/login");
      }
    };

    const fetchLastPrediction = async () => {
      try {
        const res = await api.get("/last_prediction");
        if (res.data?.score == null) {
          setRisk(null);
        } else {
          setRisk(res.data);
        }
      } catch {
        setRisk(null);
      }
    };

    fetchUser();
    fetchLastPrediction();
  }, [navigate]);

  return (
    <div className="min-h-screen bg-slate-900 text-white">
      <div className="flex flex-wrap justify-between items-center gap-3 px-6 md:px-10 py-4 border-b border-white/10 max-w-6xl mx-auto w-full">
        <h1 className="text-xl font-semibold tracking-tight">Heart Risk AI</h1>
        <nav className="flex flex-wrap items-center gap-2">
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
          <button
            type="button"
            onClick={async () => {
              await api.post("/logout");
              navigate("/login");
            }}
            className="text-sm px-3 py-1.5 rounded-lg text-red-200 bg-red-500/15 hover:bg-red-500/25 border border-red-400/30 transition"
          >
            Logout
          </button>
        </nav>
      </div>

      <div className="max-w-6xl mx-auto px-6 md:px-10 pb-16 pt-8 space-y-10">
        {/* Hero */}
        <section className="grid lg:grid-cols-[1.05fr_0.95fr] gap-10 items-center">
          <div>
            <p className="text-teal-400/90 text-sm font-semibold tracking-wide uppercase mb-3">
              Personal dashboard
            </p>
            <h2 className="text-3xl md:text-4xl font-bold mb-4 leading-tight">
              Welcome back{username ? `, ${username}` : ""}
            </h2>
            <p className="text-gray-300 text-base leading-relaxed mb-6 max-w-xl">
              Review your latest cardiovascular risk estimate, compare trends over
              time, and run a new assessment whenever your vitals or lifestyle
              inputs change. Built for clarity and prevention—not clinical diagnosis.
            </p>
            <ul className="space-y-2 text-sm text-gray-400">
              <li className="flex gap-2">
                <span className="text-teal-400 shrink-0">✓</span>
                <span>Secure session; your history stays tied to your account.</span>
              </li>
              <li className="flex gap-2">
                <span className="text-teal-400 shrink-0">✓</span>
                <span>Random Forest model trained on structured heart-health features.</span>
              </li>
            </ul>
          </div>
          <div className="relative flex justify-center lg:justify-end">
            <div className="absolute inset-0 bg-teal-500/10 blur-3xl rounded-full scale-90 pointer-events-none" />
            <img
              src={heroIllustration}
              alt=""
              className="relative w-full max-w-md rounded-2xl shadow-lg shadow-black/30 ring-1 ring-white/10"
              width={560}
              height={360}
            />
          </div>
        </section>

        {/* Main cards */}
        <section className="grid md:grid-cols-2 gap-6">
          <div className="bg-white/10 border border-white/10 rounded-2xl p-6 md:p-7">
            <h3 className="text-lg font-semibold mb-1">Last assessment</h3>
            <p className="text-gray-400 text-sm mb-6">
              Most recent model output for your account.
            </p>

            {risk ? (
              <>
                <div className="text-4xl md:text-5xl font-bold mb-2 text-teal-400 tabular-nums">
                  {risk.score}%
                </div>
                <div className="text-sm mb-5">
                  {risk.level === "High" && (
                    <span className="text-red-400 font-medium">High risk band</span>
                  )}
                  {risk.level === "Moderate" && (
                    <span className="text-yellow-400 font-medium">Moderate risk band</span>
                  )}
                  {risk.level === "Low" && (
                    <span className="text-green-400 font-medium">Low risk band</span>
                  )}
                </div>
                <div className="w-full h-2 bg-white/10 rounded-full overflow-hidden">
                  <div
                    className="h-2 bg-gradient-to-r from-teal-500 to-cyan-400 rounded-full transition-all duration-500"
                    style={{ width: `${Math.min(100, risk.score)}%` }}
                  />
                </div>
              </>
            ) : (
              <p className="text-gray-400 text-sm leading-relaxed">
                No prediction yet. Run a full assessment to populate this card with
                your latest risk score and band.
              </p>
            )}
          </div>

          <div className="bg-white/10 border border-white/10 rounded-2xl p-6 md:p-7 flex flex-col justify-between">
            <div>
              <h3 className="text-lg font-semibold mb-1">Next steps</h3>
              <p className="text-gray-400 text-sm mb-6">
                Continue your workflow in a couple of clicks.
              </p>
            </div>
            <div className="space-y-3">
              <button
                type="button"
                onClick={() => navigate("/prediction")}
                className="w-full py-3 rounded-xl bg-gradient-to-r from-teal-500 to-teal-600 hover:from-teal-400 hover:to-teal-500 font-medium shadow-lg shadow-teal-900/30 transition"
              >
                Start new prediction
              </button>
              <button
                type="button"
                onClick={() => navigate("/history")}
                className="w-full py-3 rounded-xl bg-white/10 hover:bg-white/15 border border-white/10 transition font-medium"
              >
                View assessment history
              </button>
            </div>
          </div>
        </section>

        {/* Feature strip */}
        <section className="grid sm:grid-cols-3 gap-4">
          {[
            {
              title: "Evidence-style inputs",
              body: "Age, blood pressure, cholesterol, and related signals the model was trained on.",
            },
            {
              title: "Transparent outputs",
              body: "Risk score, category, and history so you can see change over time—not a black box.",
            },
            {
              title: "Responsible scope",
              body: "Educational use only; always follow your clinician for diagnosis and treatment.",
            },
          ].map((item) => (
            <div
              key={item.title}
              className="rounded-2xl border border-white/10 bg-slate-800/40 p-5 hover:border-teal-500/30 transition"
            >
              <h4 className="font-semibold text-white mb-2 text-sm">{item.title}</h4>
              <p className="text-gray-400 text-sm leading-relaxed">{item.body}</p>
            </div>
          ))}
        </section>

        {/* About + visual */}
        <section className="grid lg:grid-cols-[0.9fr_1.1fr] gap-10 items-start border-t border-white/10 pt-10">
          <div className="flex justify-center lg:justify-start">
            <img
              src={insightIllustration}
              alt=""
              className="w-full max-w-sm rounded-2xl ring-1 ring-white/10 opacity-95"
              width={320}
              height={240}
            />
          </div>
          <div className="space-y-6">
            <div>
              <h3 className="text-lg font-semibold mb-2">About this system</h3>
              <p className="text-gray-400 text-sm leading-relaxed">
                Heart Risk AI applies a validated supervised-learning pipeline to the
                same class of structured attributes used in classic heart-disease
                datasets. It is meant to support awareness, self-education, and
                conversations with qualified health professionals—not to replace them.
              </p>
            </div>
            <div className="rounded-2xl bg-amber-500/10 border border-amber-500/20 p-4">
              <h4 className="text-amber-200 text-sm font-semibold mb-2">Important</h4>
              <p className="text-amber-100/80 text-sm leading-relaxed">
                Do not use this tool for emergency decisions. If you have chest pain,
                sudden shortness of breath, or other acute symptoms, seek emergency
                care immediately.
              </p>
            </div>
            <div>
              <h3 className="text-lg font-semibold mb-2">Quick clinical context</h3>
              <p className="text-gray-400 text-sm leading-relaxed">
                Sustained high blood pressure, unfavourable cholesterol patterns, and
                reduced heart-rate reserve on exercise testing are among the most
                discussed markers in population cardiovascular risk models—aligned with
                the kinds of inputs you provide here.
              </p>
            </div>
          </div>
        </section>
      </div>
    </div>
  );
}
