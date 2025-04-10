from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, DeclarativeBase
import os
import logging

#Logging configuration
logging.basicConfig(level = logging.INFO, format = '%(asctime)s - %(levelname)s - %(message)s')

#DB configuration
DB_FILE = 'quickstamp.db'
DB_URL = f'sqlite:///{DB_FILE}'

#Parent class
class Base(DeclarativeBase):
    pass
#Base = declarative_base()

#Creation engine object
engine = create_engine(DB_URL, echo = False)

#Session factories
SessionLocal = sessionmaker(autocommit = False, autoflush = False, bind = engine)

def get_db():
    '''Create and close properly the SQLAlchemy session'''
    db = SessionLocal()
    try:
        return db
    finally:
        db.close()

def init_db():
    '''Creation DB if not already present'''
    if not os.path.exists(DB_FILE):
        logging.info('DB creation')
        Base.metadata.create_all(bind = engine)
        logging.info('DB installed successfully')
    else:
        logging.info('DB already installed, nothing done')

def is_first_launch():
    'Check if app is run for the 1st time'
    if not os.path.exists(DB_FILE):
        return True
    
    db = get_db()
    from .models import User
    user_count = db.query(User).count()
    return user_count == 0