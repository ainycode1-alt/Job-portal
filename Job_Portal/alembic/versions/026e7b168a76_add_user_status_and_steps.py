"""add_user_status_and_steps

Revision ID: 026e7b168a76
Revises: 7d22163290f4
Create Date: 2026-07-10 17:20:21.171338

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


"""add_user_status_and_steps

Revision ID: 026e7b168a76
Revises: 7d22163290f4
Create Date: 2026-07-10 17:20:21.171338

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = '026e7b168a76'
down_revision: Union[str, None] = '7d22163290f4'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Create ENUM types first
    account_status_enum = sa.Enum('active', 'locked', 'suspended', 'deleted', name='accountstatusenum')
    registration_step_enum = sa.Enum('otp_pending', 'profile_pending', 'subscription_pending', 'completed', name='registrationstepenum')
    
    account_status_enum.create(op.get_bind(), checkfirst=True)
    registration_step_enum.create(op.get_bind(), checkfirst=True)

    # Add columns with server default for existing rows
    op.add_column('users', sa.Column('account_status', account_status_enum, nullable=False, server_default='active'))
    op.add_column('users', sa.Column('registration_step', registration_step_enum, nullable=False, server_default='otp_pending'))


def downgrade() -> None:
    # Drop columns first
    op.drop_column('users', 'registration_step')
    op.drop_column('users', 'account_status')

    # Drop ENUM types
    sa.Enum(name='accountstatusenum').drop(op.get_bind(), checkfirst=True)
    sa.Enum(name='registrationstepenum').drop(op.get_bind(), checkfirst=True)
