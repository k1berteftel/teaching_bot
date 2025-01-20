import datetime
import os
import json
from pprint import pformat
from os import getenv

from aiogram import Router, F, Bot
from aiogram.fsm.context import FSMContext
from aiogram.filters import StateFilter, and_f
from aiogram.types import CallbackQuery, FSInputFile, Message
from aiogram.utils.media_group import MediaGroupBuilder

from src.gpt.ask import fetch_response
from src.handlers.fsm_models import TrainingInput, AIChat, Promo
from src.database.products import get_product_by_id, get_subject_categories, \
    get_products_by_category, get_languages_categories, get_subject_teachers
from src.database import update_user_role, get_user_data, add_product_to_user, get_user_by_username, get_count, add_count
from src.keyboards import subjects, subject_categories_builder, products_builder, product_actions_keyboard, \
    student_menu_back, language_categories_builder, training_type_builder, choose_lessons_builder, confirm_contract_builder, \
    user_name_builder, contract_builder, close_quiz_builder, payment_builder, custom_poll_builder, choose_teacher_builder, \
    choose_teacher_builder, confirmed_student, promo_close_keyboard
from src.payment.tbank_pay import init_payment, check_payment

from docx import Document
from typing import Any, Dict


def make_agreement(
        data: Dict[str, Any],
        output_path: str,
) -> str:
    example_doc = Document("src/files/student_agreement/Публичная_оферта.docx")

    # Перебираем все абзацы и ищем плейсхолдеры в формате {{key}}.
    for paragraph in example_doc.paragraphs:
        for key, value in data.items():
            if f'{{{{ {key} }}}}' in paragraph.text:
                paragraph.text = paragraph.text.replace(f'{{{{ {key} }}}}', str(value))

    example_doc.save(output_path)

    return output_path


group_prices = {
    8: 8898,
    16: 17535,
    24: 25911,
    32: 34026,
    40: 41879,
    48: 49470,
    56: 56801,
    64: 63870,
    72: 70678,
    80: 77224,
    88: 83509,
    96: 89533,
    104: 95295,
    112: 100796,
    120: 106036,
    128: 111014
}

individual_prices = {
    8: 12712,
    16: 25072,
    24: 37008,
    32: 48608,
    40: 59880,
    48: 70656,
    56: 81144,
    64: 91264,
    72: 100944,
    80: 110320,
    88: 119328,
    96: 127872,
    104: 136136,
    112: 144032,
    120: 151440,
    128: 158592
}


def get_price(lessons: int, training_type: str) -> int | None:
    if lessons not in [8, 16, 24, 32, 40, 48, 56, 64, 72, 80, 88, 96, 104, 112, 120, 128]:
        return None

    if training_type == 'individual':
        return individual_prices[lessons]
    else:
        return group_prices[lessons]


def get_discount_price(lessons: int, price: int) -> int | float:
    if lessons in range(16, 24):
        return round(price * 0.95)
    elif lessons in range(24, 32):
        return round(price * 0.90)
    elif lessons in range(32, 40):
        return round(price * 0.85)
    elif lessons in range(40, 129):
        return round(price * 0.80)
    else:
        return price


subject_router = Router()
APPLICATION_GROUP_ID = int(getenv('APPLICATION_GROUP_ID'))


@subject_router.callback_query(F.data == "subjects")
async def start_picking(call: CallbackQuery, state: FSMContext):
    await call.message.delete()
    await call.message.answer_photo(
        # ID в боте
        # photo="AgACAgIAAxkDAAIJC2cjpiAy94BElSlxMcjU7F-8avrKAALf4zEbeX8ZSTCFEuR8x_0QAQADAgADdwADNgQ",
        photo=FSInputFile("src/pics/subjects/subjects1.png"),
        caption="Выберите опцию ниже", reply_markup=subjects
    )


