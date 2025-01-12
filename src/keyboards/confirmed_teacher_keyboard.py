from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

confirmed_teacher_agreement_keyboard = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text="Ознакомился(ась)", callback_data="teacher_main_menu")],
    [InlineKeyboardButton(text="Поддержка", callback_data="support")],
])

