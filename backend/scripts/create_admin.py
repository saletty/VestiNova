"""Alta explícita de administrador; nunca guarda ni imprime contraseña en claro."""
from getpass import getpass

from sqlalchemy import select

from app.config import Settings
from app.db import build_engine, build_session_factory
from app.models import Administrador
from app.password_policy import PASSWORD_POLICY_MESSAGE, validate_new_password
from app.schemas import normalizar_correo
from app.security import hash_password, verify_password


def main() -> None:
    settings = Settings.from_env()
    nombre = input("Nombre del administrador: ").strip()
    if not 3 <= len(nombre) <= 120:
        raise ValueError("El nombre debe tener entre 3 y 120 caracteres.")
    correo = normalizar_correo(input("Correo del administrador: "))
    print(PASSWORD_POLICY_MESSAGE)
    password = getpass("Contraseña nueva (oculta): ")
    confirmacion = getpass("Repite la contraseña (oculta): ")
    if password != confirmacion:
        raise ValueError("Las contraseñas no coinciden.")
    validate_new_password(password)
    engine = build_engine(settings)
    try:
        with build_session_factory(engine)() as db:
            if db.scalar(select(Administrador.id).where(Administrador.correo == correo)) is not None:
                raise ValueError("Ese correo ya existe. No se modificó su cuenta ni contraseña.")
            encoded = hash_password(password)
            if not verify_password(password, encoded):
                raise ValueError("No se pudo comprobar el hash de la contraseña.")
            administrator = Administrador(nombre=nombre, correo=correo, password_hash=encoded, activo=True)
            db.add(administrator)
            db.commit()
            print("Administrador creado con hash Argon2 y contraseña verificada.")
            print("Acceso: http://127.0.0.1:4201/admin/login")
    finally:
        engine.dispose()


if __name__ == "__main__":
    try:
        main()
    except ValueError as error:
        print(str(error))
        raise SystemExit(1) from None
    except (Exception, KeyboardInterrupt):
        print("No se completó el alta. Comprueba que .env y las migraciones estén configurados; no se mostraron credenciales.")
        raise SystemExit(1) from None
