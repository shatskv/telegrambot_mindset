"""base_migration

Revision ID: e75e80308c02
Revises: 
Create Date: 2022-03-17 07:35:36.404773

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = 'e75e80308c02'
down_revision = None
branch_labels = None
depends_on = None

tag_options = ('instagram', 'list_tags')
tagformat = postgresql.ENUM(*tag_options, name='tagformat', create_type=False, schema='bot')
act_options = ('desc_tags', 'desc', 'tags')
action = postgresql.ENUM(*act_options, name='action', create_type=False, schema='bot')


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    tagformat.create(op.get_bind())
    action.create(op.get_bind())
    op.create_table('rating_query',
    sa.Column('message_id', sa.Integer(), nullable=False),
    sa.Column('image_uuid', sa.String(length=50), nullable=True),
    sa.PrimaryKeyConstraint('message_id'),
    schema='bot'
    )
    op.create_index(op.f('ix_bot_rating_query_message_id'), 'rating_query', ['message_id'], unique=False, schema='bot')
    op.create_table('tg_users',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('tg_user_id', sa.Integer(), nullable=False),
    sa.Column('user_id', sa.Integer(), nullable=True),
    sa.Column('tg_user_name', sa.String(length=255), nullable=True),
    sa.Column('first_name', sa.String(length=255), nullable=True),
    sa.Column('last_name', sa.String(length=255), nullable=True),
    sa.Column('lang', sa.String(length=4), nullable=True),
    sa.Column('tags_format', tagformat, nullable=True),
    sa.Column('rating', sa.Boolean(), nullable=True),
    sa.Column('free_act', sa.Integer(), nullable=True),
    sa.Column('create_at', sa.DateTime(), nullable=True),
    sa.Column('bot_feedback', sa.String(length=10000), nullable=True),
    sa.Column('is_banned', sa.Boolean(), nullable=True),
    sa.PrimaryKeyConstraint('id'),
    schema='bot'
    )
    op.create_index(op.f('ix_bot_tg_users_tg_user_id'), 'tg_users', ['tg_user_id'], unique=True, schema='bot')
    op.create_index(op.f('ix_bot_tg_users_user_id'), 'tg_users', ['user_id'], unique=False, schema='bot')
    op.create_table('tg_actions',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('tg_user_id', sa.Integer(), nullable=True),
    sa.Column('action_type', action, nullable=True),
    sa.Column('image_uuid', sa.String(length=50), nullable=True),
    sa.Column('image_name', sa.String(), nullable=True),
    sa.Column('lang', sa.String(length=4), nullable=True),
    sa.Column('image_type', sa.String(), nullable=True),
    sa.Column('image_size', sa.Integer(), nullable=True),
    sa.Column('create_at', sa.DateTime(), nullable=True),
    sa.Column('responce', sa.String(length=20000), nullable=True),
    sa.ForeignKeyConstraint(['tg_user_id'], ['bot.tg_users.tg_user_id'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id'),
    schema='bot'
    )
    op.create_index(op.f('ix_bot_tg_actions_image_uuid'), 'tg_actions', ['image_uuid'], unique=False, schema='bot')
    op.create_table('tg_chat_history',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('tg_msg_id', sa.Integer(), nullable=True),
    sa.Column('tg_user_id', sa.Integer(), nullable=True),
    sa.Column('user_msg', sa.String(length=10000), nullable=True),
    sa.Column('bot_msg', sa.String(length=10000), nullable=True),
    sa.Column('bot_message_edit', sa.Boolean(), nullable=True),
    sa.Column('create_at', sa.DateTime(), nullable=True),
    sa.ForeignKeyConstraint(['tg_user_id'], ['bot.tg_users.tg_user_id'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id'),
    schema='bot'
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('tg_chat_history', schema='bot')
    op.drop_index(op.f('ix_bot_tg_actions_image_uuid'), table_name='tg_actions', schema='bot')
    op.drop_table('tg_actions', schema='bot')
    op.drop_index(op.f('ix_bot_tg_users_user_id'), table_name='tg_users', schema='bot')
    op.drop_index(op.f('ix_bot_tg_users_tg_user_id'), table_name='tg_users', schema='bot')
    op.drop_table('tg_users', schema='bot')
    op.drop_index(op.f('ix_bot_rating_query_message_id'), table_name='rating_query', schema='bot')
    op.drop_table('rating_query', schema='bot')
    tagformat.drop(op.get_bind())
    action.drop(op.get_bind())
    # ### end Alembic commands ###
