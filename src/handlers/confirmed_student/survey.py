import datetime
import json
from os import getenv
from pprint import pformat

from aiogram import Router, F, Bot
from aiogram.fsm.context import FSMContext
from aiogram.filters import StateFilter, and_f
from aiogram.types import CallbackQuery, FSInputFile, Message
from aiogram.utils.media_group import MediaGroupBuilder

from src.gpt.ask import fetch_response, get_assistant_and_thread, get_text_answer, delete_assistant_and_thread
from src.database import UserModel, ProductModel
from src.database.products import get_product_by_id, get_partner_subject, get_product_by_subject
from src.database.rating import get_rating, get_subject_rating
from src.database.user import get_user_data, get_user_products, get_user_partners
from src.keyboards import (subjects, chatting_teacher_builder, confirmed_student,
                           stop_chatting_student, stop_chatting_teacher, student_subjects_builder,
                           back_survey)
from src.handlers.fsm_models import StudentSurvey


survey_router = Router()


@survey_router.callback_query(F.data.startswith('survey'))
async def start_student_survey(clb: CallbackQuery, state: FSMContext):
    await clb.answer('Процесс генерации вопросов...')
    teacher_id = int(clb.data.split('|')[1])
    subject = await get_partner_subject(clb.from_user.id, teacher_id)
    prompt = f'''
Ты методист вводного урока по предмету {subject.subject} в телеграмм-боте. 
Тебе нужно разработать индивидуальную образовательную траекторию для ученика нашей школы. 
Чтобы ее разработать тебе нужно в боте в виде текстовых сообщений протестировать ученика по этому 
предмету (10 вопросов), выявить цели обучения, предпочтения ученика и все другие особенности. 
Задай максимум 10 вопросов
Верни вопросы в формате JSON (БЕЗ РАЗМЕТОК, ПРОСТО ФИГУРНЫЕ СКОБКИ - ЭТО ВАЖНО), где каждый вопрос обозначен ключом от 1 до 10:
{{
     "1": "вопрос 1",
     "2": "вопрос 2",
     ...
     "10": "вопрос 10"
}}
    '''
    response = await fetch_response(prompt)
    if not response:
        await clb.message.answer("Ошибка при генерации вопросов. Попробуйте снова.")
        return
    try:
        questions = json.loads(response)
    except json.JSONDecodeError or TypeError as err:
        print(err)
        await clb.message.answer("Ошибка при генерации вопросов. Попробуйте снова.")
        return
    count = 1
    await state.update_data(questions=questions, count=count, teacher_id=teacher_id, subject=subject.subject)
    await state.set_state(StudentSurvey.collecting)
    await clb.message.answer(questions[str(count)])


@survey_router.message(and_f(F.text, StateFilter(StudentSurvey.collecting)))
async def get_user_recommendations(msg: Message, state: FSMContext):
    try:
        await msg.bot.edit_message_reply_markup(chat_id=msg.from_user.id, message_id=msg.message_id - 1)
    except Exception:
        ...
    data = await state.get_data()
    count = data.get('count')
    if count == 10:
        formatted_questions = pformat(data.get('questions'))
        subject = data.get('subject')
        prompt = f'''
Ты - методист школы. Тебе нужно проанализировать все ответы ученика и составь учебный план. Учебный план должен иметь 
следующую структуру: 1 занятие - 1 тема, в котором будет отражен порядок тем по предмету {subject}, рекомендованное 
количество времени на каждую тему, рекомендованное количество домашнего задания для каждой темы и другие детали 
необходимые для составления индивидуального учебного плана. 
Учти что в плане должно быть минимум 40 занятий. 
В учебном плане дай пометку учителю на каких темах ученику нужно уделить больше внимания и почему  
    Вот вопросы на которые отвечал ученик:\n{formatted_questions}\n
    Вот ответы ученика на данные вопросы:\n {data.get('answers')}\nТвоя задача дать ученику рекомендации по оптимальному для ученика количеству занятий в месяц
Пришли ответ в формате: номер дня - тема
'''
        answer = await fetch_response(prompt)
        await state.set_state(None)
        teacher_id = data.get('teacher_id')
        place = 0
        for i in range(0, len(answer)):
            if i % 4096 == 0:
                await msg.bot.send_message(chat_id=teacher_id, text=answer[place: i]) # Поделить текст на несколько сообщений
                place = i
        await msg.answer('Вы успешно ответили на все вопросы нашего виртуального помощника, '
                         'спасибо что помогаете нам совершенствовать наши методы обучения')
        await msg.answer('Вы в главном меню', reply_markup=confirmed_student)
        return
    questions = data.get('questions')
    answers = data.get('answers', '')
    answers += f"\nВопрос: {questions[str(count)]}\n Ответ: {msg.text}\n"
    count += 1
    await state.update_data(answers=answers, count=count)
    await msg.answer(questions[str(count)])


@survey_router.callback_query(and_f(F.data == 'back_survey_question', StateFilter(StudentSurvey.collecting)))
async def previous_question(clb: CallbackQuery, state: FSMContext):
    await clb.message.delete()
    data = await state.get_data()
    questions = data.get('questions')
    count = data.get('count')
    count -= 1
    await state.update_data(count=count)
    await clb.message.answer(questions[str(count)] if count != 1 else None)