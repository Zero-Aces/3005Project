from utils import format_datetime_for_postgres, is_equipment_under_maintenance, is_trainer_available, fetch_trainers_by_specialization, prompt_for_integer, get_date_time_input, get_duration, get_session_type
from datetime import datetime, timedelta
import logging
from Workflow.db_connection import HealthClubDatabase


# Database instance
db = HealthClubDatabase(dbname="Tester", user="postgres", password="postgres", host="localhost")

# Setup logging configuration
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


#################################################### Room Booking Management Section ###################################################

def check_room_availability(room_id, start_datetime_str, duration):
    """
    Checks if a room is available for a fitness class at the given time.
    
    Args:
        room_id (int): The ID of the room.
        start_datetime_str (str): The proposed start time for the class in 'MM/DD/YYYY HH:MM' format.
        duration (int): The duration of the class in minutes.
        
    Returns:
        bool: True if the room is available, False otherwise.
    """
    if is_equipment_under_maintenance(db, start_datetime_str, duration):
        logging.info("Room scheduling conflict due to equipment maintenance.")
        return False

    start_time = datetime.strptime(format_datetime_for_postgres(start_datetime_str), '%Y-%m-%d %H:%M:%S')
    end_time = start_time + timedelta(minutes=duration)

    query = """
    SELECT COUNT(*) FROM FitnessClasses
    WHERE RoomID = %s AND (StartTime, EndTime) OVERLAPS (%s, %s) AND Status != 'Cancelled';
    """
    params = (room_id, start_time, end_time)
    result = db.execute_query(query, params, fetch=True)

    available = result[0][0] == 0
    logging.info(f"Room {room_id} availability check: {available}")
    return available


#################################################### Equipment Maintenance Monitoring Section ###################################################


def schedule_equipment_maintenance(start_datetime_str, duration):
    """
    Schedules maintenance, ensuring no overlap with any classes or personal training sessions.
    
    Args:
        db (HealthClubDatabase): The database connection object.
        start_datetime_str (str): The start datetime in 'MM/DD/YYYY HH:MM' format.
        duration (int): The duration of the maintenance in minutes.
        
    Returns:
        str: Status message indicating the outcome of the maintenance scheduling attempt.
    """
    try:
        start_time = datetime.strptime(format_datetime_for_postgres(start_datetime_str), '%Y-%m-%d %H:%M:%S')
        end_time = start_time + timedelta(minutes=duration)
        
        if is_equipment_under_maintenance(start_datetime_str, duration):
            logging.debug("Attempted to schedule maintenance during an existing maintenance period.")
            return "Maintenance is already scheduled during this time."

        # Check for overlapping fitness classes and personal training sessions
        if not check_for_overlapping_bookings(start_time, end_time):
            insert_query = """
            INSERT INTO EquipmentMaintenance (MaintenanceSchedule, Duration, Status)
            VALUES (%s, %s, 'Scheduled');
            """
            db.execute_query(insert_query, (start_time, duration))
            return "Maintenance scheduled successfully."
        else:
            return "Cannot schedule maintenance due to conflicting bookings."
    except Exception as e:
        logging.error(f"Failed to schedule maintenance: {e}")
        return "Error scheduling maintenance."
    
    
def check_for_overlapping_bookings(start_time, end_time):
    """
    Checks for overlapping fitness classes and personal training sessions that might use the equipment.
    """
    query_classes = """
        SELECT COUNT(*) FROM FitnessClasses
        WHERE (StartTime, EndTime) OVERLAPS (%s, %s) AND ClassName IN ('Yoga', 'Swimming', 'Strength', 'Cardio') AND Status != 'Cancelled';
        """
        
    params_classes = (start_time, end_time)
    result_classes = db.execute_query(query_classes, params_classes, fetch=True)
    
    if result_classes[0][0] > 0:
            logging.debug("Maintenance scheduling conflict with a fitness class.")
    
    
    query_sessions = """
    SELECT COUNT(*) FROM MemberSchedule
    WHERE (StartTime, EndTime) OVERLAPS (%s, %s) AND Type = 'Personal Training' AND Status != 'Cancelled';
    """
    result_sessions = db.execute_query(query_sessions, params_classes, fetch=True)

    return result_classes[0][0] > 0 or result_sessions[0][0] > 0