@subject_router.callback_query(F.data == "languages")
async def languages(call: CallbackQuery):
    await call.message.delete()
    languages_list = await get_languages_categories()
    languages_list = set(languages_list)
    product = await get_products_by_category('language', 'английский')
    if languages_list:
        keyboard = await language_categories_builder(languages_list)
        await call.message.answer("Выбери язык ниже:", reply_markup=keyboard)
    else:
        await call.message.answer("К сожалению, не удалось найти ни одного языка в базе. Повторите попытку позже"
                                     , reply_markup=student_menu_back)


@subject_router.callback_query(F.data.startswith("language|"))
async def choose_product_lang(call: CallbackQuery, state: FSMContext):
    await call.message.delete()
    await state.update_data(product_type="language", category=call.data.split("|")[1])
    builder: MediaGroupBuilder = MediaGroupBuilder()
    for image in os.listdir('src/pics/subject_prices'):
        if image.endswith('png'):
            builder.add_photo(media=FSInputFile(path=f'src/pics/subject_prices/{image}'))
    keyboard = await training_type_builder('languages')
    messages = []
    for msg in await call.message.answer_media_group(media=builder.build()):
        messages.append(msg.message_id)
    await state.update_data(photos_to_delete=messages)
    await call.message.answer('Выберите формат занятий', reply_markup=keyboard)

    #category_products = await get_products_by_category(product_type="language", category=call.data.split("|")[1])
    #if category_products:
        #keyboard = await products_builder(category_products)
        #await call.message.edit_text("Выберите пункт для покупки ниже:", reply_markup=keyboard)
    #else:
        #await call.message.edit_text(
            #"Упс! Произошла внутренняя ошибка: не удалось найти предмет в базе. Пожалуйста, обратитесь в поддержку!",
            #reply_markup=student_menu_back)


@subject_router.callback_query(F.data == "school_subjects")
async def school_subjects(call: CallbackQuery):
    await call.message.delete()
    subjects_categories = await get_subject_categories()
    subjects_categories = set(subjects_categories)
    if subjects_categories:
        keyboard = await subject_categories_builder(subjects_categories)
        await call.message.answer("Выбери предмет ниже:", reply_markup=keyboard)
    else:
        await call.message.answer("К сожалению, не удалось найти ни одного предмета в базе. Повторите попытку позже",
                                     reply_markup=student_menu_back)


@subject_router.callback_query(F.data.startswith("school_subject|"))
async def choose_product_sub(call: CallbackQuery, state: FSMContext):
    await call.message.delete()
    await state.update_data(product_type="subject", category=call.data.split("|")[1])
    builder: MediaGroupBuilder = MediaGroupBuilder()
    for image in os.listdir('src/pics/subject_prices'):
        if image.endswith('png'):
            builder.add_photo(FSInputFile(f'src/pics/subject_prices/{image}'))
    keyboard = await training_type_builder('school_subjects')
    messages = []
    for msg in await call.message.answer_media_group(builder.build()):
        messages.append(msg.message_id)
    await state.update_data(photos_to_delete=messages)
    await call.message.answer('Выберите формат занятий', reply_markup=keyboard)

    #category_products = await get_products_by_category(product_type="subject", category=call.data.split("|")[1])
    #if category_products:
        #keyboard = await products_builder(category_products)
        #await call.message.edit_text("Выберите пункт для покупки ниже:", reply_markup=keyboard)
    #else:
        #await call.message.edit_text(
            #"Упс! Произошла внутренняя ошибка: не удалось найти предмет в базе. Пожалуйста, обратитесь в поддержку!",
            #reply_markup=student_menu_back)


@subject_router.callback_query(F.data.startswith('training_type'))
async def choose_training_type(call: CallbackQuery, state: FSMContext):
    await call.message.delete()
    data = await state.get_data()
    await state.update_data(training_type=call.data.split('|')[1], messages=None)
    clb = (('school_subject' if data.get('product_type') == 'subject' else data.get('product_type'))
           + f'|{data.get("category")}')
    keyboard = await choose_lessons_builder(clb)
    text = ('Если вы уже определились сколько занятий в пакете вам комфортнее и оптимальнее всего выбрать, '
            'введите число с количеством занятий, которое соответствует значению в таблице выше '
            '(например: 8, 24, 40).\n\nЕсли же сомневаетесь, мы вам рекомендуем пройти небольшой квиз!')
    await state.set_state(TrainingInput.waiting_for_integer)
    await call.message.answer(text, reply_markup=keyboard)


