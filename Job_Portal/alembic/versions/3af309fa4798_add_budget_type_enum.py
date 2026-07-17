"""add_budget_type_enum

Revision ID: 3af309fa4798
Revises: d307fd889da7
Create Date: 2026-07-16 12:44:49.695198

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = '3af309fa4798'
down_revision: Union[str, None] = 'd307fd889da7'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # 1. Create the budgettypeenum type in PostgreSQL
    op.execute("CREATE TYPE budgettypeenum AS ENUM ('hourly', 'monthly', 'daywise')")

    # 2. Sanitize existing data in jobs.budget_type to match the new enum values
    op.execute("""
        UPDATE jobs 
        SET budget_type = CASE 
            WHEN LOWER(budget_type) = 'hourly' THEN 'hourly'
            WHEN LOWER(budget_type) = 'monthly' THEN 'monthly'
            ELSE 'daywise'
        END
    """)

    # 3. Alter the column type with an explicit USING clause to cast it to budgettypeenum
    op.execute("ALTER TABLE jobs ALTER COLUMN budget_type TYPE budgettypeenum USING budget_type::budgettypeenum")


def downgrade() -> None:
    # 1. Alter the column type back to VARCHAR(50)
    op.execute("ALTER TABLE jobs ALTER COLUMN budget_type TYPE VARCHAR(50) USING budget_type::text")

    # 2. Drop the custom enum type
    op.execute("DROP TYPE budgettypeenum")
