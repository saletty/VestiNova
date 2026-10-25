"""Escribe únicamente backend/.env, con contraseña de PostgreSQL ingresada oculta."""
from getpass import getpass
import json
from pathlib import Path
import secrets

from sqlalchemy.engine import URL

from app.config import BACKEND_ROOT


def main() -> None:
    target = BACKEND_ROOT / ".env"
    if target.exists() and input("Ya existe .env. ¿Reemplazar su configuración y secreto de sesión? [s/N]: ").strip().lower() != "s":
        print("Configuración existente conservada.")
        return
    print("VestiNova MVP: PostgreSQL local, base fija vestinova_mvp.")
    host = input("Servidor [127.0.0.1]: ").strip() or "127.0.0.1"
    if host not in {"127.0.0.1", "localhost", "::1"}:
        raise ValueError("Solo se permiten servidores locales.")
    port = int(input("Puerto [5432]: ").strip() or "5432")
    if not 1 <= port <= 65535:
        raise ValueError("Puerto inválido.")
    username = input("Usuario PostgreSQL [postgres]: ").strip() or "postgres"
    password = getpass("Contraseña PostgreSQL (oculta): ")
    url = URL.create("postgresql+psycopg", username=username, password=password, host=host, port=port, database="vestinova_mvp")
    values = {
        "DATABASE_URL": url.render_as_string(hide_password=False),
        "JWT_SECRET": secrets.token_urlsafe(48),
        "SESSION_MINUTES": "120",
        "CORS_ORIGINS": "http://127.0.0.1:4201,http://localhost:4201",
    }
    content = "# VestiNova MVP: credenciales locales, no versionar.\n" + "\n".join(f"{key}={json.dumps(value, ensure_ascii=False)}" for key, value in values.items()) + "\n"
    target.write_text(content, encoding="utf-8")
    print(f"Configuración guardada en {target}. No se modificó ninguna base de datos.")
    print("Siguiente paso: python -m scripts.init_db")


if __name__ == "__main__":
    try:
        main()
    except (ValueError, OSError, EOFError, KeyboardInterrupt):
        print("No se completó la configuración. Revisa los datos introducidos y vuelve a intentar.")
        raise SystemExit(1) from None
