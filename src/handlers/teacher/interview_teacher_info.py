import os

from aiogram import Router, F
from aiogram.filters import and_f
from aiogram.types import Message, CallbackQuery, FSInputFile
from aiogram.fsm.context import FSMContext
from aiogram.utils.media_group import MediaGroupBuilder

from src.handlers.fsm_models import Interview
from src.database.products import get_languages_categories, get_subject_categories
from src.keyboards import confirm_interview_agreement, categories_for_teaching, categories_for_teacher_builder, \
    start_or_back, cancel_interview, continue_interview, have_hh_ru_resume_kb, back_to_resume, start_interview_questions

interview_router = Router()


@interview_router.callback_query(F.data == "next")
async def start_interview(call: CallbackQuery, state: FSMContext):
    await state.clear()
    await call.message.edit_text("Выберите категорию из представленных ниже:", reply_markup=categories_for_teaching)


@interview_router.callback_query(F.data.startswith("type|"))
async def pick_option_for_teaching(call: CallbackQuery, state: FSMContext):
    await state.clear()
    option = call.data.split("|")[1]
    await state.update_data(teaching_type=option)
    if option == "languages":
        categories = await get_languages_categories()
        #categories = [
            #'Английский',
            #'Китайский',
            #'Испанский'
        #]
        keyboard = await categories_for_teacher_builder(categories)
        await call.message.edit_text(text="Выберите язык, который хотите преподавать", reply_markup=keyboard)
    if option == "school_subjects":
        categories = await get_subject_categories()
        #categories = [
            #'Химия',
            #'Биология',
            #'Физика',
            #'Математика',
            #'Информатика',
            #'История',
            #'Обществознание',
            #'Русский язык',
            #'Литература'
        #]
        keyboard = await categories_for_teacher_builder(categories)
        await call.message.edit_text(text="Выберите предмет, который хотите преподавать", reply_markup=keyboard)


@interview_router.callback_query(F.data.startswith("subject|"))
async def confirm_agreement(call: CallbackQuery, state: FSMContext):
    await call.message.delete()

    picked_subject = call.data.split("|")[1]
    print(picked_subject)
    await state.update_data(picked_subject=picked_subject)

    state_data = await state.get_data()
    option = state_data.get('teaching_type')
    keyboard = await confirm_interview_agreement(option)
    
    document_media = MediaGroupBuilder()

    # ID в боте 
    # agreement_documents_ids = [
    #     'BQACAgIAAxkDAAIOW2cnPW5UvJqbsuQh_shtJPKTqa6TAAKSVwACltY5SQY4hMe97MPkNgQ',
    #     'BQACAgIAAxkDAAIOXWcnPW4eDA3K1zWiiq6AdEKGF_SiAAKTVwACltY5Se-RR4oYiw8SNgQ',
    #     'BQACAgIAAxkDAAIOX2cnPW7h7YjRbgAByQ8MdxzZP-CI8wAClFcAApbWOUkp2RnEeNiWuDYE',
    # ]

    # for document_id in agreement_documents_ids:
    #     document_media.add_document(media=document_id)
    
    agreement_docs = os.listdir('src/files/teacher_agreement_1')
    for doc in agreement_docs:
        document_media.add(
            type="document",
            media=FSInputFile('src/files/teacher_agreement_1/' + doc)
        )

    documents = await call.message.answer_media_group(media=document_media.build())
    await state.update_data(
        photos_to_delete=[msg.message_id for msg in documents])

    if option == "languages":
        await call.message.answer(text="""
Перед тем, как мы приступим к прохождению процесса интервьюирования, вам нужно подтвердить свое согласие на обработку персональных данных.  

<b>Я даю согласие ООО "Изиноу" (ОГРН 1242700016558) на обработку персональных данных на условиях Политики в отношении обработки и защиты персональных данных в целях анализа резюме, видео-собеседования и регистрации на платформе.</b>""",
                                  reply_markup=keyboard)

    if option == "school_subjects":
        await call.message.answer(text="""Перед тем, как мы приступим к прохождению процесса интервьюирования, вам нужно подтвердить своё согласие на обработку персональных данных. ✅

Я даю согласие ООО "Изиноу" (ОГРН 1242700016558) на обработку персональных данных на условиях Политики в отношении обработки и защиты персональных данных 📜 в целях анализа резюме, видео-собеседования и регистрации на платформе. 💻""",
                                  reply_markup=keyboard)


