"""Add atomic edital fields and empresa v11.8

Revision ID: ad7d572f7995
Revises: d3a152950630
Create Date: 2026-03-15 05:44:21.482158

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = 'ad7d572f7995'
down_revision = 'd3a152950630'
branch_labels = None
depends_on = None


def upgrade():
    # Only add the new columns requested for v11.8
    # Using batch_alter_table for SQLite compatibility if needed, 
    # but primarily for a cleaner syntax in Postgres via op
    with op.batch_alter_table('editais', schema=None) as batch_op:
        batch_op.add_column(sa.Column('numero_edital', sa.String(length=20), nullable=True))
        batch_op.add_column(sa.Column('ano_edital', sa.Integer(), nullable=True))
        batch_op.add_column(sa.Column('empresa', sa.String(length=150), nullable=True))


def downgrade():
    with op.batch_alter_table('editais', schema=None) as batch_op:
        batch_op.drop_column('empresa')
        batch_op.drop_column('ano_edital')
        batch_op.drop_column('numero_edital')