def update_maintenance_status(maintenance_id, new_status):
    """
    Updates the status of an equipment maintenance record. This function allows admins to mark maintenance as completed or reschedule it.
    
    Args:
        db (HealthClubDatabase): The database connection object.
        maintenance_id (int): The ID of the maintenance record to update.
        new_status (str): The new status for the maintenance ('Scheduled', 'Completed').
        
    Returns:
        str: Status message indicating the outcome of the maintenance status update.
    """
    try:
        query = """
        UPDATE EquipmentMaintenance
        SET Status = %s
        WHERE MaintenanceID = %s;
        """
        db.execute_query(query, (new_status, maintenance_id))
        return f"Maintenance status updated to {new_status} successfully."
    except Exception as e:
        logging.error(f"Failed to update maintenance status: {e}")
        return "Error updating maintenance status."



#################################################### Class Schedule Management Section ###################################################

def schedule_fitness_class(class_name, room_id, trainer_id, start_datetime_str, duration):
    """
    Schedules a new fitness class, ensuring no conflicts with room availability, trainer availability, or equipment maintenance.
    
    Args:
        class_name (str): The name of the fitness class.
        room_id (int): The ID of the room for the class.
        trainer_id (int): The ID of the trainer leading the class.
        start_datetime_str (str): The start datetime in 'MM/DD/YYYY HH:MM' format.
        duration (int): The duration of the class in minutes.
        
    Returns:
        str: Status message indicating the outcome of the scheduling attempt.
    """
    if not is_trainer_available(trainer_id, start_datetime_str, duration, "Group Class") or \
       not check_room_availability(room_id, start_datetime_str, duration) or \
       is_equipment_under_maintenance(start_datetime_str, duration):
        return "Scheduling failed due to unavailability or maintenance."

    start_time = datetime.strptime(format_datetime_for_postgres(start_datetime_str), '%Y-%m-%d %H:%M:%S')
    end_time = start_time + timedelta(minutes=duration)

    try:
        query = """
        INSERT INTO FitnessClasses (ClassName, RoomID, TrainerID, StartTime, EndTime, Status)
        VALUES (%s, %s, %s, %s, %s, 'Scheduled');
        """
        params = (class_name, room_id, trainer_id, start_time, end_time)
        db.execute_query(query, params)
        return "Fitness class scheduled successfully."
    except Exception as e:
        logging.error(f"Failed to schedule fitness class: {e}")
        return "Error scheduling class."


def update_class_schedule(class_id, new_start_datetime_str, new_duration):
    """
    Updates the schedule of an existing fitness class.
    
    Args:
        db (HealthClubDatabase): The database connection object.
        class_id (int): The ID of the fitness class to update.
        new_start_datetime_str (str): The new start datetime in 'MM/DD/YYYY HH:MM' format.
        new_duration (int): The new duration of the class in minutes.
        
    Returns:
        str: Status message indicating the outcome of the update.
    """
    new_start_time = datetime.strptime(format_datetime_for_postgres(new_start_datetime_str), '%Y-%m-%d %H:%M:%S')
    new_end_time = new_start_time + timedelta(minutes=new_duration)

    # Fetch existing class details
    query_existing = """
    SELECT RoomID, TrainerID FROM FitnessClasses WHERE ClassID = %s;
    """
    class_details = db.execute_query(query_existing, (class_id,), fetch=True)
    if not class_details:
        return "Class not found."

    room_id, trainer_id = class_details[0]

    # Check room and trainer availability
    if not check_room_availability(room_id, new_start_datetime_str, new_duration) or \
       not is_trainer_available(trainer_id, new_start_datetime_str, new_duration, "Group Class"):
        return "Cannot update class due to scheduling conflicts."

    # Update the class schedule
    query_update = """
    UPDATE FitnessClasses
    SET StartTime = %s, EndTime = %s
    WHERE ClassID = %s;
    """
    db.execute_query(query_update, (new_start_time, new_end_time, class_id))
    return "Class schedule updated successfully."


