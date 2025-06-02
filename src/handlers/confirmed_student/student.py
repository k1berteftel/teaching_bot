import datetime
import json
from os import getenv

from aiogram import Router, F, Bot
from aiogram.fsm.context import FSMContext
from aiogram.filters import StateFilter, and_f
from aiogram.types import CallbackQuery, FSInputFile, Message
from aiogram.utils.media_group import MediaGroupBuilder

from src.gpt.ask import fetch_response, get_assistant_and_thread, get_text_answer, delete_assistant_and_thread
from src.database import UserModel, ProductModel
from src.database.products import get_product_by_id, get_partner_subject, get_product_by_subject
from src.database.rating import get_rating, get_subject_rating
from src.database.user import get_user_data, get_user_products, get_user_partners, get_user_balls
from src.keyboards import (subjects, chatting_teacher_builder, confirmed_student,
                           stop_chatting_student, stop_chatting_teacher, student_subjects_builder,
                           stop_send_homework, stop_Maks, ref_menu_builder, chatting_max_builder)
from src.handlers.fsm_models import PartnerChatting, AiMaks

next_level_balls = {
    1: 70,
    2: 200,
    3: 400,
    4: 650,
    5: 950,
    6: 1300,
    7: 1700,
    8: 2150,
    9: 2650,
    10: 3200,
    11: 3800,
    12: 4450,
    13: 5150,
    14: 5900,
    15: 'max'
}


level_name = {
    1: 'Новичок Макс',
    2: 'Учёный ученик Макс',
    3: 'Исследователь Макс',
    4: 'Знаток Макс',
    5: 'Покоритель знаний Макс',
    6: 'Интеллектуал Макс',
    7: 'Мастер-наставник Макс',
    8: 'Гений Макс',
    9: 'Мудрец Макс',
    10: 'Ментор Макс',
    11: 'Мудрец-стратег Макс',
    12: 'Архитектор знаний Макс',
    13: 'Магистр Макс',
    14: 'Великий Макс',
    15: 'Легенда Макс'
}


student_router = Router()


@student_router.callback_query(F.data == 'back_student_menu')
async def start_student(clb: CallbackQuery, state: FSMContext):
    await state.clear()
    await clb.message.delete()
    await clb.message.answer('Вы в главном меню', reply_markup=confirmed_student)


@student_router.callback_query(F.data == 'my_teachers')
async def show_teachers_chats(clb: CallbackQuery, state: FSMContext):
    await state.clear()
    user = await get_user_data(clb.from_user.id)
    if user.role == 'confirmed_student':
        teachers = await get_user_partners(clb.from_user.id)
        if teachers is None:
            await clb.answer('К сожалению пока что у вас нет учителей, как только вам определят учителя мы вас уведомим')
            return
        await clb.message.delete()
        keyboard = await chatting_teacher_builder(teachers)
    else:
        products = await get_user_products(clb.from_user.id)
        keyboard = await chatting_max_builder(products)
    await clb.message.answer('Выберите чат с учителем', reply_markup=keyboard)


@student_router.callback_query(F.data.startswith('chatting'))
async def start_chatting(clb: CallbackQuery, state: FSMContext):
    await clb.message.delete()
    person = await get_user_data(clb.from_user.id)
    if person.role == 'trial_student':
        subject = await get_product_by_subject(clb.data.split('|')[1])
        await state.update_data(subject=subject)
        await state.set_state(PartnerChatting.student)
        await clb.message.answer('Отправьте сообщение своему учителю', reply_markup=stop_chatting_student)
        return
    partner_id = int(clb.data.split('|')[1])
    user = await get_user_data(partner_id)
    subject = await get_partner_subject(clb.from_user.id, partner_id)
    await state.update_data(partner=user, subject=subject)
    if person.role == 'confirmed_student':
        await state.set_state(PartnerChatting.student)
        await clb.message.answer('Отправьте сообщение своему учителю', reply_markup=stop_chatting_student)
    else:
        await state.set_state(PartnerChatting.teacher)
        await clb.message.answer('Отправьте сообщение своему ученику', reply_markup=stop_chatting_teacher)


@student_router.message(StateFilter(PartnerChatting.student))
async def send_message_to_teacher(message: Message, state: FSMContext):
    data = await state.get_data()
    user = await get_user_data(message.from_user.id)
    if user.role == 'confirmed_student':
        partner: UserModel = data.get('partner')
        subject: ProductModel = data.get('subject')
        await message.bot.send_message(
            chat_id=partner.telegram_id,
            text=f'Сообщение от ученика <b>{user.name}</b>, по предмету: <b>{subject.subject}</b>'
        )
        await message.bot.copy_message(
            chat_id=partner.telegram_id,
            from_chat_id=message.chat.id,
            message_id=message.message_id
        )
        try:
            await message.bot.edit_message_reply_markup(chat_id=message.from_user.id, message_id=message.message_id - 1)
        except Exception:  # рассчитать приблизительное расстояние для редактирования клавиатуры
            ...
        await message.answer(
            '<b>Сообщение было успешно доставлено</b>\nВы можете отправить следующее сообщение по необходимости',
            reply_markup=stop_chatting_student
        )
    else:
        subject: ProductModel = data.get('subject')
        assistant_id, thread_id = data.get('assistant_id'), data.get('thread_id')
        if not assistant_id or not thread_id:
            assistant_id, thread_id = await get_assistant_and_thread()
            await state.update_data(assistant_id=assistant_id, thread_id=thread_id)
        answer = await get_text_answer(message.text if message.text else message.caption, assistant_id, thread_id)
        if not answer:
            await message.answer('Произошла какая-то ошибка, пожалуйста попробуйте снова или обратитесь в тех.поддержку')
            return
        await message.answer(text=f'Сообщение от учителя <b>Макс</b>, по предмету: <b>{subject.subject}</b>')
        await message.answer(answer)


