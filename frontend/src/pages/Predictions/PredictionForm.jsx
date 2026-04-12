import { useState } from "react";
import { API_BASE } from "../../config.js";

export default function PredictionForm({ 
  formData, 
  setFormData, 
  setResult, 
  setLoading, 
  setError 
}) {

  const [hints, setHints] = useState({
    bp: "",
    chol: "",
    maxhr: ""
  });

  const handleChange = (e) => {
    const { name, value } = e.target;

    setFormData({ ...formData, [name]: value });

    // 🔥 Live hints
    if (name === "bp") {
      if (value < 90) setHints(h => ({ ...h, bp: "Very low BP — check again" }));
      else if (value <= 120) setHints(h => ({ ...h, bp: "Normal range" }));
      else if (value <= 139) setHints(h => ({ ...h, bp: "Elevated BP" }));
      else setHints(h => ({ ...h, bp: "High BP — verify" }));
    }

    if (name === "chol") {
      if (value < 200) setHints(h => ({ ...h, chol: "Desirable range" }));
      else if (value <= 239) setHints(h => ({ ...h, chol: "Borderline high" }));
      else setHints(h => ({ ...h, chol: "High cholesterol" }));
    }

    if (name === "maxhr") {
      if (!formData.age) return;
      const est = 220 - formData.age;
      if (value < est - 30) setHints(h => ({ ...h, maxhr: "Lower than expected" }));
      else if (value > est + 30) setHints(h => ({ ...h, maxhr: "Higher than expected" }));
      else setHints(h => ({ ...h, maxhr: "Within expected range" }));
    }
  };

  const handleRequest = async (mode = "predict") => {
    setLoading(true);
    setError(null);

    try {
      const res = await fetch(`${API_BASE}/predict`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(formData),
        credentials: "include"
      });

      const data = await res.json();

      if (!res.ok) {
        setError(data.errors?.join(", ") || "Invalid input");
        return;
      }

      setResult(data, mode);

    } catch {
      setError("Something went wrong");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="bg-white/95 backdrop-blur-md p-6 rounded-2xl shadow-xl border border-white/20">

      <h2 className="text-xl font-bold mb-1">Heart Risk Assessment</h2>
      <p className="text-sm text-gray-500 mb-4">
        Enter clinical parameters to estimate risk
      </p>

      {/* BASIC */}
      <h3 className="text-sm font-semibold mt-4 mb-3 border-b pb-1">Basic Info</h3>

      <div className="mb-4">
        <label className="block text-sm font-medium text-gray-700 mb-1">
          Age
        </label>
        <input
          name="age"
          type="number"
          value={formData.age}
          onChange={handleChange}
          className="w-full p-2 border rounded"
          required
        />
      </div>

      {/* CHEST PAIN */}
      <h3 className="text-sm font-semibold mt-4 mb-3 border-b pb-1">Symptoms</h3>

      <p className="text-sm font-medium text-gray-700 mb-2">
        Chest Pain Type
      </p>

      <div className="grid grid-cols-2 gap-2 mb-4">
        {[
          ["1", "Typical"],
          ["2", "Atypical"],
          ["3", "Non-anginal"],
          ["4", "Asymptomatic"]
        ].map(([val, label]) => (
          <button
            key={val}
            type="button"
            onClick={() => setFormData({ ...formData, cp: val })}
            className={`p-2 rounded border text-sm transition ${
              formData.cp === val
                ? "bg-teal-600 text-white border-teal-600"
                : "bg-white hover:bg-gray-50"
            }`}
          >
            {label}
          </button>
        ))}
      </div>

      {/* MEASUREMENTS */}
      <h3 className="text-sm font-semibold mt-4 mb-3 border-b pb-1">
        Clinical Measurements
      </h3>

      {[
        { name: "bp", label: "Blood Pressure (mmHg)", hint: hints.bp },
        { name: "chol", label: "Cholesterol (mg/dL)", hint: hints.chol },
        { name: "maxhr", label: "Max Heart Rate", hint: hints.maxhr }
      ].map(field => (
        <div key={field.name} className="mb-4">
          <label className="block text-sm font-medium text-gray-700 mb-1">
            {field.label}
          </label>
          <input
            name={field.name}
            value={formData[field.name]}
            onChange={handleChange}
            className="w-full p-2 border rounded"
          />
          <p className="text-xs text-gray-500 mt-1">{field.hint}</p>
        </div>
      ))}

      {[
        { name: "std", label: "ST Depression" },
        { name: "fluro", label: "Number of Vessels (0–3)" },
        { name: "th", label: "Thallium Test Result" }
      ].map(field => (
        <div key={field.name} className="mb-4">
          <label className="block text-sm font-medium text-gray-700 mb-1">
            {field.label}
          </label>
          <input
            name={field.name}
            value={formData[field.name]}
            onChange={handleChange}
            className="w-full p-2 border rounded"
          />
        </div>
      ))}

      {/* ACTIONS */}
      <button
        onClick={() => handleRequest("predict")}
        className="w-full bg-teal-600 hover:bg-teal-700 text-white p-2 rounded transition mb-2"
      >
        Run Prediction
      </button>

      <button
        onClick={() => handleRequest("simulate")}
        className="w-full border hover:bg-gray-100 p-2 rounded transition"
      >
        Simulate Changes
      </button>

    </div>
  );
}