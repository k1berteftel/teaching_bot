import os
import datetime

import openpyxl
from aiogram import Router, F
from aiogram.filters import or_f, and_f, StateFilter
from aiogram.filters.command import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery, FSInputFile
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from dotenv import load_dotenv
from os import getenv

from src.utils.schedulers import student_trial_period
from src.handlers.fsm_models import MallingInput, TeachersInput, TrialManage
from src.keyboards import (admin_panel, main_admin_builder, back_admin_builder,
                           choose_role_builder, choose_teacher_builder, student_survey_builder, teachers_manage_builder,
                           teachers_menu, choose_teacher_product_builder, teacher_products_builder, candidate_result,
                           trial_management_build, back_trial_management)
from src.middlewares import AdminMiddleware
from src.database import get_all_users, get_user_data, add_partner_to_user, reset_user_products, update_user_role, add_product_to_user, get_user_products, get_partners, update_trial_period
from src.database.products import get_subject_teachers, get_all_languages, get_all_subjects, get_product_by_id, get_partner_subject


def get_table(tables: list[list]) -> str:
    """
        Возвращает путь к файлу таблицы
    """
    wb = openpyxl.Workbook()
    sheet = wb.active

    for row in range(0, len(tables)):
        for column in range(0, len(tables[row])):
            c = sheet.cell(row=row + 1, column=column + 1)
            c.value = tables[row][column]
    wb.save(f'partners.xlsx')
    return f'partners.xlsx'


admin_router = Router()

admin_router.callback_query.outer_middleware.register(AdminMiddleware())
admin_router.message.outer_middleware.register(AdminMiddleware())

load_dotenv()

STUDENT_GROUP_ID = int(getenv('STUDENT_GROUP_ID'))
TEACHER_GROUP_ID = int(getenv('TEACHER_GROUP_ID'))
METHODICAL_GROUP_ID = int(getenv('METHODICAL_GROUP_ID'))
APPLICATION_GROUP_ID = int(getenv('APPLICATION_GROUP_ID'))
TECHNICAL_GROUP_ID = int(getenv('TECHNICAL_GROUP_ID'))


@admin_router.message(or_f(F.chat.id == STUDENT_GROUP_ID, F.chat.id == TEACHER_GROUP_ID, F.chat.id == METHODICAL_GROUP_ID, F.chat.id == TECHNICAL_GROUP_ID))
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
    subject = await get_partner_subject(teacher_id, student_id)
    text = ('<b>Вам добавили нового учителя</b>, чтобы помочь ему найти индивидуальный '
            'подход к вашему обучению наш виртуальный помощник Макс просит вас '
            'пройти небольшой опрос, который поможет нам выявить цели вашего обучения, '
            'поможет составить план рекомендации и поможет придумать лично к '
            'вам индивидуальный подход обучения')
    keyboard = await student_survey_builder(teacher_id)
    await clb.bot.send_message(
        chat_id=student_id,
        text=text,
        reply_markup=keyboard
    )
    try:
        await clb.bot.send_document(
            chat_id=teacher_id,
            document=FSInputFile(path=f'{student_id}_{subject.subject}.pdf'),
            caption='Вам добавили ученика, вот его easy-анализ'
        )
    except Exception as err:
        print(err)
    await clb.message.delete()
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


@admin_router.callback_query(F.data == 'teachers_management')
async def teachers_management_menu(clb: CallbackQuery, state: FSMContext):
    await state.clear()
    await clb.message.delete()
    text = 'Выберите действия которые вы хотели бы сделать с учителями'
    keyboard = await teachers_manage_builder()
    await clb.message.answer(text, reply_markup=keyboard)


@admin_router.callback_query(F.data == 'add_teacher')
async def add_teacher_send(clb: CallbackQuery, state: FSMContext):
    await clb.message.delete()
    await state.clear()
    await state.set_state(TeachersInput.add_teacher_waiting)
    await clb.message.answer(
        text='Отправьте ID пользователя которого вы хотели бы добавить в учителей',
        reply_markup=teachers_menu
    )


@admin_router.message(and_f(F.text, StateFilter(TeachersInput.add_teacher_waiting)))
async def add_teacher_id(msg: Message, state: FSMContext):
    await msg.delete()
    try:
        teacher_id = int(msg.text)
    except Exception:
        await msg.answer('telegram ID учителя должен быть числом, пожалуйста попробуйте снова')
        return
    try:
        await msg.bot.delete_message(chat_id=msg.from_user.id, message_id=msg.message_id - 1)
    except Exception:
        ...
    user = await get_user_data(teacher_id)
    if user is None:
        await msg.answer('Такого пользователя нету в базе пользователей, пожалуйста попробуйте снова')
        return
    await state.update_data(teacher_id=teacher_id)
    await state.set_state(TeachersInput.add_teacher_product)
    keyboard = await choose_teacher_product_builder('add_teacher')
    await msg.answer('Выберите категорию которую вы хотели бы добавить учителю', reply_markup=keyboard)


