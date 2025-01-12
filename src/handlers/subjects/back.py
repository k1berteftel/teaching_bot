import os
import datetime

from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from aiogram.filters import StateFilter, and_f
from aiogram.types import CallbackQuery, FSInputFile, Message
from aiogram.utils.media_group import MediaGroupBuilder

from src.handlers.fsm_models import TrainingInput
from src.handlers.subjects.pick_subjects import make_agreement
from src.keyboards import confirm_contract_builder, contract_builder, custom_poll_builder, user_name_builder
from src.database import get_user_data


back_subject_router = Router()


@back_subject_router.callback_query(F.data == 'back_confirm_contract')
async def back_confirm_contract(call: CallbackQuery, state: FSMContext):
    datas = await state.get_data()
    for msg in datas.get('messages'):
        await msg.delete()
    builder: MediaGroupBuilder = MediaGroupBuilder()
    for document in os.listdir('src/documents'):
        builder.add_document(media=FSInputFile(f'src/documents/{document}'))
    messages = []
    for mess in await call.message.answer_media_group(builder.build()):
        messages.append(mess.message_id)
    await state.update_data(messages=messages)
    await state.set_state(None)
    keyboard = await confirm_contract_builder()
    text = ('Перед тем, как мы приступим к заполнению заявки (Приложение в конце договора-оферты), '
            'вам нужно подтвердить свое согласие на обработку персональных данных.\n\n'
            'Я даю согласие ООО "Изиноу" (ОГРН 1242700016558) на обработку персональных данных на условиях'
            ' Политики в отношении обработки и защиты персональных данных в целях заполнения Приложения '
            'к договору-оферте (заявка), регистрации на платформе и получении информационных сообщений от школы.  ')
    await call.message.answer(text, reply_markup=keyboard)
    await call.message.delete()


@back_subject_router.callback_query(F.data == 'back_get_user_name', StateFilter(TrainingInput.waiting_for_name))
async def back_get_name(call: CallbackQuery, state: FSMContext):
    await call.message.delete()
    data = await state.get_data()
    builder: MediaGroupBuilder = MediaGroupBuilder()
    for document in os.listdir('src/files/student_agreement_1'):
        builder.add_document(media=FSInputFile(f'src/files/student_agreement_1/{document}'))
    messages = []
    for mess in await call.message.answer_media_group(builder.build()):
        messages.append(mess.message_id)
    await state.update_data(photos_to_delete=messages)
    await state.set_state(None)
    keyboard = await confirm_contract_builder(f'training_type|{data.get("training_type")}')
    text = ('Перед тем, как мы приступим к заполнению заявки (Приложение в конце договора-оферты), '
            'вам нужно подтвердить свое согласие на обработку персональных данных.\n\n'
            'Я даю согласие ООО "Изиноу" (ОГРН 1242700016558) на обработку персональных данных на условиях'
            ' Политики в отношении обработки и защиты персональных данных в целях заполнения Приложения '
            'к договору-оферте (заявка), регистрации на платформе и получении информационных сообщений от школы.  ')
    await call.message.answer(text, reply_markup=keyboard)


@back_subject_router.callback_query(and_f(F.data == 'back_get_name', StateFilter(TrainingInput.waiting_for_phone)))
async def back_get_name(clb: CallbackQuery, state: FSMContext):
    await clb.message.delete()
    text = 'Введите ваше полное имя (ФИО)'
    keyboard = await user_name_builder()
    await state.set_state(TrainingInput.waiting_for_name)
    await clb.message.answer(text=text, reply_markup=keyboard)


@back_subject_router.callback_query(and_f(F.data == 'back_get_phone', StateFilter(TrainingInput.waiting_for_mail)))
async def back_get_phone(clb: CallbackQuery, state: FSMContext):
    await clb.message.delete()
    keyboard = await custom_poll_builder('back_get_name')
    await state.set_state(TrainingInput.waiting_for_phone)
    await clb.message.answer('Введите ваш контактный телефон', reply_markup=keyboard)


@back_subject_router.callback_query(and_f(F.data == 'back_get_mail', StateFilter(TrainingInput.waiting_for_receiver_name)))
async def back_get_mail(clb: CallbackQuery, state: FSMContext):
    await clb.message.delete()
    keyboard = await custom_poll_builder('back_get_phone')
    await state.set_state(TrainingInput.waiting_for_mail)
    await clb.message.answer('Введите вашу электронную почту', reply_markup=keyboard)


@back_subject_router.callback_query(and_f(F.data == 'back_get_receiver_name', StateFilter(TrainingInput.waiting_for_receiver_mail)))
async def back_get_receiver_name(clb: CallbackQuery, state: FSMContext):
    await clb.message.delete()
    keyboard = await custom_poll_builder('back_get_mail')
    await state.set_state(TrainingInput.waiting_for_receiver_name)
    await clb.message.answer('Введите полное имя Получателя услуг (ваше или вашего ребенка)', reply_markup=keyboard)


@back_subject_router.callback_query(and_f(F.data == 'back_get_receiver_mail', StateFilter(TrainingInput.waiting_for_class)))
async def back_get_receiver_mail(clb: CallbackQuery, state: FSMContext):
    await clb.message.delete()
    keyboard = await custom_poll_builder('back_get_receiver_name')
    await state.set_state(TrainingInput.waiting_for_receiver_mail)
    await clb.message.answer('Введите электронную почту Получателя услуг', reply_markup=keyboard)


@back_subject_router.callback_query(F.data == 'back_product')
async def back_get_product(call: CallbackQuery, state: FSMContext):
    await call.message.delete()
    user = await get_user_data(call.from_user.id)
    text = (f'{user.name}, внимательно ознакомитесь  с публичной офертой и Приложением (Заявка) к ней. '
            f'Убедитесь, что все данные правильно внесены  в Заявку: ФИО, количество занятий в пакете, '
            f'формат занятий, стоимость одного занятия и общая стоимость.\n\n'
            f'Если все правильно и у вас не возникли вопросы, нажимайте на кнопку "ознакомился (-ась). '
            f'Если вам потребуется откорректировать данные - вернитесь назад и заполните данные заново.')
    keyboard = await contract_builder()
    builder: MediaGroupBuilder = MediaGroupBuilder()
    builder.add_document(FSInputFile(f'src/files/student_agreement/agreement1.docx'))
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
    for mess in await call.message.answer_media_group(builder.build()):
        messages.append(mess.message_id)
    await state.update_data(photos_to_delete=messages)
    await call.answer(text, reply_markup=keyboard)
    try:
        os.remove(agreement)
    except Exception as err:
        print(err)



