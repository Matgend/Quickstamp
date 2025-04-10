from .database import get_db
from .models import User, Company, Timestamp
from datetime import datetime
import logging

def create_user(first_name, last_name, weekly_working_time):
    '''Create a new user in the DB'''
    db = get_db()
    try:
        user = User(
            first_name = first_name.strip(),
            last_name = last_name.strip(),
            weekly_working_time = float(weekly_working_time)
        )
        db.add(user)
        db.commit()
        db.refresh(user)
        logging.info(f'User created: {user}')
        return user
    except Exception as e:
        db.rollback()
        logging.error(f'Error, user not created: {e}')
        raise

def get_or_create_company(company_name):
    '''Fecth the company name if existing, if not create a new one'''
    db = get_db()
    try: 
        company_name = company_name.lower().strip()
        company = db.query(Company).filter(Company.company_name == company_name).first()

        if not company: #if none
            company = Company(
                company_name = company_name
            )
            db.add(company)
            db.commit()
            db.refresh(company)
            logging.info(f'New company created: {company}')
        
        return company
    except Exception as e:
        db.rollback()
        logging.error(f'Erreur lors de la récupération/création de la compagnie: {e}')
        raise

def create_timestamps(status, user_id, company_name = None, time = None, date = None):
    '''Create a new timestamp'''

    if not status:
        raise ValueError("Status is required and cannot be empty.")
    
    if time is not None and not is_valid_time_format(time):
        raise ValueError('The time format must be %H:%M:%S')

    if date is not None and not is_valid_date_format(date):
        raise ValueError('The date format must be %d/%m/%Y')   

    db = get_db()
    try:
        if not time:
            time = datetime.now().strftime('%H:%M:%S')
        if not date:
            date = datetime.now().strftime('%d/%m/%Y')
        
        if not company_name:
            company_name = 'na' 

        company_id = None
        if company_name:
            company_name = get_or_create_company(company_name = company_name)
            company_id = company_name.id

        timestamp = Timestamp(
            status = status, 
            user_id = user_id  , 
            company_id = company_id,
            time = time, 
            date = date
        )

        db.add(timestamp)
        db.commit()
        db.refresh(timestamp)
        logging.info(f'Timestamp created: {timestamp}')
        return timestamp
    except Exception as e:
        db.rollback()
        logging.error(f'Erreur lors de la création du timestamp: {e}')
        raise


def get_last_10_timestamps(user_id = None):
    '''Retrieve the last 10 timestamps, filtred by mentionned user'''
    db = get_db()
    query = db.query(Timestamp).order_by(Timestamp.date.desc(), Timestamp.time.desc())

    if user_id:
        query = query.filter(Timestamp.user_id == user_id)

    return query.limit(10).all()


def get_all_companies():
    '''Retrieve all the companies'''
    db = get_db()
    return db.scalars(db.query(Company.company_name).order_by(Company.company_name)).all()

def get_last_status(user_id):
    '''Retrieve the last status by user'''
    db = get_db()
    last_timestamp = db.query(Timestamp).filter(
        Timestamp.user_id == user_id
    ).order_by(Timestamp.id.desc()).first()

    if not last_timestamp:
        return 'out'
    return last_timestamp.status

def get_last_timestamp_id():
    '''Retrieve the last ID of timestamp'''

    db = get_db()
    last_timestamps = db.query(Timestamp).order_by(Timestamp.id.desc()).first()
    
    if not last_timestamps:
        return 0
    return last_timestamps.id

def delete_timestamp(timestamp_id):
    '''Delete timestamp according to the ID'''
    db = get_db()
    try:
        timestamp = db.query(Timestamp).filter(Timestamp.id == timestamp_id).first()
        if timestamp:
            db.delete(timestamp)
            db.commit()
            logging.info(f'Timtestamp {timestamp_id} deleted')
            return True
        else:
            logging.warning(f'Timestamp {timestamp_id} not found')
            return False
    except Exception as e:
        db.rollback()
        logging.error(f'Error during the cancelation of the timestamp: {e}')
        raise

def delete_orphan_companies():
    '''Delete the companies that are not present in timestamp'''
    db = get_db()
    try:
        companies_in_timestamp_tb = db.query(Timestamp.company_id).distinct()

        orphans = db.query(Company).filter(~Company.id.in_(companies_in_timestamp_tb)).all()

        for orphan in orphans:
            db.delete(orphan)

        db.commit()
        logging.info(f'{len(orphans)} companies canceled')
        return orphans

    except Exception as e:
        db.rollback()
        logging.error(f'Error during the cancelation of the orphans in companies: {e}')
        raise

def get_current_user():
    '''Retrieve the current user'''
    db = get_db()
    return db.query(User).first()


def is_valid_time_format(time_str):
    '''Check time format'''
    try:
        datetime.strptime(time_str, '%H:%M:%S')
        return True
    except ValueError:
        return False


def is_valid_date_format(date_str):
    '''Check date format'''
    try:
        datetime.strptime(date_str, '%Y-%m-%d')
        return True
    except ValueError:
        return False
    