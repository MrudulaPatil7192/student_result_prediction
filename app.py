from flask import Flask, request, render_template_string, jsonify
import pickle
import numpy as np
import os

app = Flask(__name__)

# Safe model loader targeting model.pkl in the same directory
def load_model():
    base_path = os.path.dirname(__file__)
    # Works for 'model.pkl' or 'model (2).pkl' if renamed to model.pkl
    file_path = os.path.join(base_path, "model.pkl")
    if not os.path.exists(file_path):
        # Fallback check for alternate file names
        for f in os.listdir(base_path):
            if f.endswith(".pkl"):
                file_path = os.path.join(base_path, f)
                break
    with open(file_path, "rb") as file:
        return pickle.load(file)

try:
    model = load_model()
    print("Model loaded successfully!")
except Exception as e:
    model = None
    print(f"Error loading model binary: {e}")

# Interactive Glassmorphic UI with Keyframe Animations & Live Result Rendering
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Student Performance Analytics</title>
    <style>
        :root {
            --bg-dark: #0b0f19;
            --card-bg: rgba(23, 32, 54, 0.7);
            --card-border: rgba(255, 255, 255, 0.12);
            --accent-glow: #6366f1;
            --pass-green: #10b981;
            --fail-red: #ef4444;
            --text-light: #f8fafc;
            --text-dim: #94a3b8;
        }

        * {
            box-sizing: border-box;
            margin: 0;
            padding: 0;
            font-family: 'Segoe UI', system-ui, -apple-system, sans-serif;
        }

        body {
            background: radial-gradient(circle at top right, #1e1b4b, var(--bg-dark));
            color: var(--text-light);
            min-height: 100vh;
            padding: 30px 20px;
            display: flex;
            justify-content: center;
            align-items: center;
        }

        .dashboard-container {
            width: 100%;
            max-width: 1100px;
            animation: slideUp 0.6s cubic-bezier(0.16, 1, 0.3, 1);
        }

        .header-title {
            text-align: center;
            margin-bottom: 30px;
        }

        .header-title h1 {
            font-size: 2.2rem;
            font-weight: 800;
            background: linear-gradient(90deg, #818cf8, #c084fc, #38bdf8);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            margin-bottom: 6px;
        }

        .header-title p {
            color: var(--text-dim);
            font-size: 0.95rem;
        }

        .grid-layout {
            display: grid;
            grid-template-columns: 1fr;
            gap: 24px;
        }

        @media (min-width: 850px) {
            .grid-layout {
                grid-template-columns: 7fr 5fr;
            }
        }

        .glass-panel {
            background: var(--card-bg);
            backdrop-filter: blur(16px);
            -webkit-backdrop-filter: blur(16px);
            border: 1px solid var(--card-border);
            border-radius: 16px;
            padding: 24px;
            box-shadow: 0 10px 30px rgba(0,0,0,0.5);
            transition: transform 0.3s ease, border-color 0.3s ease;
        }

        .glass-panel:hover {
            border-color: rgba(99, 102, 241, 0.4);
        }

        .panel-title {
            font-size: 1.1rem;
            font-weight: 700;
            letter-spacing: 0.5px;
            color: #e2e8f0;
            margin-bottom: 20px;
            border-bottom: 1px solid var(--card-border);
            padding-bottom: 10px;
            display: flex;
            align-items: center;
            gap: 8px;
        }

        .input-grid {
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 14px;
        }

        .form-group {
            display: flex;
            flex-direction: column;
        }

        .full-width {
            grid-column: span 2;
        }

        label {
            font-size: 0.8rem;
            font-weight: 600;
            color: var(--text-dim);
            margin-bottom: 6px;
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }

        input, select {
            background: rgba(11, 15, 25, 0.8);
            border: 1px solid var(--card-border);
            border-radius: 8px;
            padding: 10px 12px;
            color: #ffffff;
            font-size: 0.9rem;
            outline: none;
            transition: all 0.2s ease;
        }

        input:focus, select:focus {
            border-color: var(--accent-glow);
            box-shadow: 0 0 0 3px rgba(99, 102, 241, 0.3);
        }

        .btn-submit {
            grid-column: span 2;
            margin-top: 10px;
            padding: 14px;
            background: linear-gradient(90deg, #6366f1, #8b5cf6);
            color: #ffffff;
            border: none;
            border-radius: 8px;
            font-size: 1rem;
            font-weight: 700;
            cursor: pointer;
            transition: all 0.3s ease;
            box-shadow: 0 4px 15px rgba(99, 102, 241, 0.4);
        }

        .btn-submit:hover {
            transform: translateY(-2px);
            box-shadow: 0 6px 20px rgba(99, 102, 241, 0.6);
        }

        .btn-submit:active {
            transform: translateY(0);
        }

        /* Result Display Tile */
        .result-box {
            text-align: center;
            padding: 24px;
            border-radius: 12px;
            background: rgba(11, 15, 25, 0.6);
            border: 1px solid var(--card-border);
            margin-bottom: 20px;
        }

        .result-box.pass-style {
            border-left: 6px solid var(--pass-green);
            box-shadow: 0 0 20px rgba(16, 185, 129, 0.2);
        }

        .result-box.fail-style {
            border-left: 6px solid var(--fail-red);
            box-shadow: 0 0 20px rgba(239, 68, 68, 0.2);
        }

        .badge-text {
            font-size: 2.2rem;
            font-weight: 800;
            margin-top: 8px;
            animation: bounceIn 0.5s ease;
        }

        .pass-text { color: var(--pass-green); }
        .fail-text { color: var(--fail-red); }

        .data-table {
            width: 100%;
            border-collapse: collapse;
            font-size: 0.88rem;
        }

        .data-table td {
            padding: 10px 0;
            border-bottom: 1px solid var(--card-border);
            color: var(--text-dim);
        }

        .data-table td:last-child {
            text-align: right;
            color: var(--text-light);
            font-weight: 600;
        }

        .error-alert {
            background: rgba(239, 68, 68, 0.2);
            border: 1px solid var(--fail-red);
            color: #fca5a5;
            padding: 12px;
            border-radius: 8px;
            font-size: 0.85rem;
            margin-bottom: 15px;
        }

        .placeholder-state {
            text-align: center;
            padding: 60px 20px;
            color: var(--text-dim);
        }

        /* Animations */
        @keyframes slideUp {
            from { opacity: 0; transform: translateY(20px); }
            to { opacity: 1; transform: translateY(0); }
        }

        @keyframes bounceIn {
            0% { transform: scale(0.7); opacity: 0; }
            70% { transform: scale(1.05); }
            100% { transform: scale(1); opacity: 1; }
        }
    </style>
</head>
<body>

<div class="dashboard-container">
    <div class="header-title">
        <h1>🎓 Student Performance Dashboard</h1>
        <p>Support Vector Classifier (SVC) • Live AI Prediction Canvas</p>
    </div>

    <div class="grid-layout">
        <!-- Input Form Pane -->
        <div class="glass-panel">
            <div class="panel-title">⚙️ Student Evaluation Features</div>
            
            <form method="POST" action="/">
                <div class="input-grid">
                    <div class="form-group">
                        <label for="gender">Gender</label>
                        <select name="gender" id="gender">
                            <option value="1" {% if inputs and inputs['gender'] == 1 %}selected{% endif %}>Male</option>
                            <option value="0" {% if inputs and inputs['gender'] == 0 %}selected{% endif %}>Female</option>
                        </select>
                    </div>

                    <div class="form-group">
                        <label for="age">Age</label>
                        <input type="number" name="age" id="age" min="10" max="60" value="{{ inputs['age'] if inputs else 18 }}" required>
                    </div>

                    <div class="form-group">
                        <label for="study_hours">Study Hours / Wk</label>
                        <input type="number" step="0.1" name="study_hours" id="study_hours" min="0" max="100" value="{{ inputs['study_hours'] if inputs else 15 }}" required>
                    </div>

                    <div class="form-group">
                        <label for="attendance">Attendance (%)</label>
                        <input type="number" step="0.1" name="attendance" id="attendance" min="0" max="100" value="{{ inputs['attendance'] if inputs else 85 }}" required>
                    </div>

                    <div class="form-group">
                        <label for="parent_education">Parent Education</label>
                        <select name="parent_education" id="parent_education">
                            <option value="0" {% if inputs and inputs['parent_education'] == 0 %}selected{% endif %}>High School</option>
                            <option value="1" {% if inputs and inputs['parent_education'] == 1 %}selected{% endif %}>Bachelor's</option>
                            <option value="2" {% if inputs and inputs['parent_education'] == 2 %}selected{% endif %}>Master's</option>
                            <option value="3" {% if inputs and inputs['parent_education'] == 3 %}selected{% endif %}>PhD</option>
                        </select>
                    </div>

                    <div class="form-group">
                        <label for="internet_access">Internet Access</label>
                        <select name="internet_access" id="internet_access">
                            <option value="1" {% if inputs and inputs['internet_access'] == 1 %}selected{% endif %}>Yes</option>
                            <option value="0" {% if inputs and inputs['internet_access'] == 0 %}selected{% endif %}>No</option>
                        </select>
                    </div>

                    <div class="form-group">
                        <label for="extracurricular">Extracurriculars</label>
                        <select name="extracurricular" id="extracurricular">
                            <option value="1" {% if inputs and inputs['extracurricular'] == 1 %}selected{% endif %}>Yes</option>
                            <option value="0" {% if inputs and inputs['extracurricular'] == 0 %}selected{% endif %}>No</option>
                        </select>
                    </div>

                    <div class="form-group">
                        <label for="previous_score">Previous Score</label>
                        <input type="number" step="0.1" name="previous_score" id="previous_score" min="0" max="100" value="{{ inputs['previous_score'] if inputs else 70 }}" required>
                    </div>

                    <div class="form-group full-width">
                        <label for="final_score">Final Exam Score</label>
                        <input type="number" step="0.1" name="final_score" id="final_score" min="0" max="100" value="{{ inputs['final_score'] if inputs else 75 }}" required>
                    </div>

                    <button type="submit" class="btn-submit">⚡ RUN MODEL PREDICTION</button>
                </div>
            </form>
        </div>

        <!-- Output Analytics Pane -->
        <div class="glass-panel">
            <div class="panel-title">📊 Analytics & Outcome</div>

            {% if error_msg %}
                <div class="error-alert">
                    ⚠️ <strong>Error:</strong> {{ error_msg }}
                </div>
            {% endif %}

            {% if prediction is not none %}
                {% set is_pass = prediction|string|lower in ['yes', '1', 'pass'] %}
                
                <div class="result-box {{ 'pass-style' if is_pass else 'fail-style' }}">
                    <div style="font-size: 0.8rem; color: var(--text-dim); font-weight: 700; text-transform: uppercase;">
                        Predicted Outcome Result
                    </div>
                    <div class="badge-text {{ 'pass-text' if is_pass else 'fail-text' }}">
                        {{ '🎉 ' if is_pass else '⚠️ ' }}{{ prediction }}
                    </div>
                </div>

                <table class="data-table">
                    <tr>
                        <td>Study Effort</td>
                        <td>{{ inputs['study_hours'] }} hrs / week</td>
                    </tr>
                    <tr>
                        <td>Attendance Rate</td>
                        <td>{{ inputs['attendance'] }}%</td>
                    </tr>
                    <tr>
                        <td>Academic Average</td>
                        <td>{{ ((inputs['previous_score'] + inputs['final_score']) / 2)|round(1) }} / 100</td>
                    </tr>
                    <tr>
                        <td>Model Architecture</td>
                        <td>Support Vector Classifier (RBF)</td>
                    </tr>
                </table>
            {% else %}
                <div class="placeholder-state">
                    <svg width="48" height="48" fill="none" stroke="currentColor" stroke-width="1.5" viewBox="0 0 24 24" style="color: var(--text-dim); margin-bottom: 12px;">
                        <path stroke-linecap="round" stroke-linejoin="round" d="M3.75 13.5l10.5-11.25L12 10.5h8.25L9.75 21.75 12 13.5H3.75z"/>
                    </svg>
                    <p>Set values on the left panel and click <strong>RUN MODEL PREDICTION</strong> to compute real-time student outcomes.</p>
                </div>
            {% endif %}
        </div>
    </div>
</div>

</body>
</html>
"""

@app.route("/", methods=["GET", "POST"])
def index():
    prediction = None
    inputs = None
    error_msg = None

    if request.method == "POST":
        try:
            # Extract form values cleanly with direct type coercion
            gender = int(request.form.get("gender", 1))
            age = float(request.form.get("age", 18))
            study_hours = float(request.form.get("study_hours", 15))
            attendance = float(request.form.get("attendance", 85))
            parent_education = int(request.form.get("parent_education", 1))
            internet_access = int(request.form.get("internet_access", 1))
            extracurricular = int(request.form.get("extracurricular", 1))
            previous_score = float(request.form.get("previous_score", 70))
            final_score = float(request.form.get("final_score", 75))

            inputs = {
                "gender": gender,
                "age": age,
                "study_hours": study_hours,
                "attendance": attendance,
                "parent_education": parent_education,
                "internet_access": internet_access,
                "extracurricular": extracurricular,
                "previous_score": previous_score,
                "final_score": final_score
            }

            if model is not None:
                # Feature array order matching SVC model:
                # [gender, age, study_hours_per_week, attendance_rate, parent_education, internet_access, extracurricular, previous_score, final_score]
                feature_matrix = np.array([[
                    gender, age, study_hours, attendance, parent_education,
                    internet_access, extracurricular, previous_score, final_score
                ]], dtype=object)

                pred_raw = model.predict(feature_matrix)[0]
                prediction = str(pred_raw)
            else:
                error_msg = "Model file ('model.pkl') is not loaded properly on the server."

        except Exception as e:
            error_msg = f"Failed to execute prediction: {str(e)}"

    return render_template_string(HTML_TEMPLATE, prediction=prediction, inputs=inputs, error_msg=error_msg)

@app.route("/predict", methods=["POST"])
def predict_api():
    if model is None:
        return jsonify({"error": "Model binary not found on server"}), 500
    try:
        data = request.get_json(force=True)
        features = np.array([[
            int(data["gender"]),
            float(data["age"]),
            float(data["study_hours_per_week"]),
            float(data["attendance_rate"]),
            int(data["parent_education"]),
            int(data["internet_access"]),
            int(data["extracurricular"]),
            float(data["previous_score"]),
            float(data["final_score"])
        ]], dtype=object)
        
        pred = model.predict(features)[0]
        return jsonify({"prediction": str(pred)})
    except Exception as e:
        return jsonify({"error": str(e)}), 400

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
