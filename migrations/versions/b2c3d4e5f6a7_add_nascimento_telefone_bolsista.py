"""Add data_nascimento and telefone to bolsistas

Revision ID: b2c3d4e5f6a7
Revises: a1b2c3d4e5f6
Create Date: 2026-09-19 09:40:00.000000

"""
from alembic import op
import sqlalchemy as sa

revision = 'b2c3d4e5f6a7'
down_revision = 'a1b2c3d4e5f6'
branch_labels = None
depends_on = None


def upgrade():
    with op.batch_alter_table('bolsistas', schema=None) as batch_op:
        batch_op.add_column(sa.Column('telefone', sa.String(length=30), nullable=True))
        batch_op.add_column(sa.Column('data_nascimento', sa.Date(), nullable=True))


def downgrade():
    with op.batch_alter_table('bolsistas', schema=None) as batch_op:
        batch_op.drop_column('data_nascimento')
        batch_op.drop_column('telefone')