@admin_router.callback_query(and_f(F.data.startswith('teacher_set'), StateFilter(TeachersInput.add_teacher_product)))
async def add_teacher_product(clb: CallbackQuery, state: FSMContext):
    await clb.message.delete()
    category = clb.data.split('|')[1]
    await state.update_data(category=category)
    if category == 'languages':
        products = await get_all_languages()
    else:
        products = await get_all_subjects()
    keyboard = await teacher_products_builder(products, 'add_teacher')
    await clb.message.answer(
        text='Выберите предмет|язык которые вы хотели бы добавить своему учителю',
        reply_markup=keyboard
    )


@admin_router.callback_query(and_f(F.data.startswith('set'), StateFilter(TeachersInput.add_teacher_product)))
async def add_teacher_subject(clb: CallbackQuery, state: FSMContext):
    await clb.message.delete()
    data = await state.get_data()
    teacher_id = data.get('teacher_id')
    product_id = int(clb.data.split('_')[1])
    user = await get_user_data(teacher_id)
    if not user.role == 'confirmed_teacher':
        await update_user_role(teacher_id, 'confirmed_teacher')
    user_products = await get_user_products(teacher_id)
    if product_id in [product.id for product in user_products]:
        await clb.message.answer('Этот учитель уже преподает данный предмет, пожалуйста выберите другой предмет')
        if data.get('category') == 'languages':
            products = await get_all_languages()
        else:
            products = await get_all_subjects()
        keyboard = await teacher_products_builder(products, 'add_teacher')
        await clb.message.answer(
            text='Выберите предмет|язык которые вы хотели бы добавить учителю',
            reply_markup=keyboard
        )
        return
    product = await get_product_by_id(product_id)
    await add_product_to_user(teacher_id, product.subject)
    await clb.message.answer('Предмет был успешно добавлен учителю')
    await clb.bot.send_message(chat_id=user.telegram_id, text=f"""
    Здравствуйте, {user.name}!   
    Рады сообщить, что вы успешно прошли отбор в нашу команду easyknow! 🎉 
    Мы видим, что ваши профессиональные навыки и подход к обучению отлично соответствуют нашему стремлению делать обучение интересным и доступным для наших учеников.     

    С уважением, Команда easyknow          
    """, reply_markup=(await candidate_result('accept')))
    await state.clear()
    text = 'Выберите действия которые вы хотели бы сделать с учителями'
    keyboard = await teachers_manage_builder()
    await clb.message.answer(text, reply_markup=keyboard)


@admin_router.callback_query(F.data == 'del_teacher')
async def send_del_teacher(clb: CallbackQuery, state: FSMContext):
    await clb.message.delete()
    await state.set_state(TeachersInput.del_teacher_waiting)
    await clb.message.answer('Отправьте ID учителя которого вы хотели бы удалить', reply_markup=teachers_menu)


@admin_router.message(and_f(F.text, StateFilter(TeachersInput.del_teacher_waiting)))
async def del_teacher(msg: Message, state: FSMContext):
    await msg.delete()
    try:
        teacher_id = int(msg.text)
    except Exception:
        await msg.answer('telegram ID учителя должен быть числом, пожалуйста попробуйте снова')
        return
    user = await get_user_data(teacher_id)
    if user is None:
        await msg.answer('Такого пользователя нету в базе пользователей, пожалуйста попробуйте снова')
        return
    await update_user_role(teacher_id, 'teacher')
    await reset_user_products(teacher_id)
    await msg.answer('Данные о пользователе были успешно обновленны')
    await state.clear()
    text = 'Выберите действия которые вы хотели бы сделать с учителями'
    keyboard = await teachers_manage_builder()
    await msg.answer(text, reply_markup=keyboard)


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


@admin_router.callback_query(F.data == 'get_partners_table')
async def get_partners_table(clb: CallbackQuery):
    partners = await get_partners()
    datas = []
    for partner in partners:
        user = await get_user_data(partner.telegram_id)
        datas.append(
            [
                '@' + user.username if user.username else '-',
                user.name,
                partner.refs,
                partner.sum,
                partner.earn
            ]
        )
    datas.insert(0, ['Юзернейм', 'Имя', 'Рефералов', 'Сумма продаж', 'Заработал'])
    table = get_table(datas)
    await clb.message.answer_document(FSInputFile(table))
    try:
        os.remove(table)
    except Exception:
        ...


@admin_router.callback_query(F.data == 'trial_period_menu')
async def trial_period_management(clb: CallbackQuery, state: FSMContext):
    await state.clear()
    await clb.message.delete()
    keyboard = await trial_management_build()
    text = 'Выберите действие'
    await clb.message.answer(
        text=text,
        reply_markup=keyboard
    )


