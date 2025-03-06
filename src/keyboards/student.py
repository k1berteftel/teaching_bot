from aiogram.types import KeyboardButton, ReplyKeyboardMarkup, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder, ReplyKeyboardBuilder


async def chatting_teacher_builder(datas: list[dict]) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    for data in datas:
        builder.button(text=f'{data.get("subject")}|{data.get("name")}', callback_data=f'chatting|{data.get("user_id")}')
    builder.button(text='Назад', callback_data='back_student_menu')
    return builder.as_markup()


async def homework_teacher_builder(datas: list[dict]) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.max_width = 1
    for data in datas:
        builder.button(text=f'{data.get("subject")}|{data.get("name")}', callback_data=f'homework|{data.get("user_id")}')
    builder.button(text='Назад', callback_data='back_student_menu')
    return builder.as_markup()


async def student_subjects_builder(subjects: list[str]):
    builder = InlineKeyboardBuilder()
    builder.max_width = 1
    for subject in subjects:
        builder.button(text=subject, callback_data=f'progress|{subject}')
    builder.button(text='Назад', callback_data='back_student_menu')
    return builder.as_markup()


async def student_survey_builder(teacher_id: int) -> InlineKeyboardMarkup:
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text='Начать опрос', callback_data=f'survey|{teacher_id}|')]
        ]
    )
    return keyboard


async def ref_menu_builder(user_id: int) -> InlineKeyboardMarkup:
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text='🌐Поделиться',
                                  url=f'http://t.me/share/url?url=https://t.me/easyknow_bot?start={user_id}')],
            [InlineKeyboardButton(text='Назад', callback_data='back_student_menu')]
        ]
    )
    return keyboard


async def balls_menu_builder() -> InlineKeyboardMarkup:
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text='Обменять баллы на занятие', callback_data='buy_student_lesson')],
            [InlineKeyboardButton(text='Назад', callback_data='back_student_menu')]
        ]
    )
    return keyboard


confirm_buy_keyboard = InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton(text='Обменять', callback_data='confirm_buy_lessons')],
        [InlineKeyboardButton(text='Назад', callback_data='back_student_menu')]
    ]
)


back_balls_menu = InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton(text='Назад', callback_data='back_student_menu')]
    ]
)


back_survey = InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton(text='Назад', callback_data='back_survey_question')]
    ]
)



stop_Maks = InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton(text='Закончить диалог', callback_data='back_student_menu')]
    ]
)


stop_send_homework = InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton(text='Назад', callback_data='back_student_menu')]
    ]
)


stop_chatting_student = InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton(text='Закрыть чат', callback_data='back_student_menu')]
    ]
)
