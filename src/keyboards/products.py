from aiogram.types import KeyboardButton, ReplyKeyboardMarkup, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder, ReplyKeyboardBuilder

subjects = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text="Языки", callback_data="languages")],
    [InlineKeyboardButton(text="Школьные предметы", callback_data="school_subjects")],
    [InlineKeyboardButton(text="В меню", callback_data="student_main_menu")]
])


async def language_categories_builder(categories_list):
    builder = InlineKeyboardBuilder()
    builder.max_width = 1
    for category in categories_list:
        builder.button(text=category, callback_data=f"language|{category}")
    builder.row(InlineKeyboardButton(text="Назад", callback_data="subjects"))
    return builder.as_markup()


async def product_actions_keyboard(product_type, category):
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Выбрать", callback_data="buy_product")],
        [InlineKeyboardButton(text="Назад",
                              callback_data=f"school_subject|{category}" if product_type == "subject" else f"language|{category}")]
    ])


async def products_builder(subjects_list):
    builder = InlineKeyboardBuilder()
    for subject in subjects_list:
        builder.button(text=subject.name, callback_data=f"product|{subject.id}")
    builder.row(InlineKeyboardButton(text="Назад",
                                     callback_data="school_subjects" if subjects_list[0].product_type == "subject" else "languages"))
    return builder.as_markup()


async def subject_categories_builder(categories_list):
    builder = InlineKeyboardBuilder()
    builder.max_width = 1
    for category in categories_list:
        builder.button(text=category, callback_data=f"school_subject|{category}")
    builder.row(InlineKeyboardButton(text="Назад", callback_data="subjects"))
    return builder.as_markup()


async def categories_builder(categories):
    keyboard = ReplyKeyboardBuilder()
    for category in categories:
        keyboard.button(text=category)
    return keyboard.as_markup(resize_keyboard=True, one_time_keyboard=True)


product_or_language = ReplyKeyboardMarkup(keyboard=[
    [KeyboardButton(text="Язык")],
    [KeyboardButton(text="Предмет")]
], resize_keyboard=True, one_time_keyboard=True)

confirm_product_creation = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text="Создать", callback_data="create")],
    [InlineKeyboardButton(text="Отменить", callback_data="admin_menu_back")]
])


async def training_type_builder(data):
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text='Индивидуальные', callback_data='training_type|individual')],
            [InlineKeyboardButton(text='Групповые', callback_data='training_type|group')],
            [InlineKeyboardButton(text='Назад', callback_data=data)],
            [InlineKeyboardButton(text='Поддержка', callback_data='help')]
        ]
    )
    return keyboard


async def choose_lessons_builder(data):
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text='Квиз', callback_data='quiz')],
            [InlineKeyboardButton(text='Поддержка', callback_data='help')],
            [InlineKeyboardButton(text='Назад', callback_data=data)],
            [InlineKeyboardButton(text="Главное меню", callback_data="student_main_menu")]
        ]
    )
    return keyboard


async def confirm_contract_builder(data):
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text='✅Подтверждаю', callback_data='confirm_contract')],
            [InlineKeyboardButton(text='Поддержка', callback_data='help')],
            [InlineKeyboardButton(text='Назад', callback_data=data)]
        ]
    )
    return keyboard


async def user_name_builder():
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text='Поддержка', callback_data='help')],
            [InlineKeyboardButton(text='Назад', callback_data='back_get_user_name')]
        ]
    )
    return keyboard


promo_close_keyboard = InlineKeyboardMarkup(
    inline_keyboard=[[InlineKeyboardButton(text='Пропустить', callback_data='back_get_user_name')]]
)


async def contract_builder():
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text='Ознакомился (-ась)', callback_data='confirm')],
            [InlineKeyboardButton(text='Назад', callback_data='confirm_contract')]
        ]
    )
    return keyboard


async def custom_poll_builder(data):
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text='Назад', callback_data=data)]
        ]
    )
    return keyboard


async def close_quiz_builder(data):
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text='Назад', callback_data=data)]
        ]
    )
    return keyboard


async def payment_builder(url: str):
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text='Оплатить', url=url)],
            [InlineKeyboardButton(text='Оплатил', callback_data='check_payment')],
            [InlineKeyboardButton(text='Назад', callback_data='back_product')]
        ]
    )
    return keyboard
