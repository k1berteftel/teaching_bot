import datetime
import json
from os import getenv

from aiogram import Router, F, Bot
from aiogram.fsm.context import FSMContext
from aiogram.filters import StateFilter, and_f
from aiogram.types import CallbackQuery, FSInputFile, Message
from aiogram.utils.media_group import MediaGroupBuilder

from src.gpt.ask import fetch_response
from src.database import UserModel, ProductModel
from src.database.products import get_product_by_id, get_partner_subject
from src.database.user import get_user_data, get_user_products, get_user_partners
from src.keyboards import subjects, chatting_teacher_builder, confirmed_student, stop_chatting_student, stop_chatting_teacher
from src.handlers.fsm_models import PartnerChatting


student_router = Router()


@student_router.callback_query(F.data == 'back_student_menu')
async def start_student(clb: CallbackQuery, state: FSMContext):
    await state.clear()
    await clb.message.delete()
    await clb.message.answer('Вы в главном меню', reply_markup=confirmed_student)


@student_router.callback_query(F.data == 'my_teachers')
async def show_teachers_chats(clb: CallbackQuery, state: FSMContext):
    await state.clear()
    teachers = await get_user_partners(clb.from_user.id)
    if teachers is None:
        await clb.answer('К сожалению пока что у вас нет учителей, как только вам определят учителя мы вас уведомим')
        return
    await clb.message.delete()
    keyboard = await chatting_teacher_builder(teachers)
    await clb.message.answer('Выберите чат с учителем', reply_markup=keyboard)


@student_router.callback_query(F.data.startswith('chatting'))
async def start_chatting(clb: CallbackQuery, state: FSMContext):
    await clb.message.delete()
    partner_id = int(clb.data.split('|')[1])
    user = await get_user_data(partner_id)
    subject = await get_partner_subject(clb.from_user.id, partner_id)
    await state.update_data(partner=user, subject=subject)
    person = await get_user_data(clb.from_user.id)
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
        '<b>Сообщение было доставлено</b>\nВы можете отправить следующее сообщение по необходимости',
        reply_markup=stop_chatting_student
    )