@interview_router.callback_query(F.data == "hh_ru")
async def check_hh_ru_resume(call: CallbackQuery, state: FSMContext):
    state_data = await state.get_data()
    option = state_data.get('teaching_type')

    if option == "languages":
        info = f"""
Отлично! Сейчас мы переходим к следующему этапу.
На этапе интервью бот задаст вам 12 вопросов:
- 9 вопросов на проверку знания предмета.
- 3 вопроса для психологического теста.
- 3 вопроса для оценки навыков управления конфликтными ситуациями на занятии.

<b>Каждый вопрос будет показываться на экране в течение 1 минуты, после чего удалится. 
Как только бот покажет вопрос, сразу начинайте записывать кружок с ответом, не превышая 1 минуты</b>❗️

Инструкция по записи:
- Нажмите на значок микрофона и переключитесь на значок камеры, чтобы записать кружок.
- Говорите уверенно и чётко, следите за временем — на ответ у вас есть 1 минута.
- Пожалуйста, записывайте в тихом месте, чтобы вас было хорошо слышно.

Желаем вам удачи!
"""
    elif option == "school_subjects":
        info = f"""
Отлично! Сейчас мы переходим к следующему этапу. 
На этапе интервью бот задаст вам 12 вопросов: 
- 6 вопросов на проверку знания предмета. 
- 3 вопроса для психологического теста. 
- 3 вопроса для оценки навыков управления конфликтными ситуациями на занятии.  

Каждый вопрос будет показываться на экране в течение 1 минуты, после чего удалится.   
Как только бот покажет вопрос, сразу начинайте записывать кружок с ответом, не превышая 1 минуты.  

Инструкция по записи: 
- Нажмите на значок микрофона и переключитесь на значок камеры, чтобы записать кружок.    
- Говорите уверенно и чётко, следите за временем — на ответ у вас есть 1 минута.    
- Пожалуйста, записывайте в тихом месте, чтобы вас было хорошо слышно.  

Желаем вам удачи!
"""
    else:
        info = """
Отлично! Теперь мы приступаем к процессу прохождения интервьюирования.     
Вам предстоит пройти следующие этапы: 
1) Заполнить резюме в боте (или приложить с hh.ru) 
2) Записывать аудио сообщение
3) Отправить записанное аудио

Прохождение всех этапов займет около 20-30 минут. Теперь мы начинаем! Ниже выберите одну из опций.      
"""
    back_data = state_data.get('picked_subject')
    await call.message.edit_text(text=info, reply_markup=have_hh_ru_resume_kb(back_data))


@interview_router.callback_query(F.data == "have_hh_ru_resume")
async def get_hh_ru_resume(call: CallbackQuery, state: FSMContext):
    await state.update_data(fast_interview=True)
    await state.set_state(Interview.hhru_resume)
    await call.message.edit_text("Отправьте ниже pdf-файл - ваше резюме с hh.ru", reply_markup=back_to_resume)


