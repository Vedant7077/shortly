"""add outbox events table

Revision ID: 7d3355facf82
Revises: 268cb522729f
Create Date: 2026-11-03 23:45:00.670898

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '7d3355facf82'
down_revision: Union[str, Sequence[str], None] = '268cb522729f'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None



def upgrade() -> None:
    """Upgrade schema."""
    op.create_table(
        'outbox_events',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('event_type', sa.String(length=100), nullable=False),
        sa.Column('payload', sa.JSON(), nullable=False),
        sa.Column(
            'status',
            sa.String(length=20),
            server_default='pending',
            nullable=False,
        ),
        sa.Column(
            'attempts',
            sa.Integer(),
            server_default='0',
            nullable=False,
        ),
        sa.Column(
            'created_at',
            sa.DateTime(timezone=True),
            server_default=sa.text('now()'),
            nullable=False,
        ),
        sa.Column(
            'processed_at',
            sa.DateTime(timezone=True),
            nullable=True,
        ),
        sa.Column('last_error', sa.Text(), nullable=True),
        sa.PrimaryKeyConstraint('id'),
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_table('outbox_events')

    # ### end Alembic commands ###
