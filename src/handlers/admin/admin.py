from aiogram import Router, F
from aiogram.filters import or_f
from aiogram.filters.command import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery
from dotenv import load_dotenv
from os import getenv

from src.keyboards import admin_panel
from src.middlewares import AdminMiddleware

admin_router = Router()
admin_router.callback_query.middleware.register(AdminMiddleware())

load_dotenv()

STUDENT_GROUP_ID = int(getenv('STUDENT_GROUP_ID'))
TEACHER_GROUP_ID = int(getenv('TEACHER_GROUP_ID'))
METHODICAL_GROUP_ID = int(getenv('METHODICAL_GROUP_ID'))


@admin_router.message(or_f(F.chat.id == STUDENT_GROUP_ID, F.chat.id == TEACHER_GROUP_ID, F.chat.id == METHODICAL_GROUP_ID))
async def handle_group_message(message: Message):
    if message.reply_to_message and message.reply_to_message.from_user.id == (await message.bot.me()).id:
        original_message = message.reply_to_message.text

        user_id_line = [line for line in original_message.split('\n') if 'User id:' in line]
        if user_id_line:
            user_id = int(user_id_line[0].split('User id:')[1].strip())

            await message.bot.send_message(chat_id=user_id, text=f"<b>Ответ поддержки:</b>\n{message.text}")


@admin_router.callback_query(F.data == "admin_menu_back")
async def show_admin_panel_call(call: CallbackQuery, state: FSMContext):
    await state.clear()
    await call.message.edit_text(f"Вы попали в админ панель!", reply_markup=admin_panel)


@admin_router.message(Command('admin'))
async def show_admin_panel(message: Message, state: FSMContext):
    await state.clear()
    await message.answer(f"Вы попали в админ панель!", reply_markup=admin_panel)
