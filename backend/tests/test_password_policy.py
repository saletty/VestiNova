from unittest.mock import Mock

import pytest

from app.config import Settings
from app.models import Administrador
from app.password_policy import PASSWORD_POLICY_MESSAGE, validate_new_password
from app.security import hash_password, verify_password
from scripts import create_admin


EXPECTED_MESSAGE = "La contraseña debe tener entre 8 y 128 caracteres e incluir una mayúscula, una minúscula, un número y un carácter especial."


@pytest.mark.parametrize("password", ["Aa1!aaaa", "Aa1!" + "a" * 124])
def test_new_password_accepts_both_inclusive_length_limits(password):
    assert len(password) in {8, 128}
    assert validate_new_password(password) is None


@pytest.mark.parametrize("password", ["Aa1!aaa", "Aa1!" + "a" * 125])
def test_new_password_rejects_outside_length_limits(password):
    assert len(password) in {7, 129}
    with pytest.raises(ValueError) as error:
        validate_new_password(password)
    assert str(error.value) == EXPECTED_MESSAGE


@pytest.mark.parametrize("password", ["aa1!aaaa", "AA1!AAAA", "Aaa!aaaa", "Aa12aaaa", "Aa12aa a", "Aa12aa\ta", "Aa12aa\na", "Aa12aa\u00a0a", "Aa12aa\u200ba", "Aa12aa\u0301a"])
def test_each_required_category_and_whitespace_special_rule(password):
    with pytest.raises(ValueError) as error:
        validate_new_password(password)
    assert str(error.value) == EXPECTED_MESSAGE
    assert password not in str(error.value)


def test_policy_message_is_exact_and_does_not_modify_valid_password():
    password = " Aa1!aaa "
    assert PASSWORD_POLICY_MESSAGE == EXPECTED_MESSAGE
    validate_new_password(password)
    encoded = hash_password(password)
    assert encoded.startswith("$argon2id$")
    assert verify_password(password, encoded) is True
    assert verify_password(password.strip(), encoded) is False


def test_legacy_short_password_hash_can_still_login(client, session_factory):
    # La política nueva solo protege altas/cambios; no invalida hashes previos.
    old_password = "abc"
    encoded = hash_password(old_password)
    with session_factory() as db:
        account = Administrador(nombre="Cuenta anterior", correo="anterior@vestinova.test", password_hash=encoded, activo=True)
        db.add(account)
        db.commit()
        account_id = account.id
    response = client.post("/api/auth/login", json={"correo": "anterior@vestinova.test", "password": old_password})
    assert response.status_code == 200
    assert response.json()["administrador"]["id"] == account_id
    with session_factory() as db:
        assert db.get(Administrador, account_id).password_hash == encoded


@pytest.mark.parametrize("password", ["Aa1!aaa", "Aa1!" + "a" * 125, "aa1!aaaa", "AA1!AAAA", "Aaa!aaaa", "Aa12aa a"])
def test_admin_command_rejects_invalid_password_before_connecting_or_writing(monkeypatch, capsys, password):
    settings = Settings("sqlite://", "solo-prueba-del-comando-no-se-conecta")
    monkeypatch.setattr(create_admin.Settings, "from_env", lambda: settings)
    answers = iter(["Administrador local", "admin@vestinova.test"])
    monkeypatch.setattr("builtins.input", lambda _: next(answers))
    secret_answers = iter([password, password])
    secret_prompt = Mock(side_effect=lambda _: next(secret_answers))
    monkeypatch.setattr(create_admin, "getpass", secret_prompt)
    connect = Mock(side_effect=AssertionError("No debe conectarse con una contraseña inválida"))
    session_factory = Mock(side_effect=AssertionError("No debe crear una sesión ni escribir datos"))
    monkeypatch.setattr(create_admin, "build_engine", connect)
    monkeypatch.setattr(create_admin, "build_session_factory", session_factory)
    with pytest.raises(ValueError) as error:
        create_admin.main()
    assert str(error.value) == EXPECTED_MESSAGE
    connect.assert_not_called()
    session_factory.assert_not_called()
    assert secret_prompt.call_count == 2
    assert password not in capsys.readouterr().out