@admin_router.callback_query(F.data.startswith('trial_student'))
async def switch_trail_action(clb: CallbackQuery, state: FSMContext):
    await state.clear()
    await clb.message.delete()
    action = clb.data.split('_')[-1]
    keyboard = back_trial_management
    if action == 'add':
        await state.set_state(TrialManage.add_student)
        text = 'Введите telegram id (User Id) пользователя, которому вы хотели бы активировать пробный период'
    else:
        await state.set_state(TrialManage.del_student)
        text = 'Введите telegram id (User Id) пользователя, которому вы хотели бы ДЕактивировать пробный период'
    await clb.message.answer(text, reply_markup=keyboard)


@admin_router.message(and_f(F.text, StateFilter(TrialManage.add_student)))
async def get_trial_student_id(msg: Message, state: FSMContext, scheduler: AsyncIOScheduler):
    await msg.delete()
    try:
        user_id = int(msg.text)
    except Exception:
        await msg.answer('Telegram id должен быть числом, пожалуйста попробуйте еще раз')
        return
    user = await get_user_data(user_id)
    if not user:
        await msg.answer('К сожалению такой пользователь не был найден, пожалуйста попробуйте еще раз')
        return
    if user.role in ['confirmed_teacher', 'confirmed_student']:
        await msg.answer('Данный пользователь уже является принятым учителем или учеников купившим пакет уроков\n'
                         'Требуется чтобы пользователь вышел из данных статусов')
        return
    if user.role == 'trial_student':
        await msg.answer('Данный пользователь уже активировал пробный период')
        return
    await state.update_data(user_id=user.telegram_id)
    keyboard = await choose_teacher_product_builder('trial_student_add')
    await msg.answer('Выберите категорию в которую вы хотели бы добавить ученика пробного периода', reply_markup=keyboard)


@admin_router.callback_query(and_f(F.data.startswith('teacher_set'), StateFilter(TrialManage.add_student)))
async def add_trial_product(clb: CallbackQuery, state: FSMContext):
    await clb.message.delete()
    category = clb.data.split('|')[1]
    await state.update_data(category=category)
    if category == 'languages':
        products = await get_all_languages()
    else:
        products = await get_all_subjects()
    keyboard = await teacher_products_builder(products, 'trial_student_add')
    await clb.message.answer(
        text='Выберите предмет|язык которые вы хотели бы поставить ученику на пробный период',
        reply_markup=keyboard
    )


@admin_router.callback_query(and_f(F.data.startswith('set'), StateFilter(TrialManage.add_student)))
async def add_trial_student(clb: CallbackQuery, state: FSMContext, scheduler: AsyncIOScheduler):
    await clb.message.delete()
    data = await state.get_data()
    user_id = data.get('user_id')
    product_id = int(clb.data.split('_')[1])
    product = await get_product_by_id(product_id)
    await add_product_to_user(user_id, product.subject)
    await update_user_role(user_id, 'trial_student')
    date = datetime.datetime.today() + datetime.timedelta(days=5)
    await update_trial_period(user_id, date)
    text = ('<b>🌟 Поздравляем! Вы успешно активировали пробный период! 🌟</b>\n\nВ течение 5 дней вы '
            'получаете полный доступ ко всему функционалу, который доступен нашим реальным ученикам. '
            'Исследуйте возможности, обучайтесь и погружайтесь в процесс так, будто вы уже часть нашей '
            'онлайн-школы!\n\n⏳ Время начать ваше путешествие прямо сейчас!')
    job = scheduler.get_job(job_id=f'trial_period_{user_id}')
    if job:
        job.remove()
    scheduler.add_job(
        student_trial_period,
        'interval',
        args=[user_id, clb.bot, scheduler],
        id=f'trial_period_{user_id}',
        days=1
    )
    await clb.bot.send_message(
        chat_id=user_id,
        text=text
    )
    await clb.message.answer('У указанного ученика был успешно активирован пробный период ')
    await state.clear()
    keyboard = await trial_management_build()
    text = 'Выберите действие'
    await clb.message.answer(
        text=text,
        reply_markup=keyboard
    )


@admin_router.message(and_f(F.text, StateFilter(TrialManage.del_student)))
async def del_trial_student(msg: Message, state: FSMContext, scheduler: AsyncIOScheduler):
    await msg.delete()
    try:
        user_id = int(msg.text)
    except Exception:
        await msg.answer('Telegram id должен быть числом, пожалуйста попробуйте еще раз')
        return
    user = await get_user_data(user_id)
    if not user:
        await msg.answer('К сожалению такой пользователь не был найден, пожалуйста попробуйте еще раз')
        return
    if user.role != 'trial_student':
        await msg.answer('Данный пользователь еще не активировал пробный период')
        return
    await update_trial_period(user_id, None)
    job = scheduler.get_job(job_id=f'trial_period_{user_id}')
    if job:
        job.remove()
    await msg.answer('У данного пользователя был успешно отключен пробный период')
    await state.clear()
    keyboard = await trial_management_build()
    text = 'Выберите действие'
    await msg.answer(
        text=text,
        reply_markup=keyboard
    )