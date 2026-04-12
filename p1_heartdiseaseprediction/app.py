from flask import Flask, render_template, request, redirect, session, url_for, send_from_directory, abort
from flask_cors import CORS
from sqlite3 import connect
from random import randrange
import smtplib
from email.message import EmailMessage
from werkzeug.security import generate_password_hash, check_password_hash
import pickle
import pandas as pd
import os
import logging
from flask import jsonify
import json
import struct
from datetime import datetime

# Always use the directory containing this file (immune to cwd / where you run `flask run` from).
_BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(_BASE_DIR, "mohithheart.db")
MODEL_PATH = os.path.join(_BASE_DIR, "heartdiseaseprediction.model")
# Production: copy Vite `dist/` here (see scripts/build.sh). Same-origin API + React.
SPA_DIR = os.path.join(_BASE_DIR, "static", "spa")


def _sqlite_int(val):
    """INTEGER read back as int, or BLOB if a numpy scalar was bound by mistake (sqlite3 quirk)."""
    if val is None:
        return None
    if isinstance(val, (bytes, memoryview)):
        b = bytes(val)
        if len(b) == 8:
            return struct.unpack("<q", b)[0]
        if len(b) == 4:
            return struct.unpack("<i", b)[0]
        return int.from_bytes(b, "little", signed=True)
    return int(val)


def ensure_db_schema():
    with connect(DB_PATH) as con:
        con.execute("""
            CREATE TABLE IF NOT EXISTS user (
                username TEXT PRIMARY KEY,
                password TEXT NOT NULL,
                email    TEXT NOT NULL
            )
        """)
        con.execute("""
            CREATE TABLE IF NOT EXISTS history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT,
                age REAL,
                cp INTEGER,
                bp REAL,
                chol REAL,
                maxhr REAL,
                std REAL,
                fluro REAL,
                th REAL,
                prediction INTEGER,
                probability REAL,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        """)
        con.commit()

# logging.basicConfig(
#     filename="app.log",
#     level=logging.INFO,
#     format="%(asctime)s - %(levelname)s - %(message)s"
# )

app = Flask(__name__)
# Fixed dev key keeps sessions after restart; set FLASK_SECRET_KEY in production.
app.secret_key = os.environ.get("FLASK_SECRET_KEY", "dev-only-not-for-production")

if os.environ.get("RENDER") or os.environ.get("FLASK_ENV") == "production":
    app.config["SESSION_COOKIE_SECURE"] = True
    app.config["SESSION_COOKIE_SAMESITE"] = "Lax"
    app.config["SESSION_COOKIE_HTTPONLY"] = True

_default_cors = "" if os.environ.get("RENDER") else "http://localhost:5173,http://127.0.0.1:5173"
_cors_raw = os.environ.get("CORS_ORIGINS", _default_cors)
_cors_origins = [o.strip() for o in _cors_raw.split(",") if o.strip()]
if _cors_origins:
    CORS(app, origins=_cors_origins, supports_credentials=True)

# ---------------- MAIL CONFIG ----------------
app.config["MAIL_SERVER"] = "smtp.gmail.com"
app.config["MAIL_PORT"] = 587
app.config["MAIL_USERNAME"] = os.getenv("MAIL_USERNAME")
app.config["MAIL_PASSWORD"] = os.getenv("MAIL_PASSWORD")
app.config["MAIL_USE_TLS"] = True
app.config["MAIL_USE_SSL"] = False
app.config["MAIL_DEFAULT_SENDER"] = os.getenv(
    "MAIL_DEFAULT_SENDER", "yannammohithreddy@gmail.com"
)

ensure_db_schema()

# ---------------- LOAD MODEL ONCE ----------------
print("Starting app...")
print(f"Database: {DB_PATH}")
with open(MODEL_PATH, "rb") as f:
    model = pickle.load(f)

# logging.info("Model loaded successfully")

# ---------------- HELPER: Send Password Email ----------------
def _mail_credentials_configured():
    u = (os.getenv("MAIL_USERNAME") or "").strip()
    p = (os.getenv("MAIL_PASSWORD") or "").strip()
    return bool(u and p)


def send_password_email(recipient_email, username, password, subject="Your Heart Disease Prediction System Password"):
    """
    Returns: "sent" | "skipped" (no MAIL_* on server) | "failed" (SMTP error/timeout).

    Uses smtplib with an explicit timeout so Gunicorn workers are not blocked for 30s+ when
    SMTP is unreachable (common on misconfigured deploys).
    """
    body = f"""Hello {username},

Your temporary password for the Heart Disease Prediction System is:

    {password}

Please log in and keep this password safe.

— Heart Disease Prediction System
(Educational & Research Use Only)
"""
    if not _mail_credentials_configured():
        logging.info("MAIL_USERNAME/MAIL_PASSWORD not set; skipping SMTP send")
        return "skipped"
    try:
        msg = EmailMessage()
        msg["Subject"] = subject
        msg["From"] = app.config["MAIL_DEFAULT_SENDER"]
        msg["To"] = recipient_email
        msg.set_content(body)
        timeout = int(os.environ.get("MAIL_SMTP_TIMEOUT", "20"))
        with smtplib.SMTP(
            app.config["MAIL_SERVER"], int(app.config["MAIL_PORT"]), timeout=timeout
        ) as smtp:
            smtp.starttls()
            smtp.login(app.config["MAIL_USERNAME"], app.config["MAIL_PASSWORD"])
            smtp.send_message(msg)
        return "sent"
    except Exception as e:
        logging.error("Mail sending failed: %s", e)
        return "failed"

