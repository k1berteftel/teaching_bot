from aiogram import Router, F
from aiogram.filters import and_f, or_f
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery

from src.keyboards import admin_panel, product_or_language
from src.handlers.fsm_models import AddNewProduct, DeleteProduct
from src.database.products import create_product, get_products_categories, get_all_products, delete_product
from src.keyboards import confirm_product_creation, categories_builder
from src.middlewares import AdminMiddleware


product_router = Router()
product_router.callback_query.middleware.register(AdminMiddleware())


@product_router.message(F.text == "Удалить продукт")
async def start_delete(message: Message, state: FSMContext):
    products = await get_all_products()
    if not products:
        await message.answer("В базе нет ни одного продукта.")
        return
    await state.set_state(DeleteProduct.product_name)
    info = f""""""
    for product in products:
        info += f"{product.name} - {product.id}\n"
    await message.answer(info)
    await message.answer("Введите ID продукта, который хотите удалить, ниже")


@product_router.message(DeleteProduct.product_name)
async def delete(message: Message, state: FSMContext):
    if message.text.isdigit():
        is_deleted = await delete_product(id_=int(message.text))
        if is_deleted:
            await message.answer(f"Продукт с ID = {message.text} был успешно удален из базы")
        else:
            await message.answer("При удалении продукта произошла ошибка.")
        await state.clear()
    else:
        await message.answer("ID это целое число.")


@product_router.message(F.text == "Добавить продукт")
async def start_adding(message: Message, state: FSMContext):
    await state.set_state(AddNewProduct.product_type)
    await message.answer("Новый продукт это язык или предмет?", reply_markup=product_or_language)


@product_router.message(and_f(AddNewProduct.product_type, or_f(F.text == "Язык", F.text == "Предмет")))
async def get_product_type(message: Message, state: FSMContext):
    await state.update_data(product_type="subject" if message.text == "Предмет" else "language")
    categories = await get_products_categories("subject" if message.text == "Предмет" else "language")
    keyboard = None
    categories = set(categories)
    if categories:
        keyboard = await categories_builder(categories)
    await state.set_state(AddNewProduct.subject)
    await message.answer(f"Выбранный тип продукта - {message.text}.\n"
                         f"Напишите ниже <b>язык/предмет</b> нового продукта:", reply_markup=keyboard)


@product_router.message(AddNewProduct.subject)
async def get_product_type(message: Message, state: FSMContext):
    await state.update_data(subject=message.text)
    await state.set_state(AddNewProduct.name)
    await message.answer(f"Выбранный язык/предмет продукта - {message.text}.\n"
                         f"Напишите ниже <b>название</b> нового продукта:")


@product_router.message(AddNewProduct.name)
async def get_product_name(message: Message, state: FSMContext):
    if message.text:
        await state.update_data(name=message.text)
        await state.set_state(AddNewProduct.description)
        await message.answer(f"Название продукта - {message.text}.\n"
                             f"Напишите ниже <b>описание</b> нового продукта:")
    else:
        await message.answer('Это не похоже на текст для названия продукта. Отправьте мне текст')


@product_router.message(AddNewProduct.description)
async def get_description(message: Message, state: FSMContext):
    if message.text:
        await state.update_data(description=message.text)
        await state.set_state(AddNewProduct.lessons_quantity)
        data = await state.get_data()
        await message.answer(f"""
Описание продукта: {data.get('description')}

<b>Введите целое число - количество уроков в пакете для этого продукта</b>
""")
    else:
        await message.answer('Это не похоже на текст для описания продукта. Отправьте мне текст')


@product_router.message(AddNewProduct.lessons_quantity)
async def get_lessons_quantity(message: Message, state: FSMContext):
    if message.text.isdigit():
        await state.update_data(lessons_quantity=int(message.text))
        await state.set_state(AddNewProduct.price)
        await message.answer(f"""
Количество уроков в пакете: {message.text}

<b>Введите число (не обязательно целое) - цену для этого продукта</b>""")
    else:
        await message.answer('Это не похоже на целое число количества уроков в пакете. Отправьте целое число')


@product_router.message(AddNewProduct.price)
async def get_price(message: Message, state: FSMContext):
    try:
        float(message.text.replace(',', '.'))
        await state.update_data(price=float(message.text))
        data = await state.get_data()
        await message.answer(f"""
Сводка:
Тип продукта: {data.get('product_type')}
Название: {data.get('name')}
Количество уроков: {data.get('lessons_quantity')}
Цена: {data.get('price')}
Описание: {data.get('description')}
""", reply_markup=confirm_product_creation)
    except ValueError:
        await message.answer("Ваше сообщение не является числом.")


@product_router.callback_query(F.data == "create")
async def create_new_product(call: CallbackQuery, state: FSMContext):
    try:
        await call.message.bot.edit_message_reply_markup(chat_id=call.from_user.id, message_id=call.message.message_id)
    except Exception as e:
        print(e)
    data = await state.get_data()
    is_created = await create_product(product_type=data.get('product_type'),
                                      name=data.get('name'),
                                      lessons_quantity=data.get('lessons_quantity'),
                                      price=data.get('price'),
                                      description=data.get('description'),
                                      subject=data.get('subject'))
    if is_created:
        await call.message.answer("Продукт успешно создан.", reply_markup=admin_panel)
    else:
        await call.message.answer("Произошла ошибка при создании продукта.", reply_markup=admin_panel)