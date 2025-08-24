"""Create posts table

Revision ID: 20250824121025
Revises: 
Create Date: 2025-08-24T12:10:25.708665

"""
from alembic import op
import sqlalchemy as sa
import uuid


# revision identifiers, used by Alembic.
revision = '20250824121025'
down_revision = '20250824120512'
branch_labels = None
depends_on = None


def upgrade() -> None:
    """Create posts table."""
    op.create_table(
        'posts',
        sa.Column('id', sa.UUID(as_uuid=True), primary_key=True, default=uuid.uuid4),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),        sa.Column('title', sa.String(255)),        sa.Column('content', sa.Text),        sa.Column('user_id', sa.UUID(as_uuid=True)),    )


def downgrade() -> None:
    """Drop posts table."""
    op.drop_table('posts')