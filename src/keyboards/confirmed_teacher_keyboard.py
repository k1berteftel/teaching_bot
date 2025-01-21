from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder

confirmed_teacher_agreement_keyboard = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text="Ознакомился(ась)", callback_data="teacher_main_menu")],
    [InlineKeyboardButton(text="Поддержка", callback_data="support")],
])


async def chatting_student_builder(datas: list[dict]) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.max_width = 1
    for data in datas:
        builder.button(text=f'{data.get("subject")}|{data.get("name")}', callback_data=f'chatting|{data.get("user_id")}')
    builder.button(text='Назад', callback_data='teacher_main_menu')
    return builder.as_markup()


async def access_homework(student_id: int, subject: str) -> InlineKeyboardMarkup:
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text='Дать оценку', callback_data=f'access|{student_id}|{subject}')]
        ]
    )
    return keyboard


stop_chatting_teacher = InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton(text='Закрыть чат', callback_data='teacher_main_menu')]
    ]
)



