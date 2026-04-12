import PredictionForm from "./PredictionForm";
import PredictionResult from "./PredictionResult";
import { useState, useEffect } from "react";
import { AppTopNav } from "../../components/AppTopNav";

export default function Prediction() {
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [baseline, setBaseline] = useState(null);

  const [formData, setFormData] = useState({
    age: "",
    cp: "1",
    bp: "",
    chol: "",
    maxhr: "",
    std: "",
    fluro: "",
    th: "",
  });

  useEffect(() => {
    const stored = sessionStorage.getItem("baselineRisk");
    if (stored) setBaseline(Number(stored));
  }, []);

  const handleSetResult = (data, mode = "predict") => {
    setResult(data);

    const score = Number(data?.risk_score_percent);

    if (mode === "predict" && !Number.isNaN(score)) {
      setBaseline(score);
      sessionStorage.setItem("baselineRisk", String(score));
    }
  };

  const clearResult = () => {
    setResult(null);
    setError(null);
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-[#0f172a] via-[#0b3c5d] to-[#115e59] p-6 md:p-8 transition-all duration-500">
      <div className="max-w-6xl mx-auto">
        <AppTopNav
          title="Risk assessment"
          subtitle="Enter validated clinical inputs. Results are educational estimates only—not a diagnosis."
          extra={
            result ? (
              <button
                type="button"
                onClick={clearResult}
                className="text-sm px-3 py-1.5 rounded-lg bg-teal-500/20 text-teal-100 border border-teal-400/40 hover:bg-teal-500/30 transition"
              >
                Clear result
              </button>
            ) : null
          }
        />

        {!result ? (
          <div className="max-w-xl mx-auto transition-all duration-500">
            <PredictionForm
              formData={formData}
              setFormData={setFormData}
              setResult={handleSetResult}
              setLoading={setLoading}
              setError={setError}
            />

            {loading ? (
              <div className="flex justify-center mt-6" aria-live="polite">
                <div className="h-8 w-8 border-2 border-white border-t-transparent rounded-full animate-spin" />
              </div>
            ) : null}

            {error ? (
              <div
                className="bg-red-500/20 border border-red-400/50 text-red-100 p-4 rounded-xl text-sm mt-6"
                role="alert"
              >
                {error}
              </div>
            ) : null}
          </div>
        ) : (
          <div className="grid md:grid-cols-2 gap-6 items-start transition-all duration-500">
            <PredictionForm
              formData={formData}
              setFormData={setFormData}
              setResult={handleSetResult}
              setLoading={setLoading}
              setError={setError}
            />
            <PredictionResult data={result} baseline={baseline} />
          </div>
        )}
      </div>
    </div>
  );
}
