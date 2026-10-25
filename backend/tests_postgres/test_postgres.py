"""Solo para scripts.test_postgres y su instancia temporal, jamás para la base operativa."""
import os
from pathlib import Path
from uuid import uuid4

from alembic import command
from alembic.config import Config
from alembic.migration import MigrationContext
from fastapi.testclient import TestClient
import pytest
from sqlalchemy import create_engine, inspect, select
from sqlalchemy.engine import make_url

from app.config import BACKEND_ROOT, Settings, validate_local_database_url
from app.db import build_session_factory
from app.main import create_app
from app.models import Administrador, Producto, SesionAdministrador
from app.security import hash_password


@pytest.fixture(scope="module")
def engine():
    if os.environ.get("MVP_ISOLATED_POSTGRES") != "1":
        pytest.skip("Ejecutar mediante python -m scripts.test_postgres, con PostgreSQL aislado.")
    database_url = os.environ.get("DATABASE_URL", "")
    validate_local_database_url(database_url)
    if make_url(database_url).port in {None, 5432}:
        pytest.fail("La prueba exige un puerto temporal diferente de 5432.")
    database_engine = create_engine(database_url)
    config = Config(str(BACKEND_ROOT / "alembic.ini"))
    config.set_main_option("script_location", str(BACKEND_ROOT / "migrations"))
    with database_engine.begin() as connection:
        config.attributes["connection"] = connection
        command.upgrade(config, "head")
    yield database_engine
    database_engine.dispose()


@pytest.fixture
def factory(engine):
    return build_session_factory(engine)


@pytest.fixture
def client(engine):
    settings = Settings(database_url=os.environ["DATABASE_URL"], jwt_secret=os.environ.get("JWT_SECRET", "solo-test-postgres-aislado-nunca-servidor-real-1234"))
    # Cada cliente usa el mismo motor, las consultas abren sesiones independientes.
    with TestClient(create_app(settings, engine=engine)) as test_client:
        yield test_client


def administrator_credentials(client, factory):
    email = f"admin-{uuid4().hex}@vestinova.test"
    password = "Clave aislada PostgreSQL!2026"
    with factory() as session:
        administrator = Administrador(nombre="Prueba aislada", correo=email, password_hash=hash_password(password), activo=True)
        session.add(administrator)
        session.commit()
    response = client.post("/api/auth/login", json={"correo": email, "password": password})
    assert response.status_code == 200
    return {"Authorization": f"Bearer {response.json()['access_token']}"}


def test_alembic_initialization_is_complete_and_repeatable(engine):
    assert set(inspect(engine).get_table_names()) == {"alembic_version", "administradores", "sesiones_administrador", "productos"}
    config = Config(str(BACKEND_ROOT / "alembic.ini"))
    config.set_main_option("script_location", str(BACKEND_ROOT / "migrations"))
    with engine.begin() as connection:
        config.attributes["connection"] = connection
        command.upgrade(config, "head")
        assert MigrationContext.configure(connection).get_current_revision() == "0001_base"


def test_logout_revokes_persisted_session(client, factory):
    headers = administrator_credentials(client, factory)
    assert client.get("/api/auth/me", headers=headers).status_code == 200
    assert client.post("/api/auth/logout", headers=headers).status_code == 204
    assert client.get("/api/admin/productos", headers=headers).status_code == 401
    with factory() as independent:
        assert independent.scalar(select(SesionAdministrador.id).where(SesionAdministrador.revocada.is_(True))) is not None


def test_products_persist_between_requests_and_sessions(client, factory):
    headers = administrator_credentials(client, factory)
    slug = f"prueba-{uuid4().hex}"
    created = client.post("/api/admin/productos", headers=headers, json={"nombre": "Prueba de persistencia", "slug": slug, "precio": "45.90"})
    assert created.status_code == 201
    product_id = created.json()["id"]
    with factory() as independent:
        stored = independent.get(Producto, product_id)
        assert str(stored.precio) == "45.90"
        assert stored.moneda == "BOB"
    changed = client.patch(f"/api/admin/productos/{product_id}", headers=headers, json={"precio": "55.50", "activo": False})
    assert changed.status_code == 200
    with factory() as another:
        assert str(another.get(Producto, product_id).precio) == "55.50"
    assert client.get(f"/api/catalogo/productos/{slug}").status_code == 404
    assert client.get(f"/api/admin/productos/{product_id}", headers=headers).json()["activo"] is False
