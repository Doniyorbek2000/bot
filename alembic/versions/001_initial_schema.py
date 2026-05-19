"""Initial schema

Revision ID: 001
Revises: 
Create Date: 2024-01-01 00:00:00.000000

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa

revision: str = '001'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # regions
    op.create_table('regions',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('viloyat', sa.String(100), nullable=False),
        sa.Column('tuman', sa.String(100), nullable=False),
        sa.Column('latitude', sa.Float(), nullable=True),
        sa.Column('longitude', sa.Float(), nullable=True),
        sa.Column('timezone', sa.String(50), nullable=False, server_default='Asia/Tashkent'),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=False),
        sa.Column('updated_at', sa.DateTime(), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('viloyat', 'tuman', name='uq_region_viloyat_tuman')
    )

    # users
    op.create_table('users',
        sa.Column('id', sa.BigInteger(), nullable=False),
        sa.Column('telegram_id', sa.BigInteger(), nullable=False),
        sa.Column('username', sa.String(100), nullable=True),
        sa.Column('full_name', sa.String(200), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default='1'),
        sa.Column('is_blocked', sa.Boolean(), nullable=False, server_default='0'),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=False),
        sa.Column('updated_at', sa.DateTime(), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('telegram_id')
    )
    op.create_index('ix_users_telegram_id', 'users', ['telegram_id'])

    # groups
    op.create_table('groups',
        sa.Column('id', sa.BigInteger(), nullable=False),
        sa.Column('telegram_id', sa.BigInteger(), nullable=False),
        sa.Column('title', sa.String(255), nullable=False),
        sa.Column('username', sa.String(100), nullable=True),
        sa.Column('chat_type', sa.String(20), nullable=False, server_default='group'),
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default='1'),
        sa.Column('is_blocked', sa.Boolean(), nullable=False, server_default='0'),
        sa.Column('region_id', sa.Integer(), nullable=True),
        sa.Column('added_by', sa.BigInteger(), nullable=True),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=False),
        sa.Column('updated_at', sa.DateTime(), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=False),
        sa.ForeignKeyConstraint(['region_id'], ['regions.id'], ondelete='SET NULL'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('telegram_id')
    )
    op.create_index('ix_groups_telegram_id', 'groups', ['telegram_id'])

    # group_settings
    op.create_table('group_settings',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('group_id', sa.BigInteger(), nullable=False),
        sa.Column('weather_enabled', sa.Boolean(), nullable=False, server_default='0'),
        sa.Column('prayer_enabled', sa.Boolean(), nullable=False, server_default='0'),
        sa.Column('news_enabled', sa.Boolean(), nullable=False, server_default='0'),
        sa.Column('jobs_enabled', sa.Boolean(), nullable=False, server_default='0'),
        sa.Column('ai_enabled', sa.Boolean(), nullable=False, server_default='0'),
        sa.Column('subscription_enabled', sa.Boolean(), nullable=False, server_default='0'),
        sa.Column('invite_enabled', sa.Boolean(), nullable=False, server_default='0'),
        sa.Column('moderation_enabled', sa.Boolean(), nullable=False, server_default='0'),
        sa.Column('news_topics', sa.Text(), nullable=True),
        sa.Column('ban_penalty', sa.String(20), nullable=False, server_default='warn'),
        sa.Column('invite_threshold', sa.Integer(), nullable=False, server_default='3'),
        sa.Column('language', sa.String(10), nullable=False, server_default='uz'),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=False),
        sa.Column('updated_at', sa.DateTime(), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=False),
        sa.ForeignKeyConstraint(['group_id'], ['groups.telegram_id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('group_id')
    )

    # weather_schedules
    op.create_table('weather_schedules',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('group_id', sa.BigInteger(), nullable=False),
        sa.Column('schedule_time', sa.String(5), nullable=False),
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default='1'),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=False),
        sa.Column('updated_at', sa.DateTime(), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=False),
        sa.ForeignKeyConstraint(['group_id'], ['groups.telegram_id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )

    # prayer_schedules
    op.create_table('prayer_schedules',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('group_id', sa.BigInteger(), nullable=False),
        sa.Column('schedule_time', sa.String(5), nullable=False),
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default='1'),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=False),
        sa.Column('updated_at', sa.DateTime(), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=False),
        sa.ForeignKeyConstraint(['group_id'], ['groups.telegram_id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )

    # news_sources
    op.create_table('news_sources',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(100), nullable=False),
        sa.Column('url', sa.String(500), nullable=False),
        sa.Column('source_type', sa.String(20), nullable=False, server_default='rss'),
        sa.Column('topic', sa.String(50), nullable=False, server_default='local'),
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default='1'),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=False),
        sa.Column('updated_at', sa.DateTime(), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('url')
    )

    # job_sources
    op.create_table('job_sources',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(100), nullable=False),
        sa.Column('url', sa.String(500), nullable=False),
        sa.Column('source_type', sa.String(20), nullable=False, server_default='rss'),
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default='1'),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=False),
        sa.Column('updated_at', sa.DateTime(), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('url')
    )

    # sent_posts
    op.create_table('sent_posts',
        sa.Column('id', sa.BigInteger(), nullable=False),
        sa.Column('group_id', sa.BigInteger(), nullable=False),
        sa.Column('post_type', sa.String(20), nullable=False),
        sa.Column('content_hash', sa.String(64), nullable=False),
        sa.Column('source_url', sa.String(500), nullable=True),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_sent_posts_group_hash', 'sent_posts', ['group_id', 'content_hash'])

    # required_channels
    op.create_table('required_channels',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('group_id', sa.BigInteger(), nullable=False),
        sa.Column('channel_id', sa.BigInteger(), nullable=False),
        sa.Column('channel_username', sa.String(100), nullable=True),
        sa.Column('channel_title', sa.String(255), nullable=True),
        sa.Column('invite_link', sa.String(500), nullable=True),
        sa.Column('is_global', sa.Boolean(), nullable=False, server_default='0'),
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default='1'),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=False),
        sa.Column('updated_at', sa.DateTime(), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=False),
        sa.ForeignKeyConstraint(['group_id'], ['groups.telegram_id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )

    # user_subscriptions
    op.create_table('user_subscriptions',
        sa.Column('id', sa.BigInteger(), nullable=False),
        sa.Column('user_id', sa.BigInteger(), nullable=False),
        sa.Column('group_id', sa.BigInteger(), nullable=False),
        sa.Column('is_subscribed', sa.Boolean(), nullable=False, server_default='0'),
        sa.Column('checked_at', sa.DateTime(), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=False),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=False),
        sa.Column('updated_at', sa.DateTime(), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('user_id', 'group_id', name='uq_user_group_subscription')
    )

    # invite_tracking
    op.create_table('invite_tracking',
        sa.Column('id', sa.BigInteger(), nullable=False),
        sa.Column('inviter_id', sa.BigInteger(), nullable=False),
        sa.Column('invited_id', sa.BigInteger(), nullable=False),
        sa.Column('group_id', sa.BigInteger(), nullable=False),
        sa.Column('is_valid', sa.Boolean(), nullable=False, server_default='1'),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('inviter_id', 'invited_id', 'group_id', name='uq_invite_tracking')
    )
    op.create_index('ix_invite_tracking_inviter_group', 'invite_tracking', ['inviter_id', 'group_id'])

    # banned_words
    op.create_table('banned_words',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('group_id', sa.BigInteger(), nullable=False),
        sa.Column('word', sa.String(200), nullable=False),
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default='1'),
        sa.Column('added_by', sa.BigInteger(), nullable=True),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=False),
        sa.Column('updated_at', sa.DateTime(), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=False),
        sa.ForeignKeyConstraint(['group_id'], ['groups.telegram_id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('group_id', 'word', name='uq_banned_word_group')
    )

    # warnings
    op.create_table('warnings',
        sa.Column('id', sa.BigInteger(), nullable=False),
        sa.Column('user_id', sa.BigInteger(), nullable=False),
        sa.Column('group_id', sa.BigInteger(), nullable=False),
        sa.Column('reason', sa.String(500), nullable=True),
        sa.Column('warned_by', sa.BigInteger(), nullable=True),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_warnings_user_group', 'warnings', ['user_id', 'group_id'])

    # ai_logs
    op.create_table('ai_logs',
        sa.Column('id', sa.BigInteger(), nullable=False),
        sa.Column('user_id', sa.BigInteger(), nullable=True),
        sa.Column('group_id', sa.BigInteger(), nullable=True),
        sa.Column('input_hash', sa.String(64), nullable=True),
        sa.Column('response_hash', sa.String(64), nullable=True),
        sa.Column('input_text', sa.Text(), nullable=True),
        sa.Column('response_text', sa.Text(), nullable=True),
        sa.Column('status', sa.String(20), nullable=False, server_default='success'),
        sa.Column('error_message', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )

    # admin_logs
    op.create_table('admin_logs',
        sa.Column('id', sa.BigInteger(), nullable=False),
        sa.Column('admin_id', sa.BigInteger(), nullable=True),
        sa.Column('group_id', sa.BigInteger(), nullable=True),
        sa.Column('action', sa.String(100), nullable=False),
        sa.Column('details', sa.Text(), nullable=True),
        sa.Column('level', sa.String(20), nullable=False, server_default='info'),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_admin_logs_level', 'admin_logs', ['level'])
    op.create_index('ix_admin_logs_created_at', 'admin_logs', ['created_at'])

    # global_settings
    op.create_table('global_settings',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('key', sa.String(100), nullable=False),
        sa.Column('value', sa.Text(), nullable=True),
        sa.Column('description', sa.String(500), nullable=True),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=False),
        sa.Column('updated_at', sa.DateTime(), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('key')
    )

    # scheduled_posts
    op.create_table('scheduled_posts',
        sa.Column('id', sa.BigInteger(), nullable=False),
        sa.Column('group_id', sa.BigInteger(), nullable=False),
        sa.Column('content', sa.Text(), nullable=False),
        sa.Column('media_url', sa.String(500), nullable=True),
        sa.Column('scheduled_at', sa.DateTime(), nullable=False),
        sa.Column('is_sent', sa.Boolean(), nullable=False, server_default='0'),
        sa.Column('sent_at', sa.DateTime(), nullable=True),
        sa.Column('created_by', sa.BigInteger(), nullable=True),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=False),
        sa.Column('updated_at', sa.DateTime(), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=False),
        sa.ForeignKeyConstraint(['group_id'], ['groups.telegram_id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )

    # Insert default regions (Uzbekistan)
    op.execute("""
    INSERT INTO regions (viloyat, tuman, latitude, longitude) VALUES
    ('Toshkent shahri', 'Yunusobod', 41.2995, 69.2401),
    ('Toshkent shahri', 'Chilonzor', 41.2646, 69.1993),
    ('Toshkent shahri', 'Mirzo Ulug''bek', 41.3111, 69.3272),
    ('Toshkent shahri', 'Shayxontohur', 41.3123, 69.2401),
    ('Toshkent shahri', 'Yakkasaroy', 41.2879, 69.2401),
    ('Toshkent shahri', 'Olmazor', 41.3290, 69.2401),
    ('Toshkent shahri', 'Uchtepa', 41.2879, 69.1993),
    ('Toshkent shahri', 'Bektemir', 41.2646, 69.3272),
    ('Toshkent viloyati', 'Angren', 41.0167, 70.1500),
    ('Toshkent viloyati', 'Chirchiq', 41.4667, 69.5833),
    ('Toshkent viloyati', 'Olmaliq', 40.8500, 69.6000),
    ('Toshkent viloyati', 'Bekobod', 40.2167, 69.2167),
    ('Samarqand viloyati', 'Samarqand shahri', 39.6542, 66.9597),
    ('Samarqand viloyati', 'Kattaqo''rg''on', 39.9000, 66.2667),
    ('Buxoro viloyati', 'Buxoro shahri', 39.7747, 64.4286),
    ('Buxoro viloyati', 'Kogon', 39.7167, 64.5500),
    ('Namangan viloyati', 'Namangan shahri', 41.0011, 71.6722),
    ('Namangan viloyati', 'Chust', 40.9833, 71.2333),
    ('Namangan viloyati', 'Pop', 40.8667, 71.1000),
    ('Farg''ona viloyati', 'Farg''ona shahri', 40.3842, 71.7843),
    ('Farg''ona viloyati', 'Marg''ilon', 40.4667, 71.7167),
    ('Farg''ona viloyati', 'Qo''qon', 40.5286, 70.9422),
    ('Andijon viloyati', 'Andijon shahri', 40.7821, 72.3442),
    ('Andijon viloyati', 'Asaka', 40.6333, 72.2333),
    ('Qashqadaryo viloyati', 'Qarshi shahri', 38.8600, 65.7900),
    ('Qashqadaryo viloyati', 'Shahrisabz', 39.0583, 66.8333),
    ('Surxondaryo viloyati', 'Termiz shahri', 37.2242, 67.2783),
    ('Surxondaryo viloyati', 'Denov', 38.2667, 67.8833),
    ('Xorazm viloyati', 'Urganch shahri', 41.5500, 60.6333),
    ('Xorazm viloyati', 'Xiva', 41.3783, 60.3619),
    ('Navoiy viloyati', 'Navoiy shahri', 40.0842, 65.3792),
    ('Navoiy viloyati', 'Zarafshon', 41.5667, 64.2000),
    ('Jizzax viloyati', 'Jizzax shahri', 40.1158, 67.8422),
    ('Sirdaryo viloyati', 'Guliston shahri', 40.4897, 68.7842),
    ('Qoraqalpog''iston', 'Nukus shahri', 42.4600, 59.6100),
    ('Qoraqalpog''iston', 'Mo''ynoq', 43.7667, 59.0167)
    """)

    # Insert default news sources
    op.execute("""
    INSERT INTO news_sources (name, url, source_type, topic) VALUES
    ('Kun.uz', 'https://kun.uz/rss', 'rss', 'local'),
    ('Gazeta.uz', 'https://www.gazeta.uz/rss/uz/', 'rss', 'local'),
    ('Daryo.uz', 'https://daryo.uz/feed/', 'rss', 'local'),
    ('Sport.uz', 'https://sport.uz/rss', 'rss', 'sport'),
    ('Xabar.uz', 'https://xabar.uz/rss', 'rss', 'government')
    """)

    # Insert default job sources
    op.execute("""
    INSERT INTO job_sources (name, url, source_type) VALUES
    ('HH.uz', 'https://hh.uz/search/vacancy/rss?area=97&text=', 'rss'),
    ('Ishbor.uz', 'https://ishbor.uz/rss', 'rss')
    """)


def downgrade() -> None:
    op.drop_table('scheduled_posts')
    op.drop_table('global_settings')
    op.drop_table('admin_logs')
    op.drop_table('ai_logs')
    op.drop_table('warnings')
    op.drop_table('banned_words')
    op.drop_table('invite_tracking')
    op.drop_table('user_subscriptions')
    op.drop_table('required_channels')
    op.drop_table('sent_posts')
    op.drop_table('job_sources')
    op.drop_table('news_sources')
    op.drop_table('prayer_schedules')
    op.drop_table('weather_schedules')
    op.drop_table('group_settings')
    op.drop_table('groups')
    op.drop_table('users')
    op.drop_table('regions')
