from .handlers import subject_router, menu_router, learning_router, teacher_router, start_router, support_router, \
    interview_router, student_router, admin_router, product_router, interview_questions_router, back_subject_router
from .database import create_tables
from .middlewares import UserCheckMiddleware, GroupMessageMiddleware, GroupCallbackMiddleware, DeletePhotosMiddleware
from .gpt import fetch_response