from .other import start_router, menu_router, support_router
from .student import student_router
from .admin import admin_router, product_router

from .fsm_models import NameInput, AIChat
from src.handlers.student.learning import learning_router
from .subjects import subject_router, back_subject_router
from .fsm_models import AddNewProduct, Support, DeleteProduct, Interview, TrainingInput
from .confirmed_student import student_router as confirmed_student_router
from .teacher import teacher_router, interview_router, interview_questions_router
