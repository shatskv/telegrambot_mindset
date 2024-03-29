"""Bot's handlers."""
import logging
import os

from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

from bot_init import _, bot, dp

from db import TagFormat

from queiries import (get_or_create_user_in_db, update_user, add_rating_query,
                      get_uuid_from_db_query)
from config import settings

from utils import (async_get_desc, async_set_rating, form_file_path_url,
                   silentremove)


class ImageDlg(StatesGroup):
    """States for image dialog."""

    rating = State()


class ChangeTags(StatesGroup):
    """States for change format dialog."""

    choose = State()


class ChangeLang(StatesGroup):
    """States for change lang dialog."""

    choose = State()


class ChangeRateSet(StatesGroup):
    """States for change rating setting dialog."""

    choose = State()


class Feedback(StatesGroup):
    """States for feedback dialog."""

    leave = State()


def get_tag_name(key):
    tags_format_dict = {'list': _('list'),
                        'instagram': _('instagram')}
    return tags_format_dict.get(key)


# inline_btn_desc_ru = InlineKeyboardButton('Описание и теги на русском', callback_data='desc_ru')
# inline_btn_desc_en = InlineKeyboardButton('Description and tags on english', callback_data='desc_en')
# inline_kb_desc = InlineKeyboardMarkup().add(inline_btn_desc_ru)
# inline_kb_desc.add(inline_btn_desc_en)

inline_btn_rat_1 = InlineKeyboardButton('1', callback_data='rat_1')
inline_btn_rat_2 = InlineKeyboardButton('2', callback_data='rat_2')
inline_btn_rat_3 = InlineKeyboardButton('3', callback_data='rat_3')
inline_btn_rat_4 = InlineKeyboardButton('4', callback_data='rat_4')
inline_btn_rat_5 = InlineKeyboardButton('5', callback_data='rat_5')
inline_kb_rat = InlineKeyboardMarkup().row(inline_btn_rat_1, inline_btn_rat_2, inline_btn_rat_3,
                                           inline_btn_rat_4, inline_btn_rat_5)


inline_btn_lang_ru = InlineKeyboardButton('Русский', callback_data='lang_ru')
inline_btn_lang_en = InlineKeyboardButton('English', callback_data='lang_en')
inline_kb_langs = InlineKeyboardMarkup().add(inline_btn_lang_ru)
inline_kb_langs.add(inline_btn_lang_en)


def get_tag_kb():
    inline_btn_tag1 = InlineKeyboardButton(_('#tag1 #tag2 #tag3'), callback_data='tags_instagram')
    inline_btn_tag2 = InlineKeyboardButton(_('tag1, tag2, tag3'), callback_data='tags_list_tags')
    inline_kb_tags = InlineKeyboardMarkup().add(inline_btn_tag1)
    inline_kb_tags.add(inline_btn_tag2)
    return inline_kb_tags


def get_rate_kb():
    inline_btn_rate_1 = InlineKeyboardButton(_('On'), callback_data='rating_1')
    inline_btn_rate_0 = InlineKeyboardButton(_('Off'), callback_data='rating_0')
    inline_kb_rating = InlineKeyboardMarkup().row(inline_btn_rate_0, inline_btn_rate_1)
    return inline_kb_rating


@dp.callback_query_handler(lambda c: c.data and c.data.startswith('rating'), state='*')
async def process_callback_rating(callback_query: types.CallbackQuery, state: FSMContext):
    await bot.answer_callback_query(callback_query.id)
    rating = callback_query.data[-1:]
    await get_or_create_user_in_db(callback_query)
    rating = bool(int(rating))
    await update_user(callback_query, rating=rating)
    if rating:
        rating = _('on')
    else:
        rating = _('off')
    await state.finish()
    await bot.edit_message_text(chat_id=callback_query.from_user.id,
                                message_id=callback_query.message.message_id,
                                text=_('Rating was turned {state}').format(state=rating))


