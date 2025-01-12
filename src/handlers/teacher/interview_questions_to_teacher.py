
from aiogram import Router, F, Bot
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message
from aiogram.filters import StateFilter
from aiogram.utils.media_group import MediaGroupBuilder

import json
from asyncio import sleep
from pprint import pformat

import asyncio
import subprocess
import tempfile
import os

from src.database import get_user_data, update_user_role, add_product_to_user, get_user_products
from src.gpt.ask import fetch_response
from src.handlers.fsm_models import Interview
from dotenv import load_dotenv
from os import getenv

from src.loader import client

from src.keyboards import generate_questions_try_again, recruiter_keyboard, teacher_menu_back, candidate_result

load_dotenv()
RECRUITERS_GROUP_ID = int(getenv('RECRUITERS_GROUP_ID'))
TIME_TO_QUESTION = int(getenv('TIME_TO_QUESTION'))
interview_questions_router = Router()

import logging


@interview_questions_router.callback_query(F.data == "continue_interview")
async def start_questions(call: CallbackQuery, state: FSMContext):
    state_data = await state.get_data()

    await call.message.bot.edit_message_reply_markup(chat_id=call.from_user.id, message_id=call.message.message_id,
                                                     reply_markup=None)
    await call.answer("Генерирую вопросы...")

    picked_subject = state_data.get('picked_subject')
    option = state_data.get('teaching_type')

    subjects_links = {
        "Математика": "https://math-ege.sdamgia.ru/?ysclid=m39qhd8x2i601634293",
        "Информатика": "https://inf-ege.sdamgia.ru/?ysclid=m39qj08qtu675515505",
        "Химия": "https://chem-ege.sdamgia.ru/?r&ysclid=m39qjvq478741484083",
        "Биология": "https://bio-ege.sdamgia.ru/?r&ysclid=m39qkp7bwc945518452",
        "Русский": "https://rus-ege.sdamgia.ru/?ysclid=m39qmox2v1938837090",
        "Физика": "https://phys-ege.sdamgia.ru/?ysclid=m39qnnp3og580074535",
        "История": "https://neofamily.ru/istoriya/smart-directory",
        "Обществознание": "https://neofamily.ru/obshchestvoznanie/smart-directory",
        "Литература": "https://lit-ege.sdamgia.ru/?ysclid=m3fzxsc6ky880715212",
    }

    if option == "languages":
        response = await fetch_response(prompt=f"""
ты рекрутер в онлайн-школе easyknow. Тебе нужно провести собеседование с преподавателем. 
Твоя задача задавать вопросы преподавателю, чтобы понять на сколько у него глубокие навыки владения предметом, психика и способность вести себя в нестандартных ситуациях. 
Собеседование будет состоять из 3 этапов. Сначала придумай 3 общих вопроса про их жизнь на (Предмет), чтобы преподаватель ответил на них на  {picked_subject}. 
Затем придумай 3 предложения с акцентом на разную грамматику по {picked_subject}, чтобы преподаватель их перевел c русского языка на {picked_subject}. 
Затем попроси преподавателя объяснить 3 непростых темы по {picked_subject} русском языке. Затем задай 3 вопроса на психологию, чтобы понять насколько психически устойчив преподаватель. 
И в конце задай 3 вопроса про нестандартные ситуации на занятии и как бы преподаватель с ними справится.

Верни вопросы в формате JSON (БЕЗ РАЗМЕТОК, ПРОСТО ФИГУРНЫЕ СКОБКИ - ЭТО ВАЖНО), где каждый вопрос обозначен ключом от 1 до 12:
{{
     "1": "вопрос 1",
     "2": "вопрос 2",
     ...
     "12": "вопрос 12"
}}
""")
    elif option == "school_subjects":
        response = await fetch_response(prompt=f"""
ты рекрутер в онлайн-школе easyknow. Тебе нужно провести собеседование с преподавателем.
Твоя задача задавать вопросы преподавателю, чтобы понять на сколько у него глубокие навыки владения предметом, психика и способность вести себя в нестандартных ситуациях.
Собеседование будет состоять из 3 этапов.
Сначала придумай 6 непростых заданий по {picked_subject} согласно темам предоставленным по ссылке ({subjects_links.get(picked_subject.lower(), "ссылка не найдена, придумай темы сам.")}), которые преподаватель сможет объяснить словами.
Затем задай 3 вопроса на психологию, чтобы понять насколько психически устойчив преподаватель.
И в конце задай 3 вопроса про нестандартные ситуации на занятии и как бы преподаватель с ними справится.

Верни вопросы в формате JSON (БЕЗ РАЗМЕТОК, ПРОСТО ФИГУРНЫЕ СКОБКИ - ЭТО ВАЖНО), где каждый вопрос обозначен ключом от 1 до 12:
{{
     "1": "вопрос 1",
     "2": "вопрос 2",
     ...
     "12": "вопрос 12"
}}
""")
    else:
        response = await fetch_response(prompt=f""""
Ты рекрутер в онлайн-школе easyknow. Тебе нужно провести собеседование с преподавателем.
Твоя задача задавать вопросы преподавателю, чтобы понять на сколько у него глубокие навыки владения предметом, психика и способность вести себя в нестандартных ситуациях.
Собеседование будет состоять из 3 этапов.
Всего будет 12 вопросов.
Сначала придумай 6 непростых заданий по {picked_subject} согласно темам предоставленным по ссылке - {subjects_links.get(picked_subject.lower(), "ссылка не найдена, придумай темы сам.")}, которые преподаватель сможет объяснить словами.
Затем задай 3 вопроса на психологию, чтобы понять насколько психически устойчив преподаватель.
И в конце задай 3 вопроса про нестандартные ситуации на занятии и как бы преподаватель с ними справится.


Верни вопросы в формате JSON (БЕЗ РАЗМЕТОК, ПРОСТО ФИГУРНЫЕ СКОБКИ - ЭТО ВАЖНО), где каждый вопрос обозначен ключом от 1 до 12:
{{
     "1": "вопрос 1",
     "2": "вопрос 2",
     ...
     "12": "вопрос 12"
}}
""")
    if not response:
        await call.message.answer("Ошибка при генерации вопросов. Попробуйте снова.",
                                  reply_markup=generate_questions_try_again)
    try:
        questions = json.loads(response)
