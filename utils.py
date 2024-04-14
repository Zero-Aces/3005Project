from Workflow.db_connection import HealthClubDatabase
from datetime import datetime, timedelta
import logging

# Database instance
db = HealthClubDatabase(dbname="Tester", user="postgres", password="postgres", host="localhost")

# Setup logging configuration
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def format_datetime_for_postgres(datetime_str): 
    """
    Formats a datetime string into PostgreSQL's preferred format.
    
    Args:
        datetime_str (str): The datetime string in 'MM/DD/YYYY HH:MM' format.
    
    Returns:
        str: Formatted datetime string in 'YYYY-MM-DD HH:MM:SS' format.
    """
    dt = datetime.strptime(datetime_str, '%m/%d/%Y %H:%M')
    formatted_dt = dt.strftime('%Y-%m-%d %H:%M:%S')
    logging.info(f"Formatted datetime: {formatted_dt}")
    return formatted_dt


def is_equipment_under_maintenance(start_datetime_str, duration):
    """
    Checks if there is any equipment maintenance scheduled during the proposed session time that is not completed.
    
    Args:
        start_datetime_str (str): The proposed start time for the session in 'MM/DD/YYYY HH:MM' format.
        duration (int): The duration of the session in minutes.
        
    Returns:
        bool: True if any equipment maintenance is scheduled and not completed during the session, False otherwise.
    """
    try:
        start_time = datetime.strptime(format_datetime_for_postgres(start_datetime_str), '%Y-%m-%d %H:%M:%S')
        end_time = start_time + timedelta(minutes=duration)
        query = """
        SELECT COUNT(*) FROM EquipmentMaintenance
        WHERE (MaintenanceSchedule, MaintenanceSchedule + INTERVAL '1 minute' * Duration)
        OVERLAPS (%s, %s)
        AND Status = 'Scheduled';
        """
        params = (start_time, end_time)
        result = db.execute_query(query, params, fetch=True)
        
        if result[0][0] > 0:
            logging.info("Equipment maintenance conflicts with the proposed session time.")
            return True
        else:
            logging.info("No equipment maintenance conflicts.")
            return False
    except Exception as e:
        logging.error(f"Error checking equipment maintenance during session time: {e}")
        return False
    
    
def is_trainer_available(trainer_id, start_datetime_str, duration, session_type):
    """
    Checks if the trainer is available for a session at the given time, utilizing formatted datetime strings and considering equipment maintenance based on trainer specialization.
    
    Args:
        trainer_id (int): The ID of the trainer.
        start_datetime_str (str): The proposed start time for the session in 'MM/DD/YYYY HH:MM' format.
        duration (int): The duration of the session in minutes.
        session_type (str): Type of session ('Personal Training' or 'Group Class').
        
    Returns:
        bool: True if the trainer is available, False otherwise.
    """
    try:
        start_time = datetime.strptime(format_datetime_for_postgres(start_datetime_str), '%Y-%m-%d %H:%M:%S')
        end_time = start_time + timedelta(minutes=duration)

        # Check for unavailability due to equipment maintenance
        if is_equipment_under_maintenance(db, start_datetime_str, duration):
            query = "SELECT Specialization FROM Trainers WHERE TrainerID = %s"
            specialization_result = db.execute_query(query, (trainer_id,), fetch=True)
            specialization = specialization_result[0][0] if specialization_result else None

            if specialization not in ['Weight Loss', 'Strength', 'Cardio', 'Rehab', 'Health']:
                logging.debug(f"Session scheduling conflict due to equipment maintenance for {specialization}.")
                return False

        # Check for trainer-specific unavailability
        query_unavailability = """
        SELECT COUNT(*) FROM TrainerUnavailability
        WHERE TrainerID = %s AND (
            (StartTime <= %s AND EndTime > %s) OR
            (StartTime < %s AND EndTime >= %s) OR
            (StartTime <= %s AND EndTime >= %s)
        );
        """
        params_unavailability = (trainer_id, start_time, start_time, end_time, end_time, start_time, end_time)
        unavailability_result = db.execute_query(query_unavailability, params_unavailability, fetch=True)

        if unavailability_result[0][0] > 0:
            logging.debug("Trainer is not available due to specified unavailability.")
            return False

        # Check if the trainer has other overlapping appointments that are not canceled
        query_appointments = """
        SELECT COUNT(*) FROM MemberSchedule
        WHERE TrainerID = %s AND NOT (
            StartTime >= %s OR EndTime <= %s
        ) AND Status != 'Cancelled';
        """
        params_appointments = (trainer_id, start_time, end_time)
        appointments_result = db.execute_query(query_appointments, params_appointments, fetch=True)

        available = appointments_result[0][0] == 0
        logging.info(f"Trainer {trainer_id} availability check for {session_type}: {available}")
        return available
    except Exception as e:
        logging.error(f"Failed to check availability for trainer {trainer_id}: {e}")
        return False


# Function to fetch trainers based on specialization
def fetch_trainers_by_specialization(specialization):
    query = "SELECT TrainerID, FirstName, LastName FROM Trainers WHERE Specialization = %s ORDER BY TrainerID"
    trainers = db.execute_query(query, (specialization,), fetch=True)
    return {trainer[0]: f"{trainer[1]} {trainer[2]}" for trainer in trainers}

# Function to prompt for integer input within a specific range
def prompt_for_integer(prompt_message, min_value, max_value):
    while True:
        input_value = input(prompt_message)
        if input_value.isdigit() and min_value <= int(input_value) <= max_value:
            return int(input_value)
        print(f"Invalid input. Please enter a number between {min_value} and {max_value}.")
        
        
def get_date_time_input(year, month):
    """
    Gathers input for day, hour, and minute with validation.
    """
    day = prompt_for_integer("Enter day (1-31): ", 1, 31)
    hour = prompt_for_integer("Enter hour (0-23): ", 0, 23)
    minute = prompt_for_integer("Enter minute (0 or 30): ", 0, 30)
    if minute not in [0, 30]:
        raise ValueError("Minute must be 0 or 30.")
    return datetime.datetime(year, month, day, hour, minute)

def get_duration():
    """
    Allows the user to select a session duration.
    """
    duration_choices = [60, 90, 120]  # 1 hour, 1.5 hours, 2 hours
    print("Select Duration:")
    for idx, duration in enumerate(duration_choices):
        print(f"{idx + 1}. {duration} minutes")
    duration_choice = prompt_for_integer("Choose duration (number): ", 1, len(duration_choices))
    return duration_choices[duration_choice - 1]

def get_session_type():
    """
    Gets the session type from the user.
    """
    session_types = ['Personal Training', 'Group Class']
    print("Select Session Type:")
    for idx, type in enumerate(session_types):
        print(f"{idx + 1}. {type}")
    type_choice = prompt_for_integer("Choose session type (number): ", 1, len(session_types))
    return session_types[type_choice - 1]