# ---------------- Explanations ----------------
def generate_explanations(age, cp, BP, CH, maxhr, STD, fluro, Th):
    """
    Model-aligned local drivers (Point #18).
    We approximate "feature importance" by perturbing each input slightly and
    measuring how much the model probability changes.
    """

    def clamp(v, lo, hi):
        return max(lo, min(hi, v))

    def predict_prob_percent(a, cpt, bpp, ch, mhr, std, fl, thv):
        feats = pd.DataFrame([{
            "Age": a,
            "Chest pain type": cpt,
            "BP": bpp,
            "Cholesterol": ch,
            "Max HR": mhr,
            "ST depression": std,
            "Number of vessels fluro": fl,
            "Thallium": thv
        }])

        # Keep preprocessing identical to /check and /predict
        feats["Chol_Age_Ratio"] = feats["Cholesterol"] / feats["Age"]
        feats["Heart_Stress"] = feats["ST depression"] * feats["BP"]

        prob = model.predict_proba(feats)[0][1]
        return round(prob * 100, 2)

    base_prob = predict_prob_percent(age, cp, BP, CH, maxhr, STD, fluro, Th)

    # (feature_key, options) where options are candidate perturbed values
    candidates = []

    # Continuous features: small perturbations
    age_opts = [age - 2, age + 2]
    age_opts = [clamp(float(v), 1, 120) for v in age_opts]
    candidates.append(("age", age_opts))

    bp_opts = [BP - 5, BP + 5]
    bp_opts = [clamp(float(v), 80, 200) for v in bp_opts]
    candidates.append(("pressure", bp_opts))

    ch_opts = [CH - 10, CH + 10]
    ch_opts = [clamp(float(v), 100, 400) for v in ch_opts]
    candidates.append(("cholesterol", ch_opts))

    maxhr_opts = [maxhr - 5, maxhr + 5]
    maxhr_opts = [clamp(float(v), 60, 220) for v in maxhr_opts]
    candidates.append(("heart_rate", maxhr_opts))

    std_opts = [STD - 0.5, STD + 0.5]
    std_opts = [clamp(float(v), 0, 6) for v in std_opts]
    candidates.append(("ischemia", std_opts))

    # Discrete features
    cp_opts = [clamp(int(cp) - 1, 1, 4), clamp(int(cp) + 1, 1, 4)]
    candidates.append(("symptom", cp_opts))

    fluro_opts = [clamp(int(fluro) - 1, 0, 3), clamp(int(fluro) + 1, 0, 3)]
    candidates.append(("vessel", fluro_opts))

    allowed_th = [3, 6, 7]
    th_opts = [v for v in allowed_th if float(v) != float(Th)]
    candidates.append(("ischemia_thallium", th_opts if th_opts else [Th]))

    def best_delta_for_feature(feature_key, opts):
        best_delta = 0.0
        best_new_val = None
        for new_val in opts:
            # Build perturbed inputs
            a2, cpt2, bpp2, ch2, mhr2, std2, fl2, th2 = age, cp, BP, CH, maxhr, STD, fluro, Th

            if feature_key == "age":
                a2 = float(new_val)
                if a2 == float(age):
                    continue
            elif feature_key == "pressure":
                bpp2 = float(new_val)
                if bpp2 == float(BP):
                    continue
            elif feature_key == "cholesterol":
                ch2 = float(new_val)
                if ch2 == float(CH):
                    continue
            elif feature_key == "heart_rate":
                mhr2 = float(new_val)
                if mhr2 == float(maxhr):
                    continue
            elif feature_key == "ischemia":
                std2 = float(new_val)
                if std2 == float(STD):
                    continue
            elif feature_key == "symptom":
                cpt2 = int(new_val)
                if cpt2 == int(cp):
                    continue
            elif feature_key == "vessel":
                fl2 = int(new_val)
                if fl2 == int(fluro):
                    continue
            elif feature_key == "ischemia_thallium":
                th2 = float(new_val)
                if th2 == float(Th):
                    continue
            else:
                continue

            prob1 = predict_prob_percent(a2, cpt2, bpp2, ch2, mhr2, std2, fl2, th2)
            delta = prob1 - base_prob
            if abs(delta) > abs(best_delta):
                best_delta = delta
                best_new_val = new_val
        return best_delta, best_new_val

    feature_deltas = []
    for feature_key, opts in candidates:
        # Ensure opts has unique values to avoid extra predictions
        uniq_opts = []
        seen = set()
        for v in opts:
            fv = float(v)
            if fv not in seen:
                uniq_opts.append(v)
                seen.add(fv)
        delta, best_new_val = best_delta_for_feature(feature_key, uniq_opts)
        feature_deltas.append((abs(delta), feature_key, delta, best_new_val))

    feature_deltas.sort(key=lambda x: x[0], reverse=True)

    # Sign gate (Point #18): prevent contradiction between risk label and driver direction.
    # If overall risk is High (>=50%), show only drivers that increase predicted risk (delta > 0).
    # If overall risk is Low (<50%), show only drivers that decrease predicted risk (delta < 0).
    target_sign = 1 if base_prob >= 50 else -1
    selected = []
    for abs_delta, feature_key, delta, best_new_val in feature_deltas:
        if delta == 0:
            continue
        if (delta > 0 and target_sign == 1) or (delta < 0 and target_sign == -1):
            selected.append((abs_delta, feature_key, delta, best_new_val))
        if len(selected) >= 3:
            break

    # NOTE: We intentionally do NOT fall back to top-3 by sensitivity.
    # This avoids contradictory explanations (e.g., High risk explained by drivers that decrease risk).
    # UI can handle fewer than 3 drivers.

    orig_map = {
        "age": age,
        "pressure": BP,
        "cholesterol": CH,
        "heart_rate": maxhr,
        "ischemia": STD,
        "symptom": cp,
        "vessel": fluro,
        "ischemia_thallium": Th,
    }

    def direction_word(new_val, orig_val):
        try:
            nv = float(new_val)
            ov = float(orig_val)
        except Exception:
            return "changing"
        if nv > ov:
            return "Higher"
        if nv < ov:
            return "Lower"
        return "Changing"

    def feature_term(feature_key):
        if feature_key == "cholesterol":
            return "cholesterol"
        if feature_key == "pressure":
            return "blood pressure"
        if feature_key == "heart_rate":
            return "maximum heart rate"
        if feature_key == "ischemia":
            return "ST depression (ischemia)"
        if feature_key == "vessel":
            return "vessel count (vessels)"
        if feature_key == "symptom":
            return "chest pain type"
        if feature_key == "ischemia_thallium":
            return "Thallium pattern (ischemia)"
        if feature_key == "age":
            return "age"
        return feature_key

    def driver_text(feature_key, new_val, delta_prob):
        term = feature_term(feature_key)
        dir_word = direction_word(new_val, orig_map.get(feature_key))

        if delta_prob > 0:
            risk_change = "increases predicted risk"
        elif delta_prob < 0:
            risk_change = "decreases predicted risk"
        else:
            risk_change = "has little effect on predicted risk"

        return f"{dir_word} {term} {risk_change} in this case."

    top_risks = []
    for abs_delta, feature_key, delta, best_new_val in selected:
        top_risks.append({
            "text": driver_text(feature_key, best_new_val, delta),
            "weight": float(abs_delta),
            "type": feature_key
        })

    # Protective factors are not used by the current UI logic; keep empty.
    return top_risks, []