@subject_router.callback_query(F.data == 'quiz')
async def quiz_dialog(call: CallbackQuery, state: FSMContext):
    await state.set_state(AIChat.chatting)
    await call.message.delete()
    data = await state.get_data()
    prompt = (f'''Ты - методист школы. Твоя задача помочь ученику выбрать оптимальное количество занятий, чтобы заниматься и дать рекомендации после прохождения опроса. 
Учти что мы онлайн-школа.
Информация по предмету обучения:\nПредмет: {data.get('category')}\nТип занятий: {"Индивидуальный" if data.get('training_type') == 'individual' else "Групповые"}
Задай ученику ряд вопросов, которые включают цели, сроки для изучения предмета, спроси про домашку и так далее. 
Задай максимум 10 вопросов
Верни вопросы в формате JSON (БЕЗ РАЗМЕТОК, ПРОСТО ФИГУРНЫЕ СКОБКИ - ЭТО ВАЖНО), где каждый вопрос обозначен ключом от 1 до 10:
{{
     "1": "вопрос 1",
     "2": "вопрос 2",
     ...
     "10": "вопрос 10"
}}''')
    response = await fetch_response(prompt)
    if not response:
        await call.message.answer("Ошибка при генерации вопросов. Попробуйте снова.")
        return
    try:
        questions = json.loads(response)
    except json.JSONDecodeError or TypeError as err:
        print(err)
        await call.message.answer("Ошибка при генерации вопросов. Попробуйте снова.")
        return
    count = 1
    await state.update_data(questions=questions, count=count)
    keyboard = await close_quiz_builder(f'training_type|{data.get("training_type")}')
    await call.message.answer(questions[str(count)], reply_markup=keyboard)


@subject_router.message(StateFilter(AIChat.chatting))
async def get_recommendation(msg: Message, state: FSMContext):
    try:
        await msg.bot.edit_message_reply_markup(chat_id=msg.from_user.id, message_id=msg.message_id - 1)
    except Exception:
        ...
    data = await state.get_data()
    count = data.get('count')
    if count == 10:
        formatted_questions = pformat(data.get('questions'))
        prompt = (f'''Ты - методист школы. Твоя задача помочь ученику выбрать оптимальное количество занятий, 
чтобы заниматься и дать рекомендации после прохождения опроса. Учти что мы онлайн-школа.\n
Вот вопросы на которые отвечал ученик:\n{formatted_questions}\n
Вот ответы ученика на данные вопросы:\n {data.get('answers')}\nТвоя задача дать ученику рекомендации по оптимальному для ученика количеству занятий в месяц''')
        answer = await fetch_response(prompt)
        keyboard = await close_quiz_builder(f'training_type|{data.get("training_type")}')
        await state.set_state(None)
        await msg.answer(answer, reply_markup=keyboard)
        return
    questions = data.get('questions')
    answers = data.get('answers', '')
    answers += f"\nВопрос: {questions[str(count)]}\n Ответ: {msg.text}\n"
    count += 1
    await state.update_data(answers=answers, count=count)
    keyboard = await close_quiz_builder(f'training_type|{data.get("training_type")}')
    await msg.answer(questions[str(count)], reply_markup=keyboard)


