import pytest

from app.config import validate_local_database_url


@pytest.mark.parametrize("url", ["postgresql+psycopg://postgres:local@127.0.0.1:5432/vestinova_mvp", "postgresql+psycopg://local@localhost:15432/vestinova_mvp"])
def test_configuration_accepts_only_new_local_database(url):
    validate_local_database_url(url)


@pytest.mark.parametrize("url", ["postgresql+psycopg://postgres:secret@127.0.0.1:5432/vestinova", "postgresql+psycopg://postgres:secret@remote.example:5432/vestinova_mvp", "postgresql+psycopg2://postgres:secret@localhost/vestinova_mvp", "postgresql+psycopg://postgres:secret@localhost/vestinova_mvp?host=remote.example", "sqlite:///local.db", "not-a-url"])
def test_configuration_blocks_inherited_remote_and_wrong_driver(url):
    with pytest.raises(ValueError) as error:
        validate_local_database_url(url)
    assert "secret" not in str(error.value)
