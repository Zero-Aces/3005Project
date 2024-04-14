from Workflow.db_connection import HealthClubDatabase

# Constants for specializations
SPECIALIZATIONS = ['Weight Loss', 'Strength', 'Cardio', 'Yoga', 'Swimming', 'Rehab', 'Health']

# Database instance
db = HealthClubDatabase(dbname="Tester", user="postgres", password="postgres", host="localhost")

def setup_admin():
    query = "SELECT Password FROM AdministrativeStaff WHERE AdminID = 1"
    admin_password = db.execute_query(query, fetch=True)
    if admin_password and not admin_password[0][0]:  # Check if password is empty
        password = input("Detecting Admin has not been setup yet!\nPlease enter a Password for admin: ")
        update_query = "UPDATE AdministrativeStaff SET Password = %s WHERE AdminID = 1"
        db.execute_query(update_query, (password,))
        print("Admin setup successfully.")
        return True
    elif admin_password:
        return False

def admin_login():
    password = input("Please enter Password: ")
    query = "SELECT Password FROM AdministrativeStaff WHERE AdminID = 1"
    admin_password = db.execute_query(query, fetch=True)
    if password == admin_password[0][0]:
        print("Successful Login, Welcome Admin!")
        return True
    else:
        print("Login failed. Incorrect password.")
        return False

def trainer_login():
    query = "SELECT TrainerID, FirstName, LastName, Email, Password FROM Trainers"
    trainers = db.execute_query(query, fetch=True)
    print("\nList of Trainers:")
    for i, trainer in enumerate(trainers, start=1):
        print(f"{i}. {trainer[1]} {trainer[2]} ({trainer[3]})")
    while True:
        try:
            choice = int(input("Choose a trainer to login (number): "))
            if 1 <= choice <= len(trainers):
                trainer = trainers[choice - 1]
                attempts = 0
                while attempts < 5:
                    if handle_trainer_login(trainer):
                        return trainer[0]  # Return TrainerID
                    else:
                        attempts += 1
                        if attempts == 5:
                            print("Too many failed login attempts.")
                            return False
                break
            else:
                print("Invalid selection.")
        except ValueError:
            print("Invalid input. Please enter a number.")

def handle_trainer_login(trainer):
    if not trainer[4]:  # Password field is empty
        new_password = input(f"Detecting First Login for Trainer {trainer[1]} {trainer[2]}.\nPlease set a password: ")
        update_query = "UPDATE Trainers SET Password = %s WHERE TrainerID = %s"
        db.execute_query(update_query, (new_password, trainer[0]))
        print(f"Password Set, Logging in Trainer {trainer[1]} {trainer[2]}")
        return True
    else:
        password = input("Please enter Password: ")
        if password == trainer[4]:
            print(f"Successful Login, Welcome Trainer {trainer[1]} {trainer[2]}!")
            return True
        else:
            print("Login failed. Incorrect password.")
            return False

def register_trainer():
    first_name = input("Please enter new Trainer's First Name: ")
    last_name = input("Please enter new Trainer's Last Name: ")
    email = f"{first_name.lower()}.{last_name.lower()}@hfc.com"
    print("Available Specializations:")
    for idx, spec in enumerate(SPECIALIZATIONS, 1):
        print(f"{idx}. {spec}")
    spec_choice = int(input("Choose specialization by number: "))
    if 1 <= spec_choice <= len(SPECIALIZATIONS):
        specialization = SPECIALIZATIONS[spec_choice - 1]
        password = input("Set an initial password for the trainer: ")
        insert_query = "INSERT INTO Trainers (FirstName, LastName, Email, Password, Specialization) VALUES (%s, %s, %s, %s, %s)"
        db.execute_query(insert_query, (first_name, last_name, email, password, specialization))
        print(f"Successfully registered new Trainer '{first_name} {last_name}'")
        return True
    else:
        print("Invalid specialization choice.")
        return False

def register_member():
    first_name = input("Please enter First Name: ")
    last_name = input("Please enter Last Name: ")
    email = input("Please enter Email: ")
    password = input("Please enter Password: ")
    insert_query = "INSERT INTO Members (FirstName, LastName, Email, Password) VALUES (%s, %s, %s, %s) RETURNING MemberID"
    member_id = db.execute_query(insert_query, (first_name, last_name, email, password), fetch=True)[0][0]
    payment_query = "INSERT INTO Payments (MemberID, Amount, Service, Status) VALUES (%s, 50.00, 'Membership Fee', 'Unprocessed')"
    db.execute_query(payment_query, (member_id,))
    print(f"Successfully registered new Member '{first_name} {last_name}' and recorded initial unprocessed payment.")
    return True
            
def member_login():
    count_query = "SELECT COUNT(*) FROM Members"
    member_count = db.execute_query(count_query, fetch=True)[0][0]
    if member_count == 0:
        print("Detecting that there are currently no members registered.")
        print("Automatically beginning registration process!")
        if register_member():
            return member_login()  # Recursive call to re-attempt login after registration

    while True:
        method = input("Would you like to login by (1) Email or (2) Name? Enter 1 or 2: ")
        if method not in ['1', '2']:
            print("Invalid choice, please enter 1 for Email or 2 for Name.")
        else:
            option = "Email" if method == '1' else "Name"
            attempts = 0
            while attempts < 5:
                identifier = input(f"Please enter your {option}: ")
                if method == '1':
                    query = "SELECT MemberID, Password FROM Members WHERE Email = %s"
                else:
                    query = "SELECT MemberID, Password FROM Members WHERE FirstName = %s OR LastName = %s"

                member = db.execute_query(query, (identifier, identifier if method != '1' else None), fetch=True)
                if member:
                    member_id, stored_password = member[0]
                    password = input("Please enter Password: ")
                    if password == stored_password:
                        print("Successful Login, Welcome Member!")
                        return member_id  # Return MemberID
                    else:
                        print("Login failed. Incorrect password.")
                        attempts += 1
                        if attempts == 5:
                            print("Too many failed login attempts.")
                            return False
                else:
                    print("Member not found.")

