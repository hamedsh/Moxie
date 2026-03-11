"""varient response type

Revision ID: e09c497d9188
Revises: 1be6750e9453
Create Date: 2023-09-13 14:11:59.640581

"""

# revision identifiers, used by Alembic.
revision = 'e09c497d9188'
down_revision = '1be6750e9453'

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql
import os


def upgrade():
    db_type = os.getenv("DB_TYPE", "sqlite").lower()

    if db_type == "sqlite":
        # SQLite doesn't support ENUM types or complex ALTER COLUMN operations
        # Just add the column as String type
        op.add_column('rule', sa.Column('response_type', sa.String(), nullable=True, default='json'))
    else:
        # PostgreSQL specific operations
        response_types = postgresql.ENUM('xml', 'json', 'text', name='response_types', create_type=False)
        response_types.create(op.get_bind(), checkfirst=True)
        op.add_column('rule', sa.Column(
            'response_type', response_types, nullable=True, default='json',
        ))
        op.alter_column('rule', 'response',
                   existing_type=postgresql.JSON(astext_type=sa.Text()),
                   type_=sa.String(),
                   existing_nullable=True)


def downgrade():
    db_type = os.getenv("DB_TYPE", "sqlite").lower()

    if db_type == "sqlite":
        # SQLite: just drop the column
        op.drop_column('rule', 'response_type')
    else:
        # PostgreSQL specific operations
        op.alter_column('rule', 'response',
                   existing_type=sa.String(),
                   type_=postgresql.JSON(astext_type=sa.Text()),
                   existing_nullable=True)
        op.drop_column('rule', 'response_type')