@subject_router.message(and_f(F.text, StateFilter(TrainingInput.waiting_for_integer)))
async def confirm_contract(msg: Message, state: FSMContext):
    await msg.delete()
    try:
        trainings = int(msg.text)
    except Exception as err:
        await msg.answer('Кол-во занятий должно быть числом, пожалуйста попробуйте снова')
        return
    data = await state.get_data()
    price = get_price(trainings, data.get('training_type'))
    if price is None:
        await msg.answer('Кол-во занятий должно соответствовать выбранному покету занятий, пожалуйста попробуйте снова')
        return
    try:
        await msg.bot.delete_message(chat_id=msg.from_user.id, message_id=msg.message_id - 1)
    except Exception:
        ...
    await state.update_data(trainings=trainings, price=price)
    discount_price = get_discount_price(trainings, price)
    if discount_price != price:
        await state.set_state(Promo.waiting)
        await msg.answer('Введите промокод', reply_markup=promo_close_keyboard)
        return
    builder: MediaGroupBuilder = MediaGroupBuilder()
    for document in os.listdir('src/files/student_agreement_1'):
        builder.add_document(media=FSInputFile(f'src/files/student_agreement_1/{document}'))
    messages = []
    for mess in await msg.answer_media_group(builder.build()):
        messages.append(mess.message_id)
    await state.update_data(photos_to_delete=messages)
    await state.set_state(None)
    keyboard = await confirm_contract_builder(f'training_type|{data.get("training_type")}')
    text = ('Перед тем, как мы приступим к заполнению заявки (Приложение в конце договора-оферты), '
            'вам нужно подтвердить свое согласие на обработку персональных данных.\n\n'
            'Я даю согласие ООО "Изиноу" (ОГРН 1242700016558) на обработку персональных данных на условиях'
            ' Политики в отношении обработки и защиты персональных данных в целях заполнения Приложения '
            'к договору-оферте (заявка), регистрации на платформе и получении информационных сообщений от школы.  ')
    await msg.answer(text, reply_markup=keyboard)


@subject_router.message(StateFilter(Promo.waiting))
async def get_promo(msg: Message, state: FSMContext):
    data = await state.get_data()
    count = await get_count()
    if msg.text == 'EASY100' and count < 100:
        discount_price = get_discount_price(data.get('trainings'), data.get('price'))
        await state.update_data(price=discount_price, discount=True)
        await msg.answer('Промокод был успешно засчитан, вы получили скидку!')
    elif msg.text == '-':
        ...
    else:
        await msg.answer('Промокод неверен')
    builder: MediaGroupBuilder = MediaGroupBuilder()
    for document in os.listdir('src/files/student_agreement_1'):
        builder.add_document(media=FSInputFile(f'src/files/student_agreement_1/{document}'))
    messages = []
    for mess in await msg.answer_media_group(builder.build()):
        messages.append(mess.message_id)
    await state.update_data(photos_to_delete=messages)
    await state.set_state(None)
    keyboard = await confirm_contract_builder(f'training_type|{data.get("training_type")}')
    text = ('Перед тем, как мы приступим к заполнению заявки (Приложение в конце договора-оферты), '
            'вам нужно подтвердить свое согласие на обработку персональных данных.\n\n'
            'Я даю согласие ООО "Изиноу" (ОГРН 1242700016558) на обработку персональных данных на условиях'
            ' Политики в отношении обработки и защиты персональных данных в целях заполнения Приложения '
            'к договору-оферте (заявка), регистрации на платформе и получении информационных сообщений от школы.  ')
    await msg.answer(text, reply_markup=keyboard)


@subject_router.callback_query(F.data == 'confirm_contract')
async def confirm_agreement(call: CallbackQuery, state: FSMContext):
    await state.update_data(messages=None)
    await call.message.delete()
    text = ('Для оформления заявки на оказание образовательных услуг, пожалуйста, заполните следующие '
            'данные. Сначала укажите свои данные как Заказчика, затем информацию о Получателе услуг. '
            'Например, ваш ребенок. Если вы являетесь Получателем услуг, продублируйте свои данные во '
            'второй части заявки\n\nВведите ваше полное имя (ФИО)')
    keyboard = await user_name_builder()
    await state.set_state(TrainingInput.waiting_for_name)
    await call.message.answer(text=text, reply_markup=keyboard)


@subject_router.message(and_f(F.text, StateFilter(TrainingInput.waiting_for_name)))
async def get_name(msg: Message, state: FSMContext):
    await msg.delete()
    try:
        await msg.bot.delete_message(chat_id=msg.from_user.id, message_id=msg.message_id - 1)
    except Exception:
        ...
    await state.update_data(name=msg.text)
    keyboard = await custom_poll_builder('back_get_name')
    await state.set_state(TrainingInput.waiting_for_phone)
    await msg.answer('Введите ваш контактный телефон', reply_markup=keyboard)


