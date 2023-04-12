from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

from keyboards.inline.callback_datas import stat_callback

choice = InlineKeyboardMarkup(
    inline_keyboard=[
        [
            InlineKeyboardButton(text='Все сообщения', callback_data=stat_callback.new(
                type='all_message'
            ))
        ],
        [
            InlineKeyboardButton(text='Голосовые', callback_data=stat_callback.new(
                type='voice'
            ))
        ],
        [
            InlineKeyboardButton(text='Кружочки', callback_data=stat_callback.new(
                type='video_note'
            ))
        ],
        [
            InlineKeyboardButton(text='Скрыть', callback_data='hide')
        ]
    ]
)