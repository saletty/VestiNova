"""Política exclusiva para crear o cambiar contraseñas; no se aplica al login."""
import unicodedata


PASSWORD_MIN_LENGTH = 8
PASSWORD_MAX_LENGTH = 128
PASSWORD_POLICY_MESSAGE = "La contraseña debe tener entre 8 y 128 caracteres e incluir una mayúscula, una minúscula, un número y un carácter especial."


def validate_new_password(password: str) -> None:
    """Valida sin recortar ni modificar la contraseña.

    Un carácter especial es un signo o símbolo Unicode. Los espacios,
    caracteres de control y marcas de acento aisladas no cuentan como tales.
    """
    valid = (
        isinstance(password, str)
        and PASSWORD_MIN_LENGTH <= len(password) <= PASSWORD_MAX_LENGTH
        and any(character.isupper() for character in password)
        and any(character.islower() for character in password)
        and any(character.isdecimal() for character in password)
        and any(unicodedata.category(character)[0] in {"P", "S"} for character in password)
    )
    if not valid:
        raise ValueError(PASSWORD_POLICY_MESSAGE)
