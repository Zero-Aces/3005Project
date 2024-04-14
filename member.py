import logging
from datetime import datetime, timedelta
from utils import format_datetime_for_postgres, is_trainer_available
from Workflow.db_connection import HealthClubDatabase

db = HealthClubDatabase(dbname="Tester", user="postgres", password="postgres", host="localhost")

# Setup basic configuration for logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

#################################################### Profile Management Section ################################################### 
def update_member_profile(member_id, first_name=None, last_name=None, email=None, password=None):
    """
    Updates the member's profile information.

    Args:
        member_id (int): The ID of the member.
        first_name (str): Optional. The first name to update.
        last_name (str): Optional. The last name to update.
        email (str): Optional. The email to update.
        password (str): Optional. The password to update.
        
    Returns:
        str: Status message indicating the outcome of the update.
    """
    updates = []
    params = []
    if first_name:
        updates.append("FirstName = %s")
        params.append(first_name)
    if last_name:
        updates.append("LastName = %s")
        params.append(last_name)
    if email:
        updates.append("Email = %s")
        params.append(email)
    if password:
        updates.append("Password = %s")
        params.append(password)

    if not updates:
        return "No updates provided."
    
    query = f"UPDATE Members SET {', '.join(updates)} WHERE MemberID = %s;"
    params.append(member_id)
    try:
        db.execute_query(query, tuple(params))
        return "Profile updated successfully."
    except Exception as e:
        logging.error(f"Error updating member profile: {e}")
        return f"Error updating profile: {e}"


#helper functions:

def add_fitness_goal(member_id, goal_type, target_value):
    """
    Adds a new fitness goal for a member.
    
    Args:
        member_id (int): The member's ID.
        goal_type (str): The type of fitness goal.
        target_value (str): The target value for the goal.
        
    Returns:
        str: Status message about the addition of the fitness goal.
    """
    query = """
    INSERT INTO FitnessGoals (MemberID, GoalType, TargetValue)
    VALUES (%s, %s, %s);
    """
    query = "INSERT INTO FitnessGoals (MemberID, GoalType, TargetValue) VALUES (%s, %s, %s);"
    try:
        db.execute_query(query, (member_id, goal_type, target_value))
        return "Fitness goal added successfully."
    except Exception as e:
        logging.error(f"Failed to add fitness goal: {e}")
        return f"Error adding fitness goal: {e}"


def update_fitness_goal(fitness_goal_id, new_target_value):
    """
    Updates the target value of an existing fitness goal.
    
    Args:
        fitness_goal_id (int): The ID of the fitness goal.
        new_target_value (str): The new target value.
        
    Returns:
        str: Status message about the update of the fitness goal.
    """
    query = "UPDATE FitnessGoals SET TargetValue = %s WHERE FitnessGoalID = %s;"
    try:
        db.execute_query(query, (new_target_value, fitness_goal_id))
        return "Fitness goal updated successfully."
    except Exception as e:
        logging.error(f"Failed to update fitness goal: {e}")
        return f"Error updating fitness goal: {e}"


def add_health_metric(member_id, metric_type, metric_value):
    """
    Adds a new health metric for a member.
    
    Args:
        member_id (int): The member's ID.
        metric_type (str): The type of health metric.
        metric_value (str): The metric value.
        
    Returns:
        str: Status message about the addition of the health metric.
    """
    query = "INSERT INTO HealthMetrics (MemberID, MetricType, MetricValue) VALUES (%s, %s, %s);"
    try:
        db.execute_query(query, (member_id, metric_type, metric_value))
        return "Health metric added successfully."
    except Exception as e:
        logging.error(f"Failed to add health metric: {e}")
        return f"Error adding health metric: {e}"


def update_health_metric(health_metric_id, new_metric_value):
    """
    Updates an existing health metric with a new value.
    
    Args:
        health_metric_id (int): The ID of the health metric.
        new_metric_value (str): The new value for the health metric.
        
    Returns:
        str: Status message about the update of the health metric.
    """
    query = "UPDATE HealthMetrics SET MetricValue = %s WHERE HealthMetricID = %s;"
    try:
        db.execute_query(query, (new_metric_value, health_metric_id))
        return "Health metric updated successfully."
    except Exception as e:
        logging.error(f"Failed to update health metric: {e}")
        return f"Error updating health metric: {e}"


