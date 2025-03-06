from aiogram.client.default import DefaultBotProperties
from dotenv import load_dotenv
from os import getenv
from asyncio import run
from aiogram import Bot, Dispatcher
from loguru import logger

from src.database import update_user_role, create_counter, reset_user_partners
from src import student_router, start_router, learning_router, subject_router, admin_router, teacher_router, \
    menu_router, support_router, interview_router, product_router, interview_questions_router, back_subject_router, \
    confirmed_student_router, survey_router, homework_router, student_balls_router
from src import create_tables
from src import UserCheckMiddleware, GroupMessageMiddleware, GroupCallbackMiddleware, DeletePhotosMiddleware

load_dotenv()

BOT_TOKEN = getenv('TEST_BOT_TOKEN')
STUDENT_GROUP_ID = getenv('STUDENT_GROUP_ID')
TEACHER_GROUP_ID = getenv('TEACHER_GROUP_ID')
RECRUITERS_GROUP_ID = getenv('RECRUITERS_GROUP_ID')
METHODICAL_GROUP_ID = getenv('METHODICAL_GROUP_ID')
APPLICATION_GROUP_ID = getenv('APPLICATION_GROUP_ID')
TECHNICAL_GROUP_ID = getenv('TECHNICAL_GROUP_ID')

bot = Bot(token=BOT_TOKEN, default=DefaultBotProperties(parse_mode='HTML'))
dp = Dispatcher()

dp.message.middleware.register(UserCheckMiddleware())

dp.message.middleware.register(GroupMessageMiddleware(
    group_id_student=int(STUDENT_GROUP_ID),
    group_id_teacher=int(TEACHER_GROUP_ID),
    group_id_recruiter=int(RECRUITERS_GROUP_ID),
    group_id_methodical=int(METHODICAL_GROUP_ID),
    group_id_technical=int(TECHNICAL_GROUP_ID)
))


dp.callback_query.middleware.register(GroupCallbackMiddleware(
    group_id_student=int(STUDENT_GROUP_ID),
    group_id_teacher=int(TEACHER_GROUP_ID),
    group_id_recruiter=int(RECRUITERS_GROUP_ID),
    group_id_application=int(APPLICATION_GROUP_ID),
    allowed_callback_data={"candidate_accept", "candidate_decline"}
))

dp.callback_query.middleware.register(DeletePhotosMiddleware())

logger.add("bot_log.log", rotation="10 MB", level='ERROR')


async def bot_start():
    await create_tables()
    #await update_user_role(471219957, 'student')
    #await reset_user_partners(471219957)
    #await create_counter()
    logger.info("Bot is starting...")
    try:
        dp.include_routers(
            interview_questions_router,
            start_router,
            menu_router,
            confirmed_student_router,
            survey_router,
            homework_router,
            student_balls_router,
            teacher_router,
            interview_router,
            student_router,
            learning_router,
            subject_router,
            support_router,
            back_subject_router,
            admin_router,
            product_router
        )
        await bot.delete_webhook(drop_pending_updates=True)
        await dp.start_polling(bot)
    except KeyboardInterrupt:
        return
    except Exception as e:
        logger.error(f"Bot encountered an error: {e}")


if __name__ == "__main__":
    logger.info("Initializing bot...")
    run(bot_start())
