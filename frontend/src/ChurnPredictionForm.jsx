import { useState } from "react";
import "./churn-form.css";

const RISK_COPY = {
  high: "Likely to churn",
  medium: "At some risk",
  low: "Likely to stay",
};

function riskTier(prob) {
  if (prob >= 0.5) return "high";
  if (prob >= 0.25) return "medium";
  return "low";
}

export default function ChurnPredictionForm() {
  const [form, setForm] = useState({
    tenure: "",
    MonthlyCharges: "",
    TotalCharges: "",
    SeniorCitizen: "0",
    Contract: "Month-to-month",
    InternetService: "Fiber optic",
    PaymentMethod: "Electronic check",
    Partner: "No",
    Dependents: "No",
  });

  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const handleChange = (e) => {
    const { name, value } = e.target;
    setForm((prev) => ({ ...prev, [name]: value }));
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError(null);
    setResult(null);
    try {
      const payload = {
        ...form,
        tenure: Number(form.tenure),
        MonthlyCharges: Number(form.MonthlyCharges),
        TotalCharges: Number(form.TotalCharges),
        SeniorCitizen: Number(form.SeniorCitizen),
      };

      const API_URL = import.meta.env.VITE_API_URL || "http://127.0.0.1:8000";
      const response = await fetch(`${API_URL}/api/predict/`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload),
      });

      if (!response.ok) {
        throw new Error(`Server responded with status ${response.status}`);
      }

      const data = await response.json();
      setResult(data);
    } catch (err) {
      setError("Couldn't reach the prediction API. Check that the Django server is running.");
    } finally {
      setLoading(false);
    }
  };

  const probPct = result ? Math.round(result.churn_probability * 100) : null;
  const tier = result ? riskTier(result.churn_probability) : null;

  return (
    <div className="churn-app">
      <header className="churn-header">
        <span className="churn-tag">Retention tool</span>
        <h1>Will this customer churn?</h1>
        <p>Enter a customer's account details to estimate their churn risk.</p>
      </header>

      <div className="churn-layout">
        <form className="churn-form" onSubmit={handleSubmit}>
          <div className="field-row">
            <label>
              Tenure (months)
              <input name="tenure" type="number" min="0" required value={form.tenure} onChange={handleChange} />
            </label>
            <label>
              Monthly charges ($)
              <input name="MonthlyCharges" type="number" min="0" step="0.01" required value={form.MonthlyCharges} onChange={handleChange} />
            </label>
          </div>

          <div className="field-row">
            <label>
              Total charges ($)
              <input name="TotalCharges" type="number" min="0" step="0.01" required value={form.TotalCharges} onChange={handleChange} />
            </label>
            <label>
              Senior citizen
              <select name="SeniorCitizen" value={form.SeniorCitizen} onChange={handleChange}>
                <option value="0">No</option>
                <option value="1">Yes</option>
              </select>
            </label>
          </div>

          <div className="field-row">
            <label>
              Contract type
              <select name="Contract" value={form.Contract} onChange={handleChange}>
                <option>Month-to-month</option>
                <option>One year</option>
                <option>Two year</option>
              </select>
            </label>
            <label>
              Internet service
              <select name="InternetService" value={form.InternetService} onChange={handleChange}>
                <option>DSL</option>
                <option>Fiber optic</option>
                <option>No</option>
              </select>
            </label>
          </div>

          <div className="field-row">
            <label>
              Payment method
              <select name="PaymentMethod" value={form.PaymentMethod} onChange={handleChange}>
                <option>Electronic check</option>
                <option>Mailed check</option>
                <option>Bank transfer (automatic)</option>
                <option>Credit card (automatic)</option>
              </select>
            </label>
            <label>
              Has partner
              <select name="Partner" value={form.Partner} onChange={handleChange}>
                <option>No</option>
                <option>Yes</option>
              </select>
            </label>
          </div>

          <div className="field-row">
            <label>
              Has dependents
              <select name="Dependents" value={form.Dependents} onChange={handleChange}>
                <option>No</option>
                <option>Yes</option>
              </select>
            </label>
          </div>

          <button type="submit" disabled={loading}>
            {loading ? "Calculating…" : "Predict churn risk"}
          </button>

          {error && <p className="churn-error">{error}</p>}
        </form>

        <aside className={`churn-readout ${result ? `is-${tier}` : ""}`}>
          {!result && !loading && (
            <div className="readout-empty">
              <p>Fill in the form and run a prediction to see the risk readout here.</p>
            </div>
          )}
          {loading && <div className="readout-empty"><p>Scoring customer…</p></div>}
          {result && (
            <>
              <span className="readout-label">Churn probability</span>
              <span className="readout-figure">{probPct}%</span>
              <span className="readout-verdict">{RISK_COPY[tier]}</span>
              <div className="readout-bar">
                <div className="readout-bar-fill" style={{ width: `${probPct}%` }} />
              </div>
              <p className="readout-note">
                Based on tenure, contract type, and billing pattern relative to
                historical churn behavior in similar accounts.
              </p>
            </>
          )}
        </aside>
      </div>
    </div>
  );
}