def cancel_class_by_admin(class_id):
    """
    Cancels a scheduled fitness class by an admin. This action also deregisters all members registered for the class.
    
    Args:
        db (HealthClubDatabase): The database connection object.
        class_id (int): The ID of the fitness class to cancel.
        
    Returns:
        str: Status message indicating the outcome of the cancellation.
    """
    try:
        # First, deregister all members from the class
        deregister_query = """
        DELETE FROM MemberSchedule
        WHERE ClassID = %s;
        """
        db.execute_query(deregister_query, (class_id,))

        # Then, cancel the class
        cancel_query = """
        UPDATE FitnessClasses
        SET Status = 'Cancelled'
        WHERE ClassID = %s;
        """
        db.execute_query(cancel_query, (class_id,))
        return "Class cancelled successfully and all members were deregistered."
    except Exception as e:
        logging.error(f"Failed to cancel class by admin: {e}")
        return "Error cancelling class."


#################################################### Billing and Payment Processing Section ###################################################

def update_payment_status(payment_id, new_status):
    """
    Updates the status of a specific payment, useful for marking payments as processed.
    
    Args:
        db (HealthClubDatabase): The database connection object.
        payment_id (int): The ID of the payment to update.
        new_status (str): The new status for the payment ('Processed').
        
    Returns:
        str: Status message indicating the outcome of the payment status update.
    """
    
    query = """
    UPDATE Payments
    SET Status = %s
    WHERE PaymentID = %s;
    """
    db.execute_query(query, (new_status, payment_id))
    return "Payment status updated successfully."







# helper functions:


def fetch_unprocessed_payments():
    """
    Fetches unprocessed payments from the database.
    Returns a list of dictionaries containing payment details.
    """
    query = """
    SELECT PaymentID, MemberID, Amount, Service, Status
    FROM Payments
    WHERE Status = 'Unprocessed';
    """
    results = db.execute_query(query, fetch=True)
    return [{'PaymentID': res[0], 'MemberID': res[1], 'Amount': res[2], 'Service': res[3], 'Status': res[4]} for res in results]


def fetch_scheduled_fitness_classes():
    """
    Fetches scheduled fitness classes from the database.
    Returns a list of dictionaries containing class details.
    """
    query = """
    SELECT ClassID, ClassName, StartTime, EndTime, Status
    FROM FitnessClasses
    WHERE Status = 'Scheduled';
    """
    results = db.execute_query(query, fetch=True)
    return [{'ClassID': res[0], 'ClassName': res[1], 'StartTime': res[2], 'EndTime': res[3], 'Status': res[4]} for res in results]


def fetch_scheduled_maintenance():
    """
    Fetches scheduled maintenance records from the database.
    Returns a list of dictionaries containing maintenance details.
    """
    query = """
    SELECT MaintenanceID, MaintenanceSchedule, Status
    FROM EquipmentMaintenance
    WHERE Status = 'Scheduled';
    """
    results = db.execute_query(query, fetch=True)
    return [{'MaintenanceID': res[0], 'MaintenanceSchedule': res[1], 'Status': res[2]} for res in results]


def process_user_choice_for_payments():
    payments = fetch_unprocessed_payments()
    if payments:
        while True:
            print("Unprocessed Payments:")
            for idx, payment in enumerate(payments):
                print(f"{idx+1}. Payment ID: {payment['PaymentID']}, Member ID: {payment['MemberID']}, Amount: ${payment['Amount']}, Service: {payment['Service']}, Status: {payment['Status']}")
            choice = input("Select a payment to process (number) or type 'exit' to exit: ")
            if choice.lower() == 'exit':
                return "Exiting payment processing."
            try:
                choice = int(choice) - 1
                if 0 <= choice < len(payments):
                    return update_payment_status(payments[choice]['PaymentID'], 'Processed')
                else:
                    print("Invalid selection, please try again.")
            except ValueError:
                print("Invalid input, please enter a valid number.")
    else:
        return "No unprocessed payments available."


