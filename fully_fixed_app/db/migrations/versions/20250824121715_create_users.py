"""Create users table

Revision ID: 20250824121715
Revises: Create Date: 2025-08-24T12:17:16.114033

"""
from alembic import op
import sqlalchemy as sa
import uuid


# revision identifiers, used by Alembic.
revision = '20250824121715'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    """Create users table."""
    op.create_table(
        'users',
        sa.Column('id', sa.UUID(as_uuid=True), primary_key=True, default=uuid.uuid4),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),        sa.Column('name', sa.String(255)),        sa.Column('email', sa.String(255)),        sa.Column('age', sa.Integer),    )


def downgrade() -> None:
    """Drop users table."""
    op.drop_table('users')