@subject_router.message(and_f(F.text, StateFilter(TrainingInput.waiting_for_phone)))
async def get_phone(msg: Message, state: FSMContext):
    await msg.delete()
    try:
        await msg.bot.delete_message(chat_id=msg.from_user.id, message_id=msg.message_id - 1)
    except Exception:
        ...
    try:
        int(msg.text)
    except Exception:
        await msg.answer('Номер телефона некорректен, пожалуйста попробуйте снова')
        return
    await state.update_data(phone=msg.text)
    keyboard = await custom_poll_builder('back_get_phone')
    await state.set_state(TrainingInput.waiting_for_mail)
    await msg.answer('Введите вашу электронную почту', reply_markup=keyboard)


@subject_router.message(and_f(F.text, StateFilter(TrainingInput.waiting_for_mail)))
async def get_mail(msg: Message, state: FSMContext):
    await msg.delete()
    try:
        await msg.bot.delete_message(chat_id=msg.from_user.id, message_id=msg.message_id - 1)
    except Exception:
        ...
    await state.update_data(mail=msg.text)
    keyboard = await custom_poll_builder('back_get_mail')
    await state.set_state(TrainingInput.waiting_for_receiver_name)
    await msg.answer('Введите полное имя Получателя услуг (ваше или вашего ребенка)', reply_markup=keyboard)


@subject_router.message(and_f(F.text, StateFilter(TrainingInput.waiting_for_receiver_name)))
async def get_receiver_name(msg: Message, state: FSMContext):
    await msg.delete()
    try:
        await msg.bot.delete_message(chat_id=msg.from_user.id, message_id=msg.message_id - 1)
    except Exception:
        ...
    await state.update_data(receiver_name=msg.text)
    keyboard = await custom_poll_builder('back_get_receiver_name')
    await state.set_state(TrainingInput.waiting_for_receiver_mail)
    await msg.answer('Введите электронную почту Получателя услуг', reply_markup=keyboard)


@subject_router.message(and_f(F.text, StateFilter(TrainingInput.waiting_for_receiver_mail)))
async def get_receiver_mail(msg: Message, state: FSMContext):
    await msg.delete()
    try:
        await msg.bot.delete_message(chat_id=msg.from_user.id, message_id=msg.message_id - 1)
    except Exception:
        ...
    await state.update_data(receiver_mail=msg.text)
    keyboard = await custom_poll_builder('back_get_receiver_mail')
    await state.set_state(TrainingInput.waiting_for_username)
    await msg.answer('Введите юзернейм пользователя на которого вы хотите приобрести обучение или "-" если '
                     'вы приобретаете на данный аккаунт\n'
                     '<em>! Важно чтобы пользователь хоть раз запускал бота</em>', reply_markup=keyboard)


@subject_router.message(and_f(F.text, StateFilter(TrainingInput.waiting_for_username)))
async def get_username(msg: Message, state: FSMContext):
    try:
        await msg.bot.delete_message(chat_id=msg.from_user.id, message_id=msg.message_id - 1)
    except Exception:
        ...
    if msg.text != '-':
        user = await get_user_by_username(msg.text)
        if user is None:
            await msg.answer('Данного пользователя нет в базе данных бота, пожалуйста попробуйте снова')
            return
        await state.update_data(username=msg.text)
    else:
        await state.update_data(username=None)
    await msg.delete()
    keyboard = await custom_poll_builder('back_get_username')
    await state.set_state(TrainingInput.waiting_for_class)
    await msg.answer('Введите класс обучения Получателя услуг (укажите цифру или поставьте прочерк)', reply_markup=keyboard)


