import datetime
import json
from os import getenv

from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from aiogram.filters import StateFilter, and_f
from aiogram.types import CallbackQuery, Message
from src.database.user import get_user_balls, add_user_balls
from src.keyboards import (balls_menu_builder, confirm_buy_keyboard,
                           custom_poll_builder, back_balls_menu)
from src.handlers.fsm_models import BallsExchange

APPLICATION_GROUP_ID = int(getenv('APPLICATION_GROUP_ID'))
student_balls_router = Router()


@student_balls_router.callback_query(F.data == 'student_balls_menu')
async def student_balls_menu(clb: CallbackQuery, state: FSMContext):
    await state.clear()
    await clb.message.delete()
    referral = await get_user_balls(clb.from_user.id)
    text = (f'<b>Текущий баланс</b>: {referral.balls} баллов\nВы можете зарабатывать баллы чтобы <b>обменивать '
            'их на бесплатные уроки</b>. Чтобы зарабатывать баллы надо:\n - 1. Проявлять активность на занятиях\n'
            ' - 2. Выполнять домашние задания и прокачивать уровень вашего персонажа\n - 3. Быть '
            'регулярным, не пропускать занятия\n - 4. Приглашать друзей, чтобы прокачиваться и получать '
            'больше баллов вместе\nВы можете обменять 1000 баллов на 1 бесплатное занятие по кнопки снизу')
    keyboard = await balls_menu_builder()
    await clb.message.answer(text, reply_markup=keyboard)


@student_balls_router.callback_query(F.data == 'buy_student_lesson')
async def buy_bulls(clb: CallbackQuery, state: FSMContext):
    referral = await get_user_balls(clb.from_user.id)
    if referral.balls < 1000:
        await clb.answer('У вас пока недостаточно баллов, чтобы обменять их на бесплатный урок')
        return
    await clb.message.delete()
    text = ('Для оформления заявки на оказание образовательных услуг, пожалуйста, заполните следующие '
            'данные. Сначала укажите свои данные как Заказчика, затем информацию о Получателе услуг. '
            'Например, ваш ребенок. Если вы являетесь Получателем услуг, продублируйте свои данные во '
            'второй части заявки\n\nВведите ваше полное имя (ФИО)')
    keyboard = back_balls_menu
    await state.set_state(BallsExchange.waiting_for_name)
    await clb.message.answer(text=text, reply_markup=keyboard)


@student_balls_router.message(and_f(F.text, StateFilter(BallsExchange.waiting_for_name)))
async def get_name(msg: Message, state: FSMContext):
    await msg.delete()
    try:
        await msg.bot.delete_message(chat_id=msg.from_user.id, message_id=msg.message_id - 1)
    except Exception:
        ...
    await state.update_data(name=msg.text)
    keyboard = await custom_poll_builder('back_get_name')
    await state.set_state(BallsExchange.waiting_for_mail)
    await msg.answer('Введите вашу почту', reply_markup=keyboard)


@student_balls_router.callback_query(and_f(F.data == 'back_get_name', StateFilter(BallsExchange.waiting_for_mail)))
async def back_get_name(clb: CallbackQuery, state: FSMContext):
    await clb.message.delete()
    text = 'Введите ваше полное имя (ФИО)'
    keyboard = back_balls_menu
    await state.set_state(BallsExchange.waiting_for_name)
    await clb.message.answer(text=text, reply_markup=keyboard)


@student_balls_router.message(and_f(F.text, StateFilter(BallsExchange.waiting_for_mail)))
async def get_mail(msg: Message, state: FSMContext):
    await msg.delete()
    try:
        await msg.bot.delete_message(chat_id=msg.from_user.id, message_id=msg.message_id - 1)
    except Exception:
        ...
    await state.update_data(mail=msg.text)
    await state.set_state(BallsExchange.confirm)
    keyboard = confirm_buy_keyboard
    await msg.answer(
        text='Вы уверены что вы хотите обменять 1000 баллов на бесплатный урок?',
        reply_markup=keyboard
    )


@student_balls_router.callback_query(and_f(F.data == 'confirm_buy_lessons', StateFilter(BallsExchange.confirm)))
async def balls_exchange(clb: CallbackQuery, state: FSMContext):
    await add_user_balls(clb.from_user.id, -1000)
    await clb.message.delete()
    data = await state.get_data()
    # partners = await get_user_partners(clb.from_user.id)
    text = (
        f'Ученик произвел обмен баллов на одно бесплатное занятие\nВот данные для заявки:\n - Имя: {data.get("name")}'
        f'\n - Почта: {data.get("mail")}\n - USER ID: {clb.from_user.id}')
    await clb.bot.send_message(
        chat_id=APPLICATION_GROUP_ID,
        text=text
    )
    await clb.message.answer('Ваша заявка на получение бесплатного урока была успешно отправлена')
    #  ____
    await state.clear()
    referral = await get_user_balls(clb.from_user.id)
    text = (f'<b>Текущий баланс</b>: {referral.balls} баллов\nВы можете зарабатывать баллы чтобы <b>обменивать '
            'их на бесплатные уроки</b>. Чтобы зарабатывать баллы надо:\n - 1. Проявлять активность на занятиях\n'
            ' - 2. Выполнять домашние задания и прокачивать уровень вашего персонажа\n - 3. Быть '
            'регулярным, не пропускать занятия\n - 4. Приглашать друзей, чтобы прокачиваться и получать '
            'больше баллов вместе')
    keyboard = await balls_menu_builder()
    await clb.message.answer(text, reply_markup=keyboard)