#-------------------------Summary--------------------------------------
def generate_summary(risk, factors):

    if len(factors) >= 2:
        return f"{risk} risk driven by {factors[0].lower()} and {factors[1].lower()}."
    
    elif len(factors) == 1:
        return f"{risk} risk primarily due to {factors[0].lower()}."
    
    else:
        return f"{risk} risk with no major contributing factors."

def generate_narrative(risk, prob, factors):

    # ---------------- INTRO ----------------
    if risk == "High":
        intro = f"Your heart disease risk is high ({prob}%)."
    elif risk == "Moderate":
        intro = f"Your heart disease risk is moderate ({prob}%)."
    else:
        intro = f"Your heart disease risk is low ({prob}%)."

    # ---------------- CLEAN FACTORS ----------------
    clean_factors = [f.replace("st depression", "ST depression") for f in factors]

    # ---------------- CORE INTERPRETATION ----------------
    if len(clean_factors) >= 2:
        core = f"The combination of {clean_factors[0].lower()} and {clean_factors[1].lower()}"
    elif len(clean_factors) == 1:
        core = f"The primary contributing factor is {clean_factors[0].lower()}"
    else:
        core = "No major high-risk indicators were detected"

    # ---------------- INTERACTION ----------------
    if any("ischemia" in f.lower() for f in clean_factors):
        interaction = " indicates reduced blood flow to the heart"
    elif any("vessel" in f.lower() for f in clean_factors):
        interaction = " suggests possible coronary artery blockage"
    elif any("pressure" in f.lower() for f in clean_factors):
        interaction = " increases strain on the cardiovascular system"
    else:
        interaction = " contributes to increased cardiovascular stress"

    # ---------------- ADDITIONAL FACTOR ----------------
    additional = ""
    if len(clean_factors) >= 3:
        additional = f" This effect is further worsened by {clean_factors[2].lower()}."

    # ---------------- IMPLICATION ----------------
    if risk == "High":
        implication = (
            " This pattern is strongly associated with underlying cardiovascular disease "
            "and requires prompt medical evaluation."
        )
    elif risk == "Moderate":
        implication = (
            " This suggests an emerging risk that should be addressed with lifestyle changes "
            "and regular monitoring."
        )
    else:
        implication = (
            " This indicates stable cardiovascular health, but maintaining healthy habits is important."
        )

    # ---------------- FINAL ----------------
    narrative = f"{intro} {core}{interaction}.{additional}{implication}"

    return narrative