#         questions = {
#      "1": "Can you tell me a little about your background and what motivated you to become a teacher?",
#      "2": "What is your teaching philosophy, and how do you think it impacts your students?",
#      "3": "How do you stay current with developments in your field and incorporate them into your teaching?",
#      "4": "Переведите на английский: Я люблю преподавать, потому что это дает возможность делиться знаниями.",
#      "5": "Переведите на английский: Ученики часто задают вопросы, и я всегда готов им помочь.",
#      "6": "Переведите на английский: Мы должны придерживаться расписания, но иногда бывают непредвиденные обстоятельства.",
#      "7": "Как вы оцениваете уровень своих учеников и что делаете, если они не понимают материал?",
#      "8": "Какой самый сложный вызов вы сталкивались в своей преподавательской практике и как вы его преодолели?",
#      "9": "Как вы работаете с учениками, у которых разные уровни подготовки и потребности?",
#      "10": "Как вы реагируете на критику своей работы, и как она влияет на вашу преподавательскую практику?",
#      "11": "Что вы делаете, если во время урока возникает конфликт между учениками?",
#      "12": "Как бы вы поступили, если один из ваших учеников начал вести себя агрессивно во время занятия?"
# }

        await state.update_data(questions=questions, all_transcripts="")
        await call.message.edit_text("Вопросы успешно сгенерированы. Начинаем собеседование через 5 секунд...")
        await sleep(5)
        await ask_questions(call, questions, state)
    except json.JSONDecodeError or TypeError:
        await call.message.answer("Ошибка при генерации вопросов. Попробуйте снова.",
                                  reply_markup=generate_questions_try_again)


async def ask_questions(call: CallbackQuery, questions, state):
    await call.message.edit_text("<b>Отвечайте на вопросы, которые появляются ниже:</b>")
    await sleep(2)
    await state.set_state(Interview.waiting_video_answers)
    for key, question in questions.items():
        q = await call.message.answer(question)
        await state.update_data(last_question=question)
        await sleep(TIME_TO_QUESTION)
        try:
            await call.message.bot.delete_message(chat_id=call.from_user.id, message_id=q.message_id)
        except Exception as e:
            ...
    await call.message.answer(
        "Надеюсь, вы успели ответить на все вопросы! У вас есть еще одна минута для отправки оставшихся видеосообщений.")
    await sleep(30)

    await call.message.answer(
        "30 секунд до конца собеседования.")
    await sleep(30)

    await send_interview_results(call, state)
    text = ('✨ Благодарим вас за участие в интервью и проявленный интерес к нашей школе easyknow. '
            'Мы ценим ваше время и готовность делиться своим опытом. 💡\nСейчас наша команда внимательно '
            'изучает результаты всех этапов отбора. ⏳ Пожалуйста, ожидайте обратной связи '
            'в ближайшее время — мы свяжемся с вами, чтобы обсудить дальнейшие шаги. 📩\nСпасибо за '
            'ваше терпение и доверие к easyknow! 💙')
    await call.message.answer(
        text=text,
        reply_markup=teacher_menu_back)


