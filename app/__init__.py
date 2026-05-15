# app/__init__.py
import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_login import LoginManager
from flask_migrate import Migrate

from config import Config

db = SQLAlchemy()
bcrypt = Bcrypt()
login_manager = LoginManager()
migrate = Migrate()

login_manager.login_view = "auth.login_page"

def create_app():
    app = Flask(
        __name__,
        static_folder="static",
        template_folder="templates",  # ahora dentro de app/
    )

    app.config.from_object(Config)

    db.init_app(app)
    bcrypt.init_app(app)
    login_manager.init_app(app)
    migrate.init_app(app, db)

    @app.get("/healthz")
    def healthz():
        return "ok", 200

    @app.get("/dbcheck")
    def dbcheck():
        try:
            with db.engine.connect() as conn:
                conn.exec_driver_sql("SELECT 1")
            return "db ok", 200
        except Exception as e:
            return f"db error: {e}", 500

    from app.models import user, post  # noqa: F401

    from app.controllers.auth_controller import auth_bp
    app.register_blueprint(auth_bp, url_prefix="/auth")

    from app.controllers.main_controller import main_controller
    app.register_blueprint(main_controller)

    from app.controllers.forum_controller import forum_bp
    app.register_blueprint(forum_bp)

    from app.controllers.forum_pages_controller import forum_pages_bp
    app.register_blueprint(forum_pages_bp)

    @login_manager.user_loader
    def load_user(user_id: str):
        from app.models.user import User
        return User.query.get(int(user_id))

    with app.app_context():
        print("=== URL MAP ===")
        for rule in app.url_map.iter_rules():
            print(rule.endpoint, "->", rule)

    return app
