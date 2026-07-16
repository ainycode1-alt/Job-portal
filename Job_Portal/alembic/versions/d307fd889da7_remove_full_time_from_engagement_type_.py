"""remove_full_time_from_engagement_type_enum

Revision ID: d307fd889da7
Revises: d90feacc1ae1
Create Date: 2026-07-15 16:07:49.231286

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = 'd307fd889da7'
down_revision: Union[str, None] = 'd90feacc1ae1'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # 1. Update existing records that use 'full_time'
    op.execute("UPDATE jobs SET engagement_type = 'c2c' WHERE engagement_type::text = 'full_time'")
    op.execute("UPDATE candidates SET engagement_types = array_remove(engagement_types, 'full_time'::engagementtypeenum)")
    op.execute("UPDATE candidates SET engagement_types = ARRAY['c2c'::engagementtypeenum] WHERE cardinality(engagement_types) = 0")

    # 2. Rename the old enum type
    op.execute("ALTER TYPE engagementtypeenum RENAME TO engagementtypeenum_old")

    # 3. Create the new enum type
    op.execute("CREATE TYPE engagementtypeenum AS ENUM ('c2c', 'c2h')")

    # 4. Alter table columns to use the new enum type
    op.execute("ALTER TABLE jobs ALTER COLUMN engagement_type TYPE engagementtypeenum USING engagement_type::text::engagementtypeenum")
    op.execute("ALTER TABLE candidates ALTER COLUMN engagement_types TYPE engagementtypeenum[] USING engagement_types::text[]::engagementtypeenum[]")

    # 5. Drop the old enum type
    op.execute("DROP TYPE engagementtypeenum_old")


def downgrade() -> None:
    # 1. Rename current type
    op.execute("ALTER TYPE engagementtypeenum RENAME TO engagementtypeenum_old")

    # 2. Create old type
    op.execute("CREATE TYPE engagementtypeenum AS ENUM ('full_time', 'c2c', 'c2h')")

    # 3. Alter columns back
    op.execute("ALTER TABLE jobs ALTER COLUMN engagement_type TYPE engagementtypeenum USING engagement_type::text::engagementtypeenum")
    op.execute("ALTER TABLE candidates ALTER COLUMN engagement_types TYPE engagementtypeenum[] USING engagement_types::text[]::engagementtypeenum[]")

    # 4. Drop old type
    op.execute("DROP TYPE engagementtypeenum_old")
