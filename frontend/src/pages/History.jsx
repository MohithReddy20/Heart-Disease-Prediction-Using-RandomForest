import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import { API_BASE } from "../config.js";
import { AppTopNav } from "../components/AppTopNav";

export default function History() {
  const [history, setHistory] = useState([]);
  const [trend, setTrend] = useState(null);
  const [loading, setLoading] = useState(true);
  const navigate = useNavigate();

  useEffect(() => {
    const fetchHistory = async () => {
      try {
        const res = await fetch(`${API_BASE}/api/history`, {
          credentials: "include",
        });

        if (res.status === 401) {
          navigate("/login");
          return;
        }

        if (!res.ok) {
          const text = await res.text();
          console.error("History API error:", res.status, text.slice(0, 200));
          setHistory([]);
          setTrend(null);
          return;
        }

        const data = await res.json();
        setHistory(Array.isArray(data.rows) ? data.rows : []);
        setTrend(data.trend);
      } catch (err) {
        console.error("History fetch error:", err);
      } finally {
        setLoading(false);
      }
    };

    fetchHistory();
  }, [navigate]);

  const getTrendStyle = () => {
    if (trend === "increasing")
      return "bg-red-500/20 text-red-100 border-red-400/50";
    if (trend === "decreasing")
      return "bg-emerald-500/20 text-emerald-100 border-emerald-400/50";
    return "bg-white/10 text-gray-200 border-white/20";
  };

  const getRiskColor = (level) => {
    if (level === "Low") return "text-emerald-400";
    if (level === "Moderate") return "text-amber-300";
    return "text-red-400";
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-[#0f172a] via-[#0b3c5d] to-[#115e59] p-6 md:p-8">
      <div className="max-w-6xl mx-auto space-y-8">
        <AppTopNav
          title="Assessment history"
          subtitle="Chronological view of your saved model runs. Compare scores over time."
        />

        {trend ? (
          <div className={`p-4 rounded-xl border ${getTrendStyle()}`}>
            <strong className="font-semibold">Risk trend:</strong>{" "}
            {trend === "increasing" && "Your estimated risk increased versus the previous assessment."}
            {trend === "decreasing" && "Your estimated risk decreased versus the previous assessment."}
            {trend === "stable" && "Your estimated risk is unchanged between the last two assessments."}
          </div>
        ) : null}

        {loading ? (
          <div className="flex justify-center py-12" aria-live="polite">
            <div className="h-9 w-9 border-2 border-white border-t-transparent rounded-full animate-spin" />
          </div>
        ) : null}

        {!loading && history.length === 0 ? (
          <div className="text-center rounded-2xl border border-white/10 bg-white/5 py-14 px-6 text-gray-300">
            <p className="text-lg font-medium text-white mb-2">No history yet</p>
            <p className="text-sm max-w-md mx-auto leading-relaxed">
              Run an assessment from the prediction page. Each completed run is stored
              here with timestamp and inputs summary.
            </p>
          </div>
        ) : null}

        {!loading && history.length > 0 ? (
          <div className="space-y-4">
            {history.map((row, index) => (
              <div
                key={`${row.timestamp}-${index}`}
                className="bg-white/95 backdrop-blur-md p-5 rounded-2xl shadow-lg border border-white/20 hover:border-teal-400/30 transition"
              >
                <div className="flex flex-wrap justify-between items-start gap-3">
                  <div>
                    <p className="text-sm text-gray-500 font-medium">
                      {row.timestamp || "N/A"}
                    </p>
                    <p className="text-2xl font-bold text-slate-800 tabular-nums">
                      {row.probability ?? 0}%
                    </p>
                  </div>
                  <span className={`text-sm font-bold px-3 py-1 rounded-full bg-slate-100 ${getRiskColor(row.risk_level)}`}>
                    {row.risk_level}
                  </span>
                </div>

                <div className="mt-4 grid grid-cols-3 gap-2 text-sm text-gray-600">
                  <div>
                    <span className="text-gray-400">Age</span> {row.age ?? "—"}
                  </div>
                  <div>
                    <span className="text-gray-400">BP</span> {row.bp ?? "—"}
                  </div>
                  <div>
                    <span className="text-gray-400">Chol</span> {row.chol ?? "—"}
                  </div>
                </div>

                <div className="mt-3 pt-3 border-t border-gray-100">
                  {row.prediction === 1 ? (
                    <span className="text-red-600 text-sm font-semibold">
                      Model class: likely heart disease pattern
                    </span>
                  ) : (
                    <span className="text-emerald-700 text-sm font-semibold">
                      Model class: unlikely heart disease pattern
                    </span>
                  )}
                </div>
              </div>
            ))}
          </div>
        ) : null}
      </div>
    </div>
  );
}
