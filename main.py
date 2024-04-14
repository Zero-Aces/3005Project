import time
from Workflow.auth import setup_admin, admin_login, trainer_login, register_trainer, member_login, register_member
from Operations.admin import manage_classes, manage_maintenance, manage_payments
from Operations.member import view_dashboard, manage_appointments, update_profile
from Operations.trainer import view_schedule, manage_availability, view_member_profiles

def main_menu():
    print("""
Welcome to the Health and Fitness Club Management Simulation!
Please wait while the simulation boots up!
""")
    for percent in [0, 25, 75, 100]:
        print(f"{percent}%")
        time.sleep(1)  # Simulate loading

    while True:
        print("""
What would you like to continue as:
1. Admin
2. Trainer
3. Member
4. Quit
""")
        choice = input("Enter your choice: ")
        if choice == '1':
            admin_workflow()
        elif choice == '2':
            trainer_workflow()
        elif choice == '3':
            member_workflow()
        elif choice == '4':
            print("Exiting the simulation...")
            break
        else:
            print("Invalid choice, please select a valid option.")

def admin_workflow():
    if not setup_admin():  # Returns True if setup was needed and completed
        if not admin_login():
            return
    print("Accessing Admin Management System...")
    admin_manage()

def trainer_workflow():
    print("Would you like to:")
    print("1. Login")
    print("2. Register New Trainer")
    choice = input("Choose an option: ")
    if choice == '1':
        trainer_id = trainer_login()
        if trainer_id:
            print(f"Trainer ID {trainer_id} logged in successfully.")
            trainer_manage()
    elif choice == '2':
        if register_trainer():
            trainer_id = trainer_login()
            if trainer_id:
                print(f"Trainer ID {trainer_id} logged in successfully.")
                trainer_manage()

def member_workflow():
    print("Would you like to:")
    print("1. Login")
    print("2. Register New Member")
    choice = input("Choose an option: ")
    if choice == '1':
        member_id = member_login()
        if member_id:
            print(f"Member ID {member_id} logged in successfully.")
            member_manage()
    elif choice == '2':
        if register_member():
            member_id = member_login()
            if member_id:
                print(f"Member ID {member_id} logged in successfully.")
                member_manage()
            
   
         
def admin_manage():
    while True:
        print("""
Select an option:
1. Manage Classes
2. Manage Equipment Maintenance
3. Manage Payments
4. Logout""")
        choice = input("Enter your choice: ")
        if choice == '1':
            manage_classes()
        elif choice == '2':
            manage_maintenance()
        elif choice == '3':
            manage_payments()
        elif choice == '4':
            print("Logging out...")
            break
        else:
            print("Invalid choice.")

def trainer_manage():
    while True:
        print("""
Select an option:
1. View Schedule
2. Manage Availability
3. View Member Profiles
4. Logout""")
        choice = input("Enter your choice: ")
        if choice == '1':
            view_schedule()
        elif choice == '2':
            manage_availability()
        elif choice == '3':
            view_member_profiles()
        elif choice == '4':
            print("Logging out...")
            break
        else:
            print("Invalid choice.")


def member_manage():
    while True:
        print("""
Select an option:
1. View Dashboard
2. Update Profile
3. Manage Classes/Sessions
4. Logout""")
        choice = input("Enter your choice: ")
        if choice == '1':
            view_dashboard()
        elif choice == '2':
            update_profile()
        elif choice == '3':
            manage_appointments()
        elif choice == '4':
            print("Logging out...")
            break
        else:
            print("Invalid choice.")