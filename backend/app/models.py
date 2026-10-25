from datetime import datetime, timezone
from decimal import Decimal

from sqlalchemy import Boolean, CheckConstraint, DateTime, ForeignKey, Index, Integer, Numeric, String, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from app.db import Base


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


class Administrador(Base):
    __tablename__ = "administradores"
    __table_args__ = (UniqueConstraint("correo", name="uq_administradores_correo"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    nombre: Mapped[str] = mapped_column(String(120), nullable=False)
    correo: Mapped[str] = mapped_column(String(254), nullable=False)
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    activo: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    creado_en: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, default=utc_now)


class SesionAdministrador(Base):
    __tablename__ = "sesiones_administrador"

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    administrador_id: Mapped[int] = mapped_column(ForeignKey("administradores.id", ondelete="CASCADE"), nullable=False, index=True)
    creado_en: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, default=utc_now)
    expira_en: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    revocada: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)


class Producto(Base):
    __tablename__ = "productos"
    __table_args__ = (
        UniqueConstraint("slug", name="uq_productos_slug"),
        CheckConstraint("precio > 0 AND precio <= 99999999.99", name="ck_productos_precio"),
        CheckConstraint("moneda = 'BOB'", name="ck_productos_moneda"),
        Index("ix_productos_activo_id", "activo", "id"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    slug: Mapped[str] = mapped_column(String(140), nullable=False)
    nombre: Mapped[str] = mapped_column(String(120), nullable=False)
    descripcion: Mapped[str] = mapped_column(Text, nullable=False, default="")
    precio: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False)
    moneda: Mapped[str] = mapped_column(String(3), nullable=False, default="BOB")
    imagen_url: Mapped[str | None] = mapped_column(String(2048), nullable=True)
    activo: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    creado_en: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, default=utc_now)
    actualizado_en: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, default=utc_now)
