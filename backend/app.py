from flask import Flask, request, jsonify
from flask_cors import CORS
import joblib

app = Flask(__name__)
CORS(app)

# Load placement (classification) model and feature list
placement_model = joblib.load("placement_model.pkl")
FEATURES = joblib.load("model_features.pkl")  # ["ssc_p", "hsc_p", "degree_p", "etest_p", "workex_bin"]


def workex_to_bin(value):
    """Convert different formats of work experience to 0 or 1."""
    if isinstance(value, bool):
        return int(value)
    if isinstance(value, (int, float)):
        return int(value != 0)
    if isinstance(value, str):
        v = value.strip().lower()
        if v in ["yes", "y", "true", "t", "1", "experience", "exp"]:
            return 1
        return 0
    return 0


def safe_float(v, default=0.0):
    try:
        return float(v)
    except (TypeError, ValueError):
        return default


def safe_int(v, default=0):
    try:
        return int(v)
    except (TypeError, ValueError):
        return default


def compute_profile_score(
    degree_p,
    projects,
    internships,
    hackathons,
    clubs,
    cp_level_str,
    has_dsa,
    has_web,
    has_ml,
    has_app,
    has_cloud,
    workex_bin,
):
    """
    Compute a profile score based on non-academic features.
    Higher score = stronger profile, used to adjust placement probability and salary.
    """
    score = 0.0

    # Degree performance
    if degree_p >= 75:
        score += 2.0
    elif degree_p >= 65:
        score += 1.0

    # Projects
    if projects >= 3:
        score += 2.0
    elif projects >= 1:
        score += 1.0

    # Internships
    if internships >= 2:
        score += 2.0
    elif internships >= 1:
        score += 1.5

    # Hackathons
    if hackathons >= 2:
        score += 1.5
    elif hackathons >= 1:
        score += 1.0

    # Clubs / leadership
    if clubs >= 2:
        score += 1.0
    elif clubs >= 1:
        score += 0.5

    # Competitive programming level
    cp = cp_level_str.lower()
    if cp in ["strong"]:
        score += 2.0
    elif cp in ["good"]:
        score += 1.5
    elif cp in ["intermediate"]:
        score += 1.0
    elif cp in ["basic"]:
        score += 0.5

    # Skills
    if has_dsa:
        score += 1.0
    if has_web:
        score += 0.8
    if has_ml:
        score += 0.8
    if has_app:
        score += 0.8
    if has_cloud:
        score += 0.8

    # Work experience
    if workex_bin == 1:
        score += 1.0

    return score


def adjust_probability(base_prob, profile_score):
    """
    Adjust baseline probability (from ML) using profile score.
    Keeps probability in [0.05, 0.98].
    """
    # Roughly normalize profile score to -1..+1 range
    # Typical profile_score might be ~0 to ~12
    # We'll center around 5 and scale.
    centered = profile_score - 5.0
    delta = 0.02 * centered  # each point ~2% shift

    # Clamp max adjustment to +/- 0.15 (15 percentage points)
    if delta > 0.15:
        delta = 0.15
    elif delta < -0.15:
        delta = -0.15

    adjusted = base_prob + delta

    # Clamp final prob
    if adjusted < 0.05:
        adjusted = 0.05
    if adjusted > 0.98:
        adjusted = 0.98

    return adjusted


def estimate_salary_band_lpa(probability, profile_score):
    """
    Rule-based salary band (in LPA) based on adjusted probability and profile strength.
    """
    # Base for a weak profile
    base_min = 4.0
    base_max = 6.0

    # Use both probability and profile score
    # Higher probability and higher score => higher band
    prob_component = (probability - 0.5) * 10  # ~ -5 to +5 range
    score_component = (profile_score - 5.0) * 0.6  # center at 5

    band_shift = prob_component * 0.3 + score_component  # combine

    min_lpa = base_min + band_shift
    max_lpa = base_max + band_shift

    # Ensure a minimum separation
    if max_lpa < min_lpa + 1.5:
        max_lpa = min_lpa + 1.5

    # Clamp to reasonable bounds
    if min_lpa < 3.0:
        min_lpa = 3.0
    if max_lpa > 22.0:
        max_lpa = 22.0

    return round(min_lpa, 1), round(max_lpa, 1)


