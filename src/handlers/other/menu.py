import os
from os import listdir

from aiogram import Router, F
from aiogram.types import CallbackQuery, FSInputFile
from aiogram.fsm.context import FSMContext
from aiogram.utils.media_group import MediaGroupBuilder

from src.database import get_user_data
from src.keyboards import student_menu_keyboard, student_menu_back, confirmed_teacher

from src.keyboards import teacher_menu_back, teacher_start_menu_keyboard

menu_router = Router()


async def show_menu(call: CallbackQuery):
    user = await get_user_data(telegram_id=call.from_user.id)
    if user.role == "teacher":
        await call.message.answer(f"""
Ты находишься в главном меню.
""", reply_markup=teacher_start_menu_keyboard)
    elif user.role == "student":
        await call.message.answer(f"""
Вы находитесь в главном меню.
""", reply_markup=student_menu_keyboard)
    elif user.role == "confirmed_teacher":
        await call.message.answer("Вы находитесь в главном меню.",
                                  reply_markup=confirmed_teacher)


@menu_router.callback_query(F.data == "exit_ai_chat")
async def exit_ai_chat(call: CallbackQuery, state: FSMContext):
    await call.message.edit_reply_markup(reply_markup=None)
    await show_menu(call)


@menu_router.callback_query(F.data == "about_us")
async def show_about_us_info(call: CallbackQuery, state: FSMContext):
    user = await get_user_data(telegram_id=call.from_user.id)
    await call.message.delete()

    media = MediaGroupBuilder()
    
    # ID в боте
    # about_us_photos_ids = [
    #     'AgACAgIAAxkDAAIGwWcgvI_pBG7s_6qXbqVCZA-CcGrjAAJt4TEbtloISQGwbxlOpZZ1AQADAgADdwADNgQ',
    #     'AgACAgIAAxkDAAIGv2cgvIyaXK4a5skri7YhAnr1w55hAAJr4TEbtloISadwr5wCNqRHAQADAgADdwADNgQ',
    #     'AgACAgIAAxkDAAIGvmcgvItxUUVFdSJLaAo_qIel0r_tAAJq4TEbtloISasOn0XW36qIAQADAgADdwADNgQ',
    #     'AgACAgIAAxkDAAIGwGcgvI6-4qxWt_mCvHIBAUKawC50AAJs4TEbtloISdOmHqauLsGgAQADAgADdwADNgQ'
    # ]
    # for photo_id in about_us_photos_ids:
    #     media.add(type="photo", media=photo_id)
    # Временная замена
    about_us_images = [
        "src/pics/about_us/pic1.png",
        "src/pics/about_us/pic2.png",
        "src/pics/about_us/pic3.png",
        "src/pics/about_us/pic4.png"
    ]
    for img in about_us_images:
        media.add(
            type="photo",
            media=FSInputFile(img)
        )

    

    start_photos = await call.message.answer_media_group(media=media.build())
    await state.update_data(photos_to_delete=[msg.message_id for msg in start_photos])

    info = """Добро пожаловать в easyknow! 🎉 

Наша школа — это пространство, где обучение становится лёгким, увлекательным и эффективным.

Нас направляют миссия и философия школы, которые помогают нам вдохновлять учеников и делать процесс обучения по-настоящему интересным и лёгким! 🌟"""

    if user.role == "teacher":
        keyboard = teacher_menu_back
    else:
        keyboard = student_menu_back
    await call.message.answer(text=info, reply_markup=keyboard)


