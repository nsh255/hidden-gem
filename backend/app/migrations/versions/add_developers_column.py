"""add developers column

Revision ID: add_developers_column
Revises: previous_revision_id
Create Date: 2025-05-02 16:33:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = 'add_developers_column'
down_revision = 'previous_revision_id'  # Replace with actual previous revision
branch_labels = None
depends_on = None


def upgrade():
    # Add the developers column to the games table
    op.add_column('games', sa.Column('developers', postgresql.ARRAY(sa.String()), nullable=True))


def downgrade():
    # Remove the developers column from the games table
    op.drop_column('games', 'developers')
