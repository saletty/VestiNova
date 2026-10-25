"""Administrador, sesiones revocables y productos propios de VestiNova MVP.

Revision: 0001_base
Revises: ninguna
"""
from alembic import op
import sqlalchemy as sa


revision = "0001_base"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table("administradores",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("nombre", sa.String(120), nullable=False),
        sa.Column("correo", sa.String(254), nullable=False),
        sa.Column("password_hash", sa.String(255), nullable=False),
        sa.Column("activo", sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.Column("creado_en", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.UniqueConstraint("correo", name="uq_administradores_correo"),
    )
    op.create_table("sesiones_administrador",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("administrador_id", sa.Integer(), sa.ForeignKey("administradores.id", ondelete="CASCADE"), nullable=False),
        sa.Column("creado_en", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("expira_en", sa.DateTime(timezone=True), nullable=False),
        sa.Column("revocada", sa.Boolean(), nullable=False, server_default=sa.false()),
    )
    op.create_index("ix_sesiones_administrador_administrador_id", "sesiones_administrador", ["administrador_id"])
    op.create_table("productos",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("slug", sa.String(140), nullable=False),
        sa.Column("nombre", sa.String(120), nullable=False),
        sa.Column("descripcion", sa.Text(), nullable=False, server_default=""),
        sa.Column("precio", sa.Numeric(10, 2), nullable=False),
        sa.Column("moneda", sa.String(3), nullable=False, server_default="BOB"),
        sa.Column("imagen_url", sa.String(2048), nullable=True),
        sa.Column("activo", sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.Column("creado_en", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("actualizado_en", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.UniqueConstraint("slug", name="uq_productos_slug"),
        sa.CheckConstraint("precio > 0 AND precio <= 99999999.99", name="ck_productos_precio"),
        sa.CheckConstraint("moneda = 'BOB'", name="ck_productos_moneda"),
    )
    op.create_index("ix_productos_activo_id", "productos", ["activo", "id"])


def downgrade() -> None:
    # No se utiliza durante la instalación normal. Un downgrade elimina datos del MVP.
    op.drop_index("ix_productos_activo_id", table_name="productos")
    op.drop_table("productos")
    op.drop_index("ix_sesiones_administrador_administrador_id", table_name="sesiones_administrador")
    op.drop_table("sesiones_administrador")
    op.drop_table("administradores")