@subject_router.message(and_f(F.text, StateFilter(TrainingInput.waiting_for_class)))
async def get_class(msg: Message, state: FSMContext):
    await msg.delete()
    try:
        await msg.bot.delete_message(chat_id=msg.from_user.id, message_id=msg.message_id - 1)
    except Exception:
        ...
    try:
        class_ = int(msg.text)
    except Exception:
        if msg.text != '-':
            await msg.answer('Класс должен быть числом или вместо него должен быть прочерк: -')
            return
        class_ = msg.text
    await state.update_data(class_=class_)
    await state.set_state(None)
    user = await get_user_data(msg.from_user.id)
    text = (f'{user.name}, внимательно ознакомитесь  с публичной офертой и Приложением (Заявка) к ней. '
            f'Убедитесь, что все данные правильно внесены  в Заявку: ФИО, количество занятий в пакете, '
            f'формат занятий, стоимость одного занятия и общая стоимость.\n\n'
            f'Если все правильно и у вас не возникли вопросы, нажимайте на кнопку "ознакомился (-ась). '
            f'Если вам потребуется откорректировать данные - вернитесь назад и заполните данные заново.')
    keyboard = await contract_builder()
    builder: MediaGroupBuilder = MediaGroupBuilder()
    builder.add_document(FSInputFile('src/files/student_agreement/Правила распорядка.docx'))
    data = await state.get_data()
    datas = {
        'name': data.get('name'),
        'phone': data.get('phone'),
        'mail': data.get('mail'),
        'receiver_name': data.get('receiver_name'),
        'receiver_mail': data.get('receiver_mail'),
        'class': data.get('class_'),
        'subject': data.get('category'),
        'trainings': data.get('trainings'),
        'training_type': "Индивидуальный" if data.get('training_type') == 'individual' else "Групповые",
        'price': data.get('price') / data.get('trainings'),
        'full_price': data.get('price'),
        'date': datetime.datetime.today().strftime('%d.%m.%Y')
    }
    agreement = make_agreement(datas, output_path=f'Публичная_оферта_{user.name}.docx')
    builder.add_document(FSInputFile(path=agreement))
    messages = []
    for mess in await msg.answer_media_group(builder.build()):
        messages.append(mess.message_id)
    await state.update_data(photos_to_delete=messages)
    await msg.answer(text, reply_markup=keyboard)
    try:
        os.remove(agreement)
    except Exception as err:
        print(err)


@subject_router.callback_query(F.data == 'confirm')
async def confirm(clb: CallbackQuery, state: FSMContext):
    await clb.message.delete()
    data = await state.get_data()
    description = (f"Покупка {data.get('trainings')} {'индивидуальных' if data.get('individual') else 'групповых'}"
                   f" по предмету: {data.get('category')}")
    payment = await init_payment(data.get('price'), description, clb.from_user.id)
    await state.update_data(payment_id=payment['payment_id'])
    text = 'Вот ваш счет на оплату\nПосле оплаты обязательно нажмите на кнопку "Проверить оплату"'
    keyboard = await payment_builder(payment['url'])
    await clb.message.answer(text, reply_markup=keyboard)