@student_router.callback_query(F.data == 'my_progress')
async def choose_my_progress_subject(clb: CallbackQuery, state: FSMContext):
    await clb.message.delete()
    subjects = await get_user_products(clb.from_user.id)
    keyboard = await student_subjects_builder([subject.subject for subject in subjects])
    await clb.message.answer('Выберите предмет по которому вы хотели бы просмотреть свой прогресс', reply_markup=keyboard)


@student_router.callback_query(F.data.startswith('progress'))
async def show_my_progress(clb: CallbackQuery, state: FSMContext):
    subject = await get_product_by_subject(clb.data.split('|')[1])
    rating = await get_rating(clb.from_user.id, subject.subject)
    if rating is None:
        await clb.message.answer('Пока что у вас нету прогресса по этому предмету')
        return
    await clb.message.delete()
    all_rating = await get_subject_rating(subject.subject)
    all_rating = all_rating[::-1]
    placed = 0
    for place in range(0, len(all_rating)):
        if all_rating[place].telegram_id == rating.telegram_id:
            placed = place
            break
    average_ball = 0
    for homework in rating.homeworks:
        average_ball += homework.balls
    average_ball = round(average_ball / len(rating.homeworks), 2)
    text = (f'<b>Ваш прогресс:</b>\n\n - Персонаж: Макс\n - Предмет: {subject.subject}\n'
            f' - Уровень: {rating.level}, "{level_name[rating.level]}"'
            f'\n - Баллов до следующего уровня: {rating.balls}/{next_level_balls[rating.level]}\n'
            f' - Ваш рейтинг среди других учеников: {placed + 1}\n\n<b>Домашние работы</b>\n'
            f' - Средний балл: {average_ball}')
    await clb.message.answer(text, reply_markup=stop_send_homework)


@student_router.callback_query(F.data == 'gamification')
async def send_start_Maks(clb: CallbackQuery, state: FSMContext):
    await clb.message.delete()
    assistant_id, thread_id = await get_assistant_and_thread()
    await state.update_data(assistant_id=assistant_id, thread_id=thread_id)
    await state.set_state(AiMaks.chatting)
    await clb.message.answer(text='Привет, Я Макс, твой виртуальный помощник по выполнению домашнего задания, '
                                  'задавай любые вопросы, чего ты не понял, с чем тебе помочь и какие проблемы у '
                                  'тебя возникли по ходу выполнения домашнего задания?', reply_markup=stop_Maks)


@student_router.message(and_f(F.text, StateFilter(AiMaks.chatting)))
async def answer_gpt(msg: Message, state: FSMContext):
    try:
        await msg.bot.edit_message_reply_markup(chat_id=msg.from_user.id, message_id=msg.message_id - 1)
    except Exception:
        ...
    data = await state.get_data()
    assistant_id = data.get('assistant_id')
    thread_id = data.get('thread_id')
    answer = await get_text_answer(msg.text, assistant_id, thread_id)
    if answer is None:
        await msg.answer('Ой, ой, что-то пошло не так, пожалуйста попробуйте еще раз или обратитесь в поддержку')
        return
    await msg.answer(answer, reply_markup=stop_Maks)


@student_router.message(StateFilter(AiMaks.chatting))
async def text_warning_answer(msg: Message, state: FSMContext):
    try:
        await msg.bot.edit_message_reply_markup(chat_id=msg.from_user.id, message_id=msg.message_id - 1)
    except Exception:
        ...
    text = 'Пишите пожалуйста только текстовые сообщения, Макс еще не достаточно умный чтобы обрабатывать файлы и фотки'
    await msg.answer(text, reply_markup=stop_Maks)


@student_router.callback_query(F.data == 'ref_menu')
async def open_ref_menu(clb: CallbackQuery, state: FSMContext):
    await clb.message.delete()
    referral = await get_user_balls(clb.from_user.id)
    ref_link = f'https://t.me/easyknow_bot?start={clb.from_user.id}'
    text = (f'<b>👥Реферальная программа</b>\nПриглашайте друзей и получайте баллы чтобы '
            f'потом обменять их на бесплатные занятия\n<b>Приглашенных друзей</b>: {referral.refs}'
            f'\n<b>Ссылка для друзей</b>:\n<code>{ref_link}</code>')
    keyboard = await ref_menu_builder(clb.from_user.id)
    await clb.message.answer(text, reply_markup=keyboard)
