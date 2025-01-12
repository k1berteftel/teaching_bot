from aiogram import Router, F
from aiogram.types import CallbackQuery, FSInputFile
from aiogram.fsm.context import FSMContext
from aiogram.utils.media_group import MediaGroupBuilder

from src.database import update_user_role
from src.keyboards import student_menu_keyboard, student_menu_back

student_router = Router()


@student_router.callback_query(F.data == "student_main_menu")
async def student_main_menu(call: CallbackQuery):
    await call.message.delete()
    await call.message.answer(f"""Ты находишься в главном меню.""", reply_markup=student_menu_keyboard)


@student_router.callback_query(F.data == "student")
async def student_start(call: CallbackQuery, state: FSMContext):
    try:
        await call.message.bot.delete_messages(chat_id=call.from_user.id, message_ids=[i for i in range(
            call.message.message_id - 7, call.message.message_id)])
    except Exception as e:
        print(e)
    try:
        await call.message.delete()
    except Exception as err:
        print(err)

    is_updated = await update_user_role(telegram_id=call.from_user.id, new_role="student")
    if is_updated:

        data = await state.get_data()

        user_name = data.get('name', "Пользователь")

        media = MediaGroupBuilder()
        # ID в телеграм боте
        # student_start_photos_ids = [
        #     'AgACAgIAAxkDAAIFXGcfY2pcuS7iPTo8EBxDZJVgT2URAAJd4zEbUgsAAUn29snyYkOi1gEAAwIAA3cAAzYE',
        #     'AgACAgIAAxkDAAIFXWcfY2sOAAEN3v7kjAOgCEjFqCfFqAACXuMxG1ILAAFJIBL1tiw-vxsBAAMCAAN3AAM2BA',
        #     'AgACAgIAAxkDAAIFXmcfY21T8pJzPrn9hKec_WS42-fWAAJf4zEbUgsAAUmv331bwJqxfAEAAwIAA3cAAzYE',
        #     'AgACAgIAAxkDAAIFX2cfY3BlozzPUKC7COayusd1iOB2AAJg4zEbUgsAAUn8u0UcidSbMgEAAwIAA3cAAzYE',
        #     'AgACAgIAAxkDAAIFYGcfY3EyFuvcE7KhVOLGfAWND4uVAAJh4zEbUgsAAUnXymY1l-KrcAEAAwIAA3cAAzYE',
        #     'AgACAgIAAxkDAAIFYWcfY3J-3swN9Rr-yMo2NI7mMh0eAAJi4zEbUgsAAUn4k0p0dVg2MwEAAwIAA3cAAzYE',
        #     'AgACAgIAAxkDAAIFYmcfY3MJ_eSYJgU4ReO9aXNpC32cAAJj4zEbUgsAAUmDVyhZrb4dnAEAAwIAA3cAAzYE'
        # ]

        # for file_id in student_start_photos_ids:
        #     media.add(type="photo", media=file_id)
        
        student_start_img = [
            "src/pics/student_start/student_start1.png",
            "src/pics/student_start/student_start2.png",
            "src/pics/student_start/student_start3.png",
            "src/pics/student_start/student_start4.png",
            "src/pics/student_start/student_start5.png",
            "src/pics/student_start/student_start6.png",
            "src/pics/student_start/student_start7.png",
        ]
        
        for img in student_start_img:
            media.add(
                type="photo",
                media=FSInputFile(img)
            )

        start_photos = await call.message.answer_media_group(media=media.build())
        await state.update_data(photos_to_delete=[msg.message_id for msg in start_photos])
        await call.message.answer(f"""
{user_name}, ты находишься в главном меню. 

Здесь можно узнать всё о процессе обучения, ценах, договоре и нашей школе.  

Чтобы начать занятия, просто следуй шагам выше! 🚀
""", reply_markup=student_menu_keyboard)
    else:
        await call.message.edit_text(f"""
Ошибка: не удалось обновить роль клиента. Обратитесь в поддержку!
""")


