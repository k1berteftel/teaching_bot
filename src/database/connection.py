from loguru import logger
from sqlalchemy.ext.asyncio import async_sessionmaker
from sqlalchemy.ext.asyncio import create_async_engine
from dotenv import load_dotenv
from os import getenv

from .models import Base

load_dotenv()
DB_USER=getenv('DB_USER')
DB_PASSWORD=getenv('DB_PASSWORD')
DB_HOST=getenv('DB_HOST')
DB_PORT=getenv('DB_PORT')
DB_NAME=getenv('DB_NAME')

#DATABASE_URL = f"postgresql+asyncpg://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
DATABASE_URL = 'postgresql+asyncpg://quest:quest@127.0.0.1:5432/data'

engine = create_async_engine(DATABASE_URL, echo=False)
async_session_maker = async_sessionmaker(engine, expire_on_commit=False)


async def create_tables():
    async with engine.begin() as connection:
        try:
            logger.info("Creating tables...")
            #await connection.run_sync(Base.metadata.drop_all)
            #await connection.run_sync(Base.metadata.create_all)
            logger.info("Tables created successfully.")
        except Exception as e:
            logger.error(f"Error creating tables: {e}")