def update_email(member_id, new_email):
    """
    Updates the email for a member.

    Args:
        member_id (int): The ID of the member.
        new_email (str): The new email to update.

    Returns:
        str: Status message indicating the outcome of the update.
    """
    if new_email:
        query = "UPDATE Members SET Email = %s WHERE MemberID = %s;"
        try:
            db.execute_query(query, (new_email, member_id))
            return "Email updated successfully."
        except Exception as e:
            logging.error(f"Error updating email: {e}")
            return f"Error updating email: {e}"
    else:
        return "No email provided."


def update_password(member_id, new_password):
    """
    Updates the password for a member.

    Args:
        member_id (int): The ID of the member.
        new_password (str): The new password to update.

    Returns:
        str: Status message indicating the outcome of the update.
    """
    if new_password:
        query = "UPDATE Members SET Password = %s WHERE MemberID = %s;"
        try:
            db.execute_query(query, (new_password, member_id))
            return "Password updated successfully."
        except Exception as e:
            logging.error(f"Error updating password: {e}")
            return f"Error updating password: {e}"
    else:
        return "No password provided."


    
#################################################### Dashboard Display Section ###################################################

def display_member_dashboard(member_id):
    """
    Displays the dashboard for a member, including account information, upcoming appointments, fitness goals, and health metrics.
    
    Args:
        member_id (int): The ID of the member whose dashboard is to be displayed.
        
    Returns:
        dict: A dictionary containing all relevant dashboard information.
    """
    dashboard = {
        "personal_info": fetch_personal_info(member_id),
        "scheduled_classes": fetch_member_schedule(member_id),
        "fitness_goals": fetch_member_fitness_goals(member_id),
        "health_metrics": fetch_member_health_metrics(member_id)
    }
    logging.info(f"Dashboard data retrieved for member ID {member_id}")
    return dashboard


def fetch_personal_info(member_id):
    """
    Fetches personal information for a member.
    """
    query = "SELECT FirstName, LastName, Email FROM Members WHERE MemberID = %s;"
    result = db.execute_query(query, (member_id,), fetch=True)
    return {"FirstName": result[0][0], "LastName": result[0][1], "Email": result[0][2]} if result else {}


def fetch_member_schedule(member_id):
    """
    Fetches scheduled fitness classes and personal training sessions for a member.
    """
    query = """
    SELECT ms.ScheduleID, fc.ClassName, ms.StartTime, ms.EndTime, ms.Status
    FROM MemberSchedule ms
    JOIN FitnessClasses fc ON ms.ClassID = fc.ClassID
    WHERE ms.MemberID = %s AND ms.Status != 'Cancelled';
    """
    results = db.execute_query(query, (member_id,), fetch=True)
    return [
        {"ScheduleID": res[0], "ClassName": res[1], "StartTime": res[2].strftime("%Y-%m-%d %H:%M:%S"), "EndTime": res[3].strftime("%Y-%m-%d %H:%M:%S"), "Status": res[4]}
        for res in results
    ] if results else []


def fetch_member_fitness_goals(member_id):
    """
    Fetches fitness goals for a member.
    """
    query = "SELECT GoalType, TargetValue FROM FitnessGoals WHERE MemberID = %s;"
    results = db.execute_query(query, (member_id,), fetch=True)
    return [{"GoalType": res[0], "TargetValue": res[1]} for res in results] if results else []


def fetch_member_health_metrics(member_id):
    """
    Fetches health metrics for a member.
    """
    query = "SELECT MetricType, MetricValue, DateRecorded FROM HealthMetrics WHERE MemberID = %s;"
    results = db.execute_query(query, (member_id,), fetch=True)
    return [
        {"MetricType": res[0], "MetricValue": res[1], "DateRecorded": res[2].strftime("%Y-%m-%d")}
        for res in results
    ] if results else []


#################################################### Schedule Management Section ###################################################


