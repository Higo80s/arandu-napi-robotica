"""v10.8: Identity and Security

Revision ID: d3a152950630
Revises: b68bf3ee60ee
Create Date: 2026-03-12 11:12:22.363848

"""
from alembic import op
import sqlalchemy as sa
import encryption

# revision identifiers, used by Alembic.
revision = 'd3a152950630'
down_revision = 'b68bf3ee60ee'
branch_labels = None
depends_on = None


def upgrade():
    # V10.8: Identidade Academica e Seguranca
    # Simplificado: apenas mudancas essenciais sem truncamento de dados

    # 1. Remover FK antes de dropar tabela agencias_fomento
    try:
        with op.batch_alter_table('editais', schema=None) as batch_op:
            batch_op.drop_constraint('editais_agencia_id_fkey', type_='foreignkey')
            batch_op.drop_column('agencia_id')
    except Exception:
        pass  # FK pode nao existir no banco atual

    # 2. Dropar tabelas legadas (idempotente)
    for table in ['bolsa_volumetria_anual', 'bolsa_historico', 'agencias_fomento',
                  'distribuicao_cotas', 'dados_financeiros', 'projetos_pesquisa']:
        try:
            op.drop_table(table)
        except Exception:
            pass

    # 3. Adicionar campo matricula (identidade institucional)
    with op.batch_alter_table('bolsistas', schema=None) as batch_op:
        batch_op.add_column(sa.Column('matricula', sa.String(length=20), nullable=True))
        batch_op.create_index('ix_bolsistas_matricula', ['matricula'], unique=False)

    # 4. Criar tabela de Mementos/Snapshots
    op.create_table(
        'database_mementos',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('timestamp', sa.DateTime(), nullable=False),
        sa.Column('contexto', sa.String(length=255), nullable=False),
        sa.Column('snapshot_data', sa.JSON(), nullable=False),
        sa.Column('total_registros', sa.Integer(), nullable=True),
        sa.Column('checksum', sa.String(length=64), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_database_mementos_timestamp', 'database_mementos', ['timestamp'], unique=False)


def downgrade():
    op.drop_index('ix_database_mementos_timestamp', table_name='database_mementos')
    op.drop_table('database_mementos')

    with op.batch_alter_table('bolsistas', schema=None) as batch_op:
        batch_op.drop_index('ix_bolsistas_matricula')
        batch_op.drop_column('matricula')