#-------------------------Confidence / Uncertainty-----------------------------
def compute_confidence(prob_percent: float):
    """
    Map raw probability into a coarse confidence band.
    This is NOT statistical calibration, just a UX-level signal.
    """
    distance_from_mid = abs(prob_percent - 50)

    if distance_from_mid >= 30:
        level = "High"
        note = "Model is strongly confident in this estimate."
    elif distance_from_mid >= 15:
        level = "Medium"
        note = "Model is reasonably confident, but results should be interpreted with context."
    else:
        level = "Low (borderline)"
        note = "Result is close to the decision boundary; interpretation should be cautious."

    return level, note

def detect_edge_cases(age, cp, BP, CH, maxhr, STD, fluro, Th):
    warnings = []

    # Extreme values (still within validation ranges)
    if BP >= 180:
        warnings.append("Resting blood pressure is extremely high. Ensure this value is correct.")
    if CH >= 350:
        warnings.append("Cholesterol is extremely high. Ensure this value is correct.")
    if maxhr <= 80:
        warnings.append("Maximum heart rate is very low. Ensure this value is correct.")
    if STD >= 5:
        warnings.append("ST depression is very high. Ensure this value is correct.")

    # Unusual combinations
    if age <= 30 and CH >= 300:
        warnings.append("Unusual combination: very young age with very high cholesterol.")
    if age <= 35 and fluro >= 2:
        warnings.append("Unusual combination: young age with multiple affected vessels.")
    if maxhr <= 90 and STD >= 3:
        warnings.append("Unusual combination: very low max heart rate with high ST depression.")
    if BP <= 95 and STD >= 3:
        warnings.append("Unusual combination: low blood pressure with high ST depression.")
    if age >= 80 and maxhr >= 200:
        warnings.append("Unusual combination: very high max heart rate for advanced age.")

    return warnings

def compute_stability(prob_percent: float, low_threshold: float = 30.0, high_threshold: float = 70.0, margin: float = 2.0):
    """
    Anti-flicker signal for UX: mark results close to category thresholds.
    """
    near_low = abs(prob_percent - low_threshold) <= margin
    near_high = abs(prob_percent - high_threshold) <= margin

    if near_low:
        return True, f"Risk score is close to the Low/Moderate threshold ({low_threshold}%)."
    if near_high:
        return True, f"Risk score is close to the Moderate/High threshold ({high_threshold}%)."
    return False, None

#-------------------------Report Generation-----------------------------
def generate_report(risk, prob, explanations):

    # -------- CLEAN INPUT --------
    factors = [exp.lower() for exp in explanations]

    # -------- SUMMARY --------
    summary = f"Your estimated heart disease risk is {risk.lower()} ({prob}%)."

    # -------- KEY DRIVERS (TOP 3 ONLY) --------
    key_drivers = []
    for f in factors:
        if "cholesterol" in f:
            key_drivers.append("elevated cholesterol levels")
        elif "st depression" in f:
            key_drivers.append("signs of myocardial ischemia (ST depression)")
        elif "vessel" in f:
            key_drivers.append("multiple affected coronary vessels")
        elif "pressure" in f:
            key_drivers.append("high blood pressure")

    key_drivers = list(dict.fromkeys(key_drivers))[:3]  # remove duplicates

    # -------- INTERPRETATION --------
    if risk == "High":
        interpretation = (
            "This pattern indicates a strong likelihood of underlying cardiovascular disease, "
            "with possible reduced blood flow to the heart and increased cardiac strain."
        )
    elif risk == "Moderate":
        interpretation = (
            "This suggests an elevated cardiovascular risk that may progress if risk factors are not managed."
        )
    else:
        interpretation = (
            "This indicates relatively stable cardiovascular health, though continued monitoring is recommended."
        )

    # -------- RECOMMENDATIONS (CASE-SPECIFIC) --------
    recommendations = []

    if any("cholesterol" in f for f in factors):
        recommendations.append("Adopt a low-fat, heart-healthy diet to manage cholesterol levels.")

    if any("pressure" in f for f in factors):
        recommendations.append("Monitor blood pressure regularly and reduce salt intake.")

    if any("st depression" in f for f in factors):
        recommendations.append("Seek further cardiac evaluation to assess possible ischemia.")

    if any("vessel" in f for f in factors):
        recommendations.append("Consult a cardiologist for detailed vascular assessment.")

    if risk == "High":
        recommendations.append("Prompt medical consultation is strongly advised.")

    # -------- ENSURE MIN RECOMMENDATIONS (REDUCE REDUNDANCY) --------
    # Keep recommendations helpful even when only one factor triggers.
    baseline_recs = [
        "Prioritize regular aerobic activity (as medically appropriate) and maintain a healthy body weight.",
        "Avoid smoking, limit alcohol, and manage stress and sleep to support cardiovascular health.",
        "Follow up with a clinician for routine monitoring if risk factors persist or symptoms develop.",
    ]

    for rec in baseline_recs:
        if len(recommendations) >= 3:
            break
        if rec not in recommendations:
            recommendations.append(rec)

    # -------- FORMAT OUTPUT --------
    report = {
        "summary": summary,
        "drivers": key_drivers,
        "interpretation": interpretation,
        "recommendations": recommendations
    }

    return report

