"""initial schema with full-text indexes

Revision ID: 20260428_000001
Revises:
Create Date: 2026-04-28 16:00:00
"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = "20260428_000001"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute("CREATE EXTENSION IF NOT EXISTS pg_trgm")

    op.create_table(
        "documentos",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("titulo", sa.String(length=255), nullable=False),
        sa.Column("autor", sa.String(length=255), nullable=False),
        sa.Column("conteudo", sa.Text(), nullable=False),
        sa.Column("data", sa.Date(), nullable=False),
        sa.Column("latitude", sa.Float(), nullable=True),
        sa.Column("longitude", sa.Float(), nullable=True),
        sa.CheckConstraint(
            "(latitude IS NULL AND longitude IS NULL) OR (latitude BETWEEN -90 AND 90 AND longitude BETWEEN -180 AND 180)",
            name="ck_documentos_coordinates_valid",
        ),
        sa.PrimaryKeyConstraint("id"),
    )

    op.create_index("ix_documentos_titulo", "documentos", ["titulo"], unique=False)
    op.create_index("ix_documentos_autor", "documentos", ["autor"], unique=False)
    op.create_index("ix_documentos_data", "documentos", ["data"], unique=False)
    op.create_index(
        "ix_documentos_search_vector",
        "documentos",
        [sa.text("to_tsvector('portuguese', coalesce(titulo, '') || ' ' || coalesce(conteudo, '') || ' ' || coalesce(autor, ''))")],
        postgresql_using="gin",
    )


def downgrade() -> None:
    op.drop_index("ix_documentos_search_vector", table_name="documentos")
    op.drop_index("ix_documentos_data", table_name="documentos")
    op.drop_index("ix_documentos_autor", table_name="documentos")
    op.drop_index("ix_documentos_titulo", table_name="documentos")
    op.drop_table("documentos")
