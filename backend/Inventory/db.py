from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker, declarative_base

from config import Config

engine = create_engine(Config.get_db_url())
db_session = scoped_session( sessionmaker(autocommit=False, autoflush=False, bind=engine) )

Base = declarative_base()
Base.query = db_session.query_property()

def init_db():
    # import all modules here that might define models so that
    # they will be registered properly on the metadata.  Otherwise
    # you will have to import them first before calling init_db()
    from db_models import Product, Storage
    Base.metadata.create_all(bind=engine)


from datetime import datetime, timezone
from sqlalchemy import Column, DateTime
class Model(Base):
    __abstract__ = True  # explicit: not a table, only a mixin

    # GLOBAL FIX: This applies to all child tables automatically
    __table_args__ = {
        'mysql_engine': 'InnoDB',
        'mysql_charset': 'utf8mb4'  # Recommended companion setting for modern MySQL
    }

    created_at = Column(
        DateTime, 
        default=lambda: datetime.now(timezone.utc).replace(tzinfo=None)
    )
    updated_at = Column(
        DateTime, 
        default=lambda: datetime.now(timezone.utc).replace(tzinfo=None), 
        onupdate=lambda: datetime.now(timezone.utc).replace(tzinfo=None)
    )
