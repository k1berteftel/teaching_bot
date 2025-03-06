from os import listdir

from aiogram import Router, F
from aiogram.types import CallbackQuery, FSInputFile, Message
from aiogram.fsm.context import FSMContext
from aiogram.filters import StateFilter, and_f
from aiogram.utils.media_group import MediaGroupBuilder
from dotenv import load_dotenv

from src.gpt.ask import fetch_response
from src.database.products import get_partner_subject
from src.database.user import get_user_partners, add_user_balls
from src.database import update_user_role, get_user_data, ProductModel, UserModel
from src.handlers import AIChat
from src.keyboards import (teacher_start_menu_keyboard, confirmed_teacher,
                           confirmed_teacher_agreement_keyboard, chatting_student_builder, stop_chatting_teacher,
                           teacher_management_builder, activity_balls_builder, choose_student_builder)
from src.keyboards.back import quit_ai_chat
from src.handlers.fsm_models import PartnerChatting, TeacherManagement

teacher_router = Router()
load_dotenv()


@teacher_router.callback_query(F.data == "teacher_main_menu")
async def teacher_main_menu(call: CallbackQuery, state: FSMContext):
    user = await get_user_data(call.from_user.id)
    if user:
        await call.message.delete()
        await state.clear()
        if user.role == "confirmed_teacher":
            await call.message.answer(f"""Ты находишься в главном меню.""", reply_markup=confirmed_teacher)
        elif user.role == "teacher":
            await call.message.answer(f"""Ты находишься в главном меню.""", reply_markup=teacher_start_menu_keyboard)
    else:
        await call.message.answer("Не удалось получить данные о пользователе. Пропишите команду /start ")


@teacher_router.callback_query(F.data == "teacher_accepted")
async def show_agreement(call: CallbackQuery, state: FSMContext):
    user = await get_user_data(call.from_user.id)
    await call.message.delete()
    documents_media = MediaGroupBuilder()

    for doc in listdir('src/files/teacher_agreement'):
        document = FSInputFile(path=f"src/files/teacher_agreement/{doc}")
        documents_media.add_document(media=document)

    start_photos = await call.message.answer_media_group(media=documents_media.build())
    await state.update_data(photos_to_delete=[msg.message_id for msg in start_photos])

    await call.message.answer(text=f"""
{user.name}!   
Перед тем как вы приступите к обучению, внимательно ознакомьтесь с Офертой на оказание информационно-консультационных услуг и с ее Приложениями (условия оказания услуг и  стандарт исполнителя). 

Оферта считается принятой, а Договор заключенным и вступившим в силу, с момента введения вами на платформе логина и пароля, полученного от нас.   

Когда ознакомитесь с Офертой и Приложениями, нажимайте кнопку "Ознакомился(-ась). 
Если у вас возникнут вопросы, обязательно обращайтесь в чат "поддержка".  

С уважением, Команда easyknow      
""", reply_markup=confirmed_teacher_agreement_keyboard)


@teacher_router.callback_query(F.data == "ai_chat")
async def ai_chat(call: CallbackQuery, state: FSMContext):
    await state.set_state(AIChat.chatting)
    await call.message.edit_text("""
Привет, учителя и наставники! Добро пожаловать в чат «Полигон». Здесь вы можете получать экспертные рекомендации от ChatGPT по вопросам методик преподавания, создания эффективных уроков и лучших практик обучения. 

Используйте ChatGPT для: 
1. Тестирования гипотез: Задавайте вопросы и проверяйте идеи о том, как улучшить учебные программы и методы преподавания. 
2. Методологические советы: Получите рекомендации по оптимальным методам обучения, планированию уроков и индивидуальному подходу к учащимся. 
3. Рекомендации по работе с учениками: Советы по адаптации учебных материалов, взаимодействию с учениками и мотивации к учебе.     

Примеры запросов: 
- «Какую методологию можно использовать для обучения трудным темам в физике?» 
- «Какие интерактивные методы преподавания подойдут для улучшения навыков общения на английском языке?» 
- «Как построить обратную связь с учениками по итогам контрольной работы?»  

Задавайте ваши вопросы и получайте ответы на основе современных исследований и опыта в педагогике!
""", reply_markup=quit_ai_chat)


@teacher_router.message(AIChat.chatting)
async def chat_with_ai(message: Message, state: FSMContext):
    if message.text:
        response = await fetch_response(
            prompt=f"Ты наставник - методист для учителей по иностранным языкам и школьным предметам. \n{message.text}")
        await message.answer(response)


@teacher_router.callback_query(F.data == "my_students")
async def my_students(clb: CallbackQuery, state: FSMContext):
    await state.clear()
    students = await get_user_partners(clb.from_user.id)
    if students is None:
        await clb.answer('К сожалению пока что у вас нет учеников, как только вам определят ученика мы вас уведомим')
        return
    await clb.message.delete()
    keyboard = await chatting_student_builder(students)
    await clb.message.answer('Выберите чат с учителем', reply_markup=keyboard)


@teacher_router.message(StateFilter(PartnerChatting.teacher))
async def send_message_to_student(message: Message, state: FSMContext):
    data = await state.get_data()
    user = await get_user_data(message.from_user.id)
    partner: UserModel = data.get('partner')
    subject: ProductModel = data.get('subject')
    await message.bot.send_message(
        chat_id=partner.telegram_id,
        text=f'Сообщение от учителя <b>{user.name}</b>, по предмету: <b>{subject.subject}</b>'
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
        reply_markup=stop_chatting_teacher
    )


@teacher_router.callback_query(F.data == 'teacher_balls_management')
async def send_choose_my_student(clb: CallbackQuery, state: FSMContext):
    await state.clear()
    students = await get_user_partners(clb.from_user.id)
    if students is None:
        await clb.answer('К сожалению пока что у вас нет учеников, как только вам определят ученика мы вас уведомим')
        return
    await clb.message.delete()
    keyboard = await choose_student_builder(students)
    await state.set_state(TeacherManagement.choose_student)
    await clb.message.answer('Выберите ученика которому вы хотели бы начислить баллов', reply_markup=keyboard)


@teacher_router.callback_query(and_f(F.data.startswith('choose_student'), StateFilter(TeacherManagement.choose_student)))
async def teacher_management_menu(clb: CallbackQuery, state: FSMContext):
    await clb.message.delete()
    student_id = int(clb.data.split('|')[1])
    await state.update_data(student_id=student_id)
    keyboard = await teacher_management_builder()
    await clb.message.answer(
        'Выберите пункт за который вы хотели бы начислить баллы ученику',
        reply_markup=keyboard
    )


@teacher_router.callback_query(F.data.startswith('manage'))
async def teacher_manage_selector(clb: CallbackQuery, state: FSMContext):
    await clb.message.delete()
    category = clb.data.split('|')[1]
    keyboard = await activity_balls_builder(category)
    await clb.message.answer('Выберите за что вы бы хотели начислить ученику', reply_markup=keyboard)


@teacher_router.callback_query(F.data.startswith('add_balls'))
async def teacher_add_balls(clb: CallbackQuery, state: FSMContext):
    await clb.message.delete()
    data = await state.get_data()
    balls = int(clb.data.split('|')[1])
    student_id = data.get('student_id')
    await add_user_balls(student_id, balls)
    await clb.answer('Баллы были успешно начислены')

    keyboard = await teacher_management_builder()
    await clb.message.answer(
        'Выберите пункт за который вы хотели бы начислить баллы ученику',
        reply_markup=keyboard
    )