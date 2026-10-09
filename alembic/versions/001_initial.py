"""Initial migration with all models

Revision ID: 001_initial
Revises:
Create Date: 2024-01-01 00:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
import geoalchemy2
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '001_initial'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Create enum types
    user_role_enum = postgresql.ENUM('citizen', 'municipal_staff', 'admin', name='userrole', create_type=False)
    complaint_status_enum = postgresql.ENUM('pending', 'acknowledged', 'in_progress', 'resolved', 'closed', 'rejected', name='complaintstatus', create_type=False)
    complaint_priority_enum = postgresql.ENUM('low', 'medium', 'high', 'urgent', name='complaintpriority', create_type=False)

    # Create enums
    op.execute("CREATE TYPE userrole AS ENUM ('citizen', 'municipal_staff', 'admin')")
    op.execute("CREATE TYPE complaintstatus AS ENUM ('pending', 'acknowledged', 'in_progress', 'resolved', 'closed', 'rejected')")
    op.execute("CREATE TYPE complaintpriority AS ENUM ('low', 'medium', 'high', 'urgent')")

    # Users table
    op.create_table(
        'users',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('email', sa.String(255), unique=True, nullable=False),
        sa.Column('hashed_password', sa.String(255), nullable=False),
        sa.Column('full_name', sa.String(255), nullable=False),
        sa.Column('phone', sa.String(20), nullable=True),
        sa.Column('role', user_role_enum, nullable=False, server_default='citizen'),
        sa.Column('is_active', sa.Boolean, nullable=False, server_default='true'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )
    op.create_index('ix_users_email', 'users', ['email'])
    op.create_index('ix_users_id', 'users', ['id'])

    # Waste categories table
    op.create_table(
        'waste_categories',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('name', sa.String(100), unique=True, nullable=False),
        sa.Column('slug', sa.String(100), unique=True, nullable=False),
        sa.Column('description', sa.Text, nullable=True),
        sa.Column('color_code', sa.String(7), nullable=True),
        sa.Column('icon', sa.String(50), nullable=True),
        sa.Column('is_active', sa.Boolean, server_default='true', nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )
    op.create_index('ix_waste_categories_name', 'waste_categories', ['name'])
    op.create_index('ix_waste_categories_slug', 'waste_categories', ['slug'])

    # Disposal rules table
    op.create_table(
        'disposal_rules',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('category_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('waste_categories.id', ondelete='CASCADE'), nullable=False),
        sa.Column('title', sa.String(255), nullable=False),
        sa.Column('description', sa.Text, nullable=True),
        sa.Column('instructions', sa.Text, nullable=False),
        sa.Column('locality', sa.String(255), nullable=True),
        sa.Column('pickup_schedule', sa.String(255), nullable=True),
        sa.Column('pickup_time', sa.String(100), nullable=True),
        sa.Column('tips', sa.Text, nullable=True),
        sa.Column('warnings', sa.Text, nullable=True),
        sa.Column('priority', sa.Integer, server_default='0', nullable=False),
        sa.Column('is_active', sa.Boolean, server_default='true', nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )
    op.create_index('ix_disposal_rules_category_id', 'disposal_rules', ['category_id'])
    op.create_index('ix_disposal_rules_locality', 'disposal_rules', ['locality'])

    # Facilities table
    op.create_table(
        'facilities',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('name', sa.String(255), nullable=False),
        sa.Column('facility_type', sa.String(100), nullable=False),
        sa.Column('description', sa.Text, nullable=True),
        sa.Column('address', sa.Text, nullable=False),
        sa.Column('city', sa.String(100), nullable=False),
        sa.Column('state', sa.String(100), nullable=True),
        sa.Column('postal_code', sa.String(20), nullable=True),
        sa.Column('country', sa.String(100), server_default='India', nullable=False),
        sa.Column('phone', sa.String(20), nullable=True),
        sa.Column('email', sa.String(255), nullable=True),
        sa.Column('website', sa.String(500), nullable=True),
        sa.Column('operating_hours', sa.Text, nullable=True),
        sa.Column('accepted_waste_types', sa.Text, nullable=True),
        sa.Column('location', geoalchemy2.types.Geography(geometry_type='POINT', srid=4326), nullable=True),
        sa.Column('latitude', sa.Float, nullable=True),
        sa.Column('longitude', sa.Float, nullable=True),
        sa.Column('is_verified', sa.Boolean, server_default='false', nullable=False),
        sa.Column('verified_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('verified_by', postgresql.UUID(as_uuid=True), sa.ForeignKey('users.id', ondelete='SET NULL'), nullable=True),
        sa.Column('last_updated', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column('is_active', sa.Boolean, server_default='true', nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )
    op.create_index('ix_facilities_name', 'facilities', ['name'])
    op.create_index('ix_facilities_facility_type', 'facilities', ['facility_type'])
    op.create_index('ix_facilities_city', 'facilities', ['city'])

    # Complaints table
    op.create_table(
        'complaints',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('client_generated_id', postgresql.UUID(as_uuid=True), unique=True, nullable=True),
        sa.Column('reporter_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('users.id', ondelete='CASCADE'), nullable=False),
        sa.Column('title', sa.String(255), nullable=False),
        sa.Column('description', sa.Text, nullable=False),
        sa.Column('waste_category_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('waste_categories.id', ondelete='SET NULL'), nullable=True),
        sa.Column('address', sa.Text, nullable=True),
        sa.Column('city', sa.String(100), nullable=True),
        sa.Column('locality', sa.String(255), nullable=True),
        sa.Column('location', geoalchemy2.types.Geography(geometry_type='POINT', srid=4326), nullable=True),
        sa.Column('latitude', sa.Float, nullable=True),
        sa.Column('longitude', sa.Float, nullable=True),
        sa.Column('facility_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('facilities.id', ondelete='SET NULL'), nullable=True),
        sa.Column('status', complaint_status_enum, nullable=False, server_default='pending'),
        sa.Column('priority', complaint_priority_enum, nullable=False, server_default='medium'),
        sa.Column('photo_url', sa.String(500), nullable=True),
        sa.Column('resolution_notes', sa.Text, nullable=True),
        sa.Column('resolved_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('resolved_by', postgresql.UUID(as_uuid=True), sa.ForeignKey('users.id', ondelete='SET NULL'), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )
    op.create_index('ix_complaints_reporter_id', 'complaints', ['reporter_id'])
    op.create_index('ix_complaints_status', 'complaints', ['status'])
    op.create_index('ix_complaints_priority', 'complaints', ['priority'])
    op.create_index('ix_complaints_created_at', 'complaints', ['created_at'])
    op.create_index('ix_complaints_city', 'complaints', ['city'])
    op.create_index('ix_complaints_locality', 'complaints', ['locality'])
    op.create_index('ix_complaints_client_generated_id', 'complaints', ['client_generated_id'])

    # Complaint status history table
    op.create_table(
        'complaint_status_history',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('complaint_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('complaints.id', ondelete='CASCADE'), nullable=False),
        sa.Column('changed_by', postgresql.UUID(as_uuid=True), sa.ForeignKey('users.id', ondelete='CASCADE'), nullable=False),
        sa.Column('previous_status', complaint_status_enum, nullable=True),
        sa.Column('new_status', complaint_status_enum, nullable=False),
        sa.Column('remarks', sa.Text, nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )
    op.create_index('ix_complaint_status_history_complaint_id', 'complaint_status_history', ['complaint_id'])
    op.create_index('ix_complaint_status_history_changed_by', 'complaint_status_history', ['changed_by'])
    op.create_index('ix_complaint_status_history_created_at', 'complaint_status_history', ['created_at'])

    # Feedbacks table
    op.create_table(
        'feedbacks',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('complaint_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('complaints.id', ondelete='CASCADE'), nullable=False),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('users.id', ondelete='CASCADE'), nullable=False),
        sa.Column('rating', sa.Integer, nullable=False),
        sa.Column('comment', sa.Text, nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )
    op.create_index('ix_feedbacks_complaint_id', 'feedbacks', ['complaint_id'])
    op.create_index('ix_feedbacks_user_id', 'feedbacks', ['user_id'])


def downgrade() -> None:
    # Drop tables in reverse order
    op.drop_table('feedbacks')
    op.drop_table('complaint_status_history')
    op.drop_table('complaints')
    op.drop_table('facilities')
    op.drop_table('disposal_rules')
    op.drop_table('waste_categories')
    op.drop_table('users')

    # Drop enums
    op.execute('DROP TYPE IF EXISTS complaintpriority')
    op.execute('DROP TYPE IF EXISTS complaintstatus')
    op.execute('DROP TYPE IF EXISTS userrole')
