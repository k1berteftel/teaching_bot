from aiogram import Router, F
from aiogram.types import CallbackQuery
from aiogram.fsm.context import FSMContext

from src.keyboards import student_menu_back

learning_router = Router()


@learning_router.callback_query(F.data == "learning")
async def learning_main(call: CallbackQuery, state: FSMContext):
    await call.message.edit_text(
        "Появляется описание форматов обучения, этапов обучения для ученика, описание домашки.",
        reply_markup=student_menu_back)
