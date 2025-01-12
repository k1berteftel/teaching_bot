import asyncio
from typing import Literal

from sqlalchemy import select, and_, delete

from .connection import async_session_maker
from .models import UserModel, ProductModel


async def create_product(product_type: str, name: str, description: str, lessons_quantity: int, price: float,
                         subject: str):
    async with async_session_maker() as session:
        new_product = ProductModel(
            product_type=product_type,
            name=name,
            description=description,
            price=price,
            lessons_quantity=lessons_quantity,
            subject=subject,
        )
        session.add(new_product)
        await session.commit()
        return True


async def get_products_categories(product_type: str):
    async with async_session_maker() as session:
        get_categories_stmt = await session.execute(
            select(ProductModel.subject).where(ProductModel.product_type == product_type))
        categories = get_categories_stmt.scalars().all()
        return categories


async def get_product_by_id(product_id: int):
    async with async_session_maker() as session:
        get_product_stmt = await session.execute(select(ProductModel).where(ProductModel.id == product_id))
        product = get_product_stmt.scalar_one_or_none()
        return product


async def get_all_subjects():
    async with async_session_maker() as session:
        subjects_stmt = await session.execute(select(ProductModel).where(ProductModel.product_type == "subject"))
        subjects = subjects_stmt.scalars().all()
        return subjects


async def get_all_languages():
    async with async_session_maker() as session:
        subjects_stmt = await session.execute(select(ProductModel).where(ProductModel.product_type == "language"))
        subjects = subjects_stmt.scalars().all()
        return subjects


async def get_languages_categories():
    async with async_session_maker() as session:
        languages_stmt = await session.execute(
            select(ProductModel.subject).where(ProductModel.product_type == "language").distinct())
        languages = languages_stmt.scalars().all()
        return languages


async def get_subject_categories():
    async with async_session_maker() as session:
        get_categories_stmt = await session.execute(
            select(ProductModel.subject).where(ProductModel.product_type == "subject"))
        categories = get_categories_stmt.scalars().all()
        return categories


async def get_products_by_category(product_type: str, category: str):
    async with async_session_maker() as session:
        products_by_category_stmt = await session.execute(
            select(ProductModel).where(
                and_(ProductModel.subject == category, ProductModel.product_type == product_type)))
        products_by_category = products_by_category_stmt.scalars().all()
        return products_by_category


async def delete_product(id_: int):
    async with async_session_maker() as session:
        await session.execute(delete(ProductModel).where(ProductModel.id == id_))
        await session.commit()
        return True


async def get_all_products():
    async with async_session_maker() as session:
        product_stmt = await session.execute(select(ProductModel))
        return product_stmt.scalars().all()
