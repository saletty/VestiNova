from dataclasses import dataclass
from functools import lru_cache
import os
from pathlib import Path

from dotenv import dotenv_values
from sqlalchemy.engine import make_url


BACKEND_ROOT = Path(__file__).resolve().parents[1]


@dataclass(frozen=True)
class Settings:
    database_url: str
    jwt_secret: str
    session_minutes: int = 120
    cors_origins: tuple[str, ...] = ("http://127.0.0.1:4201", "http://localhost:4201")

    @classmethod
    def from_env(cls) -> "Settings":
        # No buscar .env en carpetas ascendentes: el proyecto tiene configuración propia.
        values = {**dotenv_values(BACKEND_ROOT / ".env", interpolate=False), **os.environ}
        database_url = values.get("DATABASE_URL", "") or ""
        secret = values.get("JWT_SECRET", "") or ""
        validate_local_database_url(database_url)
        if len(secret) < 32 or secret.startswith("GENERAR_"):
            raise ValueError("Configura JWT_SECRET con scripts.configure_local; se necesitan al menos 32 caracteres.")
        try:
            duration = int(values.get("SESSION_MINUTES", "120") or "120")
        except ValueError:
            raise ValueError("SESSION_MINUTES debe ser un entero entre 5 y 1440.") from None
        if not 5 <= duration <= 1440:
            raise ValueError("SESSION_MINUTES debe estar entre 5 y 1440.")
        origins = tuple(origin.strip() for origin in (values.get("CORS_ORIGINS", "http://127.0.0.1:4201,http://localhost:4201") or "").split(",") if origin.strip())
        return cls(database_url, secret, duration, origins)


def validate_local_database_url(value: str) -> None:
    try:
        url = make_url(value)
    except Exception:
        raise ValueError("Configura DATABASE_URL mediante python -m scripts.configure_local.") from None
    if url.drivername != "postgresql+psycopg" or url.database != "vestinova_mvp" or url.host not in {"localhost", "127.0.0.1", "::1"} or url.query:
        raise ValueError("Este MVP solo permite PostgreSQL local, controlador postgresql+psycopg y base vestinova_mvp.")


@lru_cache
def get_settings() -> Settings:
    return Settings.from_env()
