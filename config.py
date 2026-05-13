import os
from urllib.parse import urlsplit, urlunsplit
from dotenv import load_dotenv

load_dotenv()

def _force_psycopg(url: str | None) -> str | None:
    if not url:
        return url
    parts = urlsplit(url)
    if parts.scheme in ("postgres", "postgresql", "postgresql+psycopg2"):
        scheme = "postgresql+psycopg"
        url = urlunsplit((scheme, parts.netloc, parts.path, parts.query, parts.fragment))
    return url

class Config:
    SECRET_KEY = os.environ.get("SECRET_KEY", "cambia-esta-clave-en-produccion")
    SQLALCHEMY_DATABASE_URI = _force_psycopg(os.environ.get("DATABASE_URL"))
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ENGINE_OPTIONS = {"pool_pre_ping": True}
