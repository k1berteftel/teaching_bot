from os import listdir

from aiogram import Router, F
from aiogram.types import CallbackQuery, FSInputFile, Message
from aiogram.fsm.context import FSMContext
from aiogram.filters import StateFilter, and_f
from aiogram.utils.media_group import MediaGroupBuilder
from dotenv import load_dotenv

from src.database.user import get_user_partners, add_user_balls
from src.database import update_user_role, get_user_data, ProductModel, UserModel, get_partner_data
from src.database.partner import get_partner_data
from src.keyboards import (teacher_start_menu_keyboard, confirmed_teacher,
                           confirmed_teacher_agreement_keyboard, chatting_student_builder, stop_chatting_teacher,
                           teacher_management_builder, activity_balls_builder, choose_student_builder,
                           partner_menu_builder)


partner_router = Router()


@partner_router.callback_query(F.data == 'partner')
async def set_partner(clb: CallbackQuery):
    await clb.message.delete()
    user = await get_user_data(clb.from_user.id)
    partner = await get_partner_data(clb.from_user.id)
    text = (f'<b>🌟 ПАРТНЁРСКОЕ МЕНЮ EASYKNOW 🌟</b>\n\n✨ Ваша статистика: ✨\n\n'
            f'👥 <b>Количество рефералов</b>: {partner.refs}\n➡️ Каждый ваш реферал — это шаг к новым возможностям! '
            f'Пригласите больше друзей и заработайте ещё больше. 🙌\n\n💰 <b>Общая сумма продаж</b>: {partner.sum} ₽ '
            f'\n🎯 Вы помогаете людям получать знания, а мы делимся с вами прибылью!\n\n🏆 <b>Ваш заработок '
            f'(5% от всех продаж)</b>: {partner.earn} ₽\n🎉 Поздравляем! За каждую успешную покупку вы '
            f'получаете свою долю. Чем больше продаж, тем выше ваш доход! 💸\n\n🔗 <b>Ваша реферальная ссылка</b>:'
            f'\n\t<code>https://t.me/easyknow_bot?start=partner-{clb.from_user.id}</code>\n\n'
            f'<b>⭐ Благодарим за сотрудничество! Вместе мы создаём будущее через знания. ⭐</b>')

    data = 'teacher_main_menu' if user.role != 'student' else 'student_main_menu'
    keyboard = await partner_menu_builder(clb.from_user.id, data)
    await clb.message.answer(text, reply_markup=keyboard)