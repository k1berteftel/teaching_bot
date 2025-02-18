from aiogram.types import KeyboardButton, ReplyKeyboardMarkup, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder, ReplyKeyboardBuilder
from src.database import UserModel, ProductModel


async def main_admin_builder() -> InlineKeyboardMarkup:
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text='Сделать рассылку', callback_data='malling')],
            [InlineKeyboardButton(text='Получить статистику', callback_data='statistic')],
            [InlineKeyboardButton(text='Управление учителями', callback_data='teachers_management')],
        ]
    )
    return keyboard


async def teachers_manage_builder() -> InlineKeyboardMarkup:
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text='Добавить учителя', callback_data='add_teacher')],
            [InlineKeyboardButton(text='Удалить учителя', callback_data='del_teacher')],
            [InlineKeyboardButton(text='Назад', callback_data='admin_panel')]
        ]
    )
    return keyboard


async def choose_teacher_product_builder() -> InlineKeyboardMarkup:
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text='Языки', callback_data='teacher_set|languages')],
            [InlineKeyboardButton(text='Предметы', callback_data='teacher_set|school_subjects')],
            [InlineKeyboardButton(text='Назад', callback_data='add_teacher')]
        ]
    )
    return keyboard


async def teacher_products_builder(subjects: list[ProductModel]):
    builder = InlineKeyboardBuilder()
    builder.max_width = 2
    for subject in subjects:
        builder.button(text=subject.subject, callback_data=f'set_{subject.id}')
    builder.button(text='Назад', callback_data='add_teacher')
    return builder.as_markup()


async def back_admin_builder() -> InlineKeyboardMarkup:
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text='Назад', callback_data='admin_panel')]
        ]
    )
    return keyboard


teachers_menu = InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton(text='Назад', callback_data='teachers_management')]
    ]
)


async def choose_teacher_builder(teachers: list[UserModel], student_id: int, category: str) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.max_width = 1
    for teacher in teachers:
        builder.button(text=f"{teacher.name}|{teacher.username}", callback_data=f'teacher_add|{teacher.telegram_id}|{student_id}')
    builder.button(text='Обновить список учителей', callback_data=f'refresh_teachers|{category}|{student_id}')
    return builder.as_markup()


async def choose_role_builder() -> InlineKeyboardMarkup:
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text='Всем пользователям', callback_data='choose_role|everyone')],
            [InlineKeyboardButton(text='Учителям', callback_data='choose_role|teacher')],
            [InlineKeyboardButton(text='Принятым учителям', callback_data='choose_role|confirmed_teacher')],
            [InlineKeyboardButton(text='Ученикам ', callback_data='choose_role|student')],
            [InlineKeyboardButton(text='Принятым ученикам', callback_data='choose_role|confirmed_student')],
            [InlineKeyboardButton(text='Назад', callback_data='admin_panel')]
        ]
    )
    return keyboard