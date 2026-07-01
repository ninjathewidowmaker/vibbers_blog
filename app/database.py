import os
from urllib.parse import quote_plus #I only needed this tools because me deadass used special symbol in the password
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from dotenv import load_dotenv
load_dotenv()

username = os.getenv('username')
password = os.getenv('password')
host = os.getenv('host')
port = os.getenv('port')
database = os.getenv('database')

#You can directly use password but if yours contain special char use this 
encoded_password = quote_plus(password)


DATABASE_URL = f"postgresql+asyncpg://{username}:{encoded_password}@{host}:{port}/{database}"

engine = create_async_engine(DATABASE_URL, echo=True)

AsyncSessionLocal = async_sessionmaker(
    bind=engine, 
    class_=AsyncSession, 
    expire_on_commit=False
)


async def get_db():
    async with AsyncSessionLocal() as session:
        yield session