@subject_router.callback_query(F.data == 'check_payment')
async def check_pay(call: CallbackQuery, state: FSMContext, bot: Bot):
    data = await state.get_data()
    try:
        status: bool = await check_payment(data.get('payment_id'))
    except Exception:
        await call.message.answer('Что-то пошло не так, пожалуйста попробуйте снова или обратитесь в поддержку')
        return
    if not status:
        await call.answer('Оплата не была совершенна, пожалуйста попробуйте еще')
        return
    await call.answer('Оплата была успешно подтверждена')
    datas = {
        'name': data.get('name'),
        'phone': data.get('phone'),
        'mail': data.get('mail'),
        'receiver_name': data.get('receiver_name'),
        'receiver_mail': data.get('receiver_mail'),
        'class': data.get('class_'),
        'subject': data.get('category'),
        'trainings': data.get('trainings'),
        'training_type': "Индивидуальный" if data.get('training_type') == 'individual' else "Групповые",
        'price': data.get('price') / data.get('trainings'),
        'full_price': data.get('price'),
        'date': datetime.datetime.today().strftime('%d.%m.%Y')
    }
    username = data.get("username")
    user = await get_user_data(call.from_user.id)
    agreement = make_agreement(datas, output_path=f'Публичная_оферта_{user.name}.docx')
    caption = (f'<b>Заявка от пользователя {user.name}</b>\nID: {call.from_user.id}\n\nЗаказчик:\n'
               f'- ФИО: {data.get("name")}\n- Контактный телефон: {data.get("phone")}\n'
               f'email: {data.get("mail")}\n\nПолучатель услуг:\nФИО: {data.get("receiver_name")}\n'
               f'email: {data.get("receiver_mail")}\nКласс: {data.get("class_")}\n\n'
               f'Услуги:\n- Предмет: {data.get("category")}\n- Кол-во занятий: {data.get("trainings")}\n'
               f'- Формат занятий: {"Индивидуальный" if data.get("training_type") == "individual" else "Групповые"}\n'
               f'- Итоговая стоимость: {data.get("price")}')
    user = await get_user_by_username(username) if username else user
    teachers = await get_subject_teachers(data.get('category'))
    keyboard = await choose_teacher_builder(teachers, user.telegram_id, data.get('category'))
    await bot.send_document(
        chat_id=APPLICATION_GROUP_ID,
        document=FSInputFile(path=agreement),
        caption=caption,
        reply_markup=keyboard
    )
    caption = """Добро пожаловать в вашу учебную программу в easyknow!

В главном меню вы найдете несколько полезных функций:

<b>📩 Поддержка</b>
Если у вас возникли вопросы, связанные с обучением, школой, расписанием или оплатой, смело обращайтесь сюда. Наши специалисты оперативно вам помогут!
<b>🛠️ Техническая поддержка</b>
Сюда вы можете писать, если возникли технические трудности: сбои в работе бота, проблемы с подключением к урокам или другие неполадки.
<b>👩‍🏫 Мой учитель</b>
Это ваш чат с учителем по выбранному предмету. Задавайте вопросы, уточняйте детали по урокам и получайте помощь в выполнении домашних заданий.
<b>📊 Мой прогресс</b>
В этом разделе вы можете следить за своим прогрессом: уровень вашего напарника Макса, ваш рейтинг и достижения.
<b>🤖 Мой Макс</b>
Перед началом обучения перейдите в этот раздел! Макс — ваш виртуальный напарник
    """
    media = MediaGroupBuilder(caption=caption)
    photos = os.listdir('src/pics/confirmed_student_start')
    for photo in photos:
        media.add_photo(
            media=FSInputFile(f'src/pics/confirmed_student_start/{photo}')
        )
    if username is not None:
        user = await get_user_by_username(data.get('username'))
        await update_user_role(user.telegram_id, 'confirmed_student')
        await add_product_to_user(user.telegram_id, data.get('category'))
        await call.bot.send_media_group(
            chat_id=user.telegram_id,
            media=media.build()
        )
        await call.bot.send_message(
            chat_id=user.telegram_id,
            text='Ты в главном меню',
            reply_markup=confirmed_student
        )
    else:
        await update_user_role(call.from_user.id, 'confirmed_student')
        await add_product_to_user(call.from_user.id, data.get('category'))
        await call.message.answer_media_group(media=media.build())
        await call.message.answer(
            text='Ты в главном меню',
            reply_markup=confirmed_student
        )
    if data.get('discount') is not None:
        await add_count()
    try:
        os.remove(agreement)
    except Exception as err:
        print(err)


@subject_router.callback_query(F.data.startswith("product|"))
async def product_actions(call: CallbackQuery, state: FSMContext):
    product = await get_product_by_id(int(call.data.split("|")[1]))
    if product:
        keyboard = await product_actions_keyboard(product_type=product.product_type, category=product.subject)
        await call.message.edit_text(f"""
Вы выбрали: {product.name}
{"Предмет" if product.product_type == "subject" else "Язык"}: {product.subject}
Количество уроков в пакете: {product.lessons_quantity}
Цена товара: {product.price}
Описание: {product.description}
""", reply_markup=keyboard)
