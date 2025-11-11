# app/services/moderation.py
from __future__ import annotations
import re

# --- Léxicos básicos en ES (puedes ampliarlos fácilmente) ---
POSITIVE = {
    "bueno","genial","excelente","maravilloso","estupendo","fantástico",
    "increíble","positivo","feliz","me_encanta","me_gusta","agradable",
    "recomiendo","recomendado","útil","bien","gracias","perfecto","satisfecho",
    "contento","amable","rápido","fácil","bonito","hermoso","mejor","funciona",
    "solucionado","mejoró","mejorado","eficiente","claridad","aporta","aprendí",
}

NEGATIVE = {
    "malo","terrible","horrible","pésimo","fatal","desastroso","decepcionante",
    "odio","asco","asqueroso","lento","difícil","complicado","tarde","mal","nada_bien",
    "nunca","jamás","peor","engorroso","molesto","triste","frustrante","defectuoso",
    "no_funciona","inútil","estafa","engaño","basura","fallo","error","errores",
    "pérdida","pobre","malísimo","pésima","vergüenza","pésimas","inaceptable",
}

NEGATORS = {"no","nunca","jamás"}
BOOSTERS = {"muy","super","re","extra","bastante"}

TOKEN_RE = re.compile(r"[a-záéíóúüñ]+", re.IGNORECASE)

def _normalize(text: str) -> list[str]:
    t = text.lower().strip()
    t = t.replace("me encanta", "me_encanta")
    t = t.replace("me gusta", "me_gusta")
    t = t.replace("no funciona", "no_funciona")
    t = t.replace("nada bien", "nada_bien")
    return TOKEN_RE.findall(t)

def _score_sentiment(tokens: list[str]) -> tuple[float, list[str]]:
    score = 0.0
    negate = False
    boost = 1.0
    reasons: list[str] = []

    for w in tokens:
        if w in NEGATORS:
            negate = True
            continue
        if w in BOOSTERS:
            boost = 1.5
            continue

        val = 0.0
        if w in POSITIVE:
            val = 1.0
        elif w in NEGATIVE:
            val = -1.0

        if val:
            if negate:
                val = -val
                reasons.append(f"negación→{w}")
                negate = False
            else:
                reasons.append(w)

            val *= boost
            boost = 1.0
            score += val

    # Normalización suave por longitud
    norm = max(1.0, len(tokens) / 12.0)
    s = max(-1.0, min(1.0, score / norm))

    if s >= 0.15:
        label = "positive"
    elif s <= -0.15:
        label = "negative"
    else:
        label = "neutral"

    return round(s, 3), reasons

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
    """Devuelve:
       {
         "label": "positive|neutral|negative",
         "score": float(-1..1),
         "reasons": [...],
         "suggestion": str|None,
         "length": int
       }
    """
    text = (text or "").strip()
    if not text:
        return {"label": "neutral", "score": 0.0, "reasons": [], "suggestion": None, "length": 0}

    toks = _normalize(text)
    score, reasons = _score_sentiment(toks)

    label = "positive" if score >= 0.15 else ("negative" if score <= -0.15 else "neutral")
    suggestion = _polite_rewrite(text) if label == "negative" else None

    return {
        "label": label,
        "score": score,
        "reasons": reasons[:12],
        "suggestion": suggestion,
        "length": len(toks),
    }