def display_scheduled_classes():
    classes = fetch_scheduled_fitness_classes()
    if classes:
        while True:
            print("Scheduled Fitness Classes:")
            for idx, cls in enumerate(classes):
                print(f"{idx+1}. Class ID: {cls['ClassID']}, Name: {cls['ClassName']}, Start Time: {cls['StartTime']}, End Time: {cls['EndTime']}, Status: {cls['Status']}")
            choice = input("Select a class to view or modify (number) or type 'exit' to exit: ")
            if choice.lower() == 'exit':
                return "Exiting class selection."
            try:
                choice = int(choice) - 1
                if 0 <= choice < len(classes):
                    # Here you could invoke a function to modify or view details of the selected class
                    # or just return Class ID
                    return f"Class ID {classes[choice]['ClassID']} selected."
                else:
                    print("Invalid selection, please try again.")
            except ValueError:
                print("Invalid input, please enter a valid number.")
    else:
        return "No scheduled classes available."



def manage_maintenance_schedule():
    maintenance_records = fetch_scheduled_maintenance()
    if maintenance_records:
        while True:
            print("Scheduled Maintenance:")
            for idx, record in enumerate(maintenance_records):
                print(f"{idx+1}. Maintenance ID: {record['MaintenanceID']}, Scheduled Time: {record['MaintenanceSchedule']}, Status: {record['Status']}")
            choice = input("Select a maintenance record to update or review (number) or type 'exit' to exit: ")
            if choice.lower() == 'exit':
                return "Exiting maintenance management."
            try:
                choice = int(choice) - 1
                if 0 <= choice < len(maintenance_records):
                    # Additional functionality can be added here such as updating status or viewing detailed info
                    # or can be used to just return maintenance ID
                    return f"Maintenance ID {maintenance_records[choice]['MaintenanceID']} selected."
                else:
                    print("Invalid selection, please try again.")
            except ValueError:
                print("Invalid input, please enter a valid number.")
    else:
        return "No maintenance schedules found."


def schedule_class():
    
    print("Schedule a New Class")
    # Assume the year and month are preset as 2024 and May.
    year = 2024
    month = 5

    # Available classes and their corresponding rooms and required specialization (predefined)
    classes_and_rooms = {
        'Swimming': ('Aqua Center', 1, 'Swimming'),
        'Cardio': ('Cardio Room', 2, 'Cardio'),
        'Yoga': ('Yoga Studio', 3, 'Yoga'),
        'Strength': ('Strength Room', 4, 'Strength')
    }

    # Choose class type
    print("Available Classes:")
    for idx, value in enumerate(classes_and_rooms.keys(), 1):
        print(f"{idx}. {value}")
    class_choice = prompt_for_integer("Choose a class type (number): ", 1, len(classes_and_rooms))
    class_name = list(classes_and_rooms.keys())[class_choice - 1]

    # Automatically determine room and specialization based on class type
    room_name, room_id, specialization = classes_and_rooms[class_name]
    print(f"Room automatically selected: {room_name} (Room ID: {room_id})")

    # Fetch trainers based on the required specialization
    trainers = fetch_trainers_by_specialization(specialization)
    if not trainers:
        print(f"No trainers available with specialization in {specialization}.")
        return "Failed to schedule class."

    print("Available Trainers:")
    for key, value in trainers.items():
        print(f"{key}. {value}")
    trainer_choice = prompt_for_integer("Choose a trainer (number): ", 1, len(trainers))
    trainer_id = trainer_choice

    # Get date and time
    try:
        start_datetime = get_date_time_input(year, month)
        duration = get_duration()
        # Call to schedule the fitness class
        result = schedule_fitness_class(class_name, room_id, trainer_id, start_datetime.strftime('%m/%d/%Y %H:%M'), duration)
        print(result)
    except Exception as e:
        print(f"An error occurred: {e}")


