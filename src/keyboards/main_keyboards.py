from aiogram.types import KeyboardButton, ReplyKeyboardMarkup, InlineKeyboardMarkup, InlineKeyboardButton

admin_panel = ReplyKeyboardMarkup(keyboard=[
    [KeyboardButton(text='*Полная админка')],
    [KeyboardButton(text="Добавить продукт")],
    [KeyboardButton(text="Удалить продукт")]
], resize_keyboard=True)

teacher_or_student = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text="Хочу учиться", callback_data="student")],
    [InlineKeyboardButton(text="Хочу преподавать", callback_data="teacher")],
])

teacher_start_menu_keyboard = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text="Предмет", callback_data="next")],
    [InlineKeyboardButton(text="Поддержка", callback_data="support")],
    [InlineKeyboardButton(text="Договор", callback_data="agreement")],
    [InlineKeyboardButton(text="О нас", callback_data="about_us")],
    [InlineKeyboardButton(text="Медиа", callback_data="media")],
    [InlineKeyboardButton(text="Хочу учиться", callback_data="student")],
    [InlineKeyboardButton(text='💵Партнерская программа', callback_data='partner')]
])

student_menu_keyboard = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text="Предметы", callback_data="subjects"),
     InlineKeyboardButton(text="Как мы учим", callback_data="how_we_teach")],
    [InlineKeyboardButton(text="Цены", callback_data="prices"),
     InlineKeyboardButton(text="Договор", callback_data="agreement")],
    [InlineKeyboardButton(text="О нас", callback_data="about_us"),
     InlineKeyboardButton(text="Вопросы", callback_data="questions")],
    [InlineKeyboardButton(text="Медиа", callback_data="media")],
    [InlineKeyboardButton(text="Поддержка", callback_data="support")],
    [InlineKeyboardButton(text="Хочу преподавать", callback_data="teacher")],
    [InlineKeyboardButton(text='💵Партнерская программа', callback_data='partner')],
    [InlineKeyboardButton(text='✨Пробный период', callback_data='trial_period')]
])

confirmed_student = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text='Поддержка', callback_data='support|confirmed_student')],
    [InlineKeyboardButton(text='Домашка', callback_data='choose_teacher_homework')],
    [InlineKeyboardButton(text='Техническая поддержка', callback_data='tech_support|student')],
    [InlineKeyboardButton(text='Мои учителя', callback_data='my_teachers')],
    [InlineKeyboardButton(text='Мой прогресс', callback_data='my_progress')],
    [InlineKeyboardButton(text='Мой Макс', callback_data='gamification')],
    [InlineKeyboardButton(text='Реферальная программа', callback_data='ref_menu')],
    [InlineKeyboardButton(text='🎁Бесплатное занятие', callback_data='student_balls_menu')]
])

confirmed_teacher = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text='Полигон', callback_data="ai_chat")],
    [InlineKeyboardButton(text="Методическая поддержка", callback_data="support|teacher")],
    [InlineKeyboardButton(text='Начисление баллов ученику', callback_data='teacher_balls_management')],
    [InlineKeyboardButton(text="Мои ученики", callback_data="my_students")],
    [InlineKeyboardButton(text="Поддержка", callback_data="support")],
    [InlineKeyboardButton(text="Добавить предмет", callback_data="next")],
    [InlineKeyboardButton(text='💵Партнерская программа', callback_data='partner')]
])