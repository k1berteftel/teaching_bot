from aiogram import Router, F
from aiogram.filters import or_f, and_f, StateFilter
from aiogram.filters.command import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery
from dotenv import load_dotenv
from os import getenv

from src.handlers.fsm_models import MallingInput
from src.keyboards import admin_panel, main_admin_builder, back_admin_builder, choose_role_builder, choose_teacher_builder
from src.middlewares import AdminMiddleware
from src.database import get_all_users, get_user_data, add_partner_to_user
from src.database.products import get_subject_teachers

admin_router = Router()

admin_router.callback_query.outer_middleware.register(AdminMiddleware())
admin_router.message.outer_middleware.register(AdminMiddleware())

load_dotenv()

STUDENT_GROUP_ID = int(getenv('STUDENT_GROUP_ID'))
TEACHER_GROUP_ID = int(getenv('TEACHER_GROUP_ID'))
METHODICAL_GROUP_ID = int(getenv('METHODICAL_GROUP_ID'))
APPLICATION_GROUP_ID = int(getenv('APPLICATION_GROUP_ID'))


@admin_router.message(or_f(F.chat.id == STUDENT_GROUP_ID, F.chat.id == TEACHER_GROUP_ID, F.chat.id == METHODICAL_GROUP_ID))
async def handle_group_message(message: Message):
    if message.reply_to_message and message.reply_to_message.from_user.id == (await message.bot.me()).id:
        original_message = message.reply_to_message.text

        user_id_line = [line for line in original_message.split('\n') if 'User id:' in line]
        if user_id_line:
            user_id = int(user_id_line[0].split('User id:')[1].strip())

            await message.bot.send_message(chat_id=user_id, text=f"<b>Ответ поддержки:</b>\n{message.text}")


@admin_router.callback_query(F.data.startswith('refresh_teachers'))
async def refresh_teachers_keyboard(clb: CallbackQuery, state: FSMContext):
    category = clb.data.split('|')[1]
    student_id = int(clb.data.split('|')[2])
    teachers = await get_subject_teachers(category)
    keyboard = await choose_teacher_builder(teachers, student_id, category)
    await clb.message.edit_reply_markup(reply_markup=keyboard)


@admin_router.callback_query(and_f(F.data.startswith('teacher_add')))
async def add_user_teacher(clb: CallbackQuery, state: FSMContext):
    print('success')
    teacher_id = int(clb.data.split('|')[1])
    student_id = int(clb.data.split('|')[2])
    await add_partner_to_user(student_id, teacher_id)
    await add_partner_to_user(teacher_id, student_id)
    await clb.answer('Учитель был успешно добавлен ученику')


@admin_router.callback_query(F.data == "admin_menu_back")
async def show_admin_panel_call(call: CallbackQuery, state: FSMContext):
    await state.clear()
    await call.message.edit_text(f"Вы попали в админ панель!", reply_markup=admin_panel)


@admin_router.message(Command('admin'))
async def show_admin_panel(message: Message, state: FSMContext):
    await state.clear()
    await message.answer(f"Вы попали в админ панель!", reply_markup=admin_panel)


@admin_router.message(F.text == '*Полная админка')
async def show_full_admin_panel(message: Message, state: FSMContext):
    await message.delete()
    await state.clear()
    keyboard = await main_admin_builder()
    await message.answer(
        text='Полная админ панель',
        reply_markup=keyboard
    )


@admin_router.callback_query(F.data == 'admin_panel')
async def show_full_admin_panel(clb: CallbackQuery, state: FSMContext):
    await clb.message.delete()
    await state.clear()
    keyboard = await main_admin_builder()
    await clb.message.answer(
        text='Полная админ панель',
        reply_markup=keyboard
    )


@admin_router.callback_query(F.data == 'malling')
async def send_choose_role(clb: CallbackQuery, state: FSMContext):
    await clb.message.delete()
    keyboard = await choose_role_builder()
    await clb.message.answer(
        text='Выберите группу пользователей которым вы хотели бы разослать сообщение',
        reply_markup=keyboard
    )


@admin_router.callback_query(F.data.startswith('choose_role|'))
async def send_get_mail(clb: CallbackQuery, state: FSMContext):
    await clb.message.delete()
    await state.update_data(role=clb.data.split('|')[1])
    await state.set_state(MallingInput.waiting_for_message)
    keyboard = await back_admin_builder()
    await clb.message.answer(
        text='Отправьте сообщение которое вы хотели бы разослать всем пользователям, '
             'после получения сообщения оно сразу же разошлется всем пользователям',
        reply_markup=keyboard
    )


@admin_router.message(and_f(F.text, StateFilter(MallingInput.waiting_for_message)))
async def start_malling(message: Message, state: FSMContext):
    data = await state.get_data()
    role = data.get('role')
    users = await get_all_users()
    count = 0
    if role == 'everyone':
        for user in users:
            try:
                await message.send_copy(
                    chat_id=user.telegram_id
                )
                count += 1
            except Exception as err:
                print(err)
    else:
        for user in users:
            if user.role == role:
                try:
                    await message.send_copy(
                        chat_id=user.telegram_id
                    )
                    count += 1
                except Exception as err:
                    print(err)
    await message.delete()
    await message.answer(f'Сообщение было разослано {count} пользователям')
    await state.clear()
    keyboard = await main_admin_builder()
    await message.answer(
        text='Полная админ панель',
        reply_markup=keyboard
    )


@admin_router.callback_query(F.data == 'statistic')
async def get_statistics(clb: CallbackQuery):
    users = await get_all_users()
    roles = {}
    for user in users:
        if user.role:
            if roles.get(user.role):
                roles[user.role] = roles.get(user.role) + 1
            else:
                roles[user.role] = 1
    text = (f'Всего пользователей: {len(users)}\nИз них:\n - Учителей: {roles.get("teacher") if roles.get("teacher") else 0}\n'
            f' - Принятых учителей (прошедших собеседование): {roles.get("confirmed_teacher") if roles.get("confirmed_teacher") else 0}\n'
            f' - Учеников: {roles.get("student") if roles.get("student") else 0}\n - Принятых учеников(купивших курсы): {roles.get("confirmed_student") if roles.get("confirmed_student") else 0}')
    await clb.message.answer(text)
