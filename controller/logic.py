from model import repository
from model.database import is_first_launch, init_db
from datetime import datetime, timedelta

def init_app_state():
    '''Initialize the status of the app'''
    init_db()

def validate_first_launch_data(first_name, last_name, weekly_hours):
    '''Validate the data for the first launch'''

    errors = []

    if not first_name or len(first_name) < 2:
        errors.append('The first name must contain at least 2 characters')

    if not last_name or len(last_name) < 2:
        errors.append('The last name must contain at least 2 characters')

    try:
        hours = float(weekly_hours)
        if hours <= 0 or hours > 168:
            errors.append('The weekly working time must be positive and below 168')
    except ValueError:
        errors.append('The weekly woking time number must be valid') 

    return errors

def create_timestamps(status, company_name = None, time = None, date = None):
    '''Create a new timestamp for the actual user'''

    user = repository.get_current_user()
    if not user:
        return False, 'User not found'

    try:
        repository.create_timestamps(status, user.id, company_name, time, date)
        return True, 'Timestamp recorded successfully.'
    except Exception as e:
        return False, f'Mistake during the recording: {str(e)}'
    
def delete_timestamp(timestamp_id):
    '''Delete timestamp and orphan companies'''
    try:
        result = repository.delete_timestamp(timestamp_id)
        if result:
            repository.delete_orphan_companies()
            return True, 'Timestamp deleted successfully'
        return False, 'Timestamp not found'
    except Exception as e:
        return False, f'Mistake during the deletion: {str(e)}'
    
def get_last_10_entries():
    '''Retrieve the last 10 timestamps'''
    try:
        user = repository.get_current_user()
        if not user:
            return []
        
        timestamps = repository.get_last_10_timestamps(user.id)

        #reverse order query
        timestamps.reverse()
        #format data 
        formatted_data = []
        for ts in timestamps:
            company_name = ts.company.company_name if ts.company else 'N/A'
            formatted_data.append([
                str(ts.id), 
                ts.status, 
                ts.time,
                ts.date,
                company_name
            ])

        return formatted_data
    except Exception as e:
        print(f'Error retrieving the last 10 stamps: {e}')
        return []

def fetch_companies():
    '''Retrieve company names list'''
    return repository.get_all_companies()


def last_status():
    '''Retrive the last status according to the user'''
    user = repository.get_current_user()
    if not user:
        return 'out'
    return repository.get_last_status(user.id)

def last_id():
    '''Retrive last ID in timestamp'''
    last_id = repository.get_last_timestamp_id()
    return [str(last_id + 1)]

def daily_stamp_check():
    'Check if the user has correctly filled the timestamps of the last day'
    user = repository.get_current_user()
    if not user:
        return (False, None)
    
    yesterday = (datetime.now() - timedelta(days = 1 )).strftime('%d/%m/%Y')
    db = repository.get_db()

    #count timestamps of yesterday
    count = db.query(repository.Timestamp).filter(
        repository.Timestamp.user_id == user.id,
        repository.Timestamp.date == yesterday
    ).count()

    if count % 2 != 0 and count != 0:
        return False, f'A timestamp is missid for this date: {yesterday}' 
    
    return True, yesterday

def register_user(first_name, last_name, weekly_hours):
    '''Save a new user'''
    errors = validate_first_launch_data(first_name, last_name, weekly_hours)
    if errors:
        return False, errors
    
    try:
        repository.create_user(first_name, last_name, weekly_hours)
        return True, []
    except Exception as e:
        return False, [str(e)]