@menu_router.callback_query(F.data == "questions")
async def show_answers_to_questions(call: CallbackQuery, state: FSMContext):
    await call.message.delete()
    user = await get_user_data(telegram_id=call.from_user.id)
    info = """
<b>Можно ли выбрать индивидуальные занятия?</b>
- Конечно! У нас вы можете заниматься индивидуально или в группе до 6 человек. Формат занятий вы выбираете в разделе "Предметы" у нас в боте. Также у нас есть дополнительные занятия:клубы, челленджи, лаборатории, которые проходят в групповом формате по определенному расписанию. Расписание можно запросить у оператора.  

<b>Как оплатить занятия или подписку?</b>
- Все очень просто и комфортно! Нажимайте на кнопку "Предметы" и в этом разделе следуйте инструкциям Макса. Сначала вам нужно выбрать конкретный предмет, например: химия, затем мы рекомендуем пройти квиз, чтобы понять сколько занятий вам оптимальнее всего выбрать, с какой регулярностью заниматься и получить рекомендации в целом по обучению. Затем, вы выбираете формат занятий (индивидуально, в группе или доп занятия по подписке), после этого количество занятий в пакете, подписываете договор, оплачиваете и начинаете заниматься!  

<b>Есть ли возможность получить пробный урок?</b>  
- Наши методисты и кураторы предоставляют бесплатную комфортную консультацию при выборе формата занятий и количества занятий прямо в боте через чат "поддержка" или "оператор". Мы вам проедем квиз, узнаем ваши цели, сроки и дадим рекомендации! Также, мы вам покажем как проходят занятий на платформе, каким образом вы будете выполнять домашку и как вы будете отслеживать свой прогресс! 

<b>Как я буду следить за своим прогрессом?</b> 
- Отслеживать свой прогресс вы будете также в нашем чат-боте! Это очень удобно и наглядно. Вы будете прокачивать своего персонажа Макса! Он вас сопровождает на всем пути обучения.  После каждого занятия и домашки вам будут начисляться баллы, которые будут складываться и влият на уровень Макса. 
При открытии нового уровня выбудете получать награды и дополнительные опции!   
    """
    # ID в боте 
    # photo = 'AgACAgIAAxkDAAIG3GcgwR-DIbF00AXvKj1R3XVBBKUZAAKb4TEbtloISbDzSfLbV96zAQADAgADdwADNgQ'
    photo = FSInputFile('src/pics/questions/questions1.png')
    to_delete = None
    if user.role == "teacher":
        to_delete = await call.message.answer_photo(photo=photo)
        await call.message.answer(text=info, reply_markup=teacher_menu_back)
    if user.role == "student":
        to_delete = await call.message.answer_photo(photo=photo)
        await call.message.answer(text=info, reply_markup=student_menu_back)
    await state.update_data(photos_to_delete=[to_delete.message_id])


@menu_router.callback_query(F.data == "media")
async def show_media(call: CallbackQuery):
    await call.message.delete()
    # ID в боте
    # photo = "AgACAgIAAxkDAAIGCmcgtiwdnxpStjNCWyXR0ccSlXOIAAI84TEbtloISVNmmYEcixUgAQADAgADdwADNgQ"
    
    photo = FSInputFile("src/pics/media/media1.png")
    user = await get_user_data(telegram_id=call.from_user.id)

    media_info = '''
📚 Хотите всегда быть в курсе полезных лайфхаков для учёбы, новых курсов и крутых образовательных активностей? Подписывайтесь на нас в соцсетях и других медиа easyknow!  
🎉 Только там – актуальные советы, анонсы, мотивация и вдохновение для лёгкого обучения. Будьте с нами, чтобы не пропустить ничего важного и сделать каждый день продуктивнее!       
Ждём вас в нашем сообществе #easyknow! 🚀 '''

    if user.role == "teacher":
        await call.message.answer_photo(photo=photo,
                                        caption=media_info,
                                        reply_markup=teacher_menu_back)
    if user.role == "student":
        await call.message.answer_photo(photo=photo,
                                        caption=media_info,
                                        reply_markup=student_menu_back)


