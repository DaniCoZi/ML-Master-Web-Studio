# train_moderator.py
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import Pipeline
from sklearn.metrics import classification_report, accuracy_score
import joblib
import os


# ===============================
# CONFIGURACIÓN
# ===============================

DATA_PATH = "data/moderation_dataset.csv"   # dataset que creamos
MODEL_PATH = "app/models/moderator_model.pkl"  # modelo final


# ===============================
# ENTRENAMIENTO
# ===============================

def main():
    print("📥 Cargando dataset...")
    df = pd.read_csv(DATA_PATH, encoding="latin-1")  # 👈 CAMBIO


    print("🔎 Primeras filas del dataset:")
    print(df.head())

    print("\n📌 Columnas del dataset:", list(df.columns))

    print("\n📊 Conteo de etiquetas (value_counts):")
    print(df["label"].value_counts(dropna=False))



    # Validamos columnas esperadas
    if not {"text", "label"}.issubset(df.columns):
        raise ValueError("❌ El CSV debe tener columnas: text, label")

    X = df["text"].astype(str)
    y = df["label"].astype(str)

    print("📊 Dividiendo dataset (80% train / 20% test)...")
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.20, random_state=42, stratify=y
    )

    print("⚙️ Creando pipeline TF-IDF + Logistic Regression...")
    pipeline = Pipeline([
        ("tfidf", TfidfVectorizer(
            max_features=20000,
            ngram_range=(1, 2),
            sublinear_tf=True,
        )),
        ("clf", LogisticRegression(
            max_iter=2000,
            class_weight="balanced"
        ))
    ])

    print("🚀 Entrenando modelo...")
    pipeline.fit(X_train, y_train)

    print("\n📏 Evaluando modelo...")
    y_pred = pipeline.predict(X_test)
    acc = accuracy_score(y_test, y_pred)
    print(f"\n🔍 Accuracy: {acc:.3f}\n")
    print("📄 Classification Report:")
    print(classification_report(y_test, y_pred))

    print("\n💾 Guardando modelo entrenado...")
    os.makedirs(os.path.dirname(MODEL_PATH), exist_ok=True)
    joblib.dump(pipeline, MODEL_PATH)

    print(f"✅ Modelo guardado en: {MODEL_PATH}")
    print("🎉 Entrenamiento completado con éxito.")



# Punto de entrada
if __name__ == "__main__":
    main()
