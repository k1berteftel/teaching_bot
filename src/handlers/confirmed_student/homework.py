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
from src.keyboards import subjects, homework_teacher_builder, confirmed_student, stop_send_homework, access_homework
from src.handlers.fsm_models import Homework


homework_router = Router()


@homework_router.callback_query(F.data == 'choose_teacher_homework')
async def send_choose_teacher(clb: CallbackQuery, state: FSMContext):
    await state.clear()
    teachers = await get_user_partners(clb.from_user.id)
    if teachers is None:
        await clb.answer('К сожалению пока что у вас нет учителей, как только вам определят учителя мы вас уведомим')
        return
    await clb.message.delete()
    keyboard = await homework_teacher_builder(teachers)
    await clb.message.answer('Выберите учителя которому вы хотели бы отослать домашнее задание', reply_markup=keyboard)


@homework_router.callback_query(F.data.startswith('homework'))
async def choose_teacher_homework(clb: CallbackQuery, state: FSMContext):
    await clb.message.delete()
    teacher_id = int(clb.data.split('|')[1])
    user = await get_user_data(teacher_id)
    subject = await get_partner_subject(clb.from_user.id, teacher_id)
    await state.update_data(partner=user, subject=subject)
    await state.set_state(Homework.send)
    await clb.message.answer('Отправьте домашнее задание своему учителю', reply_markup=stop_send_homework)


@homework_router.message(StateFilter(Homework.send))
async def send_homework(message: Message, state: FSMContext):
    data = await state.get_data()
    user = await get_user_data(message.from_user.id)
    partner: UserModel = data.get('partner')
    subject: ProductModel = data.get('subject')
    keyboard = await access_homework(message.from_user.id, subject.subject)
    await message.bot.send_message(
        chat_id=partner.telegram_id,
        text=f'Вам пришло домашнее задание от ученика <b>{user.name}</b> по предмету: <b>{subject.subject}</b>',
        reply_markup=keyboard
    )
    await message.bot.copy_message(
        chat_id=partner.telegram_id,
        from_chat_id=message.chat.id,
        message_id=message.message_id
    )
    try:
        await message.bot.edit_message_reply_markup(chat_id=message.from_user.id, message_id=message.message_id - 1)
    except Exception:
        ...
    await message.delete()
    await message.answer('Домашнее задание было успешно отправлено')
    await state.clear()
    await message.answer('Вы в главном меню', reply_markup=confirmed_student)