@menu_router.callback_query(F.data == "agreement")
async def show_agreement(call: CallbackQuery, state: FSMContext):
    user = await get_user_data(call.from_user.id)

    if user.role == "student":

        await call.message.delete()
        photo_media = MediaGroupBuilder()
        document_media = MediaGroupBuilder()

        # ID в боте 
        # agreement_photos_ids = [
        #     'AgACAgIAAxkDAAILiGckZnt11VDH6MLpPzulTQc3mEqpAALu4zEbeX8hSR253gacmEVaAQADAgADdwADNgQ',
        #     'AgACAgIAAxkDAAILhmckZnkxYLBHIcuCU1f5ZNByi2TPAALt4zEbeX8hSYDaDBAyZJrSAQADAgADdwADNgQ',
        #     'AgACAgIAAxkDAAILimckZn1-nC048sGluFIDp1X6LSm_AALw4zEbeX8hSfp6A6m3QmGZAQADAgADdwADNgQ',
        #     'AgACAgIAAxkDAAILjGckZoASa2KtVMPkC8aJDpC2IZpSAALx4zEbeX8hSYXgjL5RS_6TAQADAgADdwADNgQ'
        # ]

        # agreement_documents_ids = [
        #     'BQACAgIAAxkDAAIL3GckbQzrJv5F2J_-tdthbnCkiU6wAAKCXAACeX8hSZZl5w9bhdUYNgQ',
        #     'BQACAgIAAxkDAAIL3mckbQ3-GP4zSGzk_kJP1AAB4GE89QACg1wAAnl_IUlV_v2TDTubVjYE',
        # ]

        # for photo_id in agreement_photos_ids:
        #     photo_media.add(type='photo', media=photo_id)

        # for document_id in agreement_documents_ids:
        #     document_media.add(type='document', media=document_id)
        
        # Временная замена
        agreement_images = [
            "src/pics/agreement/student/agreement1.png",
            "src/pics/agreement/student/agreement2.png",
            "src/pics/agreement/student/agreement3.png",
            "src/pics/agreement/student/agreement4.png"
        ]
        
        agreement_documents = os.listdir('src/files/student_agreement')
        
        for img in agreement_images:
            photo_media.add(
                type="photo",
                media=FSInputFile(img)
            )
            
        for doc in agreement_documents:
            document_media.add(
                type="document",
                media=FSInputFile(path='src/files/student_agreement/' + doc)
            )

        photos = await call.message.answer_media_group(media=photo_media.build())
        documents = await call.message.answer_media_group(media=document_media.build())
        await state.update_data(
            photos_to_delete=[msg.message_id for msg in photos] + [msg.message_id for msg in documents])
        await call.message.answer('''
Здесь вы можете ознакомиться с Договором-Офертой и Правилами учебного распорядка. 
Если у вас возникнут какие-либо вопросы - обращайтесь в чат "Поддержка".        
''', reply_markup=student_menu_back)

    if user.role == "teacher":
        await call.message.delete()
        document_media = MediaGroupBuilder()
        for file in listdir('src/files/teacher_agreement_1'):
            document_media.add(type='document', media=FSInputFile(path=f'src/files/teacher_agreement_1/{file}'))
        documents = await call.message.answer_media_group(media=document_media.build())
        await state.update_data(
            photos_to_delete=[msg.message_id for msg in documents])
        await call.message.answer(text="""
Мы будем с вами работать по договору-оферте. 📄

Перед тем как начать проходить процесс найма, внимательно ознакомьтесь с основными положениями оферты об оказании услуг. 

Также, внимательно ознакомьтесь с Приложениями к оферте: условия оказания услуг, стандарт исполнителя, политикой по обработке персональных данных и соглашением на обработку персональных данных. 

Если у вас возникнут какие-нибудь вопросы, обязательно спрашивайте в чате "поддержка". 💬❓          
""", reply_markup=teacher_menu_back)


@menu_router.callback_query(F.data == "quit_support")
async def quit_support(call: CallbackQuery, state: FSMContext):
    await state.clear()
    try:
        await call.message.bot.edit_message_reply_markup(chat_id=call.from_user.id, message_id=call.message.message_id)
    except Exception as e:
        print(e)
    finally:
        await show_menu(call)