@interview_questions_router.message(Interview.waiting_video_answers, F.video_note)
async def handle_video_note(message: Message, state: FSMContext):
    print('success get video note')
    file_id = message.video_note.file_id
    transcript_text = await process_video_to_text(message.bot, file_id)
    state_data = await state.get_data()
    all_transcripts = state_data.get("all_transcripts", "")
    all_transcripts += f"\nВопрос: {state_data.get('last_question')}\n Ответ: {transcript_text}\n"
    await state.update_data(all_transcripts=all_transcripts)
    await state.update_data(last_video_note_id=file_id)


async def extract_audio(temp_video_path):
    audio_path = temp_video_path.replace('.mp4', '.mp3')
    command = ['ffmpeg', '-hwaccel', 'cuda', '-i', temp_video_path, '-q:a', '0', '-map', 'a', audio_path]

    process = await asyncio.create_subprocess_exec(
        *command,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE
    )

    stdout, stderr = await process.communicate()

    if process.returncode != 0:
        print(f"FFmpeg error: {stderr.decode()}")
        raise subprocess.CalledProcessError(process.returncode, command, output=stdout, stderr=stderr)

    return audio_path


async def transcribe_audio(
    file_path: str
    ) -> str:
    """
    Transcribe audio to text using the OpenAI Whisper ASR model.

    Args:
        file_path (str): The path to the audio file.

    Returns:
        str: The transcribed text or an empty string if an error occurs.
    """
     # Log the input file
    logging.info(f"Transcribing audio file: {file_path}")

    # Transcribe audio to text using OpenAI
    audio_file = open(file_path, "rb")
    try:
        transcript = await client.audio.transcriptions.create(
            model="whisper-1",
            file=audio_file,
            response_format='json'
        )
        # Log the transcription result
        logging.info(f"Transcription result: {transcript.text}")
        return transcript.text
    except Exception as e:
        logging.error(f"An error occurred: {e}")
        return ""


async def process_video_to_text(bot: Bot, file_id):
    file = await bot.get_file(file_id)
    video_data = await bot.download_file(file.file_path)

    with tempfile.NamedTemporaryFile(delete=False, suffix=".mp4") as temp_video_file:
        temp_video_file.write(video_data.read())
        temp_video_path = temp_video_file.name

    try:
        audio_path = await extract_audio(temp_video_path)
        transcript_text = await transcribe_audio(audio_path)
    finally:
        os.remove(temp_video_path)
    if audio_path and os.path.exists(audio_path):
        os.remove(audio_path)

    return transcript_text


async def send_long_message(bot, chat_id, text, chunk_size=4096):
    for i in range(0, len(text), chunk_size):
        await bot.send_message(chat_id=chat_id, text=text[i:i + chunk_size])


