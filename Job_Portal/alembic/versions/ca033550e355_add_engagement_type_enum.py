"""add_engagement_type_enum

Revision ID: ca033550e355
Revises: a0a5ed0120ab
Create Date: 2026-07-15 10:10:52.780483

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = 'ca033550e355'
down_revision: Union[str, None] = 'a0a5ed0120ab'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Create the enum type first
    engagement_type_enum = sa.Enum('full_time', 'c2c', 'c2h', name='engagementtypeenum')
    engagement_type_enum.create(op.get_bind(), checkfirst=True)

    # Alter column with explicit cast
    op.alter_column('jobs', 'engagement_type',
               existing_type=sa.VARCHAR(length=50),
               type_=engagement_type_enum,
               existing_nullable=False,
               postgresql_using="engagement_type::engagementtypeenum")


def downgrade() -> None:
    op.alter_column('jobs', 'engagement_type',
               existing_type=sa.Enum('full_time', 'c2c', 'c2h', name='engagementtypeenum'),
               type_=sa.VARCHAR(length=50),
               existing_nullable=False)

    # Drop the enum type
    sa.Enum(name='engagementtypeenum').drop(op.get_bind(), checkfirst=True)