def book_private_session(member_id, trainer_id, start_datetime_str, duration):
    """
    Books a private training session with a trainer, checking for trainer availability.
    
    Args:
        member_id (int): The ID of the member booking the session.
        trainer_id (int): The ID of the trainer for the session.
        start_datetime_str (str): The start datetime in 'MM/DD/YYYY HH:MM' format.
        duration (int): The duration of the session in minutes.
        
    Returns:
        str: Status message indicating the outcome of the booking attempt.
    """
    if not is_trainer_available(trainer_id, start_datetime_str, duration, "Personal Training"):
        return "Failed to book session due to trainer unavailability."

    start_time = datetime.strptime(format_datetime_for_postgres(start_datetime_str), '%Y-%m-%d %H:%M:%S')
    end_time = start_time + timedelta(minutes=duration)

    query = """
    INSERT INTO MemberSchedule (MemberID, TrainerID, StartTime, EndTime, Type, Status)
    VALUES (%s, %s, %s, %s, 'Personal Training', 'Scheduled');
    """
    try:
        db.execute_query(query, (member_id, trainer_id, start_time, end_time))
        return "Private training session booked successfully."
    except Exception as e:
        logging.error(f"Failed to book private session: {e}")
        return "Error booking session."

def register_for_class(member_id, class_id):
    """
    Registers a member for a fitness class if there's an available spot.
    
    Args:
        member_id (int): The ID of the member registering.
        class_id (int): The ID of the class to register for.
        
    Returns:
        str: Status message indicating the outcome of the registration attempt.
    """
    query = """
    SELECT COUNT(*) FROM MemberSchedule
    WHERE ClassID = %s AND Status != 'Cancelled';
    """
    result = db.execute_query(query, (class_id,), fetch=True)
    if result[0][0] >= 5:  # Assuming class capacity is 5
        return "Class is already full."

    query = """
    INSERT INTO MemberSchedule (MemberID, ClassID, Type, Status)
    VALUES (%s, %s, 'Group Fitness Class', 'Scheduled');
    """
    try:
        db.execute_query(query, (member_id, class_id))
        return "Registered for class successfully."
    except Exception as e:
        logging.error(f"Failed to register for class: {e}")
        return "Error registering for class."

def drop_class_by_member(member_id, class_id):
    """
    Allows a member to deregister from a fitness class.
    
    Args:
        member_id (int): The ID of the member.
        class_id (int): The ID of the class to deregister from.
        
    Returns:
        str: Status message indicating the outcome of the deregistration.
    """
    query = """
    SELECT COUNT(*) FROM MemberSchedule
    WHERE MemberID = %s AND ClassID = %s AND Status = 'Scheduled';
    """
    result = db.execute_query(query, (member_id, class_id), fetch=True)
    if result[0][0] == 0:
        return "Member is not registered for this class."

    query = """
    DELETE FROM MemberSchedule
    WHERE MemberID = %s AND ClassID = %s;
    """
    try:
        db.execute_query(query, (member_id, class_id))
        return "Successfully dropped from the class."
    except Exception as e:
        logging.error(f"Failed for member to drop class: {e}")
        return "Error dropping class."
    

def cancel_personal_training_by_member(member_id, session_id):
    """
    Cancels a personal training session booked by a member.
    
    Args:
        member_id (int): The ID of the member.
        session_id (int): The ID of the session to cancel.
        
    Returns:
        str: Status message indicating the outcome of the cancellation.
    """
    query = """
    SELECT COUNT(*) FROM MemberSchedule
    WHERE MemberID = %s AND ScheduleID = %s AND Type = 'Personal Training' AND Status = 'Scheduled';
    """
    result = db.execute_query(query, (member_id, session_id), fetch=True)
    if result[0][0] == 0:
        return "No such session found or already cancelled."

    query = """
    UPDATE MemberSchedule
    SET Status = 'Cancelled'
    WHERE MemberID = %s AND ScheduleID = %s;
    """
    try:
        db.execute_query(query, (member_id, session_id))
        return "Personal training session cancelled successfully."
    except Exception as e:
        logging.error(f"Failed to cancel personal training session: {e}")
        return "Error cancelling session."
    



def view_dashboard():
    # Implementation to view the member's dashboard including stats and upcoming sessions
    pass

def update_profile():
    # Implementation to update member's personal information
    pass

def manage_appointments():
    # Implementation to register for group classes or personal training sessions
    pass