async def send_interview_results(call: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    picked_subject = data.get('picked_subject')
    subjects = await get_user_products(call.from_user.id)
    text = f"""
Получено новые результаты интервью от @{call.from_user.username}
User ID: {call.from_user.id}
"""
    if subjects:
        text += '\nУже проходил интервью по предметам:'
        for subject in subjects:
            text += f'{subject.name}, '
    await call.message.bot.send_message(chat_id=RECRUITERS_GROUP_ID, text=text)

    video_file_id = data.get('last_video_note_id')
    # Документы

    document_media = MediaGroupBuilder()
    hh_ru_resume = data.get('hhru_file')
    ege_file = data.get('ege_file')
    education_file = data.get('education_file')
    for doc in [hh_ru_resume, ege_file, education_file]:
        try:
            if doc:
                document_media.add_document(media=doc.file_id)
        except Exception as e:
            print(e)

    formatted_questions = pformat(data.get('questions'))
    teacher_info = ""
    if not data.get('fast_interview', False):
        teacher_info = f"""
Имя - <b>{data.get('full_name')}</b>
Возраст - <b>{data.get('age')}</b>
Образование - <b>{data.get('education')}</b>
Опыт работы - <b>{data.get('work_experience')}</b>
Обо мне - <b>{data.get('about_me')}</b>
Документ "Баллы ЕГЭ": <b>{"не заполнен" if data.get('ege_file') == "-" else "заполнен"}</b>
Документ "Резюме hh.ru": <b>{"не заполнен" if data.get('hhru_file') == "-" else "заполнен"}</b>
Документ "Об образовании": <b>{"не заполнен" if data.get('education_file') == "-" else "заполнен"}</b>
Комментарий о документах: {data.get('comment_about_docs')}
Почта: <b>{data.get('mail')}</b>
    """

    if video_file_id:
        await call.message.bot.send_video(chat_id=RECRUITERS_GROUP_ID, video=video_file_id)
    if document_media.build():
        await call.message.bot.send_media_group(chat_id=RECRUITERS_GROUP_ID, media=document_media.build())

    interview_result = f"""
Информация о собеседовании:   
Выбранный предмет: {data.get('picked_subject')}

Заданные вопросы:
{formatted_questions}

Полученные ответы кандидата:
{data.get('all_transcripts', "Ответов от кандидата не поступало.")}
"""

    await send_long_message(call.message.bot, chat_id=RECRUITERS_GROUP_ID, text=interview_result)

    response = await fetch_response(
        prompt=f"""
Проанализируй результаты собеседования по {picked_subject}: 
---------

{interview_result}
        
---------
Сделай вывод по поводу кандидата, правильности его ответов. Твой ответ должен помочь рекрутеру принять решения - брать или не брать кандидата.""")

    if teacher_info:
        await call.message.bot.send_message(chat_id=RECRUITERS_GROUP_ID, text=teacher_info)

    await call.message.bot.send_message(chat_id=RECRUITERS_GROUP_ID, text=response,
                                        reply_markup=(await recruiter_keyboard(call.from_user.id, picked_subject)))


@interview_questions_router.callback_query(F.data.startswith("candidate|"))
async def interview_results(call: CallbackQuery, state: FSMContext):
    await call.answer()
    call_data = call.data.split("|")
    choose = call_data[1]
    user_id = call_data[2]
    picked_subject = call_data[3]
    await state.update_data(choose=choose, user_id=int(user_id), picked_subject=picked_subject)
    await state.set_state(Interview.feed_back_comment)
    await call.message.answer("Напишите комментарий, причину, обратную связь для этого кандидата")


@interview_questions_router.message(StateFilter(Interview.feed_back_comment))
async def interview_results_feed_back(message: Message, state: FSMContext):
    state_data = await state.get_data()
    choose = state_data.get('choose')
    user_id = state_data.get('user_id')
    user_data = await get_user_data(user_id)
    if choose == "accept":
        await message.bot.send_message(chat_id=user_id, text=f"""
Здравствуйте, {user_data.name}!   
Рады сообщить, что вы успешно прошли отбор в нашу команду easyknow! 🎉 
Мы видим, что ваши профессиональные навыки и подход к обучению отлично соответствуют нашему стремлению делать обучение интересным и доступным для наших учеников.     

Комментарии рекрутеров:
{message.text}

С уважением, Команда easyknow          
""", reply_markup=(await candidate_result(choose)))
        picked_subject = state_data.get('picked_subject')
        await add_product_to_user(telegram_id=user_id, subject=picked_subject)
        await update_user_role(telegram_id=user_id, new_role="confirmed_teacher")
    if choose == "decline":
        await message.bot.send_message(chat_id=user_id, text=f"""
Здравствуйте, {user_data.name}!    
Благодарим вас за интерес к нашей школе и участие в отборе! 
Мы внимательно рассмотрели вашу кандидатуру, и, к сожалению, сейчас не можем предложить вам сотрудничество.   

Комментарии рекрутеров:
{message.text}  

Однако мы будем рады сохранить ваш контакт и вернуться к обсуждению возможности сотрудничества в будущем. 
Надеемся на дальнейшее взаимодействие и желаем вам успехов в ваших профессиональных начинаниях!     
С уважением, Команда easyknow     
""", reply_markup=(await candidate_result(choose)))