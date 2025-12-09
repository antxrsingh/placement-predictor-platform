import React, { useState } from "react";
import "./App.css";

function App() {
  const [formData, setFormData] = useState({
    ssc_p: "",
    hsc_p: "",
    degree_p: "",
    etest_p: "",
    workex: "no",

    projects: 0,
    internships: 0,
    hackathons: 0,
    clubs: 0,
    cp_level: "none",

    has_dsa: false,
    has_web: false,
    has_ml: false,
    has_app: false,
    has_cloud: false,

    mba_p: ""
  });

  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState(null);
  const [error, setError] = useState("");

  // Handle text/number/select/checkbox changes
  const handleChange = (e) => {
    const { name, value, type, checked } = e.target;

    if (type === "checkbox") {
      setFormData((prev) => ({ ...prev, [name]: checked }));
    } else {
      setFormData((prev) => ({ ...prev, [name]: value }));
    }
  };

  const handleSubmit = async (e) => {
  e.preventDefault();
  setLoading(true);
  setError("");
  setResult(null);

  // Build payload in the format backend expects
  const payload = {
    ssc_p: parseFloat(formData.ssc_p) || 0,
    hsc_p: parseFloat(formData.hsc_p) || 0,
    degree_p: parseFloat(formData.degree_p) || 0,
    etest_p: parseFloat(formData.etest_p) || 0,
    workex: formData.workex, // "yes" or "no"

    projects: parseInt(formData.projects || 0, 10),
    internships: parseInt(formData.internships || 0, 10),
    hackathons: parseInt(formData.hackathons || 0, 10),
    clubs: parseInt(formData.clubs || 0, 10),
    cp_level: formData.cp_level,

    has_dsa: formData.has_dsa,
    has_web: formData.has_web,
    has_ml: formData.has_ml,
    has_app: formData.has_app,
    has_cloud: formData.has_cloud
  };

  // Only send mba_p if user entered it (optional)
  if (formData.mba_p !== "") {
    payload.mba_p = parseFloat(formData.mba_p) || 0;
  }

  try {
    const res = await fetch(
      "https://placement-predictor-platform.onrender.com", 
      {
        method: "POST",
        headers: {
          "Content-Type": "application/json"
        },
        body: JSON.stringify(payload)
      }
    );

    if (!res.ok) {
      // If backend is waking up or has a 5xx error
      throw new Error(`Server error: ${res.status}`);
    }

    const data = await res.json();
    setResult(data);
  } catch (err) {
    console.error(err);

    // More helpful message for free Render backend
    setError(
      "Backend may be waking up (free hosting). Wait 5–10 seconds and click Predict again. " +
      "If it still fails, refresh the page and try once more."
    );
  } finally {
    setLoading(false);
  }
};


  return (
    <div className="app">
      <h1>Placement Predictor Platform</h1>
      <p className="subtitle">
        Estimate your placement probability, expected salary and get
        personalized improvement suggestions.
      </p>

      <div className="main-layout">
        {/* LEFT: FORM */}
        <form className="form" onSubmit={handleSubmit}>
          <h2>Academic Details</h2>
          <div className="grid">
            <label>
              10th Percentage (SSC)
              <input
                type="number"
                name="ssc_p"
                value={formData.ssc_p}
                onChange={handleChange}
                min="0"
                max="100"
                step="0.1"
                required
              />
            </label>
            <label>
              12th Percentage (HSC)
              <input
                type="number"
                name="hsc_p"
                value={formData.hsc_p}
                onChange={handleChange}
                min="0"
                max="100"
                step="0.1"
                required
              />
            </label>
            <label>
              Degree Percentage
              <input
                type="number"
                name="degree_p"
                value={formData.degree_p}
                onChange={handleChange}
                min="0"
                max="100"
                step="0.1"
                required
              />
            </label>
            <label>
              Employability Test %
              <input
                type="number"
                name="etest_p"
                value={formData.etest_p}
                onChange={handleChange}
                min="0"
                max="100"
                step="0.1"
                required
              />
            </label>
          </div>

          <h2>Experience & Profile</h2>
          <div className="grid">
            <label>
              Work Experience
              <select
                name="workex"
                value={formData.workex}
                onChange={handleChange}
              >
                <option value="no">No</option>
                <option value="yes">Yes</option>
              </select>
            </label>
            <label>
              Projects (count)
              <input
                type="number"
                name="projects"
                value={formData.projects}
                onChange={handleChange}
                min="0"
              />
            </label>
            <label>
              Internships (count)
              <input
                type="number"
                name="internships"
                value={formData.internships}
                onChange={handleChange}
                min="0"
              />
            </label>
            <label>
              Hackathons (count)
              <input
                type="number"
                name="hackathons"
                value={formData.hackathons}
                onChange={handleChange}
                min="0"
              />
            </label>
            <label>
              Clubs / Leadership (count)
              <input
                type="number"
                name="clubs"
                value={formData.clubs}
                onChange={handleChange}
                min="0"
              />
            </label>
          </div>

          <h2>Skills & CP</h2>
          <div className="grid">
            <label>
              CP Level
              <select
                name="cp_level"
                value={formData.cp_level}
                onChange={handleChange}
              >
                <option value="none">None</option>
                <option value="basic">Basic</option>
                <option value="intermediate">Intermediate</option>
                <option value="good">Good</option>
                <option value="strong">Strong</option>
              </select>
            </label>
          </div>

          <div className="skills">
            <label>
              <input
                type="checkbox"
                name="has_dsa"
                checked={formData.has_dsa}
                onChange={handleChange}
              />
              Data Structures & Algorithms
            </label>
            <label>
              <input
                type="checkbox"
                name="has_web"
                checked={formData.has_web}
                onChange={handleChange}
              />
              Web Development
            </label>
            <label>
              <input
                type="checkbox"
                name="has_ml"
                checked={formData.has_ml}
                onChange={handleChange}
              />
              ML / AI
            </label>
            <label>
              <input
                type="checkbox"
                name="has_app"
                checked={formData.has_app}
                onChange={handleChange}
              />
              App Development
            </label>
            <label>
              <input
                type="checkbox"
                name="has_cloud"
                checked={formData.has_cloud}
                onChange={handleChange}
              />
              Cloud / AWS
            </label>
          </div>

          <h2>Optional (MBA Students)</h2>
          <div className="grid">
            <label>
              MBA Percentage (optional)
              <input
                type="number"
                name="mba_p"
                value={formData.mba_p}
                onChange={handleChange}
                min="0"
                max="100"
                step="0.1"
              />
            </label>
          </div>

          <button type="submit" disabled={loading}>
            {loading ? "Predicting..." : "Predict Placement & Salary"}
          </button>
          <p className="small-text">
  Note: First request may take 5–10 seconds because the free backend needs to wake up.
          </p>  
          {error && <p className="error">{error}</p>}
        </form>

        {/* RIGHT: RESULT */}
        <div className="result">
          <h2>Prediction Result</h2>
          {!result && <p>Fill the form and click predict to see your result.</p>}

          {result && (
  <>
    <div className="result-summary">
      <p>
        <strong>Placement Probability:</strong>{" "}
        {result.placement_probability}% ({result.level} chance)
      </p>
      <p>
        <strong>Expected Salary Range:</strong>{" "}
        {result.expected_salary_min_lpa} – {result.expected_salary_max_lpa} LPA
      </p>
      <p className="small-text">
        Approx. ₹
        {result.expected_salary_min_inr.toLocaleString("en-IN")} – ₹
        {result.expected_salary_max_inr.toLocaleString("en-IN")} per year
      </p>
    </div>

    <h3>Suggestions to Improve</h3>
    <ul>
      {result.suggestions.map((s, idx) => (
        <li key={idx}>{s}</li>
      ))}
    </ul>
  </>
)}

        </div>
      </div>
    </div>
  );
}

export default App;
