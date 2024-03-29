"""DB models."""
import os

import asyncio
import enum
from datetime import datetime

from sqlalchemy import (Boolean, Column, DateTime, Integer, String, BIGINT,
                       MetaData)
from sqlalchemy.dialects.postgresql import ENUM
from sqlalchemy.ext.asyncio import (AsyncSession,
                                    create_async_engine)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.sql.schema import ForeignKey
from sqlalchemy.sql.sqltypes import DateTime
from sqlalchemy.sql import func
from config import settings

# engine = create_engine(settings.SQLALCHEMY_URI)


# engine = create_async_engine(settings.SQLALCHEMY_URI)
engine = create_async_engine(os.environ.get('SQLALCHEMY_URI'))
async_session = sessionmaker(bind=engine,  expire_on_commit=False, class_=AsyncSession)
# async_session = sessionmaker(bind=engine,  expire_on_commit=True, class_=AsyncSession)

# async_session_factory = sessionmaker(some_async_engine, class_=_AsyncSession)
# AsyncSession = async_scoped_session(async_session_factory, scopefunc=asyncio.current_task)
# async_session = AsyncSession()
metadata = MetaData(schema='bot')
Base = declarative_base(metadata=metadata)
# Base.query = async_session.query_property()


class MyEnumMeta(enum.EnumMeta):
    def __contains__(cls, item):
        return item in [v.value for v in cls.__members__.values()]


class TagFormat(enum.Enum, metaclass=MyEnumMeta):
    instagram = 'instagram'
    list_tags = 'list'


class Action(enum.Enum, metaclass=MyEnumMeta):
    desc_tags = 'iu_decs_and_tags'
    desc = 'iu_decs'
    tags = 'iu_tags'


class TgUser(Base):
    __tablename__ = 'tg_users'
    id = Column(Integer, primary_key=True)
    tg_user_id = Column(Integer, nullable=False, index=True, unique=True)
    user_id = Column(Integer, index=True)
    tg_user_name = Column(String(255))
    first_name = Column(String(255))
    last_name = Column(String(255))
    lang = Column(String(4), default='en')
    tags_format = Column(ENUM(TagFormat), default=TagFormat.instagram)
    rating = Column(Boolean, default=True)
    free_act = Column(Integer())
    create_at = Column(DateTime(timezone=False), default=func.now())
    bot_feedback = Column(String(10000))
    is_banned = Column(Boolean, default=False)

    def __repr__(self):
        return f'<Telegram_user {self.id}>'


class TgAction(Base):
    __tablename__ = 'tg_actions'
    id = Column(Integer, primary_key=True)
    tg_user_id = Column(Integer, ForeignKey(TgUser.tg_user_id, ondelete='CASCADE'))
    action_type = Column(ENUM(Action))
    image_uuid = Column(String(50), index=True)
    image_name = Column(String)
    lang = Column(String(4))
    image_type = Column(String())
    image_size = Column(Integer)
    create_at = Column(DateTime(timezone=False), default=func.now())
    responce = Column(String(20000))

    def __repr__(self):
        return f'<Telegram_user_action {self.telegram_user_id} {self.action}>'


class TgChatHistory(Base):
    __tablename__ = 'tg_chat_history'
    id = Column(Integer, primary_key=True)
    tg_msg_id = Column(Integer)
    tg_user_id = Column(Integer, ForeignKey(TgUser.tg_user_id, ondelete='CASCADE'))
    user_msg = Column(String(10000))
    bot_msg = Column(String(10000))
    bot_message_edit = Column(Boolean, default=False)
    create_at = Column(DateTime(timezone=False), default=func.now())


class CallbackQuery(Base):
    __tablename__ = 'RatingQuery'
    message_id = Column(Integer, primary_key=True, index=True)
    image_uuid = Column(String(50))


async def async_create():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)


if __name__ == '__main__':
    asyncio.run(async_create())
