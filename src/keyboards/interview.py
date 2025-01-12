from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder


async def continue_interview(cancel):
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Продолжить", callback_data="continue_interview")],
        [InlineKeyboardButton(text="Поддержка", callback_data="support|back_to_interview")],
        [InlineKeyboardButton(text="Отменить собеседование", callback_data=f"type|{cancel}")]
    ])


async def start_interview_questions(cancel):
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Продолжить", callback_data="continue_interview")],
        [InlineKeyboardButton(text="Отменить собеседование", callback_data=f"type|{cancel}")]
    ])


categories_for_teaching = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text="Иностранные языки", callback_data="type|languages")],
    [InlineKeyboardButton(text="Школьные предметы", callback_data="type|school_subjects")],
    [InlineKeyboardButton(text="Поддержка", callback_data="support|back_to_interview|start")],
    [InlineKeyboardButton(text="Назад", callback_data="teacher_main_menu")]
])


async def categories_for_teacher_builder(categories):
    keyboard = InlineKeyboardBuilder()
    for category in categories:
        keyboard.button(text=category, callback_data=f"subject|{category}")
    keyboard.adjust(2)
    keyboard.row(InlineKeyboardButton(text="Назад", callback_data="next"))
    return keyboard.as_markup()

async def candidate_result(result):
    keyboard = InlineKeyboardBuilder()
    if result == "accept":
        keyboard.row(InlineKeyboardButton(text="Отлично!", callback_data="teacher_accepted"))
    keyboard.row(InlineKeyboardButton(text="Поддержка", callback_data="support"))
    keyboard.row(InlineKeyboardButton(text="Меню", callback_data="teacher_main_menu"))
    return keyboard.as_markup()

async def confirm_interview_agreement(teaching_type):
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="✅ Подтверждаю", callback_data="hh_ru")],
        [InlineKeyboardButton(text="Поддержка", callback_data=f"support|back_to_interview|to_agreement")],
        [InlineKeyboardButton(text="Назад", callback_data=f"type|{teaching_type}")]
    ])
    return keyboard


async def start_or_back(item):
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Начать", callback_data=f"start_interview|{item}")],
        [InlineKeyboardButton(text="Назад", callback_data=f"hh_ru")]
    ])


async def cancel_interview(cancel):
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Отменить собеседование", callback_data=f"type|{cancel}")],
        [InlineKeyboardButton(text="Поддержка", callback_data="support")]
    ])


def have_hh_ru_resume_kb(picked_subject: str):
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Есть резюме на hh.ru", callback_data="have_hh_ru_resume")],
        [InlineKeyboardButton(text="Нет резюме на hh.ru", callback_data="interview_start")],
        [InlineKeyboardButton(text="Назад", callback_data=f"subject|{picked_subject}")]
    ])

generate_questions_try_again = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text="Попробовать еще раз", callback_data="continue_interview")]
])

async def recruiter_keyboard(user_id, picked_subject):
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Берем", callback_data=f"candidate|accept|{user_id}|{picked_subject}")],
        [InlineKeyboardButton(text="Не берем", callback_data=f"candidate|decline|{user_id}|{picked_subject}")],
    ])
