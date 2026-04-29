"""search_vector persistido + PostGIS (location GiST)

Revision ID: 20260429_000002
Revises: 20260428_000001
Create Date: 2026-04-29
"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision = "20260429_000002"
down_revision = "20260428_000001"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.drop_index("ix_documentos_search_vector", table_name="documentos")

    op.execute("CREATE EXTENSION IF NOT EXISTS postgis")

    op.execute(
        """
        ALTER TABLE documentos ADD COLUMN search_vector tsvector
        GENERATED ALWAYS AS (
            to_tsvector(
                'portuguese',
                coalesce(titulo, '') || ' ' || coalesce(conteudo, '') || ' ' || coalesce(autor, '')
            )
        ) STORED;
        """
    )
    op.create_index(
        "ix_documentos_search_vector",
        "documentos",
        ["search_vector"],
        postgresql_using="gin",
    )

    op.execute(
        """
        ALTER TABLE documentos ADD COLUMN location geography(Point, 4326)
        GENERATED ALWAYS AS (
            CASE
                WHEN latitude IS NOT NULL AND longitude IS NOT NULL THEN
                    ST_SetSRID(ST_MakePoint(longitude, latitude), 4326)::geography
                ELSE NULL
            END
        ) STORED;
        """
    )
    op.execute("CREATE INDEX ix_documentos_location ON documentos USING GIST (location)")


def downgrade() -> None:
    op.execute("DROP INDEX IF EXISTS ix_documentos_location")
    op.drop_column("documentos", "location")

    op.drop_index("ix_documentos_search_vector", table_name="documentos")
    op.drop_column("documentos", "search_vector")

    op.create_index(
        "ix_documentos_search_vector",
        "documentos",
        [
            sa.text(
                "to_tsvector('portuguese', coalesce(titulo, '') || ' ' || coalesce(conteudo, '') || ' ' || coalesce(autor, ''))"
            )
        ],
        postgresql_using="gin",
    )
