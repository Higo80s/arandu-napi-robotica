"""Add convenio and coordenador geral to editais

Revision ID: a1b2c3d4e5f6
Revises: 60ed86c7a484
Create Date: 2026-09-19 09:25:00.000000

"""
from alembic import op
import sqlalchemy as sa

revision = 'a1b2c3d4e5f6'
down_revision = '60ed86c7a484'
branch_labels = None
depends_on = None


def upgrade():
    with op.batch_alter_table('editais', schema=None) as batch_op:
        batch_op.add_column(sa.Column('numero_convenio', sa.String(length=100), nullable=True))
        batch_op.add_column(sa.Column('coordenador_geral_proppg', sa.String(length=200), nullable=True))


def downgrade():
    with op.batch_alter_table('editais', schema=None) as batch_op:
        batch_op.drop_column('coordenador_geral_proppg')
        batch_op.drop_column('numero_convenio')
