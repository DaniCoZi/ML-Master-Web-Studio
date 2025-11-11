# app/controllers/forum_pages_controller.py

from flask import Blueprint, render_template
from flask_login import login_required

# Nuevo blueprint para las vistas HTML del foro
forum_pages_bp = Blueprint("forum_pages", __name__, url_prefix="/foro")

@forum_pages_bp.get("/")
@login_required
def index():
    """Página principal del foro (lista de publicaciones)."""
    return render_template("forum/index.html")

@forum_pages_bp.get("/publicar")
@login_required
def publicar():
    """Página para crear una nueva publicación."""
    return render_template("forum/detail.html")