@app.route("/predict", methods=["POST"])
def predict():
    data = request.get_json() or {}

    # --- 1. Core numeric inputs for the ML placement model ---
    ssc_p = safe_float(data.get("ssc_p", 0))       # 10th %
    hsc_p = safe_float(data.get("hsc_p", 0))       # 12th %
    degree_p = safe_float(data.get("degree_p", 0)) # degree %
    etest_p = safe_float(data.get("etest_p", 0))   # e-test %
    workex_bin = workex_to_bin(data.get("workex", 0))

    feature_vector = [
        ssc_p,
        hsc_p,
        degree_p,
        etest_p,
        workex_bin,
    ]

    # --- 2. Baseline placement probability from ML model ---
    base_proba = placement_model.predict_proba([feature_vector])[0][1]
    base_probability = float(base_proba)

    # --- 3. Extra inputs for profile score, salary band, and suggestions ---
    projects = safe_int(data.get("projects", 0))
    internships = safe_int(data.get("internships", 0))
    hackathons = safe_int(data.get("hackathons", 0))
    clubs = safe_int(data.get("clubs", 0))

    cp_level_str = str(data.get("cp_level", "none")).strip().lower()

    has_dsa = bool(data.get("has_dsa", False))
    has_web = bool(data.get("has_web", False))
    has_ml = bool(data.get("has_ml", False))
    has_app = bool(data.get("has_app", False))
    has_cloud = bool(data.get("has_cloud", False))

    mba_p = data.get("mba_p", None)
    mba_p_val = safe_float(mba_p, 0.0) if mba_p is not None else None

    # --- 4. Compute profile score & adjusted probability ---
    profile_score = compute_profile_score(
        degree_p=degree_p,
        projects=projects,
        internships=internships,
        hackathons=hackathons,
        clubs=clubs,
        cp_level_str=cp_level_str,
        has_dsa=has_dsa,
        has_web=has_web,
        has_ml=has_ml,
        has_app=has_app,
        has_cloud=has_cloud,
        workex_bin=workex_bin,
    )

    # Baseline adjustment using academics + full profile
    adjusted_probability = adjust_probability(base_probability, profile_score)

    # 🔽 Extra penalty for today's market:
    # No work experience and/or weak CP (none/basic)
    penalty = 0.0

    # 1) Individual penalties
    if workex_bin == 0:
        # No internships/work-ex hurts employability a lot
        penalty += 0.10  # ~10 percentage points

    if cp_level_str in ["none", "basic"]:
        # Weak CP/DSA means lower chance of clearing online rounds
        penalty += 0.10  # ~10 percentage points

    # 2) Strong extra penalty when BOTH are bad: no work ex AND CP = none
    if workex_bin == 0 and cp_level_str == "none":
        # Additional heavy penalty
        penalty += 0.20  # another 20 percentage points

        # Also hard-cap the probability so it cannot look too optimistic
        if adjusted_probability > 0.40:
            adjusted_probability = 0.40

    # Apply total penalty
    if penalty > 0:
        adjusted_probability = adjusted_probability - penalty

        # Final lower clamp – it can go quite low, but not zero
        if adjusted_probability < 0.02:
            adjusted_probability = 0.02

    placement_probability_percent = round(adjusted_probability * 100, 2)

    # Risk level based on adjusted probability
    if adjusted_probability >= 0.75:
        level = "High"
    elif adjusted_probability >= 0.5:
        level = "Medium"
    else:
        level = "Low"

    # --- 5. Estimate salary band (LPA) from adjusted probability + profile score ---
    min_lpa, max_lpa = estimate_salary_band_lpa(
        probability=adjusted_probability,
        profile_score=profile_score,
    )

    # Extra harsh cut on salary expectations when BOTH are bad:
    # No work-ex AND CP = none
    if workex_bin == 0 and cp_level_str == "none":
        # Push the band down significantly
        min_lpa = min(min_lpa, 5.0)
        max_lpa = min(max_lpa, 7.0)

        # Also ensure there is at least 1.5 LPA difference
        if max_lpa < min_lpa + 1.5:
            max_lpa = min_lpa + 1.5

    min_inr = int(min_lpa * 100000)
    max_inr = int(max_lpa * 100000)

    # --- 6. Suggestions (same idea as before) ---
    suggestions = []

    # Academics-based suggestions
    if degree_p < 65:
        suggestions.append("Try to keep your degree percentage above 65% to stay in most company criteria.")
    if hsc_p < 60 or ssc_p < 60:
        suggestions.append("Your 10th/12th scores are a bit low, so focus on strong projects and contests to compensate.")
    if etest_p < 60:
        suggestions.append("Improve your aptitude and logical reasoning by practicing e-test style questions regularly.")

    # Work experience
    if workex_bin == 0:
        suggestions.append("Consider internships or part-time roles to gain practical work experience.")

    # Projects & internships
    if projects < 2:
        suggestions.append("Build at least 2 solid projects (e.g., full-stack, ML, or Android) to strengthen your profile.")
    if internships < 1:
        suggestions.append("Try to secure at least one internship before final placements.")

    # Hackathons & clubs
    if hackathons < 1:
        suggestions.append("Participate in hackathons to showcase problem-solving and teamwork.")
    if clubs < 1:
        suggestions.append("Join or take active roles in clubs/communities to demonstrate leadership and collaboration.")

    # Competitive programming level
    if cp_level_str in ["none", "basic"]:
        suggestions.append("Improve competitive programming and DSA to clear online coding rounds.")

    # Skills
    if not has_dsa:
        suggestions.append("Strengthen Data Structures & Algorithms; most tech companies heavily test this.")
    if not (has_web or has_ml or has_app):
        suggestions.append("Add at least one development skill (Web, ML/AI, App Dev) with a real-world project.")
    if has_web and projects < 2:
        suggestions.append("Build a portfolio website or a full-stack app to showcase your web development skills.")
    if has_ml and projects < 1:
        suggestions.append("Implement at least one ML project with a clear problem statement and dataset.")
    if has_cloud and internships < 1:
        suggestions.append("Try to get cloud-related internship or certifications (e.g., AWS) to leverage your cloud skills.")

    # MBA-related suggestions (only if they provided mba_p)
    if mba_p_val is not None and mba_p_val < 60:
        suggestions.append("Improve your MBA percentage above 60% or highlight your practical skills to balance academics.")

    # No suggestions? Profile is strong.
    if not suggestions:
        suggestions.append("Your profile looks strong. Focus on mock interviews, company-specific preparation, and soft skills.")

    # --- 7. Final response ---
    return jsonify({
        "placement_probability": placement_probability_percent,
        "level": level,
        "expected_salary_min_lpa": min_lpa,
        "expected_salary_max_lpa": max_lpa,
        "expected_salary_min_inr": min_inr,
        "expected_salary_max_inr": max_inr,
        "suggestions": suggestions
    })


@app.route("/", methods=["GET"])
def home():
    return jsonify({"status": "Placement Predictor API running"})


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