@student_router.callback_query(F.data == "how_we_teach")
async def how_we_teach(call: CallbackQuery, state: FSMContext):

    await call.message.delete()

    media = MediaGroupBuilder()
    info = '''
Обучение в нашей онлайн-школе — это увлекательный и простой путь к знаниям!  

Ты получишь индивидуальный план (карту), где будут указаны предметные темы, цели и навыки.  

В боте ты сможешь отслеживать свой прогресс по карте, выполнять домашние задания, получать обратную связь и зарабатывать баллы за свою работу!  

Накапливая баллы, ты будешь прокачивать своего Макса, а с каждым новым уровнем у тебя появится возможность получать дополнительные привилегии или обменивать баллы на нашу внутреннюю валюту — «изики». 😊      
'''

    # ID в боте
    # how_we_teach_photos_ids = [
    #     'AgACAgIAAxkDAAINAmcktUm6ULt_61VkFQfigi26btWEAAIz5jEbeX8hSakTYl8l8FrFAQADAgADdwADNgQ',
    #     'AgACAgIAAxkDAAINCGcktWIydzguWR2g5PvBVS4qV9TcAAI25jEbeX8hSUe3_nc09p_6AQADAgADdwADNgQ',
    #     'AgACAgIAAxkDAAINBmcktV75gVo0H6yV_I-JVJQkStBlAAI15jEbeX8hSXU4Gu3g_M5RAQADAgADdwADNgQ',
    #     'AgACAgIAAxkDAAIM-mcktQTSrtLSiPA6WE3NdzO39JT6AAIo5jEbeX8hSSo22o6mmI3WAQADAgADdwADNgQ',
    #     'AgACAgIAAxkDAAIM_mcktSdV2VdDDjU6W7HHFYZlZYRnAAIv5jEbeX8hSQme0XbP6rkgAQADAgADdwADNgQ',
    #     'AgACAgIAAxkDAAINAAFnJLVGdD4IiGn4NQFAjH_fwAW2SgACMuYxG3l_IUnO61lNg_SYswEAAwIAA3cAAzYE',
    #     'AgACAgIAAxkDAAIM_GcktRW4iV7u8WmPb7UkZgSvlJ97AAIq5jEbeX8hSWnm48VzkClDAQADAgADdwADNgQ',
    #     'AgACAgIAAxkDAAINBGcktVcbnjbxzth8GuLfRoXLJqKoAAI05jEbeX8hSSHxFDzcczBVAQADAgADdwADNgQ'
    # ]

    # for photo_id in how_we_teach_photos_ids:
    #     media.add_photo(media=photo_id)
    
    how_we_teach_img = [
        "src/pics/how_we_teach/how_we_teach1.png",
        "src/pics/how_we_teach/how_we_teach2.png",
        "src/pics/how_we_teach/how_we_teach3.png",
        "src/pics/how_we_teach/how_we_teach4.png",
        "src/pics/how_we_teach/how_we_teach5.png",
        "src/pics/how_we_teach/how_we_teach6.png",
        "src/pics/how_we_teach/how_we_teach7.png",
        "src/pics/how_we_teach/how_we_teach8.png",
    ]
    
    for img in how_we_teach_img:
        media.add(
            type="photo",
            media=FSInputFile(img)
        )

    start_photos = await call.message.answer_media_group(media=media.build())
    await state.update_data(photos_to_delete=[msg.message_id for msg in start_photos])

    await call.message.answer(info, reply_markup=student_menu_back)

@student_router.callback_query(F.data == "prices")
async def show_prices(call: CallbackQuery, state: FSMContext):
    await call.message.delete()
    
    media = MediaGroupBuilder()

    # prices_photo_ids = [
    #     'AgACAgIAAxkDAAIKr2cjvE7sRzjUf6OQxhD1MHPGl9yfAALC5DEbeX8ZSQMKrfsQ-Qm3AQADAgADdwADNgQ',
    #                     'AgACAgIAAxkDAAIKrWcjvEzTASHTuVccC2zsPAUGhZUiAALB5DEbeX8ZSWKVW0tt5CVvAQADAgADdwADNgQ',
    #                     'AgACAgIAAxkDAAIKqWcjvEfNNHej3FCDj9lhhfx5EbE4AAK_5DEbeX8ZSVZZ0cOLZcDKAQADAgADdwADNgQ',
    #                     'AgACAgIAAxkDAAIKpWcjvENjMDr4Lfgaqo4GJr-CCqlYAAK95DEbeX8ZSZeSG3Os_4LBAQADAgADdwADNgQ',
    #                     'AgACAgIAAxkDAAIKsWcjvFHGwETL8BdYV53d8qNOyJ7yAALE5DEbeX8ZSdEd_3lzyoyUAQADAgADdwADNgQ',
    #                     'AgACAgIAAxkDAAIKq2cjvErgiyBQ8c0dUOQ4mMh-gMYpAALA5DEbeX8ZSTDmcXgUstN3AQADAgADdwADNgQ',
    #                     'AgACAgIAAxkDAAIKp2cjvEWlSRt4GHr6RRakvvse_UxIAAK-5DEbeX8ZSWyFwma5J0OxAQADAgADdwADNgQ'
    # ]
    

    # for photo_id in prices_photo_ids:
    #     media.add(type='photo', media=photo_id)
    
    prices_img = [
        "src/pics/prices/prices1.png",
        "src/pics/prices/prices2.png",
        "src/pics/prices/prices3.png",
        "src/pics/prices/prices4.png",
        "src/pics/prices/prices5.png",
        "src/pics/prices/prices6.png",
        "src/pics/prices/prices7.png",
    ]
    
    for img in prices_img:
        media.add(
            type='photo',
            media=FSInputFile(img)
        )

    start_photos = await call.message.answer_media_group(media=media.build())
    await state.update_data(photos_to_delete=[msg.message_id for msg in start_photos])

    await call.message.answer(
        '''
Здесь ты можешь узнать цены на разные пакеты занятий — как индивидуальные, так и групповые.  

Информацию о тарифах на дополнительные занятия (клубы, челленджи, лаборатории) уточняй у команды поддержки.  

Сейчас мы оптимизируем расписания и тарифы по этим направлениям.  

Спасибо за понимание! 😊             
        ''',
        reply_markup=student_menu_back)