@interview_router.message(and_f(F.document, Interview.hhru_resume))
async def get_resume(message: Message, state: FSMContext):
    try:
        await message.bot.edit_message_reply_markup(chat_id=message.from_user.id, message_id=message.message_id - 1)
    except Exception as e:
        print(e)

    if message.document:
        document = message.document

        file_info = await message.bot.get_file(document.file_id)
        file_path = file_info.file_path
        if file_path.endswith(".pdf"):
            await state.update_data(hhru_file=file_info)
        else:
            await message.answer("Пожалуйста, отправьте файл с расширением .pdf")
            return

        state_data = await state.get_data()

        keyboard = await start_interview_questions(cancel=state_data.get('teaching_type'))

        await message.answer(f"""Ваш файл {document.file_name} успешно сохранен. 
Нажмите на кнопку продолжить, <b>если готовы приступить к собеседованию</b>

Далее бот начнет вам задавать вопросы на время (вопросы будут удаляться через одну минуту)

От вас требуется в live-режиме <b>отвечать на вопросы и записывать видео сообщения (кружки)</b>, которые позже (после прохождения опроса) нужно будет отправить в этот чат""",
                             reply_markup=keyboard)


@interview_router.callback_query(F.data == "interview_start")
async def info_about_interview(call: CallbackQuery, state: FSMContext):
    await state.set_state(None)
    data = await state.get_data()
    picked_subject = data.get('picked_subject')
    keyboard = await start_or_back(picked_subject)
    await call.message.edit_text(f"""Вы выбрали - {picked_subject}

🎯 Как происходит процесс отбора?

1️⃣ Запрос данных:
Бот попросит вас указать:

• Имя
• Возраст
• Образование
• Опыт работы
• Коротко рассказать о себе 

2️⃣ Этап «Интервью»:

• Бот начнёт задавать вопросы , на которые нужно отвечать в режиме live;
• Записывайте видео-сообщения с вашими ответами (кружки).

✅ Чтобы приступить к отбору на этот предмет, нажмите кнопку "Начать". 🚀""",
    reply_markup=keyboard)


@interview_router.callback_query(F.data.startswith("start_interview|"))
async def interview_start(call: CallbackQuery, state: FSMContext):
    await state.update_data(fast_interview=False)
    item_for_interview = call.data.split("start_interview|")[1]
    await state.update_data(item_for_interview=item_for_interview)
    state_data = await state.get_data()
    keyboard = await cancel_interview(state_data.get('teaching_type'))
    await state.update_data(cancel=keyboard)
    await state.set_state(Interview.full_name)
    
    await call.message.edit_text(f"""
1. Введите ваше полное имя ниже:""", reply_markup=keyboard)


@interview_router.message(and_f(Interview.full_name, F.text))
async def get_full_name(message: Message, state: FSMContext):
    try:
        await message.bot.edit_message_reply_markup(chat_id=message.from_user.id, message_id=message.message_id - 1)
    except Exception:
        ...
    # await message.answer(f"<b>Ваше полное имя - {message.text}</b>")
    data = await state.get_data()
    await state.update_data(full_name=message.text)
    await state.set_state(Interview.age)
    await message.answer("2. Введите ниже ваш возраст", reply_markup=data.get('cancel'))


@interview_router.message(and_f(Interview.age, F.text))
async def get_age(message: Message, state: FSMContext):
    try:
        await message.bot.edit_message_reply_markup(chat_id=message.from_user.id, message_id=message.message_id - 1)
    except Exception:
        ...

    data = await state.get_data()

    if not message.text.isdigit():
        await message.answer("Возраст это целое число", reply_markup=data.get('cancel'))
        return

    #     await message.answer(f"""
    # <b>Ваша карточка преподавателя:</b>
    # Имя - <b>{data.get('full_name')}</b>
    # Возраст - <b>{message.text}</b>""")

    await state.update_data(age=message.text)
    await state.set_state(Interview.education)
    await message.answer("3. Введите ниже ваше образование (место где учились, высшее/среднее)",
                         reply_markup=data.get('cancel'))


@interview_router.message(and_f(Interview.education, F.text))
async def get_education(message: Message, state: FSMContext):
    try:
        await message.bot.edit_message_reply_markup(chat_id=message.from_user.id, message_id=message.message_id - 1)
    except Exception:
        ...
    data = await state.get_data()
    #     await message.answer(f"""
    # <b>Ваша карточка преподавателя:</b>
    # Имя - <b>{data.get('full_name')}</b>
    # Возраст - <b>{data.get('age')}</b>
    # Образование - <b>{message.text}</b>""")

    await state.update_data(education=message.text)
    await state.set_state(Interview.work_experience)
    await message.answer(
        "4. Опишите ниже ваш опыт работы, какие техники обучения применяете, как решаете конфликтные ситуации",
        reply_markup=data.get('cancel'))


