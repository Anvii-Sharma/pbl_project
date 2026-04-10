# model.py
# Trained on 267,782 real posts from 3 mental health datasets:
#   - mental_health.csv          (27,977 posts)
#   - depression_dataset_reddit  (7,731 posts)
#   - Suicide_Detection.csv      (232,074 posts)
#
# Algorithm: TF-IDF (unigrams + bigrams) + Logistic Regression
# Accuracy on held-out test set: 93.9%

import pickle
import re
import os

# ── Load the trained model once when this file is imported ────────
_MODEL_PATH = os.path.join(os.path.dirname(__file__), "trained_model.pkl")

with open(_MODEL_PATH, "rb") as f:
    _saved = pickle.load(f)

_model = _saved["model"]
_tfidf = _saved["tfidf"]


def _clean(text: str) -> str:
    """Same cleaning used during training."""
    text = str(text).lower()
    text = re.sub(r"http\S+", "", text)
    text = re.sub(r"[^a-z\s]", " ", text)
    text = re.sub(r"\s+", " ", text).strip()
    return text


def predict(text: str) -> int:
    """
    Returns 1 (concerning) or 0 (not concerning).
    Mirrors the 0/1 output of the original notebook model.
    """
    cleaned = _clean(text)
    vec = _tfidf.transform([cleaned])
    return int(_model.predict(vec)[0])


def predict_proba(text: str) -> float:
    """
    Returns probability (0.0 – 1.0) that the text is concerning.
    Useful for nuanced scoring.
    """
    cleaned = _clean(text)
    vec = _tfidf.transform([cleaned])
    return float(_model.predict_proba(vec)[0][1])


def get_concern_level(text: str) -> str:
    """
    Returns 'High concern', 'Medium concern', or 'Low concern'
    based on the model's confidence probability.
    """
    prob = predict_proba(text)
    if prob >= 0.70:
        return "High concern"
    elif prob >= 0.45:
        return "Medium concern"
    else:
        return "Low concern"


# ── Quick test ────────────────────────────────────────────────────
if __name__ == "__main__":
    tests = [
        "I feel like killing myself and there is no point living anymore",
        "I have been really exhausted and depressed, struggling to cope",
        "I feel a bit sad today but overall okay",
        "Had a great day with friends, everything is fine!",
        "I cant stop crying and i dont know why i even bother",
    ]
    for t in tests:
        prob = predict_proba(t)
        level = get_concern_level(t)
        print(f"[{level}] ({prob:.0%}) — {t[:65]}")
