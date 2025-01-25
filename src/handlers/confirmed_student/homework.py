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
from src.database.rating import create_player, get_rating, add_homework
from src.keyboards import (subjects, homework_teacher_builder, confirmed_student,
                           stop_send_homework, access_homework, custom_back_builder, confirmed_teacher)
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


@homework_router.callback_query(F.data.startswith('access'))
async def send_get_accordance(clb: CallbackQuery, state: FSMContext):
    await clb.message.delete()
    student_id = int(clb.data.split('|')[1])
    subject = clb.data.split('|')[2]
    await state.set_state(Homework.waiting_for_accordance)
    await state.update_data(student_id=student_id, subject=subject)
    text = """
Полное соответствие заданию (0–2 балла)
   - 2 балла — ученик выполнил все требования задания, ответил на все вопросы.
   - 1 балл — ученик выполнил большинство требований, но упустил некоторые детали.
   - 0 баллов — ученик выполнил лишь небольшую часть задания или не следовал инструкциям.
    """
    await clb.message.answer(text)


@homework_router.message(and_f(F.text, StateFilter(Homework.waiting_for_accordance)))
async def get_accordance(msg: Message, state: FSMContext):
    try:
        ball = int(msg.text)
    except:
        await msg.answer('Оценка должна быть числом пожалуйста попробуйте снова')
        return
    if ball not in range(0, 3):
        await msg.answer('Оценка должна быть в диапозоне от 0-2 баллов, пожалуйста попробуйте снова')
        return
    await msg.delete()
    try:
        await msg.bot.delete_message(chat_id=msg.from_user.id, message_id=msg.message_id - 1)
    except Exception:
        ...
    await state.update_data(accordance=ball)
    await state.set_state(Homework.waiting_for_accuracy)
    text = '''
Точность (0–2 балла)
   - 2 балла — отсутствуют ошибки, допущены лишь незначительные опечатки.
   - 1 балл — присутствуют небольшие ошибки, но они не искажают общий смысл.
   - 0 баллов — значительные ошибки, которые искажают смысл ответа.
    '''
    keyboard = await custom_back_builder('back_get_accordance')
    await msg.answer(text, reply_markup=keyboard)


@homework_router.callback_query(and_f(F.data == 'back_get_accordance', StateFilter(Homework.waiting_for_accuracy)))
async def send_get_accordance(clb: CallbackQuery, state: FSMContext):
    await clb.message.delete()
    await state.set_state(Homework.waiting_for_accordance)
    text = """
    Полное соответствие заданию (0–2 балла)
       - 2 балла — ученик выполнил все требования задания, ответил на все вопросы.
       - 1 балл — ученик выполнил большинство требований, но упустил некоторые детали.
       - 0 баллов — ученик выполнил лишь небольшую часть задания или не следовал инструкциям.
        """
    await clb.message.answer(text)


@homework_router.message(and_f(F.text, StateFilter(Homework.waiting_for_accuracy)))
async def get_accuracy(msg: Message, state: FSMContext):
    try:
        ball = int(msg.text)
    except:
        await msg.answer('Оценка должна быть числом пожалуйста попробуйте снова')
        return
    if ball not in range(0, 3):
        await msg.answer('Оценка должна быть в диапозоне от 0-2 баллов, пожалуйста попробуйте снова')
        return
    await msg.delete()
    try:
        await msg.bot.delete_message(chat_id=msg.from_user.id, message_id=msg.message_id - 1)
    except Exception:
        ...
    await state.update_data(accuracy=ball)
    await state.set_state(Homework.waiting_for_quality)
    text = '''
Качество оформления (0–2 балла)
   - 2 балла — структура и оформление полностью соблюдены, легко читается.
   - 1 балл — структура нарушена, но основные требования к оформлению выполнены.
   - 0 баллов — отсутствует логичная структура или последовательность, оформление не соблюдено.
    '''
    keyboard = await custom_back_builder('back_get_accuracy')
    await msg.answer(text, reply_markup=keyboard)


@homework_router.callback_query(and_f(F.data == 'back_get_accuracy', StateFilter(Homework.waiting_for_quality)))
async def send_get_accuracy(clb: CallbackQuery, state: FSMContext):
    await clb.message.delete()
    await state.set_state(Homework.waiting_for_accuracy)
    text = '''
    Точность (0–2 балла)
       - 2 балла — отсутствуют ошибки, допущены лишь незначительные опечатки.
       - 1 балл — присутствуют небольшие ошибки, но они не искажают общий смысл.
       - 0 баллов — значительные ошибки, которые искажают смысл ответа.
        '''
    keyboard = await custom_back_builder('back_get_accordance')
    await clb.message.answer(text, reply_markup=keyboard)


@homework_router.message(and_f(F.text, StateFilter(Homework.waiting_for_quality)))
async def get_quality(msg: Message, state: FSMContext):
    try:
        ball = int(msg.text)
    except:
        await msg.answer('Оценка должна быть числом пожалуйста попробуйте снова')
        return
    if ball not in range(0, 3):
        await msg.answer('Оценка должна быть в диапозоне от 0-2 баллов, пожалуйста попробуйте снова')
        return
    await msg.delete()
    try:
        await msg.bot.delete_message(chat_id=msg.from_user.id, message_id=msg.message_id - 1)
    except Exception:
        ...
    await state.update_data(quality=ball)
    await state.set_state(Homework.waiting_for_knowledge)
    text = '''
Демонстрация знаний и глубина ответа (0–2 балла)
   - 2 балла — ученик продемонстрировал глубокое понимание, при необходимости использовал дополнительные примеры.
   - 1 балл — знание показано, но имеются пробелы или не хватает аргументов.
   - 0 баллов — ответ показывает ограниченные знания или неверное понимание.
    '''
    keyboard = await custom_back_builder('back_get_quality')
    await msg.answer(text, reply_markup=keyboard)


