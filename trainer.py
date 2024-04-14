from Workflow.db_connection import HealthClubDatabase
import logging

# Setup logging configuration
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


# Database instance
db = HealthClubDatabase(dbname="Tester", user="postgres", password="postgres", host="localhost")



#################################################### Schedule Management Section ###################################################


def add_trainer_unavailability(trainer_id, start_time, end_time):
    """
    Adds a period of unavailability to a trainer's schedule.
    
    Args:
        trainer_id (int): The ID of the trainer.
        start_time (datetime): Start time of unavailability.
        end_time (datetime): End time of unavailability.
        
    Returns:
        str: Status message indicating the outcome of the operation.
    """
    try:
        query = "INSERT INTO TrainerUnavailability (TrainerID, StartTime, EndTime) VALUES (%s, %s, %s);"
        params = (trainer_id, start_time, end_time)
        db.execute_query(query, params)
        return "Trainer unavailability added successfully."
    except Exception as e:
        logging.error(f"Failed to add unavailability for trainer {trainer_id}: {e}")
        return f"Error adding unavailability: {str(e)}"


def update_trainer_unavailability(unavailability_id, new_start_time, new_end_time):
    """
    Updates the start and end times for an existing unavailability period.
    
    Args:
        unavailability_id (int): The ID of the unavailability record to update.
        new_start_time (time): The new start time of unavailability.
        new_end_time (time): The new end time of unavailability.
        
    Returns:
        str: Status message indicating the outcome of the update.
    """
    try:
        query = "UPDATE TrainerUnavailability SET StartTime = %s, EndTime = %s WHERE UnavailabilityID = %s;"
        params = (new_start_time, new_end_time, unavailability_id)
        db.execute_query(query, params)
        return "Trainer unavailability updated successfully."
    except Exception as e:
        logging.error(f"Failed to update unavailability record {unavailability_id}: {e}")
        return "Error updating unavailability."
    


#################################################### Member Profile Viewing Section ###################################################

def search_member_by_name(trainer_id, name):
    """
    Allows a trainer to search for member profiles by name to view their information and related health metrics.
    
    Args:
        trainer_id (int): The ID of the trainer performing the search.
        name (str): The name or partial name of the member to search for.
        
    Returns:
        list: A list of member profiles that match the search criteria.
    """
    try:
        query = "SELECT MemberID, FirstName, LastName, Email FROM Members WHERE FirstName LIKE %s OR LastName LIKE %s;"
        params = (f'%{name}%', f'%{name}%')
        results = db.execute_query(query, params, fetch=True)
        return [{'MemberID': res[0], 'FirstName': res[1], 'LastName': res[2], 'Email': res[3]} for res in results]
    except Exception as e:
        logging.error(f"Failed to search for members: {e}")
        return []




def view_upcoming_sessions(trainer_id):
    """
    Retrieves upcoming classes and personal training sessions scheduled by a trainer.
    
    Args:
        trainer_id (int): The ID of the trainer.
        
    Returns:
        list: A list of upcoming sessions and classes, including dates, times, and participant details.
    """
    try:
        query = """
        SELECT ClassID, ClassName, StartTime, EndTime, Status FROM FitnessClasses
        WHERE TrainerID = %s AND Status = 'Scheduled'
        UNION ALL
        SELECT ScheduleID, Type, StartTime, EndTime, Status FROM MemberSchedule
        WHERE TrainerID = %s AND Status = 'Scheduled';
        """
        params = (trainer_id, trainer_id)
        results = db.execute_query(query, params, fetch=True)
        return results
    except Exception as e:
        logging.error(f"Failed to retrieve sessions for trainer {trainer_id}: {e}")
        return []


def view_schedule():
    # Implementation to view the trainer's upcoming schedule
    pass

def manage_availability():
    # Implementation to update the trainer's availability for sessions
    pass

def view_member_profiles():
    # Implementation to search and view details of members
    pass
 


