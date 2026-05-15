# ML Master Web Studio — Revelu

Plataforma web educativa con foro comunitario y moderación de contenido mediante Machine Learning.

## Stack
- **Backend:** Python 3.14 / Flask
- **Base de datos:** PostgreSQL (Supabase)
- **ML:** scikit-learn (TF-IDF + Logistic Regression)
- **Auth:** Flask-Login + Bcrypt
- **Despliegue:** Render + Supabase

## Estructura del proyecto
```
app/
├── controllers/     # Rutas y lógica de vistas
├── models/          # Modelos de base de datos (SQLAlchemy)
├── services/        # Lógica de negocio (moderación ML)
├── ml/              # Modelo entrenado (.pkl)
├── static/          # CSS, JS, imágenes
└── templates/       # HTML (Jinja2)
migrations/          # Migraciones de BD (Alembic)
config.py            # Configuración de la app
app.py               # Punto de entrada
```

## Variables de entorno requeridas
```
SECRET_KEY=tu-clave-secreta
DATABASE_URL=postgresql://...
```

## Correr localmente
```bash
pip install -r requirements.txt
flask db upgrade
flask run
```

## Despliegue
- **App:** Render (gunicorn)
- **BD:** Supabase PostgreSQL
- **URL:** https://ml-master-web-studio-vx5t.onrender.com
