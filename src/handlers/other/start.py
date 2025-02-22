import os

from aiogram import Router, F
from aiogram.filters import CommandStart, Command
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, FSInputFile
from aiogram.utils.media_group import MediaGroupBuilder
from loguru import logger
from os import getenv
from dotenv import load_dotenv

from src.database import get_user_data, update_user_name
from src.keyboards import student_menu_keyboard, teacher_or_student, teacher_start_menu_keyboard, confirmed_teacher, confirmed_student
from src.handlers.fsm_models import NameInput

start_router = Router()

load_dotenv()

START_PICS_PATH = getenv('START_PICS_PATH')
INSTRUCTION_PICS_PATH = getenv("INSTRUCTION_PICS_PATH")


@start_router.message(Command('id'))
async def get_id(message: Message):
    await message.answer(f"CHAT ID: {message.chat.id}")


@start_router.message(CommandStart())
async def start_handler(message: Message, state: FSMContext):
    try:
        await message.bot.edit_message_reply_markup(chat_id=message.from_user.id, message_id=message.message_id - 1)
    except Exception:
        ...
    await state.clear()

    logger.info(f"Received /start command from user: {message.from_user.id}")
    user = await get_user_data(telegram_id=message.from_user.id)

    if not (user.name and user.role):
        media = MediaGroupBuilder(caption="Как тебя зовут?")
        
        # ID в боте
        # start_photos_ids = [
        #     'AgACAgIAAxUHZxy4a1xZoAyPdiQdFmvX4ubgsCMAAursMRvRkOFIrR0CNJTA6xIBAAMCAAN3AAM2BA',
        #     'AgACAgIAAxUHZxy4awSr9zXfeDk76gZSquzFZr4AAuvsMRvRkOFIljGv0chqePYBAAMCAAN3AAM2BA',
        #     'AgACAgIAAxUHZxy4a_Vomh2zYBMowqLXBtmdCx8AAujsMRvRkOFIurjoJlmp7XoBAAMCAAN3AAM2BA',
        #     'AgACAgIAAxUHZxy4a44lp0ntxbPWWY767HLdDIkAAuzsMRvRkOFI_ut0_sniEhYBAAMCAAN3AAM2BA',
        #     'AgACAgIAAxUHZxy4a73uGeeKtav9NF-TJHFa17UAAunsMRvRkOFIfjfKgnDtny8BAAMCAAN3AAM2BA'
        # ]

        # for file_id in start_photos_ids:
        #     media.add(type="photo", media=file_id)
        
        start_img = [
            'src/pics/start/start1.png',
            'src/pics/start/start2.png',
            'src/pics/start/start3.png',
            'src/pics/start/start4.png',
            'src/pics/start/start5.png'
        ]
        
        for img in start_img:
            media.add(
                type="photo",
                media=FSInputFile(path=img)
            )
        
        await message.answer_media_group(media=media.build())
        await state.set_state(NameInput.waiting_for_name)
    else:
        if user.role == "student":
            await message.answer("Приветствую в нашей онлайн школе!",
                                 reply_markup=student_menu_keyboard)
        if user.role == "teacher":
            await message.answer("Приветствую в нашей онлайн школе!",
                                 reply_markup=teacher_start_menu_keyboard)
        if user.role == "confirmed_teacher":
            await message.answer("Приветствую в нашей онлайн школе!",
                                 reply_markup=confirmed_teacher)
        if user.role == 'confirmed_student':
            await message.answer('Приветствую в нашей онлайн школе!',
                                 reply_markup=confirmed_student)


@start_router.message(NameInput.waiting_for_name)
async def get_name(message: Message, state: FSMContext):
    if message.text:

        await state.clear()
        is_updated = await update_user_name(telegram_id=message.from_user.id, new_name=message.text)
        await state.update_data(name=message.text)

        if is_updated:
            media = MediaGroupBuilder()
            
            # ID в боте
            # instruction_photos_ids = [
            #     'AgACAgIAAxkDAAIFGGceFhVG-MmLvPnTv_NZLV_HYacQAAKB5TEbLaTwSPk4nppRSs61AQADAgADdwADNgQ',
            #     'AgACAgIAAxkDAAIFIWceFjAMBV117In_cwABe9TWTweKSQACguUxGy2k8EjhEi-KMNoU7gEAAwIAA3cAAzYE',
            #     'AgACAgIAAxkDAAIFImceFjPmwXlaEmO1IWpzkRBCNTw4AAKD5TEbLaTwSPlCmlK3gyXFAQADAgADdwADNgQ',
            #     'AgACAgIAAxkDAAIFJGceFjgedg18TvsAAV0kYmsJTdH9oQAChOUxGy2k8EjMn-LcFBpmxgEAAwIAA3cAAzYE',
            #     'AgACAgIAAxkDAAIFJWceFj4AAWiHSrdeMbXMtk05j88CJwACheUxGy2k8EiMrjn-_1aDRAEAAwIAA3cAAzYE',
            #     'AgACAgIAAxkDAAIFJ2ceFkkiqYfyZwv_qzI9K2CU-YrAAAKG5TEbLaTwSP2dZ1Uncu96AQADAgADdwADNgQ',
            #     'AgACAgIAAxkDAAIFKmceFl7vzdT55_ko2oWqNeNQ_n8vAAKJ5TEbLaTwSH469BO0a1vKAQADAgADdwADNgQ'
            # ]
            # for photo_id in instruction_photos_ids:
            #     media.add(type="photo", media=photo_id)
            instructions_img = [
                'src/pics/instructions/instruction1.png',
                'src/pics/instructions/instruction2.png',
                'src/pics/instructions/instruction3.png',
                'src/pics/instructions/instruction4.png',
                'src/pics/instructions/instruction5.png',
                'src/pics/instructions/instruction6.png',
                'src/pics/instructions/instruction7.png',
            ]
            for img in instructions_img:
                media.add(
                    type="photo",
                    media=FSInputFile(path=img)
                )

            await message.answer_media_group(media=media.build())
            await message.answer(f"""{message.text}, рады приветствовать тебя! Ознакомься с инструкцией по использованию нашего бота, а затем выбери, хочешь ли ты у нас учиться или преподавать.Желаем удачи! 😊
""", reply_markup=teacher_or_student)
        else:
            await message.answer(
                f"""Ошибка: не удалось обновить имя пользователя. Пожалуйста, обратитесь в поддержку!""")
            await state.clear()
    else:
        await message.answer("Твоё сообщение не похоже на имя, попробуй ввести другое.")