#-----------------------Explanation generator---------------------------
def generate_simulation_explanation(old_inputs, new_inputs, change):

    # -------- NO CHANGE --------
    if change == 0:
        return "No change detected. Modify inputs to simulate different scenarios."

    # -------- MAGNITUDE --------
    abs_change = abs(change)

    if abs_change < 2:
        magnitude = "slightly"
    elif abs_change < 5:
        magnitude = "moderately"
    else:
        magnitude = "significantly"

    direction = "decreased" if change < 0 else "increased"

    # -------- FACTOR ANALYSIS --------
    improvements = []
    worsenings = []

    if new_inputs["CH"] < old_inputs["CH"]:
        improvements.append("lower cholesterol")

    if new_inputs["BP"] < old_inputs["BP"]:
        improvements.append("better blood pressure")

    if new_inputs["STD"] < old_inputs["STD"]:
        improvements.append("reduced ST depression")

    if new_inputs["maxhr"] > old_inputs["maxhr"]:
        improvements.append("improved heart rate response")

    # worsening factors
    if new_inputs["CH"] > old_inputs["CH"]:
        worsenings.append("higher cholesterol")

    if new_inputs["BP"] > old_inputs["BP"]:
        worsenings.append("increased blood pressure")

    if new_inputs["STD"] > old_inputs["STD"]:
        worsenings.append("higher ST depression")

    if new_inputs["maxhr"] < old_inputs["maxhr"]:
        worsenings.append("reduced heart rate response")

    # -------- BUILD SENTENCE --------
    explanation = f"Risk {direction} {magnitude}ly ({change}%)."

    # Case 1: Risk decreased → talk about improvements
    if change < 0:
        if improvements:
            explanation += f" Improvement is mainly driven by {improvements[0]}."

    # Case 2: Risk increased → talk about worsenings
    elif change > 0:
        if worsenings:
            explanation += f" Increase is mainly driven by {worsenings[0]}."
        else:
            explanation += " Increase is due to combined negative changes."

    # Add secondary factor (only if meaningful)
    if change < 0 and worsenings:
        explanation += f" However, {worsenings[0]} still contributes to risk."

    return explanation


def _spa_ready():
    return os.path.isfile(os.path.join(SPA_DIR, "index.html"))


def _send_spa_index():
    return send_from_directory(SPA_DIR, "index.html")


def _spa_or_template(template_name, **kwargs):
    if _spa_ready():
        return _send_spa_index()
    return render_template(template_name, **kwargs)


# ---------------- HOME ----------------
@app.route("/")
def home():
    if _spa_ready():
        return _send_spa_index()
    if "username" in session:
        return jsonify({"message": "Authenticated"})
    return jsonify({"message": "Unauthorized"}), 401

# ---------------- ME ----------------
@app.route("/me", methods=["GET"])
def me():
    if "username" in session:
        return jsonify({"username": session["username"]})
    return jsonify({"message": "Not logged in"}), 401

#------------------------LAST_PREDICTION----------------------
@app.route("/last_prediction", methods=["GET"])
def last_prediction():
    if "username" not in session:
        return jsonify({"message": "Unauthorized"}), 401

    with connect(DB_PATH) as con:
        cursor = con.cursor()
        cursor.execute("""
            SELECT probability
            FROM history
            WHERE username=?
            ORDER BY timestamp DESC
            LIMIT 1
        """, (session['username'],))

        row = cursor.fetchone()

    # Empty history is normal for new users — use 200 so clients/network panels
    # don't treat this as a "Not Found" route error (404).
    if not row:
        return jsonify({"score": None, "level": None, "message": "No saved predictions yet"}), 200

    prob_percent = float(row[0]) * 100

    if prob_percent < 30:
        risk = "Low"
    elif prob_percent <= 70:
        risk = "Moderate"
    else:
        risk = "High"

    return jsonify({
        "score": round(prob_percent, 2),
        "level": risk
    })

# ---------------- FIND PAGE ----------------
@app.route("/find")
def find():
    if "username" not in session:
        return redirect(url_for("login"))
    if _spa_ready():
        return _send_spa_index()
    return render_template("find.html", name=session["username"])

