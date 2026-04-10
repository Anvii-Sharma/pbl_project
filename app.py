# app.py
from flask import Flask, render_template, request, jsonify
import json
import os
from model import get_concern_level

app = Flask(__name__)
SCORES_FILE = "scores.json"

# ── PHQ-9 questions ──────────────────────────────────────────────
PHQ9_QUESTIONS = [
    "Little interest or pleasure in doing things",
    "Feeling down, depressed, or hopeless",
    "Trouble falling or staying asleep, or sleeping too much",
    "Feeling tired or having little energy",
    "Poor appetite or overeating",
    "Feeling bad about yourself — or that you are a failure",
    "Trouble concentrating on things",
    "Moving or speaking slowly (or being fidgety/restless)",
    "Thoughts that you would be better off dead or hurting yourself"
]

def get_phq9_level(score):
    if score <= 4:   return ("Minimal", "green")
    elif score <= 9: return ("Mild", "yellow")
    elif score <= 14: return ("Moderate", "orange")
    elif score <= 19: return ("Moderately severe", "red")
    else:            return ("Severe", "darkred")

# ── Score history helpers ─────────────────────────────────────────
def load_scores():
    if not os.path.exists(SCORES_FILE):
        return []
    with open(SCORES_FILE, "r") as f:
        return json.load(f)

def save_score(score, level):
    scores = load_scores()
    scores.append({"score": score, "level": level})
    if len(scores) > 5:   # keep last 5 only
        scores = scores[-5:]
    with open(SCORES_FILE, "w") as f:
        json.dump(scores, f)

# ── Routes ────────────────────────────────────────────────────────
@app.route("/")
def index():
    return render_template("index.html", questions=PHQ9_QUESTIONS)

@app.route("/submit_phq9", methods=["POST"])
def submit_phq9():
    data = request.get_json()
    answers = data.get("answers", [])
    score = sum(int(a) for a in answers)
    level, color = get_phq9_level(score)
    save_score(score, level)
    history = load_scores()
    trend = None
    if len(history) >= 2:
        diff = history[-1]["score"] - history[-2]["score"]
        if diff < 0:   trend = f"Improved by {abs(diff)} points"
        elif diff > 0: trend = f"Increased by {diff} points"
        else:          trend = "No change from last time"
    return jsonify({"score": score, "level": level, "color": color, "trend": trend})

@app.route("/analyze", methods=["POST"])
def analyze():
    data = request.get_json()
    text = data.get("text", "")
    concern = get_concern_level(text)
    return jsonify({"concern": concern})

@app.route("/chat", methods=["POST"])
def chat():
    data = request.get_json()
    message = data.get("message", "").lower()

    SAD_WORDS = ["sad", "tired", "hopeless", "worthless", "useless",
                 "depressed", "empty", "alone", "hurt", "crying",
                 "hate myself", "give up", "no point", "burden"]
    ANXIOUS_WORDS = ["anxious", "worried", "nervous", "panic", "scared",
                     "overwhelmed", "stress", "stressed", "fear"]
    ANGRY_WORDS = ["angry", "mad", "frustrated", "furious", "rage"]

    if any(w in message for w in SAD_WORDS):
        reply = "That sounds really heavy. I hear you. Would you like to talk more about what's been going on?"
    elif any(w in message for w in ANXIOUS_WORDS):
        reply = "It sounds like things feel overwhelming right now. Take a breath — you don't have to figure it all out at once."
    elif any(w in message for w in ANGRY_WORDS):
        reply = "It makes sense to feel frustrated sometimes. What do you think is behind those feelings?"
    elif any(w in ["better", "good", "happy", "great", "okay"] for w in message.split()):
        reply = "I'm really glad to hear that. What's been helping you feel this way?"
    else:
        reply = "Thank you for sharing that with me. I'm here to listen — can you tell me more?"

    return jsonify({"reply": reply})

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
