"""add_availability_enum

Revision ID: d90feacc1ae1
Revises: 28d2151a6a52
Create Date: 2026-07-15 10:17:13.696899

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = 'd90feacc1ae1'
down_revision: Union[str, None] = '28d2151a6a52'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Create the enum type first
    availability_enum = sa.Enum('immediate', 'notice_period', name='availabilityenum')
    availability_enum.create(op.get_bind(), checkfirst=True)

    # Alter column with explicit cast
    op.alter_column('candidates', 'availability',
               existing_type=sa.VARCHAR(length=50),
               type_=availability_enum,
               existing_nullable=False,
               postgresql_using="availability::availabilityenum")


def downgrade() -> None:
    op.alter_column('candidates', 'availability',
               existing_type=sa.Enum('immediate', 'notice_period', name='availabilityenum'),
               type_=sa.VARCHAR(length=50),
               existing_nullable=False)

    # Drop the enum type
    sa.Enum(name='availabilityenum').drop(op.get_bind(), checkfirst=True)
