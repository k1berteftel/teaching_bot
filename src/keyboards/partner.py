from aiogram.types import KeyboardButton, ReplyKeyboardMarkup, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder


async def partner_menu_builder(user_id: int, data: str) -> InlineKeyboardMarkup:
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text='🌐Поделиться реф-ссылкой', url=f'http://t.me/share/url?url=https://t.me/easyknow_bot?start=partner-{user_id}')],
            [InlineKeyboardButton(text='Назад', callback_data=data)]
        ]
    )
    return keyboard
