from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

back_from_support_to_interview = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text="Выйти из чата с поддержкой", callback_data="back_to_interview")]
])
exit_support = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text="Выйти из чата с поддержкой", callback_data="quit_support")]
])