@dp.callback_query_handler(lambda c: c.data and c.data.startswith('lang'), state='*')
async def process_callback_rating(callback_query: types.CallbackQuery, state: FSMContext):
    await bot.answer_callback_query(callback_query.id)
    new_lang = callback_query.data[-2:]
    await update_user(callback_query, lang=new_lang)
    await state.reset_state(with_data=False)
    await bot.edit_message_text(chat_id=callback_query.from_user.id,
                                message_id=callback_query.message.message_id,
                                text=_('Language was changed to English!', locale=new_lang))


@dp.callback_query_handler(lambda c: c.data and c.data.startswith('tags'), state='*')
async def process_callback_rating(callback_query: types.CallbackQuery, state: FSMContext):
    await bot.answer_callback_query(callback_query.id)
    tags_fmt = callback_query.data[5:]
    tags_format = getattr(TagFormat, tags_fmt)
    await update_user(callback_query, tags_format=tags_format)
    await state.reset_state(with_data=False)
    tag_format = get_tag_name(tags_format.value)
    await bot.edit_message_text(chat_id=callback_query.from_user.id,
                                message_id=callback_query.message.message_id,
                                text=_('Tags format was changed to {fmt}').format(fmt=tag_format))


@dp.callback_query_handler(lambda c: c.data and c.data.startswith('rat_'), state='*')
async def process_callback_rating(callback_query: types.CallbackQuery, state: FSMContext):
    await bot.answer_callback_query(callback_query.id)
    rating = int(callback_query.data[-1])
    call_msg_id = callback_query.message.message_id
    async with state.proxy() as data:
        uuid = data.get('uuid')
        msg_id = data.get('msg_id')
    if msg_id == call_msg_id:
        await state.reset_data()
        if not uuid:
            uuid = await get_uuid_from_db_query(msg_id=msg_id)
    else:
        uuid = await get_uuid_from_db_query(msg_id=call_msg_id)
    if uuid:
        await async_set_rating(uuid=uuid, rating=rating)
    else:
        logging.error('No uuid for rating!')

    await bot.edit_message_text(chat_id=callback_query.from_user.id,
                                message_id=call_msg_id,
                                text=_('Thank you for rating!'))


@dp.message_handler(lambda message: 'image/' in message.document.mime_type, content_types='document', state='*')
@dp.message_handler(lambda message: message.text and message.text.lower().startswith('http'), state='*')
@dp.message_handler(content_types=['photo'], state='*')
async def get_desc_and_tags_image(message: types.Message, state: FSMContext):
    await state.reset_state(with_data=False)
    user = await get_or_create_user_in_db(message)
    filename, is_url = await form_file_path_url(message)

    answer, uuid = await async_get_desc(path_url=filename,
                                        lang=user.lang,
                                        tags_format=user.tags_format.value,
                                        url_method=is_url)
    # async with state.proxy() as data:
    #     data['uuid'] = uuid
    await state.update_data(uuid=uuid)

    del_path = os.path.join('downloads', str(message.from_user.id))
    silentremove(del_path)
    for item in answer:
        last_msg = await message.answer(item)
    if user.rating:
        msg_id = last_msg.message_id + 1
        await state.update_data(msg_id=msg_id)
        await add_rating_query(msg_id=msg_id, uuid=uuid)
        await message.reply(_('Please, rate the result!'), reply_markup=inline_kb_rat)


@dp.message_handler(commands='rating', state='*')
async def rating_off(message: types.Message, state: FSMContext):
    rating = message.get_args()
    await state.reset_state(with_data=False)

    if not rating:
        # await ChangeRateSet.choose.set()
        await message.answer(_('Choose rating setting:'), reply_markup=get_rate_kb())
        return
    rating = rating.lower()
    if rating in ['1', '0', 'on', 'off']:
        if rating in ['1', 'on']:
            rating = True
        else:
            rating = False
        await update_user(message, rating=rating)
        if rating:
            rating = _('on')
        else:
            rating = _('off')
        await message.answer(_('Rating was turned {}').format(rating))
    else:
        await message.answer(_('Wrong format! Should be /rating + 1/0/on/off'))