@interview_router.message(and_f(Interview.work_experience, F.text))
async def get_work_experience(message: Message, state: FSMContext):
    try:
        await message.bot.edit_message_reply_markup(chat_id=message.from_user.id, message_id=message.message_id - 1)
    except Exception:
        ...
    data = await state.get_data()
    #     await message.answer(f"""
    # <b>Ваша карточка преподавателя:</b>
    # Имя - <b>{data.get('full_name')}</b>
    # Возраст - <b>{data.get('age')}</b>
    # Образование - <b>{data.get('education')}</b>
    # Опыт работы - <b>{message.text}</b>""")

    await state.update_data(work_experience=message.text)
    await state.set_state(Interview.about_me)
    await message.answer(
        "5. Ниже расскажите о себе, к примеру, свои сильные и слабые стороны, хобби",
        reply_markup=data.get('cancel'))


@interview_router.message(and_f(Interview.about_me, F.text))
async def get_about_me(message: Message, state: FSMContext):
    try:
        await message.bot.edit_message_reply_markup(chat_id=message.from_user.id, message_id=message.message_id - 1)
    except Exception:
        ...
    data = await state.get_data()
    #     await message.answer(f"""
    # <b>Ваша карточка преподавателя:</b>
    # Имя - <b>{data.get('full_name')}</b>
    # Возраст - <b>{data.get('age')}</b>
    # Образование - <b>{data.get('education')}</b>
    # Опыт работы - <b>{data.get('work_experience')}</b>
    # Обо мне - <b>{message.text}</b>""")

    await state.update_data(about_me=message.text)
    await state.set_state(Interview.ege_doc)
    await message.answer(
        """6. Ниже прикрепите документ в формате PDF подтверждающий ваши баллы ЕГЭ (отправьте "-" если у вас нет такого документа)""",
        reply_markup=data.get('cancel'))


@interview_router.message(and_f(Interview.ege_doc))
async def get_ege_pdf(message: Message, state: FSMContext):
    try:
        await message.bot.edit_message_reply_markup(chat_id=message.from_user.id, message_id=message.message_id - 1)
    except Exception:
        pass

    data = await state.get_data()

    if message.text == "-":
        await state.update_data(ege_file="-")
        await state.set_state(Interview.hhru_doc)
        #         await message.answer(f"""
        # <b>Ваша карточка преподавателя:</b>
        # Имя - <b>{data.get('full_name')}</b>
        # Возраст - <b>{data.get('age')}</b>
        # Образование - <b>{data.get('education')}</b>
        # Опыт работы - <b>{data.get('work_experience')}</b>
        # Обо мне - <b>{data.get('about_me')}</b>
        # Документ "Баллы ЕГЭ" - <b>не заполнен</b>""")

        await message.answer(
            """Теперь отправьте ваше резюме с hh.ru
(если у вас нет такого документа или вы учитесь отправьте "-". """, reply_markup=data.get('cancel'))

    if message.text != "-" and message.document:
        document = message.document

        file_info = await message.bot.get_file(document.file_id)
        file_path = file_info.file_path

        if not file_path.endswith('.pdf'):
            await message.answer("Пожалуйста, отправьте файл с расширением .pdf.")
            return

        await state.set_state(Interview.hhru_doc)
        await state.update_data(ege_file=file_info)

        #         await message.answer(f"""
        # <b>Ваша карточка преподавателя:</b>
        # Имя - <b>{data.get('full_name')}</b>
        # Возраст - <b>{data.get('age')}</b>
        # Образование - <b>{data.get('education')}</b>
        # Опыт работы - <b>{data.get('work_experience')}</b>
        # Обо мне - <b>{data.get('about_me')}</b>
        # Документ "Баллы ЕГЭ": <b>заполнен</b>""")

        await message.answer(
            """<b>Ваш файл успешно сохранен.</b> 
Теперь отправьте ваше резюме с hh.ru 
(если у вас нет такого документа или вы учитесь отправьте "-". """, reply_markup=data.get('cancel'))


