# app/services/moderation.py
from __future__ import annotations
import os
import logging
import joblib
import re

logger = logging.getLogger(__name__)

# Ruta al modelo entrenado (train_moderator.py lo guardó aquí)
MODEL_PATH = os.path.join(
    os.path.dirname(__file__),  # .../app/services
    "..",                       # .../app
    "models",
    "moderator_model.pkl"
)

_model = None


def _load_model():
    """Carga el modelo de ML en memoria (solo la primera vez)."""
    global _model
    if _model is None:
        try:
            path = os.path.abspath(MODEL_PATH)
            logger.info(f"Cargando modelo de moderación desde: {path}")
            _model = joblib.load(path)
            logger.info("✅ Modelo de moderación ML cargado correctamente.")
        except Exception as e:
            logger.exception("❌ No se pudo cargar el modelo de moderación ML: %s", e)
            _model = None
    return _model


def _polite_rewrite(text: str) -> str:
    """Sugerencia de reescritura más positiva/constructiva."""
    t = text.strip()
    swaps = [
        (r"\b(odio|asco|asqueros[oa])\b", "no me agrada"),
        (r"\b(horrible|terrible|pésim[oa]|fatal|desastroso)\b", "podría mejorar"),
        (r"\b(lento|difícil|complicado)\b", "podría ser más ágil"),
        (r"\b(basura|estafa|engaño)\b", "no cumple mis expectativas"),
        (r"\b(no funciona|fall[ao]s?|errores?)\b", "presenta fallas"),
        (r"\b(mal|peor)\b", "me gustaría que fuera mejor"),
    ]
    for pat, rep in swaps:
        t = re.sub(pat, rep, t, flags=re.IGNORECASE)

    if not re.search(r"(gracias|por favor|¿podrían|sería genial|recomendaría)", t, re.IGNORECASE):
        t += " ¿Podrían revisarlo? ¡Gracias!"

    t = t[0].upper() + t[1:] if t else t
    if t and t[-1] not in ".!?¡¿":
        t += "."
    return t


def analyze_text(text: str) -> dict:
    """
    Usa el modelo de ML (TF-IDF + LogisticRegression) para clasificar el texto
    como positive / neutral / negative.

    Devuelve:
       {
         "label": "positive|neutral|negative",
         "score": float(0..1)  # confianza aprox.
         "reasons": [...],
         "suggestion": str|None,
         "length": int
       }
    """
    text = (text or "").strip()
    if not text:
        return {
            "label": "neutral",
            "score": 0.0,
            "reasons": [],
            "suggestion": None,
            "length": 0,
        }

    model = _load_model()
    if model is None:
        # Fallback si no se pudo cargar el modelo
        return {
            "label": "neutral",
            "score": 0.0,
            "reasons": ["fallback_model_not_loaded"],
            "suggestion": None,
            "length": len(text.split()),
        }

    # Predicción de clase y probabilidades
    pred = model.predict([text])[0]
    proba = model.predict_proba([text])[0]
    classes = list(model.classes_)

    try:
        idx = classes.index(pred)
        score = float(proba[idx])  # probabilidad de la clase predicha
    except ValueError:
        score = 0.0

    # Normalizamos label a solo 3 valores posibles
    label = str(pred).lower()
    if label not in ("positive", "neutral", "negative"):
        label = "neutral"

    # Sugerencia solo si es negativo
    suggestion = _polite_rewrite(text) if label == "negative" else None

    return {
        "label": label,
        "score": round(score, 3),
        "reasons": [f"ml_label:{label}", f"ml_confidence:{round(score, 3)}"],
        "suggestion": suggestion,
        "length": len(text.split()),
    }