@homework_router.callback_query(and_f(F.data == 'back_get_quality', StateFilter(Homework.waiting_for_knowledge)))
async def send_get_quality(clb: CallbackQuery, state: FSMContext):
    await clb.message.delete()
    await state.set_state(Homework.waiting_for_quality)
    text = '''
    Качество оформления (0–2 балла)
       - 2 балла — структура и оформление полностью соблюдены, легко читается.
       - 1 балл — структура нарушена, но основные требования к оформлению выполнены.
       - 0 баллов — отсутствует логичная структура или последовательность, оформление не соблюдено.
        '''
    keyboard = await custom_back_builder('back_get_accuracy')
    await clb.message.answer(text, reply_markup=keyboard)


@homework_router.message(and_f(F.text, StateFilter(Homework.waiting_for_knowledge)))
async def get_knowledge(msg: Message, state: FSMContext):
    try:
        ball = int(msg.text)
    except:
        await msg.answer('Оценка должна быть числом пожалуйста попробуйте снова')
        return
    if ball not in range(0, 3):
        await msg.answer('Оценка должна быть в диапозоне от 0-2 баллов, пожалуйста попробуйте снова')
        return
    await msg.delete()
    try:
        await msg.bot.delete_message(chat_id=msg.from_user.id, message_id=msg.message_id - 1)
    except Exception:
        ...
    await state.update_data(knowledge=ball)
    await state.set_state(Homework.waiting_for_independence)
    text = '''
Самостоятельность выполнения (0–2 балла)
   - 2 балла — работа выполнена полностью самостоятельно, без признаков копирования.
   - 1 балл — основная часть выполнена самостоятельно, но некоторые элементы могли быть заимствованы.
   - 0 баллов — работа выполнена с чужой помощью или в спешке.
    '''
    keyboard = await custom_back_builder('back_get_knowledge')
    await msg.answer(text, reply_markup=keyboard)


@homework_router.callback_query(and_f(F.data == 'back_get_knowledge', StateFilter(Homework.waiting_for_independence)))
async def send_get_knowledge(clb: CallbackQuery, state: FSMContext):
    await clb.message.delete()
    await state.set_state(Homework.waiting_for_knowledge)
    text = '''
    Демонстрация знаний и глубина ответа (0–2 балла)
       - 2 балла — ученик продемонстрировал глубокое понимание, при необходимости использовал дополнительные примеры.
       - 1 балл — знание показано, но имеются пробелы или не хватает аргументов.
       - 0 баллов — ответ показывает ограниченные знания или неверное понимание.
        '''
    keyboard = await custom_back_builder('back_get_quality')
    await clb.message.answer(text, reply_markup=keyboard)


@homework_router.message(and_f(F.text, StateFilter(Homework.waiting_for_independence)))
async def get_independence(msg: Message, state: FSMContext):
    try:
        ball = int(msg.text)
    except:
        await msg.answer('Оценка должна быть числом пожалуйста попробуйте снова')
        return
    if ball not in range(0, 3):
        await msg.answer('Оценка должна быть в диапозоне от 0-2 баллов, пожалуйста попробуйте снова')
        return
    await msg.delete()
    try:
        await msg.bot.delete_message(chat_id=msg.from_user.id, message_id=msg.message_id - 1)
    except Exception:
        ...
    await state.update_data(independence=ball)
    data = await state.get_data()
    teacher = await get_user_data(msg.from_user.id)
    subject = data.get('subject')
    student_id = data.get('student_id')
    balls = data.get('accordance') + data.get("accuracy") + data.get("quality") + data.get("knowledge") + data.get("independence")
    text = (f'<b>Учитель {teacher.name} проверил вашу домашнюю работу по предмету {subject}</b>\nВот '
            f'результаты проверки домашней работы:\n\n - Полное соответствие заданию:{data.get("accordance")} (0 - 2 балла)\n'
            f' - Точность: {data.get("accuracy")} (0 - 2 балла)\n - Качество оформления: {data.get("quality")} (0 - 2 балла)\n'
            f' - Демонстрация знаний и глубина ответа: {data.get("knowledge")} (0 - 2 балла)\n'
            f' - Самостоятельность выполнения: {data.get("independence")} (0 - 2 балла)\n'
            f'Общий балл: {balls} из 10')
    await msg.bot.send_message(
        chat_id=student_id,
        text=text
    )
    rating = await get_rating(student_id, subject)
    if rating is None:
        rating = await create_player(student_id, subject)
    await add_homework(student_id, balls, subject)
    await state.clear()
    await msg.answer(f'Домашнее задание было успешно проверенно. Баллы: {balls} из 10, '
                     f'спасибо вам за проделанную работу')
    await msg.answer('Ты в главном меню', reply_markup=confirmed_teacher)
