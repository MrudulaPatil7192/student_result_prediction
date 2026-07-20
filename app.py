from flask import Flask, request, render_template_string, jsonify
import pickle
import numpy as np
import os

app = Flask(__name__)

# Safe model loading mechanism
def load_model():
    base_path = os.path.dirname(__file__)
    file_path = os.path.join(base_path, "model.pkl")
    with open(file_path, "rb") as file:
        return pickle.load(file)

try:
    model = load_model()
except Exception as e:
    model = None
    print(f"Error loading model binary: {e}")

# Embedded HTML + CSS with Animations
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Student Performance Predictor</title>
    <style>
        :root {
            --bg-gradient: linear-gradient(135deg, #0f172a 0%, #1e1b4b 100%);
            --card-bg: rgba(255, 255, 255, 0.05);
            --border-color: rgba(255, 255, 255, 0.12);
            --accent-blue: #6366f1;
            --accent-green: #10b981;
            --accent-red: #ef4444;
            --text-main: #f8fafc;
            --text-muted: #94a3b8;
        }

        * {
            box-sizing: border-box;
            margin: 0;
            padding: 0;
            font-family: 'Segoe UI', system-ui, -apple-system, sans-serif;
        }

        body {
            background: var(--bg-gradient);
            color: var(--text-main);
            min-height: 100vh;
            padding: 30px 20px;
            display: flex;
            justify-content: center;
            align-items: center;
        }

        .container {
            width: 100%;
            max-width: 1100px;
            animation: fadeIn 0.8s ease-in-out;
        }

        .header {
            text-align: center;
            margin-bottom: 30px;
        }

        .header h1 {
            font-size: 2.2rem;
            font-weight: 700;
            background: linear-gradient(90deg, #818cf8, #c084fc);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            margin-bottom: 8px;
        }

        .header p {
            color: var(--text-muted);
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

        /* Glassmorphism Cards */
        .glass-card {
            background: var(--card-bg);
            backdrop-filter: blur(16px);
            -webkit-backdrop-filter: blur(16px);
            border: 1px solid var(--border-color);
            border-radius: 16px;
            padding: 24px;
            box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.37);
            transition: transform 0.3s ease, box-shadow 0.3s ease;
        }

        .glass-card:hover {
            transform: translateY(-2px);
            box-shadow: 0 12px 40px 0 rgba(99, 102, 241, 0.15);
        }

        .card-title {
            font-size: 1.1rem;
            font-weight: 600;
            margin-bottom: 20px;
            color: #e2e8f0;
            border-bottom: 1px solid var(--border-color);
            padding-bottom: 10px;
        }

        .form-grid {
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 16px;
        }

        .form-group {
            display: flex;
            flex-direction: column;
        }

        .form-group.full-width {
            grid-column: span 2;
        }

        label {
            font-size: 0.85rem;
            color: var(--text-muted);
            margin-bottom: 6px;
            font-weight: 500;
        }

        input, select {
            background: rgba(15, 23, 42, 0.6);
            border: 1px solid var(--border-color);
            border-radius: 8px;
            padding: 10px 14px;
            color: #ffffff;
            font-size: 0.9rem;
            outline: none;
            transition: border-color 0.2s, box-shadow 0.2s;
        }

        input:focus, select:focus {
            border-color: var(--accent-blue);
            box-shadow: 0 0 0 3px rgba(99, 102, 241, 0.25);
        }

        /* Animated Submit Button */
        .submit-btn {
            grid-column: span 2;
            margin-top: 10px;
            padding: 12px;
            background: linear-gradient(90deg, #4f46e5, #7c3aed);
            color: white;
            border: none;
            border-radius: 8px;
            font-size: 1rem;
            font-weight: 600;
            cursor: pointer;
            transition: all 0.3s ease;
            position: relative;
            overflow: hidden;
        }

        .submit-btn:hover {
            opacity: 0.95;
            transform: scale(1.01);
            box-shadow: 0 4px 20px rgba(124, 58, 237, 0.4);
        }

        .submit-btn:active {
            transform: scale(0.99);
        }

        /* Results KPI Animated Tile */
        .result-tile {
            text-align: center;
            padding: 30px 20px;
            border-radius: 12px;
            background: rgba(15, 23, 42, 0.4);
            border: 1px solid var(--border-color);
            animation: pulseGlow 2s infinite alternate;
        }

        .result-tile.pass {
            border-left: 6px solid var(--accent-green);
        }

        .result-tile.fail {
            border-left: 6px solid var(--accent-red);
        }

        .result-badge {
            font-size: 2.2rem;
            font-weight: 800;
            margin-top: 10px;
            letter-spacing: 1px;
            animation: popIn 0.5s cubic-bezier(0.175, 0.885, 0.32, 1.275);
        }

        .result-badge.pass-text {
            color: var(--accent-green);
        }

        .result-badge.fail-text {
            color: var(--accent-red);
        }

        .metrics-table {
            width: 100%;
            margin-top: 20px;
            border-collapse: collapse;
            font-size: 0.88rem;
        }

        .metrics-table td {
            padding: 10px 0;
            border-bottom: 1px solid var(--border-color);
            color: var(--text-muted);
        }

        .metrics-table td:last-child {
            text-align: right;
            color: var(--text-main);
            font-weight: 600;
        }

        .empty-state {
            text-align: center;
            padding: 50px 20px;
            color: var(--text-muted);
            font-size: 0.9rem;
        }

        /* Keyframe Animations */
        @keyframes fadeIn {
            from { opacity: 0; transform: translateY(10px); }
            to { opacity: 1; transform: translateY(0); }
        }

        @keyframes popIn {
            from { opacity: 0; transform: scale(0.8); }
            to { opacity: 1; transform: scale(1); }
        }

        @keyframes pulseGlow {
            from { box-shadow: 0 0 10px rgba(99, 102, 241, 0.1); }
            to { box-shadow: 0 0 20px rgba(99, 102, 241, 0.25); }
        }
    </style>
</head>
<body>

<div class="container">
    <div class="header">
        <h1>🎓 Student Performance Dashboard</h1>
        <p>Support Vector Machine (SVC) Predictive Analytics Engine</p>
    </div>

    <div class="grid-layout">
        <!-- Input Form Card -->
        <div class="glass-card">
            <div class="card-title">📝 Student Metrics Input</div>
            <form method="POST" action="/">
                <div class="form-grid">
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
                        <label for="study_hours">Weekly Study Hours</label>
                        <input type="number" step="0.1" name="study_hours" id="study_hours" min="0" max="80" value="{{ inputs['study_hours'] if inputs else 15 }}" required>
                    </div>

                    <div class="form-group">
                        <label for="attendance">Attendance Rate (%)</label>
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
                        <label for="final_score">Final Score</label>
                        <input type="number" step="0.1" name="final_score" id="final_score" min="0" max="100" value="{{ inputs['final_score'] if inputs else 75 }}" required>
                    </div>

                    <button type="submit" class="submit-btn">🚀 Predict Outcome</button>
                </div>
            </form>
        </div>

        <!-- Evaluation Results Card -->
        <div class="glass-card">
            <div class="card-title">📊 Real-Time Classification</div>

            {% if prediction is not none %}
                {% set is_pass = prediction|string|lower in ['yes', '1', 'pass'] %}
                <div class="result-tile {{ 'pass' if is_pass else 'fail' }}">
                    <div style="font-size: 0.85rem; color: var(--text-muted); font-weight: 600; text-transform: uppercase;">
                        Predicted Outcome
                    </div>
                    <div class="result-badge {{ 'pass-text' if is_pass else 'fail-text' }}">
                        {{ '🎉 ' if is_pass else '⚠️ ' }}{{ prediction }}
                    </div>
                </div>

                <table class="metrics-table">
                    <tr>
                        <td>Study Time</td>
                        <td>{{ inputs['study_hours'] }} hrs/wk</td>
                    </tr>
                    <tr>
                        <td>Attendance</td>
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
                <div class="empty-state">
                    <p>⚡ Adjust parameters and click <strong>Predict Outcome</strong> to evaluate student performance in real-time.</p>
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

    if request.method == "POST":
        try:
            gender = int(request.form.get("gender"))
            age = float(request.form.get("age"))
            study_hours = float(request.form.get("study_hours"))
            attendance = float(request.form.get("attendance"))
            parent_education = int(request.form.get("parent_education"))
            internet_access = int(request.form.get("internet_access"))
            extracurricular = int(request.form.get("extracurricular"))
            previous_score = float(request.form.get("previous_score"))
            final_score = float(request.form.get("final_score"))

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

            if model:
                # 9 feature order extracted from model.pkl
                feature_matrix = np.array([[
                    gender, age, study_hours, attendance, parent_education,
                    internet_access, extracurricular, previous_score, final_score
                ]])
                prediction = model.predict(feature_matrix)[0]

        except Exception as e:
            print(f"Error during model evaluation: {e}")

    return render_template_string(HTML_TEMPLATE, prediction=prediction, inputs=inputs)

@app.route("/predict", methods=["POST"])
def predict_api():
    if not model:
        return jsonify({"error": "Model missing or not loaded"}), 500
    try:
        data = request.json
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
        ]])
        prediction = model.predict(features)[0]
        return jsonify({"prediction": str(prediction)})
    except Exception as e:
        return jsonify({"error": str(e)}), 400

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