def update_existing_class():
    db = HealthClubDatabase(dbname="Tester", user="postgres", password="postgres", host="localhost")
    print("Updating an Existing Class")

    # Function to display all scheduled classes and choose one to update
    def choose_class_to_update():
        classes = fetch_scheduled_classes()
        if not classes:
            print("No classes available to update.")
            return None
        for idx, cls in enumerate(classes):
            print(f"{idx + 1}. ClassID: {cls['ClassID']}, Name: {cls['ClassName']}, Start Time: {cls['StartTime']}, Duration: {cls['Duration']} minutes")
        class_choice = prompt_for_integer("Choose a class to update (number): ", 1, len(classes))
        return classes[class_choice - 1]

    # Fetch details for all classes that are not cancelled
    def fetch_scheduled_classes():
        query = "SELECT ClassID, ClassName, StartTime, Duration FROM FitnessClasses WHERE Status != 'Cancelled'"
        result = db.execute_query(query, fetch=True)
        return [{'ClassID': res[0], 'ClassName': res[1], 'StartTime': res[2], 'Duration': res[3]} for res in result]

    # Get new time and duration input
    def get_new_timing():
        print("Enter new start time and duration for the class:")
        new_start_datetime = get_date_time_input(2024, 5)  # Example year and month
        new_duration = get_duration()
        return new_start_datetime, new_duration

    # Main update process
    selected_class = choose_class_to_update()
    if selected_class:
        new_start_datetime, new_duration = get_new_timing()
        if is_trainer_available(selected_class['TrainerID'], new_start_datetime.strftime('%m/%d/%Y %H:%M'), new_duration, "Group Class") and \
           check_room_availability(selected_class['RoomID'], new_start_datetime.strftime('%m/%d/%Y %H:%M'), new_duration) and \
           not is_equipment_under_maintenance(new_start_datetime.strftime('%m/%d/%Y %H:%M'), new_duration):
            
            update_query = """
            UPDATE FitnessClasses SET StartTime = %s, Duration = %s WHERE ClassID = %s;
            """
            db.execute_query(update_query, (new_start_datetime, new_duration, selected_class['ClassID']))
            print("Class updated successfully.")
        else:
            print("Failed to update class due to a scheduling conflict or maintenance issue.")
    else:
        print("No class selected or available for update.")
        

        
def manage_classes():
    while True:
        print("\nManage Fitness Classes:")
        print("1. Schedule a new class")
        print("2. Update an existing class")
        print("3. Cancel a class")
        print("4. Return to main menu")
        choice = input("Please enter your choice: ")

        if choice == '1':
            schedule_class()
        elif choice == '2':
            update_existing_class()
        elif choice == '3':
            cancel_existing_class()
        elif choice == '4':
            break
        else:
            print("Invalid input, please try again.")


def manage_maintenance():
    
    while True:
        print("\nManage Equipment Maintenance:")
        print("1. Schedule new maintenance")
        print("2. Update existing maintenance")
        print("3. Review scheduled maintenance")
        print("4. Return to main menu")
        choice = input("Please enter your choice: ")

        if choice == '1':
            schedule_new_maintenance()
        elif choice == '2':
            update_existing_maintenance()
        elif choice == '3':
            review_maintenance()
        elif choice == '4':
            break
        else:
            print("Invalid input, please try again.")


def manage_payments():
    while True:
        print("\nManage Payments:")
        print("1. Process unprocessed payments")
        print("2. Review all payments")
        print("3. Return to main menu")
        choice = input("Please enter your choice: ")

        if choice == '1':
            process_payments()
        elif choice == '2':
            review_payments()
        elif choice == '3':
            break
        else:
            print("Invalid input, please try again.")







