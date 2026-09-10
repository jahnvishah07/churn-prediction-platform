import { useState } from "react";

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

  const handleSubmit = async () => {
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

      const response = await fetch("http://127.0.0.1:8000/api/predict/", {
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
      setError("Could not reach the prediction API. Is the Django server running?");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div style={{ maxWidth: 480, margin: "40px auto", fontFamily: "sans-serif" }}>
      <h2>Customer Churn Predictor</h2>

      <label>Tenure (months)</label>
      <input name="tenure" type="number" value={form.tenure} onChange={handleChange} />

      <label>Monthly Charges ($)</label>
      <input name="MonthlyCharges" type="number" value={form.MonthlyCharges} onChange={handleChange} />

      <label>Total Charges ($)</label>
      <input name="TotalCharges" type="number" value={form.TotalCharges} onChange={handleChange} />

      <label>Senior Citizen</label>
      <select name="SeniorCitizen" value={form.SeniorCitizen} onChange={handleChange}>
        <option value="0">No</option>
        <option value="1">Yes</option>
      </select>

      <label>Contract Type</label>
      <select name="Contract" value={form.Contract} onChange={handleChange}>
        <option>Month-to-month</option>
        <option>One year</option>
        <option>Two year</option>
      </select>

      <label>Internet Service</label>
      <select name="InternetService" value={form.InternetService} onChange={handleChange}>
        <option>DSL</option>
        <option>Fiber optic</option>
        <option>No</option>
      </select>

      <label>Payment Method</label>
      <select name="PaymentMethod" value={form.PaymentMethod} onChange={handleChange}>
        <option>Electronic check</option>
        <option>Mailed check</option>
        <option>Bank transfer (automatic)</option>
        <option>Credit card (automatic)</option>
      </select>

      <label>Has Partner</label>
      <select name="Partner" value={form.Partner} onChange={handleChange}>
        <option>Yes</option>
        <option>No</option>
      </select>

      <label>Has Dependents</label>
      <select name="Dependents" value={form.Dependents} onChange={handleChange}>
        <option>Yes</option>
        <option>No</option>
      </select>

      <button onClick={handleSubmit} disabled={loading}>
        {loading ? "Predicting..." : "Predict Churn"}
      </button>

      {error && <p style={{ color: "red" }}>{error}</p>}

      {result && (
        <div>
          <h3>Prediction: {result.churn_prediction}</h3>
          <p>Churn Probability: {(result.churn_probability * 100).toFixed(1)}%</p>
        </div>
      )}
    </div>
  );
}
