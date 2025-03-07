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


async def choose_student_builder(datas: list[dict]) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.max_width = 1
    for data in datas:
        builder.button(text=f'{data.get("subject")}|{data.get("name")}', callback_data=f'choose_student|{data.get("user_id")}')
    builder.button(text='Назад', callback_data='teacher_main_menu')
    return builder.as_markup()


async def access_homework(student_id: int, subject: str) -> InlineKeyboardMarkup:
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text='Дать оценку', callback_data=f'access|{student_id}|{subject}')]
        ]
    )
    return keyboard


async def custom_back_builder(data: str):
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text='Назад', callback_data=data)]
        ]
    )
    return keyboard


async def teacher_management_builder() -> InlineKeyboardMarkup:
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text='Регулярность', callback_data='manage|regularity')],
            [InlineKeyboardButton(text='Активность на занятиях', callback_data='manage|activity')],
            [InlineKeyboardButton(text='Назад', callback_data='teacher_balls_management')]
        ]
    )
    return keyboard


async def activity_balls_builder(category: str) -> InlineKeyboardMarkup:
    if category == 'regularity':
        keyboard = InlineKeyboardMarkup(
            inline_keyboard=[
                [InlineKeyboardButton(text='4 недели подряд', callback_data='add_balls|100')],
                [InlineKeyboardButton(text='8 недель подряд', callback_data='add_balls|200')],
                [InlineKeyboardButton(text='12 недель подряд', callback_data='add_balls|300')],
            ]
        )
    else:
        keyboard = InlineKeyboardMarkup(
            inline_keyboard=[
                [InlineKeyboardButton(text='💪Мощь', callback_data='add_balls|10')],
                [InlineKeyboardButton(text='👍Неплохо', callback_data='add_balls|5')],
                [InlineKeyboardButton(text='👌Пойдет', callback_data='add_balls|2')],

            ]
        )
    keyboard.inline_keyboard.append([InlineKeyboardButton(text='Назад', callback_data='teacher_balls_management')])
    return keyboard


stop_chatting_teacher = InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton(text='Закрыть чат', callback_data='teacher_main_menu')]
    ]
)



