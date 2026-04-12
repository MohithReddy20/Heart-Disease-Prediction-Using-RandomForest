import { useState } from "react";

function riskChipClasses(riskCss) {
  if (riskCss === "low-risk")
    return "bg-emerald-50 text-emerald-900 border border-emerald-200";
  if (riskCss === "moderate-risk")
    return "bg-amber-50 text-amber-950 border border-amber-200";
  return "bg-red-50 text-red-900 border border-red-200";
}

function riskBarClass(riskCss) {
  if (riskCss === "low-risk") return "bg-gradient-to-r from-emerald-500 to-teal-500";
  if (riskCss === "moderate-risk") return "bg-gradient-to-r from-amber-400 to-amber-500";
  return "bg-gradient-to-r from-red-500 to-rose-600";
}

export default function PredictionResult({ data, baseline }) {
  const [showNarrative, setShowNarrative] = useState(false);
  const [showInsights, setShowInsights] = useState(false);
  const [showReport, setShowReport] = useState(false);

  const score = Number(data?.risk_score_percent || 0);
  const riskCss = data?.risk_css || "moderate-risk";
  const recommendations = data?.clinical_report?.recommendations ?? [];

  return (
    <div className="space-y-4 max-h-[85vh] overflow-y-auto pr-1 md:pr-2 animate-fadeIn">
      <div className="bg-white/95 backdrop-blur-md p-5 md:p-6 rounded-2xl shadow-xl border border-white/20">
        <p className="text-xs font-semibold text-gray-500 uppercase tracking-wide">Risk score</p>

        <div className="flex flex-wrap justify-between items-center gap-3 mt-1">
          <h2 className="text-3xl md:text-4xl font-bold text-slate-900 tabular-nums">{score}%</h2>
          <span
            className={`px-3 py-1.5 rounded-full text-sm font-semibold ${riskChipClasses(riskCss)}`}
          >
            {data.risk_level}
          </span>
        </div>

        <div className="w-full h-2.5 bg-slate-200 rounded-full mt-4 overflow-hidden">
          <div
            className={`h-full rounded-full ${riskBarClass(riskCss)} transition-all duration-500`}
            style={{ width: `${Math.min(100, score)}%` }}
          />
        </div>

        <p className="text-sm text-gray-600 mt-3">
          Confidence: <span className="font-semibold text-slate-800">{data.confidence_level}</span>
          <span className="text-gray-500"> — {data.confidence_note}</span>
        </p>

        {data.stability_note ? (
          <p className="text-xs text-gray-500 mt-1">{data.stability_note}</p>
        ) : null}
      </div>

      {baseline !== null && !Number.isNaN(baseline) ? (
        <div className="bg-slate-50/95 backdrop-blur p-4 rounded-xl border border-slate-200/80">
          <p className="text-sm font-semibold text-slate-800">Compared to last run (this browser)</p>
          <p className="text-sm text-slate-600 mt-1">
            Previous baseline: <b className="text-slate-900">{baseline}%</b>
          </p>
          <p className="text-sm text-slate-600">
            Change:{" "}
            <b className="text-slate-900">
              {(score - baseline).toFixed(2)}% (
              {score > baseline ? "increase" : score < baseline ? "decrease" : "no change"})
            </b>
          </p>
        </div>
      ) : null}

      {data.edge_warnings?.length > 0 ? (
        <div className="bg-amber-50 border border-amber-200 p-4 rounded-xl">
          <p className="font-semibold text-sm text-amber-950">Input warnings</p>
          <ul className="text-sm text-amber-900 mt-2 list-disc ml-5 space-y-1">
            {data.edge_warnings.map((w, i) => (
              <li key={i}>{w}</li>
            ))}
          </ul>
        </div>
      ) : null}

      {data.summary ? (
        <div className="bg-slate-50 border border-slate-200 p-4 rounded-xl text-sm font-medium text-slate-800 leading-relaxed">
          {data.summary}
        </div>
      ) : null}

      {data.clinical_narrative ? (
        <div className="bg-white/95 backdrop-blur-md p-4 rounded-xl shadow border border-white/20">
          <button
            type="button"
            onClick={() => setShowNarrative(!showNarrative)}
            className="w-full flex justify-between items-center font-semibold text-left text-slate-800 hover:bg-slate-50 p-2 rounded-lg transition"
          >
            <span>Clinical narrative</span>
            <span className="text-sm text-gray-500">{showNarrative ? "▲" : "▼"}</span>
          </button>
          <p className="text-xs text-gray-500 mt-1 px-2">
            {showNarrative ? "Collapse" : "Expand"} for plain-language interpretation.
          </p>
          {showNarrative ? (
            <p className="text-sm mt-3 text-slate-700 leading-relaxed px-1">{data.clinical_narrative}</p>
          ) : null}
        </div>
      ) : null}

      {data.clinical_insights?.length > 0 ? (
        <div className="bg-white/95 backdrop-blur-md p-4 rounded-xl shadow border border-white/20">
          <button
            type="button"
            onClick={() => setShowInsights(!showInsights)}
            className="w-full flex justify-between items-center font-semibold text-left text-slate-800 hover:bg-slate-50 p-2 rounded-lg transition"
          >
            <span>Key drivers</span>
            <span className="text-sm text-gray-500">{showInsights ? "▲" : "▼"}</span>
          </button>
          <p className="text-xs text-gray-500 mt-1 px-2">
            Factors that most influenced this estimate.
          </p>
          <div className="mt-3 flex flex-wrap gap-2">
            {data.clinical_insights.slice(0, 3).map((i, idx) => (
              <span
                key={idx}
                className="bg-teal-50 text-teal-900 border border-teal-100 px-2.5 py-1 rounded-full text-xs font-medium"
              >
                {i}
              </span>
            ))}
          </div>
          {showInsights ? (
            <ul className="mt-3 text-sm text-slate-700 list-disc ml-5 space-y-1">
              {data.clinical_insights.map((i, idx) => (
                <li key={idx}>{i}</li>
              ))}
            </ul>
          ) : null}
        </div>
      ) : null}

      {data.clinical_report ? (
        <div className="bg-white/95 backdrop-blur-md p-4 rounded-xl shadow border border-white/20">
          <button
            type="button"
            onClick={() => setShowReport(!showReport)}
            className="w-full flex justify-between items-center font-semibold text-left text-slate-800 hover:bg-slate-50 p-2 rounded-lg transition"
          >
            <span>Structured report</span>
            <span className="text-sm text-gray-500">{showReport ? "▲" : "▼"}</span>
          </button>
          <p className="text-xs text-gray-500 mt-1 px-2">Interpretation and suggestions.</p>
          {showReport ? (
            <div className="mt-3 text-sm text-slate-700 space-y-3 px-1">
              {data.clinical_report.interpretation ? (
                <p>
                  <span className="font-semibold text-slate-900">Interpretation: </span>
                  {data.clinical_report.interpretation}
                </p>
              ) : null}
              {recommendations.length > 0 ? (
                <ul className="list-disc ml-5 space-y-1">
                  {recommendations.map((r, i) => (
                    <li key={i}>{r}</li>
                  ))}
                </ul>
              ) : null}
            </div>
          ) : null}
        </div>
      ) : null}
    </div>
  );
}