@interview_router.message(Interview.hhru_doc)
async def get_hhru_pdf(message: Message, state: FSMContext):
    try:
        await message.bot.edit_message_reply_markup(chat_id=message.from_user.id, message_id=message.message_id - 1)
    except Exception:
        pass

    data = await state.get_data()

    if message.text == "-":
        await state.update_data(hhru_file="-")
        await state.set_state(Interview.education_doc)
        #         await message.answer(f"""
        # <b>Ваша карточка преподавателя:</b>
        # Имя - <b>{data.get('full_name')}</b>
        # Возраст - <b>{data.get('age')}</b>
        # Образование - <b>{data.get('education')}</b>
        # Опыт работы - <b>{data.get('work_experience')}</b>
        # Обо мне - <b>{data.get('about_me')}</b>
        # Документ "Баллы ЕГЭ": <b>{"не заполнен" if data.get('ege_file') == "-" else "заполнен"}</b>
        # Документ "Резюме hh.ru": <b>не заполнен</b>""")

        await message.answer(
            """Теперь отправьте документ подтверждающий ваше образование в формате PDF 
(если у вас нет такого документа или вы учитесь отправьте "-". """, reply_markup=data.get('cancel'))

    if message.text != "-" and message.document:
        document = message.document

        file_info = await message.bot.get_file(document.file_id)
        file_path = file_info.file_path

        if not file_path.endswith('.pdf'):
            await message.answer("Пожалуйста, отправьте файл с расширением .pdf.")
            return
        await state.set_state(Interview.education_doc)
        await state.update_data(hhru_file=file_info)

        #         await message.answer(f"""
        # <b>Ваша карточка преподавателя:</b>
        # Имя - <b>{data.get('full_name')}</b>
        # Возраст - <b>{data.get('age')}</b>
        # Образование - <b>{data.get('education')}</b>
        # Опыт работы - <b>{data.get('work_experience')}</b>
        # Обо мне - <b>{data.get('about_me')}</b>
        # Документ "Баллы ЕГЭ": <b>{"не заполнен" if data.get('ege_file') == "-" else "заполнен"}</b>
        # Документ "Резюме hh.ru": <b>заполнен</b>""")

        await message.answer(
            """<b>Ваш файл успешно сохранен.</b> 
Теперь отправьте документ подтверждающий ваше образование в формате PDF 
(если у вас нет такого документа или вы учитесь отправьте "-". """, reply_markup=data.get('cancel'))


