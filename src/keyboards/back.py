from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

student_menu_back = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text="В меню", callback_data="student_main_menu")]
])

teacher_menu_back = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text="В меню", callback_data="teacher_main_menu")]
])


back_to_resume = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text="Назад", callback_data="hh_ru")]
])

quit_ai_chat = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text="Выйти из полигона", callback_data="exit_ai_chat")]
])