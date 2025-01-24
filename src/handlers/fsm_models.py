from aiogram.fsm.state import State, StatesGroup


class Base(StatesGroup):
    pass


class NameInput(Base):
    waiting_for_name = State()


class DeleteProduct(Base):
    product_name = State()


class AddNewProduct(Base):
    product_type = State()
    subject = State()
    name = State()
    description = State()
    lessons_quantity = State()
    price = State()


class Support(Base):
    student_support_state = State()
    teacher_support_state = State()
    method_support_state = State()
    student_tech_support_state = State()
    get_message_to_send = State()


class Interview(Base):
    full_name = State()
    age = State()
    education = State()
    work_experience = State()
    about_me = State()
    mail = State()
    ege_doc = State()
    hhru_doc = State()
    education_doc = State()
    comment_about_docs = State()
    hhru_resume = State()
    video = State()
    waiting_video_answers = State()
    feed_back_comment = State()

class AIChat(Base):
    chatting = State()


class TrainingInput(Base):
    waiting_for_integer = State()
    waiting_for_name = State()
    waiting_for_phone = State()
    waiting_for_mail = State()
    waiting_for_receiver_name = State()
    waiting_for_receiver_mail = State()
    waiting_for_username = State()
    waiting_for_class = State()


class MallingInput(Base):
    waiting_for_message = State()


class PartnerChatting(Base):
    student = State()
    teacher = State()


class Promo(Base):
    waiting = State()


class Homework(Base):
    send = State()
    waiting_for_accordance = State()
    waiting_for_accuracy = State()
    waiting_for_quality = State()
    waiting_for_knowledge = State()
    waiting_for_independence = State()


class AiMaks(Base):
    chatting = State()


class StudentSurvey(Base):
    collecting = State()