@dp.message_handler(commands='lang', state='*')
async def change_lang(message: types.Message, state: FSMContext):
    new_lang = message.get_args()
    await state.reset_state(with_data=False)

    if not new_lang:
        # await ChangeLang.choose.set()
        await message.answer(_('Choose your language:'), reply_markup=inline_kb_langs)
        return
    if new_lang in settings.langs:
        await update_user(message, lang=new_lang)
        await message.answer(_('Language was change to English!', locale=new_lang))
    else:
        await message.answer(_('Language not supported or wrong format!'))


@dp.message_handler(commands='tags', state='*')
async def tags_format(message: types.Message, state: FSMContext):
    tags_fmt = message.get_args()
    await state.reset_state(with_data=False)

    if not tags_fmt:
        # await ChangeTags.choose.set()
        await message.answer(_('Choose tags format:'), reply_markup=get_tag_kb())
        return
    tags_fmt = tags_fmt.lower()
    if tags_fmt in TagFormat:
        if tags_fmt == 'list':
            tags_fmt += '_tags'
        tags_fmt = getattr(TagFormat, tags_fmt)
        await update_user(message, tags_format=tags_fmt.name)
        tag_value = get_tag_name(tags_fmt.value)
        await message.answer(_('Tags format was changed to {tag_value}').format(tag_value=tag_value))
    else:
        await message.answer(_('Wrong tags format!'))


@dp.message_handler(commands=['start', 'help'], state='*')
async def send_welcome(message: types.Message):
    await get_or_create_user_in_db(message)
    langs = ', '.join(settings.langs)
    text = _('<b>Picpack Bot</b>\n'
             'Bot generates description and list of tags for any image. Just send a picture\n'
             'Also it supports link to picture\n'
             'Visite ower site: http://app.picpack.io/demo_en\n'
             'Chat with owner: @FrankShikhaliev\n'
             'Below is a list of available commands, also they could have arguments (in brackets):\n'
             '/lang - change language ({})\n'
             '/tags - change format tags (list, instagram)\n'
             '/rating - rate result on/off (1, 0, on, off)\n'
             '/feedback - leave feedback about our bot').format(langs)
    await message.answer(text)


async def check_edit_keyboard_message(msg: types.Message, state: FSMContext):
    current_state = await state.get_state()
    if current_state:
        async with state.proxy() as data:
            if data.get('inline'):
                await bot.edit_message_text(chat_id=msg.from_user.id,
                                            message_id=msg.message_id-1,
                                            text=_('No action selected!'),
                                            reply_markup=None)
    await state.finish()


@dp.message_handler(lambda message: message.text, state=Feedback.leave)
async def update_feedback(message: types.Message, state: FSMContext):
    await update_user(message, bot_feedback=message.text)
    await state.finish()
    await message.answer(_('Thank you for feedback!'))


@dp.message_handler(commands='feedback', state='*')
async def leave_feedback(message: types.Message, state: FSMContext):
    await get_or_create_user_in_db(message)
    await Feedback.leave.set()
    await message.answer(_('Please, leave feedback:'))

@dp.message_handler(lambda message: 'video/' in message.document.mime_type, content_types='document', state='*')
@dp.message_handler(content_types=['video'], state='*')
async def video_unsupport(message: types.Message, state: FSMContext):
    await state.reset_state(with_data=False)
    await message.answer(_("Sorry, bot doesn't support videos!"))


@dp.message_handler(content_types='document', state='*')
async def video_unsupport(message: types.Message, state: FSMContext):
    await state.reset_state(with_data=False)
    await message.answer(_("Sorry, bot doesn't support this file format!"))


@dp.message_handler(content_types=['text'], state='*')
async def echo(message: types.Message, state):
    await get_or_create_user_in_db(message)
    await message.answer(_("Don't understand you!"))
