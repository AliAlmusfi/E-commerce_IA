
import os
from dotenv import load_dotenv

load_dotenv('./inventory.env')

# config.py
class Config:
    DATABASE_ENGINE   = os.getenv('DATABASE_ENGINE' , 'mysql+pymysql')
    DATABASE_NAME     = os.getenv('DATABASE_NAME' , 'ecommerce_ia_inventory')
    DATABASE_USER     = os.getenv('DATABASE_USER' , 'root')
    DATABASE_PASSWORD = os.getenv('DATABASE_PASSWORD' , '')
    DATABASE_HOST     = os.getenv('DATABASE_HOST' , 'localhost')
    DATABASE_PORT     = os.getenv('DATABASE_PORT' , '3306')
    UPLOAD_FOLDER     = os.getenv('UPLOAD_FOLDER' , 'static/uploads')

    @classmethod
    def get_db_url(cls) -> str:
        return f"{cls.DATABASE_ENGINE}://{cls.DATABASE_USER}:{cls.DATABASE_PASSWORD}@{cls.DATABASE_HOST}:{cls.DATABASE_PORT}/{cls.DATABASE_NAME}"