# ---------------- PREDICTION ----------------
@app.route("/predict", methods=["POST"])
def predict():
    if 'username' not in session:
        return jsonify({"error": "Unauthorized"}), 401

    try:
        data = request.get_json()

        age = float(data["age"])
        cp = int(data["cp"])
        BP = float(data["bp"])
        CH = float(data["chol"])
        maxhr = float(data["maxhr"])
        STD = float(data["std"])
        fluro = float(data["fluro"])
        Th = float(data["th"])

        # 🔒 Validation
        errors = []

        if not (1 <= age <= 120):
            errors.append("Age must be between 1 and 120.")
        if not (80 <= BP <= 200):
            errors.append("Blood pressure should be between 80 and 200 mm Hg.")
        if not (100 <= CH <= 400):
            errors.append("Cholesterol should be between 100 and 400 mg/dl.")
        if not (60 <= maxhr <= 220):
            errors.append("Max heart rate should be between 60 and 220.")
        if not (0 <= STD <= 6):
            errors.append("ST depression must be between 0 and 6.")
        if not (0 <= fluro <= 3):
            errors.append("Number of vessels must be between 0 and 3.")
        if Th not in [3, 6, 7]:
            errors.append("Thallium value must be 3, 6, or 7.")

        if errors:
            return jsonify({"errors": errors}), 400

        # -------- FEATURES --------
        features = pd.DataFrame([{
            "Age": age,
            "Chest pain type": cp,
            "BP": BP,
            "Cholesterol": CH,
            "Max HR": maxhr,
            "ST depression": STD,
            "Number of vessels fluro": fluro,
            "Thallium": Th
        }])

        features["Chol_Age_Ratio"] = features["Cholesterol"] / features["Age"]
        features["Heart_Stress"] = features["ST depression"] * features["BP"]

        prediction = int(model.predict(features)[0])
        probability = float(model.predict_proba(features)[0][1])
        prob_percent = round(probability * 100, 2)

        # -------- EXPLANATIONS --------
        top_risks, protective = generate_explanations(age, cp, BP, CH, maxhr, STD, fluro, Th)
        explanations = [f["text"] for f in top_risks]

        # -------- SESSION CACHE (RESTORED) --------
        session['last_inputs'] = {
            "age": age,
            "cp": cp,
            "BP": BP,
            "CH": CH,
            "maxhr": maxhr,
            "STD": STD,
            "fluro": fluro,
            "Th": Th
        }

        session['last_probability'] = prob_percent

        # -------- DATABASE HISTORY (RESTORED) --------
        previous_risk_score_percent = None
        delta_percent = None
        trend_text = None

        with connect(DB_PATH) as con:
            cursor = con.cursor()

            cursor.execute("""
                SELECT probability
                FROM history
                WHERE username=?
                ORDER BY timestamp DESC, id DESC
                LIMIT 1
            """, (session['username'],))
            previous_row = cursor.fetchone()

            if previous_row is not None:
                previous_risk_score_percent = round(float(previous_row[0]) * 100, 2)
                delta_percent = round(prob_percent - previous_risk_score_percent, 2)

                if delta_percent > 0:
                    trend_text = "increased"
                elif delta_percent < 0:
                    trend_text = "decreased"
                else:
                    trend_text = "stable"

            cursor.execute("""
            INSERT INTO history (
                username, age, cp, bp, chol, maxhr, std, fluro, th,
                prediction, probability, timestamp
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                session['username'],
                age, cp, BP, CH, maxhr, STD, fluro, Th,
                prediction,
                probability,
                datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            ))
            con.commit()

        # -------- RISK --------
        if prob_percent < 30:
            risk = "Low"
            risk_css = "low-risk"
        elif prob_percent <= 70:
            risk = "Moderate"
            risk_css = "moderate-risk"
        else:
            risk = "High"
            risk_css = "high-risk"

        # -------- EXTRA --------
        confidence_level, confidence_note = compute_confidence(prob_percent)
        stability_near_threshold, stability_note = compute_stability(prob_percent)
        report = generate_report(risk, prob_percent, explanations)
        narrative = generate_narrative(risk, prob_percent, explanations)
        summary = generate_summary(risk, explanations)
        edge_warnings = detect_edge_cases(age, cp, BP, CH, maxhr, STD, fluro, Th)

        # -------- FINAL RESPONSE --------
        return jsonify({
            "risk_score_percent": prob_percent,
            "risk_level": risk,
            "risk_css": risk_css,

            "summary": summary,
            "clinical_narrative": narrative,
            "clinical_insights": explanations,
            "clinical_report": report,

            "confidence_level": confidence_level,
            "confidence_note": confidence_note,
            "stability_near_threshold": stability_near_threshold,
            "stability_note": stability_note,

            "edge_warnings": edge_warnings,

            # 🔥 RESTORED COMPARISON DATA
            "previous_risk_score_percent": previous_risk_score_percent,
            "delta_percent": delta_percent,
            "trend_text": trend_text
        })

    except Exception as e:
        logging.error(f"Prediction error: {e}")
        return jsonify({"error": "Something went wrong"}), 500

# ---------------- SIGNUP ----------------
@app.route("/signup", methods=["GET", "POST"])
def signup():
    if request.method == "POST":

        # 🔁 SUPPORT BOTH FORM + JSON (important)
        if request.is_json:
            data = request.get_json()
            un = data.get("un")
            em = data.get("em")
        else:
            un = request.form["un"]
            em = request.form["em"]

        # Generate 6-digit password
        pw = "".join(str(randrange(10)) for _ in range(6))
        hashed_pw = generate_password_hash(pw)

        try:
            with connect(DB_PATH) as con:
                cursor = con.cursor()

                cursor.execute(
                    "INSERT INTO user VALUES (?, ?, ?)",
                    (un, hashed_pw, em)
                )
                con.commit()

            mail_status = send_password_email(
                em, un, pw, subject="Welcome — Your Login Password"
            )

            if mail_status == "sent":
                message = "Account created successfully! Password sent to email."
            elif mail_status == "skipped":
                message = (
                    "Account created. Outbound email is not configured on this server. "
                    f"Your temporary password is: {pw}"
                )
            else:
                logging.warning("Signup email failed for %s; user can use returned password", un)
                message = (
                    "Account created, but email delivery failed. "
                    f"Your temporary password is: {pw}"
                )

            if request.is_json:
                payload = {"message": message}
                if mail_status in ("skipped", "failed"):
                    payload["temporary_password"] = pw
                return jsonify(payload), 200
            else:
                return render_template("login.html", msg=message)

        except Exception:
            error_msg = "Username already exists. Please choose a different one."

            if request.is_json:
                return jsonify({"message": error_msg}), 400
            else:
                return render_template("signup.html", msg=error_msg)

    return _spa_or_template("signup.html")

# ---------------- LOGIN ----------------
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":

        # 🔁 SUPPORT BOTH JSON + FORM
        if request.is_json:
            data = request.get_json()
            un = data.get("un")
            pw = data.get("pw")
        else:
            un = request.form["un"]
            pw = request.form["pw"]

        try:
            with connect(DB_PATH) as con:
                cursor = con.cursor()
                cursor.execute(
                    "SELECT password FROM user WHERE username=?",
                    (un,)
                )
                data = cursor.fetchone()

            if data and check_password_hash(data[0], pw):
                session['username'] = un

                message = "Login successful"

                # 🔁 JSON response for React
                if request.is_json:
                    return jsonify({
                        "message": message,
                        "username": un
                    }), 200

                # 🔁 HTML fallback
                return redirect(url_for('home'))

            else:
                error_msg = "Invalid username or password."

                if request.is_json:
                    return jsonify({"message": error_msg}), 401

                return render_template("login.html", msg=error_msg)

        except Exception as e:
            error_msg = "Issue: " + str(e)

            if request.is_json:
                return jsonify({"message": error_msg}), 500

            return render_template("login.html", msg=error_msg)

    return _spa_or_template("login.html")

# ---------------- FORGOT PASSWORD ----------------
@app.route("/forgot", methods=["GET", "POST"])
def forgot():
    if request.method == "POST":

        # 🔁 SUPPORT BOTH JSON + FORM
        if request.is_json:
            data = request.get_json()
            un = data.get("un")
            em = data.get("em")
        else:
            un = request.form["un"]
            em = request.form["em"]

        try:
            with connect(DB_PATH) as con:
                cursor = con.cursor()
                cursor.execute(
                    "SELECT email FROM user WHERE username=?",
                    (un,)
                )
                data = cursor.fetchone()

            if not data:
                msg = "Username not found."

                if request.is_json:
                    return jsonify({"message": msg}), 400
                return render_template("forgot.html", msg=msg)

            # Verify email
            if data[0].strip().lower() != em.strip().lower():
                msg = "Email does not match our records."

                if request.is_json:
                    return jsonify({"message": msg}), 400
                return render_template("forgot.html", msg=msg)

            # Generate new password
            new_pw = "".join(str(randrange(10)) for _ in range(6))
            hashed_pw = generate_password_hash(new_pw)

            with connect(DB_PATH) as con:
                cursor = con.cursor()
                cursor.execute(
                    "UPDATE user SET password=? WHERE username=?",
                    (hashed_pw, un)
                )
                con.commit()

            mail_status = send_password_email(
                em, un, new_pw,
                subject="Your New Password — Heart Disease Prediction System",
            )

            if mail_status == "sent":
                msg = "A new password has been sent to your registered email."
            elif mail_status == "skipped":
                msg = (
                    "Password updated. Email is not configured on this server. "
                    f"Your new password is: {new_pw}"
                )
            else:
                logging.warning("Forgot-password email failed for %s", un)
                msg = (
                    "Password reset, but email delivery failed. "
                    f"Your new password is: {new_pw}"
                )

            if request.is_json:
                payload = {"message": msg}
                if mail_status in ("skipped", "failed"):
                    payload["temporary_password"] = new_pw
                return jsonify(payload), 200

            return render_template("login.html", msg=msg)

        except Exception as e:
            msg = "Issue: " + str(e)

            if request.is_json:
                return jsonify({"message": msg}), 500

            return render_template("forgot.html", msg=msg)

    return _spa_or_template("forgot.html")

# ---------------- LOGOUT ----------------
@app.route("/logout", methods=["POST"])
def logout():
    session.clear()

    if request.is_json:
        return jsonify({"message": "Logged out successfully"}), 200

    return redirect(url_for("login"))

# ---------------------History (JSON API; /history path is the React route)-------------
@app.route("/api/history")
def history_api():
    if 'username' not in session:
        return jsonify({"error": "Unauthorized"}), 401

    with connect(DB_PATH) as con:
        cursor = con.cursor()

        cursor.execute("""
            SELECT age, cp, bp, chol, maxhr, std, fluro, th,
                   prediction, probability, timestamp
            FROM history
            WHERE username=?
            ORDER BY timestamp DESC
        """, (session['username'],))

        rows = cursor.fetchall()

    processed_rows = []

    for row in rows:
        prob_percent = float(row[9]) * 100

        if prob_percent < 30:
            risk = "Low"
        elif prob_percent <= 70:
            risk = "Moderate"
        else:
            risk = "High"

        ts = row[10]
        if isinstance(ts, bytes):
            ts = ts.decode("utf-8", errors="replace")
        elif hasattr(ts, "isoformat"):
            ts = ts.isoformat(sep=" ", timespec="seconds")

        processed_rows.append({
            "age": float(row[0]) if row[0] is not None else None,
            "cp": int(row[1]) if row[1] is not None else None,
            "bp": float(row[2]) if row[2] is not None else None,
            "chol": float(row[3]) if row[3] is not None else None,
            "maxhr": float(row[4]) if row[4] is not None else None,
            "std": float(row[5]) if row[5] is not None else None,
            "fluro": float(row[6]) if row[6] is not None else None,
            "th": float(row[7]) if row[7] is not None else None,
            "prediction": _sqlite_int(row[8]),
            "probability": round(prob_percent, 2),
            "timestamp": ts,
            "risk_level": risk
        })

    # 🔥 Correct trend calculation (OUTSIDE loop)
    trend = None
    if len(rows) >= 2:
        latest = float(rows[0][9])
        previous = float(rows[1][9])

        if latest > previous:
            trend = "increasing"
        elif latest < previous:
            trend = "decreasing"
        else:
            trend = "stable"

    return jsonify({
        "rows": processed_rows,
        "trend": trend
    })

#---------------------Simulation-------------------
@app.route("/simulate", methods=["POST"])
def simulate():
    if 'username' not in session:
        return redirect(url_for('login'))

    try:
        old_inputs = session.get('last_inputs')
        old_prob = session.get('last_probability')
        if not old_inputs or old_prob is None:
            return render_template(
                "find.html",
                msg="Please run a prediction before using simulation.",
                name=session['username']
            )
        age = float(request.form["age"])
        cp = int(request.form["r1"])
        BP = float(request.form["BP"])
        CH = float(request.form["CH"])
        maxhr = float(request.form["maxhr"])
        STD = float(request.form["STD"])
        fluro = float(request.form["fluro"])
        Th = float(request.form["Th"])

        new_inputs = {
            "age": age,
            "cp": cp,
            "BP": BP,
            "CH": CH,
            "maxhr": maxhr,
            "STD": STD,
            "fluro": fluro,
            "Th": Th
        }

        features = pd.DataFrame([{
            "Age": age,
            "Chest pain type": cp,
            "BP": BP,
            "Cholesterol": CH,
            "Max HR": maxhr,
            "ST depression": STD,
            "Number of vessels fluro": fluro,
            "Thallium": Th
        }])
        # -------- FEATURE ENGINEERING (MATCH TRAINING) --------
        features["Chol_Age_Ratio"] = features["Cholesterol"] / features["Age"]
        features["Heart_Stress"] = features["ST depression"] * features["BP"]

        prediction = int(model.predict(features)[0])
        probability = float(model.predict_proba(features)[0][1])
        prob_percent = round(probability * 100, 2)
        sim_prob = prob_percent
        change = round(sim_prob - old_prob, 2)
        sim_explanation = generate_simulation_explanation(old_inputs, new_inputs, change)

        if change > 0:
            trend = "increase"
        elif change < 0:
            trend = "decrease"
        else:
            trend = "no change"

        return render_template(
            "find.html",
            sim_prediction=prediction,
            sim_probability=sim_prob,
            sim_change=change,
            sim_trend=trend,
            sim_explanation=sim_explanation,
            name=session['username'],
            form_data=request.form
        )

    except Exception as e:
        logging.error(f"Simulation error: {e}")

        return render_template(
            "find.html",
            msg="Something went wrong during simulation.",
            name=session['username']
        )


# ---------------- Production React bundle (Vite → static/spa/) ----------------
@app.route("/assets/<path:filename>")
def spa_asset_files(filename):
    if not _spa_ready():
        abort(404)
    assets_dir = os.path.join(SPA_DIR, "assets")
    if not os.path.isdir(assets_dir):
        abort(404)
    return send_from_directory(assets_dir, filename)


@app.route("/<path:path>")
def spa_catchall(path):
    """Serve built files (favicon, etc.) or index.html for client-side routes."""
    if not _spa_ready():
        abort(404)
    base = os.path.realpath(SPA_DIR)
    if ".." in path.split("/"):
        abort(404)
    full = os.path.realpath(os.path.join(SPA_DIR, path))
    if not (full == base or full.startswith(base + os.sep)):
        abort(404)
    if os.path.isfile(full):
        return send_from_directory(SPA_DIR, path)
    return _send_spa_index()


# ---------------- RUN APP ----------------
if __name__ == "__main__":
    # Default 5001 — port 5000 is often taken (other dev tools, system services). Override: PORT=5000 python3 app.py
    _port = int(os.environ.get("PORT", os.environ.get("FLASK_RUN_PORT", "5001")))
    print(f"Listening on http://127.0.0.1:{_port}  (set PORT=... to change)")
    # use_reloader=False avoids two Python processes fighting for the same port.
    app.run(debug=True, use_reloader=False, host="127.0.0.1", port=_port)