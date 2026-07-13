"""add_subscriptions_documents_and_otp_relationships

Revision ID: c79252644d25
Revises: 026e7b168a76
Create Date: 2026-07-10 17:28:48.017208

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


revision: str = 'c79252644d25'
down_revision: Union[str, None] = '026e7b168a76'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Truncate otp_verifications to avoid NotNullViolation on existing rows
    op.execute("TRUNCATE TABLE otp_verifications CASCADE")

    # Drop existing ENUM types if they exist to prevent DuplicateObject errors
    op.execute("DROP TYPE IF EXISTS documenttypeenum CASCADE")
    op.execute("DROP TYPE IF EXISTS subscriptionplanenum CASCADE")
    op.execute("DROP TYPE IF EXISTS subscriptionstatusenum CASCADE")
    op.execute("DROP TYPE IF EXISTS otppurposeenum CASCADE")

    # Create ENUM types explicitly
    postgresql.ENUM('jd', 'cv', name='documenttypeenum').create(op.get_bind(), checkfirst=True)
    postgresql.ENUM('free_trial', 'paid', name='subscriptionplanenum').create(op.get_bind(), checkfirst=True)
    postgresql.ENUM('active', 'expired', 'cancelled', name='subscriptionstatusenum').create(op.get_bind(), checkfirst=True)
    postgresql.ENUM('registration', 'login', 'resend', name='otppurposeenum').create(op.get_bind(), checkfirst=True)

    # Create tables referencing the ENUMs without re-creating them
    op.create_table('documents',
    sa.Column('id', sa.String(length=36), nullable=False),
    sa.Column('user_id', sa.String(length=36), nullable=False),
    sa.Column('doc_type', postgresql.ENUM(name='documenttypeenum', create_type=False), nullable=False),
    sa.Column('file_url', sa.String(length=500), nullable=False),
    sa.Column('original_filename', sa.String(length=255), nullable=True),
    sa.Column('uploaded_at', sa.DateTime(), server_default=sa.text('now()'), nullable=False),
    sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_documents_user_id'), 'documents', ['user_id'], unique=False)
    
    op.create_table('subscriptions',
    sa.Column('id', sa.String(length=36), nullable=False),
    sa.Column('user_id', sa.String(length=36), nullable=False),
    sa.Column('plan', postgresql.ENUM(name='subscriptionplanenum', create_type=False), nullable=False),
    sa.Column('status', postgresql.ENUM(name='subscriptionstatusenum', create_type=False), nullable=False),
    sa.Column('is_trial', sa.Boolean(), nullable=False),
    sa.Column('started_at', sa.Date(), server_default=sa.text('CURRENT_DATE'), nullable=False),
    sa.Column('expires_at', sa.Date(), nullable=True),
    sa.Column('created_at', sa.DateTime(), server_default=sa.text('now()'), nullable=False),
    sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_subscriptions_user_id'), 'subscriptions', ['user_id'], unique=False)
    
    # Alter otp_verifications table
    op.add_column('otp_verifications', sa.Column('user_id', sa.String(length=36), nullable=False))
    op.add_column('otp_verifications', sa.Column('max_attempts', sa.Integer(), nullable=False, server_default='5'))
    
    op.alter_column('otp_verifications', 'purpose',
               existing_type=sa.VARCHAR(length=50),
               type_=postgresql.ENUM(name='otppurposeenum', create_type=False),
               existing_nullable=False,
               postgresql_using="purpose::otppurposeenum")
               
    op.create_index(op.f('ix_otp_verifications_user_id'), 'otp_verifications', ['user_id'], unique=False)
    op.create_foreign_key(None, 'otp_verifications', 'users', ['user_id'], ['id'])


def downgrade() -> None:
    # Drop foreign keys and columns
    op.drop_constraint(None, 'otp_verifications', type_='foreignkey')
    op.drop_index(op.f('ix_otp_verifications_user_id'), table_name='otp_verifications')
    op.alter_column('otp_verifications', 'purpose',
               existing_type=postgresql.ENUM(name='otppurposeenum', create_type=False),
               type_=sa.VARCHAR(length=50),
               existing_nullable=False)
    op.drop_column('otp_verifications', 'max_attempts')
    op.drop_column('otp_verifications', 'user_id')
    op.drop_index(op.f('ix_subscriptions_user_id'), table_name='subscriptions')
    op.drop_table('subscriptions')
    op.drop_index(op.f('ix_documents_user_id'), table_name='documents')
    op.drop_table('documents')

    # Drop ENUM types
    sa.Enum(name='documenttypeenum').drop(op.get_bind(), checkfirst=True)
    sa.Enum(name='subscriptionplanenum').drop(op.get_bind(), checkfirst=True)
    sa.Enum(name='subscriptionstatusenum').drop(op.get_bind(), checkfirst=True)
    sa.Enum(name='otppurposeenum').drop(op.get_bind(), checkfirst=True)
