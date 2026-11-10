"""create links and processed batches tables

Revision ID: c70d856f22bd
Revises: 7d3355facf82
Create Date: 2026-11-10 13:18:09.788902

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'c70d856f22bd'
down_revision: Union[str, Sequence[str], None] = '7d3355facf82'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None



def upgrade() -> None:
    """Create links and processed_batches tables."""

    op.create_table(
        "links",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("short_code", sa.String(length=6), nullable=False),
        sa.Column("original_url", sa.String(length=2048), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
        ),
        sa.Column(
            "clicks",
            sa.Integer(),
            nullable=False,
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("short_code"),
    )

    op.create_table(
        "processed_batches",
        sa.Column("batch_id", sa.String(length=100), nullable=False),
        sa.Column(
            "processed_at",
            sa.DateTime(),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.PrimaryKeyConstraint("batch_id"),
    )


def downgrade() -> None:
    """Drop links and processed_batches tables."""

    op.drop_table("processed_batches")
    op.drop_table("links")
