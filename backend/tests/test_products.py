from decimal import Decimal

import pytest
from sqlalchemy import select

from app.models import Producto


def product(**values):
    return {"nombre": "Camisa de lino", "descripcion": "Prenda de prueba", "precio": "149.90", **values}


def create(client, auth, **values):
    response = client.post("/api/admin/productos", headers=auth, json=product(**values))
    assert response.status_code == 201, response.text
    return response.json()


def test_create_product_persists_decimal_and_generates_slug(client, auth, session_factory):
    response = client.post("/api/admin/productos", headers=auth, json=product())
    assert response.status_code == 201
    data = response.json()
    assert data["slug"] == "camisa-de-lino"
    assert data["precio"] == "149.90"
    assert data["moneda"] == "BOB"
    assert data["imagen_url"] is None
    assert data["activo"] is True
    with session_factory() as new_session:
        stored = new_session.get(Producto, data["id"])
        assert stored.precio == Decimal("149.90")
        assert stored.slug == data["slug"]
    assert client.get(f"/api/admin/productos/{data['id']}", headers=auth).json() == data


def test_edit_only_updates_fields_sent_and_allows_clearing_image(client, auth, session_factory):
    original = create(client, auth, imagen_url="https://example.com/camisa.jpg")
    response = client.patch(f"/api/admin/productos/{original['id']}", headers=auth, json={"nombre": "Camisa de lino natural", "precio": "175.50", "imagen_url": None})
    assert response.status_code == 200
    data = response.json()
    assert data["nombre"] == "Camisa de lino natural"
    assert data["descripcion"] == original["descripcion"]
    assert data["slug"] == original["slug"]  # cambiar nombre no rompe la URL pública automáticamente.
    assert data["imagen_url"] is None
    with session_factory() as new_session:
        assert new_session.get(Producto, original["id"]).precio == Decimal("175.50")


def test_duplicate_slug_is_conflict_and_transaction_rolls_back(client, auth):
    original = create(client, auth)
    duplicate = client.post("/api/admin/productos", headers=auth, json=product())
    assert duplicate.status_code == 409
    second = create(client, auth, nombre="Pantalón recto")
    conflict = client.patch(f"/api/admin/productos/{second['id']}", headers=auth, json={"slug": original["slug"], "precio": "999.00"})
    assert conflict.status_code == 409
    stored = client.get(f"/api/admin/productos/{second['id']}", headers=auth).json()
    assert stored["slug"] == "pantalon-recto"
    assert stored["precio"] == "149.90"
    assert client.get("/api/admin/productos", headers=auth).json()["total"] == 2


@pytest.mark.parametrize("changes", [{"nombre": "ab"}, {"nombre": "   "}, {"nombre": "x" * 121}, {"slug": "No Valido"}, {"slug": "a--b"}, {"slug": "a/b"}, {"slug": "ab"}, {"descripcion": "x" * 3001}, {"precio": "0.00"}, {"precio": "-1"}, {"precio": "2.999"}, {"precio": "NaN"}, {"precio": "100000000.00"}, {"imagen_url": "javascript:alert(1)"}, {"imagen_url": "data:image/png;base64,a"}, {"imagen_url": "https://user:password@example.com/image.jpg"}, {"moneda": "USD"}])
def test_invalid_product_cannot_be_persisted(client, auth, changes, session_factory):
    response = client.post("/api/admin/productos", headers=auth, json=product(**changes))
    assert response.status_code == 422
    with session_factory() as db:
        assert db.scalar(select(Producto.id)) is None


@pytest.mark.parametrize("changes", [{}, {"nombre": None}, {"precio": None}, {"slug": None}, {"descripcion": None}, {"activo": None}, {"id": 90}])
def test_patch_rejects_empty_payload_or_null_required_fields(client, auth, changes):
    original = create(client, auth)
    response = client.patch(f"/api/admin/productos/{original['id']}", headers=auth, json=changes)
    assert response.status_code == 422


def test_public_contract_lists_only_active_and_detail_needs_no_login(client, auth):
    active = create(client, auth)
    hidden = create(client, auth, nombre="Borrador no publicado", activo=False)
    public_list = client.get("/api/catalogo/productos?activo=false").json()
    assert public_list["total"] == 1
    assert public_list["items"] == [active]
    assert client.get(f"/api/catalogo/productos/{active['slug']}").json() == active
    assert client.get(f"/api/catalogo/productos/{hidden['slug']}").status_code == 404
    assert client.get("/api/catalogo/productos/no-existe").status_code == 404
    assert client.get("/api/admin/productos", headers=auth).json()["total"] == 2


def test_filters_pagination_and_unpublish_are_persisted(client, auth):
    first = create(client, auth)
    second = create(client, auth, nombre="Camisa verde", slug="camisa-verde")
    create(client, auth, nombre="Pantalón recto", activo=False)
    page = client.get("/api/admin/productos?q=camisa&activo=true&limit=1&offset=1", headers=auth).json()
    assert page == {"items": [first], "total": 2, "limit": 1, "offset": 1}
    response = client.patch(f"/api/admin/productos/{second['id']}", headers=auth, json={"activo": False})
    assert response.status_code == 200
    assert client.get(f"/api/catalogo/productos/{second['slug']}").status_code == 404
    assert client.get("/api/admin/productos?activo=false", headers=auth).json()["total"] == 2


def test_search_does_not_interpret_sql_wildcards(client, auth):
    create(client, auth)
    assert client.get("/api/catalogo/productos?q=%25").json()["total"] == 0


@pytest.mark.parametrize("query", ["limit=0", "limit=101", "offset=-1", "q=" + "x" * 121])
def test_pagination_bounds_are_validated(client, auth, query):
    assert client.get(f"/api/admin/productos?{query}", headers=auth).status_code == 422


def test_missing_products_return_404_without_creating_anything(client, auth):
    assert client.get("/api/admin/productos/999", headers=auth).status_code == 404
    assert client.patch("/api/admin/productos/999", headers=auth, json={"nombre": "Nuevo nombre"}).status_code == 404