@interview_router.message(and_f(Interview.education_doc))
async def get_education_pdf(message: Message, state: FSMContext):
    try:
        await message.bot.edit_message_reply_markup(chat_id=message.from_user.id, message_id=message.message_id - 1)
    except Exception:
        pass

    data = await state.get_data()

    if message.text == "-":
        await state.update_data(education_file="-")
        await state.set_state(Interview.mail)
        #         await message.answer(f"""
        # <b>Ваша карточка преподавателя:</b>
        # Имя - <b>{data.get('full_name')}</b>
        # Возраст - <b>{data.get('age')}</b>
        # Образование - <b>{data.get('education')}</b>
        # Опыт работы - <b>{data.get('work_experience')}</b>
        # Обо мне - <b>{data.get('about_me')}</b>
        # Документ "Баллы ЕГЭ": <b>{"не заполнен" if data.get('ege_file') == "-" else "заполнен"}</b>
        # Документ "Резюме hh.ru": <b>{"не заполнен" if data.get('hhru_file') == "-" else "заполнен"}</b>
        # Документ "Об образовании": <b>не заполнен</b>""")

        await message.answer(
            text='<b>Ваш файл успешно сохранен.</b>Теперь отправьте вашу почту для дальнейшей связи с вами',
            reply_markup=data.get('cancel'))

    if message.text != "-" and message.document:
        document = message.document

        file_info = await message.bot.get_file(document.file_id)
        file_path = file_info.file_path

        if not file_path.endswith('.pdf'):
            await message.answer("Пожалуйста, отправьте файл с расширением .pdf.")
            return
        await state.set_state(Interview.mail)
        await state.update_data(education_file=file_info)

        #         await message.answer(f"""
        # <b>Ваша карточка преподавателя:</b>
        # Имя - <b>{data.get('full_name')}</b>
        # Возраст - <b>{data.get('age')}</b>
        # Образование - <b>{data.get('education')}</b>
        # Опыт работы - <b>{data.get('work_experience')}</b>
        # Обо мне - <b>{data.get('about_me')}</b>
        # Документ "Баллы ЕГЭ": <b>{"не заполнен" if data.get('ege_file') == "-" else "заполнен"}</b>
        # Документ "Резюме hh.ru": <b>{"не заполнен" if data.get('hhru_file') == "-" else "заполнен"}</b>
        # Документ "Об образовании": <b>заполнен</b>""")

        await message.answer(
            text='Теперь отправьте вашу почту для дальнейшей связи с вами',
            #"""<b>Ваш файл успешно сохранен.</b>
#Теперь напишите комментарий. В нем расскажите почему отсутствуют те или иные документы.
#Если все документы заполнены, отправьте прочерк ("-"). """
            reply_markup=data.get('cancel')
        )


@interview_router.callback_query(F.data == "back_to_interview")
async def back_to_interview(call: CallbackQuery, state: FSMContext):
    await call.message.delete()
    data = await state.get_data()
    keyboard = await continue_interview(data.get('teaching_type'))
    await state.set_state(None)
    await call.message.answer(f"""
<b>Ваша карточка преподавателя:</b>
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


Нажмите на кнопку продолжить, <b>если готовы приступить к собеседованию</b>
Далее бот начнет вам задавать вопросы на время (сообщения будут удаляться через некоторое количество времени)
От вас требуется в live-режиме <b>отвечать на вопросы и записывать аудио сообщение</b>, которое позже (после прохождения опроса) нужно будет отправить в этот чат"
""",
                              reply_markup=keyboard)


@interview_router.message(Interview.mail)
async def get_mail(message: Message, state: FSMContext):
    await state.update_data(mail=message.text)
    await state.set_state(Interview.comment_about_docs)
    data = await state.get_data()
    await message.answer(
        """<b>Ваша почта успешно сохранена</b>
Теперь напишите комментарий. В нем расскажите почему отсутствуют те или иные документы.
Если все документы заполнены, отправьте прочерк ("-"). """,
        reply_markup=data.get('cancel')
    )


@interview_router.message(and_f(F.text, Interview.comment_about_docs))
async def get_comment_about_docs(message: Message, state: FSMContext):
    try:
        await message.bot.edit_message_reply_markup(chat_id=message.from_user.id, message_id=message.message_id - 1)
    except Exception:
        pass
    await state.set_state(None)
    await state.update_data(comment_about_docs=message.text)
    data = await state.get_data()
    keyboard = await continue_interview(data.get('teaching_type'))
    await message.answer(f"""
<b>Ваша карточка преподавателя:</b>
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


Нажмите на кнопку продолжить, <b>если готовы приступить к собеседованию</b>
Далее бот начнет вам задавать вопросы на время (сообщения будут удаляться через некоторое количество времени)
От вас требуется в live-режиме <b>отвечать на вопросы и записывать аудио сообщение</b>, которое позже (после прохождения опроса) нужно будет отправить в этот чат"
""",
                         reply_markup=keyboard)
