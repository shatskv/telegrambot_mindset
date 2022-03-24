"""add table tg_group, atrs for yandex_disk

Revision ID: c2c15c19c51d
Revises: e75e80308c02
Create Date: 2022-03-24 10:45:29.943333

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'c2c15c19c51d'
down_revision = 'e75e80308c02'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('tg_groups',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('tg_chat_id', sa.BIGINT(), nullable=False),
    sa.Column('lang', sa.String(length=4), nullable=True),
    sa.Column('yandex_on', sa.Boolean(), nullable=True),
    sa.Column('yandex_only_save', sa.Boolean(), nullable=True),
    sa.Column('yandex_token', sa.String(length=100), nullable=True),
    sa.PrimaryKeyConstraint('id'),
    schema='bot'
    )
    op.create_index(op.f('ix_bot_tg_groups_tg_chat_id'), 'tg_groups', ['tg_chat_id'], unique=True, schema='bot')
    op.add_column('tg_actions', sa.Column('tg_chat_id', sa.BIGINT(), nullable=True), schema='bot')
    op.create_index(op.f('ix_bot_tg_actions_tg_chat_id'), 'tg_actions', ['tg_chat_id'], unique=False, schema='bot')
    op.add_column('tg_chat_history', sa.Column('tg_chat_id', sa.BIGINT(), nullable=True), schema='bot')
    op.create_index(op.f('ix_bot_tg_chat_history_tg_chat_id'), 'tg_chat_history', ['tg_chat_id'], unique=False, schema='bot')
    op.create_index(op.f('ix_bot_tg_chat_history_tg_user_id'), 'tg_chat_history', ['tg_user_id'], unique=False, schema='bot')
    op.add_column('tg_users', sa.Column('yandex_on', sa.Boolean(), nullable=True), schema='bot')
    op.add_column('tg_users', sa.Column('yandex_only_save', sa.Boolean(), nullable=True), schema='bot')
    op.add_column('tg_users', sa.Column('yandex_token', sa.String(length=100), nullable=True), schema='bot')
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('tg_users', 'yandex_token', schema='bot')
    op.drop_column('tg_users', 'yandex_only_save', schema='bot')
    op.drop_column('tg_users', 'yandex_on', schema='bot')
    op.drop_index(op.f('ix_bot_tg_chat_history_tg_user_id'), table_name='tg_chat_history', schema='bot')
    op.drop_index(op.f('ix_bot_tg_chat_history_tg_chat_id'), table_name='tg_chat_history', schema='bot')
    op.drop_column('tg_chat_history', 'tg_chat_id', schema='bot')
    op.drop_index(op.f('ix_bot_tg_actions_tg_chat_id'), table_name='tg_actions', schema='bot')
    op.drop_column('tg_actions', 'tg_chat_id', schema='bot')
    op.drop_index(op.f('ix_bot_tg_groups_tg_chat_id'), table_name='tg_groups', schema='bot')
    op.drop_table('tg_groups', schema='bot')
    # ### end Alembic commands ###