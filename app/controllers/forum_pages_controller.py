# app/controllers/forum_pages_controller.py
from flask import Blueprint, render_template
from flask_login import login_required

forum_pages_bp = Blueprint("forum_pages", __name__)

@forum_pages_bp.get("/foro")
@login_required
def index():
    return render_template("forum/forums.html")

@forum_pages_bp.get("/foro/publicaciones")
@login_required
def posts_page():
    return render_template("forum/posts.html")

@forum_pages_bp.get("/foro/nuevo")
@login_required
def new_post_page():
    # abre el editor (detail.html) para crear una publicación
    return render_template("forum/detail.html")
