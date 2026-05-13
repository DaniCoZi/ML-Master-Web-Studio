# app/services/moderation.py
from __future__ import annotations
import os
import re
import logging
import joblib

logger = logging.getLogger(__name__)

MODEL_PATH = os.path.join(os.path.dirname(__file__), "..", "models", "moderator_model.pkl")

_model = None

NEGATIVE_KEYWORDS = [
    "odio", "asco", "asqueroso", "asquerosa", "imbecil", "idiota", "estupido",
    "estupida", "inutil", "basura", "estafa", "engano", "mentira", "mentiroso",
    "horrible", "horroroso", "pesimo", "pesima", "terrible", "desastroso",
    "desastre", "maldito", "maldita", "repugnante", "fraude", "robo", "ladron",
    "ridiculo", "ridicula", "porqueria", "mugre", "patetico", "patetica",
    "mediocre", "vergonzoso", "vergonzosa", "incompetente", "nefasto", "nefasta",
    "detesto", "detestable", "fatal", "deplorable", "lamentable", "calamidad",
    "odio", "horrible", "pesimos", "terribles", "horribles", "inutiles",
]

NEGATIVE_PATTERN = re.compile(
    r"\b(" + "|".join(re.escape(w) for w in NEGATIVE_KEYWORDS) + r")\b",
    re.IGNORECASE,
)

NEGATIVE_ACCENTED = [
    "imbécil", "inútil", "pésimo", "pésima", "pésimos", "pésimas",
    "estúpido", "estúpida", "ridículo", "ridícula", "patético", "patética",
    "nefasto", "nefasta", "maldito", "maldita", "ladrón", "porquería",
    "odié", "detesté",
]

SWAPS = [
    (r"odio|detesto",           "no me agrada"),
    (r"asco|repugnante",        "me parece mejorable"),
    (r"horrible|horroroso",     "tiene aspectos a mejorar"),
    (r"terrible|desastroso",    "podria mejorar bastante"),
    (r"pesimo|nefasto",         "no cumple mis expectativas"),
    (r"basura|porqueria",       "no es de buena calidad"),
    (r"estafa|fraude|engano",   "no cumple lo prometido"),
    (r"inutil|incompetente",    "tiene mucho por mejorar"),
    (r"imbecil|idiota|estupido","comete errores"),
    (r"maldito|patetico",       "es frustrante"),
    (r"ridiculo|vergonzoso",    "deja mucho que desear"),
    (r"fatal|lamentable",       "es decepcionante"),
]


def _polite_rewrite(text: str) -> str:
    import unicodedata
    def strip_accents(s):
        return ''.join(c for c in unicodedata.normalize('NFD', s) if unicodedata.category(c) != 'Mn')
    
    t = strip_accents(text.strip())
    for pat, rep in SWAPS:
        t = re.sub(pat, rep, t, flags=re.IGNORECASE)
    if not re.search(r"(gracias|por favor|podrian|seria genial)", t, re.IGNORECASE):
        t += " Podrian revisarlo? Gracias!"
    t = t[0].upper() + t[1:] if t else t
    if t and t[-1] not in ".!?":
        t += "."
    return t


def _is_negative_accented(text: str) -> bool:
    text_lower = text.lower()
    return any(w in text_lower for w in NEGATIVE_ACCENTED)


def _load_model():
    global _model
    if _model is None:
        try:
            _model = joblib.load(os.path.abspath(MODEL_PATH))
            logger.info("Modelo ML cargado correctamente.")
        except Exception as e:
            logger.warning("No se pudo cargar el modelo ML: %s", e)
            _model = None
    return _model


def analyze_text(text: str) -> dict:
    text = (text or "").strip()
    if not text:
        return {"label": "neutral", "score": 0.0, "reasons": [], "suggestion": None, "length": 0}

    # 1. Palabras clave sin acento
    keyword_matches = NEGATIVE_PATTERN.findall(text)
    # 2. Palabras clave con acento
    accented_hit = _is_negative_accented(text)

    if keyword_matches or accented_hit:
        unique = list(set(m.lower() for m in keyword_matches))
        score = round(min(0.55 + len(unique) * 0.12, 0.99), 3)
        return {
            "label": "negative",
            "score": score,
            "reasons": [f"keyword:{w}" for w in unique] if unique else ["keyword:accented"],
            "suggestion": _polite_rewrite(text),
            "length": len(text.split()),
        }

    # 3. Modelo ML
    model = _load_model()
    if model is not None:
        try:
            proba = model.predict_proba([text])[0]
            classes = list(model.classes_)
            proba_dict = {cls: float(p) for cls, p in zip(classes, proba)}
            neg_p = proba_dict.get("negative", 0.0)
            neu_p = proba_dict.get("neutral", 0.0)
            pos_p = proba_dict.get("positive", 0.0)

            if neg_p >= 0.50:
                return {
                    "label": "negative",
                    "score": round(neg_p, 3),
                    "reasons": [f"ml:negative:{round(neg_p,3)}"],
                    "suggestion": _polite_rewrite(text),
                    "length": len(text.split()),
                }
            elif pos_p >= neu_p:
                return {"label": "positive", "score": round(pos_p, 3), "reasons": [], "suggestion": None, "length": len(text.split())}
            else:
                return {"label": "neutral", "score": round(neu_p, 3), "reasons": [], "suggestion": None, "length": len(text.split())}
        except Exception as e:
            logger.warning("Error ML: %s", e)

    return {"label": "neutral", "score": 0.5, "reasons": ["fallback"], "suggestion": None, "length": len(text.split())}