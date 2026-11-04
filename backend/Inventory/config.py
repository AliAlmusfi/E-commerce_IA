# config.py
class Config:
    DATABASE_ENGINE   = "mysql+pymysql"
    DATABASE_NAME     = "ecommerce_ia_inventory"
    DATABASE_USER     = "root"
    DATABASE_PASSWORD = ""
    DATABASE_HOST     = "localhost"
    DATABASE_PORT     = "3306"
    UPLOAD_FOLDER     = "static/uploads"

    @classmethod
    def get_db_url(cls) -> str:
        return f"{cls.DATABASE_ENGINE}://{cls.DATABASE_USER}:{cls.DATABASE_PASSWORD}@{cls.DATABASE_HOST}:{cls.DATABASE_PORT}/{cls.DATABASE_NAME}"