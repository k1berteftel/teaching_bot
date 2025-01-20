from aiogram.types import KeyboardButton, ReplyKeyboardMarkup, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder, ReplyKeyboardBuilder


async def chatting_teacher_builder(datas: list[dict]) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    for data in datas:
        builder.button(text=f'{data.get("subject")}|{data.get("name")}', callback_data=f'chatting|{data.get("user_id")}')
    builder.button(text='Назад', callback_data='back_student_menu')
    return builder.as_markup()


stop_chatting_student = InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton(text='Закрыть чат', callback_data='back_student_menu')]
    ]
)
