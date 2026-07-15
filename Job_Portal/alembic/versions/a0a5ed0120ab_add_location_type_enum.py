"""add_location_type_enum

Revision ID: a0a5ed0120ab
Revises: 33b4d64c93f8
Create Date: 2026-07-14 18:13:49.028144

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = 'a0a5ed0120ab'
down_revision: Union[str, None] = '33b4d64c93f8'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Create the enum type first
    location_type_enum = sa.Enum('onsite', 'hybrid', 'remote', name='locationtypeenum')
    location_type_enum.create(op.get_bind(), checkfirst=True)

    # Alter column with explicit cast
    op.alter_column('jobs', 'location_type',
               existing_type=sa.VARCHAR(length=50),
               type_=location_type_enum,
               existing_nullable=False,
               postgresql_using="location_type::locationtypeenum")


def downgrade() -> None:
    op.alter_column('jobs', 'location_type',
               existing_type=sa.Enum('onsite', 'hybrid', 'remote', name='locationtypeenum'),
               type_=sa.VARCHAR(length=50),
               existing_nullable=False)

    # Drop the enum type
    sa.Enum(name='locationtypeenum').drop(op.get_bind(), checkfirst=True)
