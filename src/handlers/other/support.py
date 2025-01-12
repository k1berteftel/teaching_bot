from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram import Router, F
from dotenv import load_dotenv
from os import getenv

from src.database import get_user_data
from src.handlers.fsm_models import Support
from src.keyboards import exit_support, back_from_support_to_interview

load_dotenv()

STUDENT_GROUP_ID = int(getenv('STUDENT_GROUP_ID'))
TEACHER_GROUP_ID = int(getenv('TEACHER_GROUP_ID'))
METHODICAL_GROUP_ID = int(getenv('METHODICAL_GROUP_ID'))

support_router = Router()
print(METHODICAL_GROUP_ID)


@support_router.message(Support.method_support_state)
async def contact_support(message: Message):
    await message.bot.send_message(
        chat_id=METHODICAL_GROUP_ID, text=f"""
Поступило новое обращение в методическую поддержку:        
От кого: @{message.from_user.username}
User id: {message.from_user.id}
<b>Чтобы ответить на обращение нужно ответить на это сообщение от бота (reply)</b>

{message.text}""")


@support_router.message(Support.student_support_state)
async def contact_support(message: Message):
    await message.bot.send_message(
        chat_id=STUDENT_GROUP_ID, text=f"""
Поступило новое обращение в поддержку:        
От кого: @{message.from_user.username}
User id: {message.from_user.id}
<b>Чтобы ответить на обращение нужно ответить на это сообщение от бота (reply)</b>

{message.text}""")


@support_router.message(Support.teacher_support_state)
async def contact_support(message: Message):
    await message.bot.send_message(
        chat_id=TEACHER_GROUP_ID, text=f"""
Поступило новое обращение в поддержку:        
От кого: @{message.from_user.username}
User id: {message.from_user.id}
<b>Чтобы ответить на обращение нужно ответить на это сообщение от бота (reply)</b>

{message.text}""")


@support_router.callback_query(F.data.startswith("support"))
async def contact_support(call: CallbackQuery, state: FSMContext):
    user = await get_user_data(telegram_id=call.from_user.id)
    data = call.data.split("|")
    if user.role == 'confirmed_teacher' and (len(data) > 1 and data[1] == 'teacher'):
        print('here')
        await state.set_state(Support.method_support_state)
    elif user.role in ["teacher", "confirmed_teacher"]:
        await state.set_state(Support.teacher_support_state)
    if user.role == "student":
        await state.set_state(Support.student_support_state)

    keyboard = exit_support

    if len(data) > 1:
        if data[1] == 'teacher':
            keyboard = InlineKeyboardMarkup(inline_keyboard=[
                [InlineKeyboardButton(text="Выйти из чата с поддержкой", callback_data="teacher_main_menu")]
            ])
        if data[1] == "back_to_interview":
            if len(data) == 3 and data[2] == "start":
                keyboard = InlineKeyboardMarkup(inline_keyboard=[
                    [InlineKeyboardButton(text="Выйти из чата с поддержкой", callback_data="next")]
                ])
            elif len(data) == 3 and data[2] == "to_agreement":
                state_data = await state.get_data()
                picked_subject = state_data.get('picked_subject')
                keyboard = InlineKeyboardMarkup(inline_keyboard=[
                    [InlineKeyboardButton(text="Выйти из чата с поддержкой",
                                          callback_data=f"subject|{picked_subject}")]
                ])
            else:
                keyboard = back_from_support_to_interview

    await call.message.edit_text(
        "Напиши своё обращение в поддержку ниже. "
        "Чтобы общаться с оператором в рамках бота не выходи в меню, и не нажимай на любые кнопки в боте.",
        reply_markup=keyboard)


@support_router.message(Command('send_message'))
async def send_message_to_user(message: Message, state: FSMContext):
    text = message.text.split(' ', maxsplit=2)
    await message.bot.send_message(
        chat_id=int(text[1]),
        text=f'<b>Вам пришло сообщение от поддержки:</b>\n{text[2]}'
    )
    await message.answer('Сообщение было успешно отправлено юзеру')


