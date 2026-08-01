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
`DATABASE_URL` puede apuntar tanto a Supabase (producción) como a una instancia de PostgreSQL local — cualquiera de las dos funciona igual.

Opcionales (solo si querés probar el formulario de contacto; sin ellas la app corre normal y el envío de correo se omite con un warning en el log):
```
SENDGRID_API_KEY=SG.xxxxxxxxxxxx
SENDGRID_FROM_EMAIL=noreply@tudominio.com
CONTACT_EMAIL=tu@correo.com
```

## Correr localmente
```bash
python -m venv venv
venv\Scripts\activate       # Windows
# source venv/bin/activate  # macOS/Linux

cp .env.example .env        # y completá los valores reales

pip install -r requirements.txt
flask db upgrade
flask run
```
La app queda disponible en `http://127.0.0.1:5000`. Podés verificar que todo esté funcionando con `/healthz` (estado del server) y `/dbcheck` (conexión a la base de datos).

## Despliegue
- **App:** Render (gunicorn)
- **BD:** Supabase PostgreSQL
- **URL:** https://ml-master-web-studio-vx5t.onrender.com
