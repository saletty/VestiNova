from datetime import datetime, timedelta, timezone
from uuid import uuid4

from argon2 import PasswordHasher
from argon2.exceptions import InvalidHashError, VerificationError
from fastapi import Depends, HTTPException, Request, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
import jwt
from sqlalchemy.orm import Session

from app.db import get_db
from app.models import Administrador, SesionAdministrador, utc_now


PASSWORD_HASHER = PasswordHasher()
_DUMMY_HASH = PASSWORD_HASHER.hash("vestinova-only-for-timing-not-an-account")
bearer = HTTPBearer(auto_error=False)
JWT_ISSUER = "vestinova-mvp"
JWT_AUDIENCE = "vestinova-administracion"


def hash_password(password: str) -> str:
    return PASSWORD_HASHER.hash(password)


def verify_password(password: str, encoded: str) -> bool:
    try:
        return PASSWORD_HASHER.verify(encoded, password)
    except (VerificationError, InvalidHashError):
        return False


def verify_unknown_password(password: str) -> None:
    verify_password(password, _DUMMY_HASH)


def unauthorized() -> HTTPException:
    return HTTPException(status.HTTP_401_UNAUTHORIZED, "La sesión no es válida o ha expirado.", headers={"WWW-Authenticate": "Bearer"})


def issue_session(db: Session, administrator: Administrador, request: Request):
    settings = request.app.state.settings
    now = utc_now()
    expiry = now + timedelta(minutes=settings.session_minutes)
    session = SesionAdministrador(id=str(uuid4()), administrador_id=administrator.id, expira_en=expiry, revocada=False)
    db.add(session)
    token = jwt.encode({"sub": str(administrator.id), "jti": session.id, "tipo": "administrador", "iat": now, "exp": expiry, "iss": JWT_ISSUER, "aud": JWT_AUDIENCE}, settings.jwt_secret, algorithm="HS256")
    db.commit()
    return token, expiry


def get_current_session(request: Request, credentials: HTTPAuthorizationCredentials | None = Depends(bearer), db: Session = Depends(get_db)) -> tuple[Administrador, SesionAdministrador]:
    if credentials is None or credentials.scheme.lower() != "bearer":
        raise unauthorized()
    try:
        claims = jwt.decode(credentials.credentials, request.app.state.settings.jwt_secret, algorithms=["HS256"], issuer=JWT_ISSUER, audience=JWT_AUDIENCE, options={"require": ["sub", "jti", "tipo", "iat", "exp", "iss", "aud"]})
        administrator_id = int(claims["sub"])
        session_id = str(claims["jti"])
    except (jwt.InvalidTokenError, ValueError, TypeError, KeyError):
        raise unauthorized() from None
    if claims["tipo"] != "administrador":
        raise HTTPException(status.HTTP_403_FORBIDDEN, "Se requiere acceso de administrador.")
    session = db.get(SesionAdministrador, session_id)
    administrator = db.get(Administrador, administrator_id)
    if session is None or administrator is None or not administrator.activo or session.revocada or session.administrador_id != administrator.id:
        raise unauthorized()
    expiry = session.expira_en
    if expiry.tzinfo is None:
        expiry = expiry.replace(tzinfo=timezone.utc)
    if expiry <= utc_now():
        raise unauthorized()
    return administrator, session


def require_administrator(current: tuple[Administrador, SesionAdministrador] = Depends(get_current_session)) -> Administrador:
    return current[0]
