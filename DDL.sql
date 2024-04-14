-- Drop existing tables to avoid conflicts (if re-running this script)
DROP TABLE IF EXISTS MemberSchedule, Payments, EquipmentMaintenance, FitnessClasses, HealthMetrics, FitnessGoals, Members, Trainers, Rooms, AdministrativeStaff CASCADE;

-- AdministrativeStaff Table for a single admin user
CREATE TABLE AdministrativeStaff (
    AdminID SERIAL PRIMARY KEY,
    Password VARCHAR(255)
);

-- Members Table
CREATE TABLE Members (
    MemberID SERIAL PRIMARY KEY,
    FirstName VARCHAR(255) NOT NULL,
    LastName VARCHAR(255) NOT NULL,
    Email VARCHAR(255) UNIQUE NOT NULL,
    Password VARCHAR(255) NOT NULL
);

-- Trainers Table with Specializations
CREATE TABLE Trainers (
    TrainerID SERIAL PRIMARY KEY,
    FirstName VARCHAR(255) NOT NULL,
    LastName VARCHAR(255) NOT NULL,
    Email VARCHAR(255) UNIQUE NOT NULL,
    Password VARCHAR(255),
    Specialization VARCHAR(255) CHECK (Specialization IN ('Weight Loss', 'Strength', 'Cardio', 'Yoga', 'Swimming', 'Rehab', 'Health')),
    UnavailableTimes VARCHAR(255) DEFAULT NULL;
);

-- FitnessGoals Table
CREATE TABLE FitnessGoals (
    FitnessGoalID SERIAL PRIMARY KEY,
    MemberID INTEGER REFERENCES Members(MemberID),
    GoalType VARCHAR(255) CHECK (GoalType IN ('Muscle Gain', 'Endurance', 'Flexibility', 'Strength', 'Overall Health')),
    TargetValue VARCHAR(255)
);

-- HealthMetrics Table
CREATE TABLE HealthMetrics (
    HealthMetricID SERIAL PRIMARY KEY,
    MemberID INTEGER REFERENCES Members(MemberID),
    MetricType VARCHAR(255) CHECK (MetricType IN ('Weight', 'Height', 'BMI', 'Allergies', 'BFP', 'Conditions')),
    MetricValue VARCHAR(255),
    DateRecorded TIMESTAMP
);

-- Rooms Table with specified types
CREATE TABLE Rooms (
    RoomID SERIAL PRIMARY KEY,
    RoomName VARCHAR(255),
    RoomType VARCHAR(255) CHECK (RoomType IN ('Swimming', 'Cardio', 'Yoga', 'Strength')),
    Capacity INTEGER DEFAULT 5
);

-- FitnessClasses Table for scheduling
CREATE TABLE FitnessClasses (
    ClassID SERIAL PRIMARY KEY,
    ClassName VARCHAR(255) CHECK (ClassName IN ('Swimming', 'Cardio', 'Yoga', 'Strength')),
    RoomID INTEGER REFERENCES Rooms(RoomID),
    TrainerID INTEGER REFERENCES Trainers(TrainerID),
    StartTime TIMESTAMP,
    EndTime TIMESTAMP,
    Status VARCHAR(255) CHECK (Status IN ('Scheduled', 'Completed', 'Cancelled'))
);

-- EquipmentMaintenance Table
CREATE TABLE EquipmentMaintenance (
    MaintenanceID SERIAL PRIMARY KEY,
    MaintenanceSchedule TIMESTAMP,
    Status VARCHAR(255) DEFAULT 'Scheduled' CHECK (Status IN ('Scheduled', 'Completed'))
);

-- Payments Table
CREATE TABLE Payments (
    PaymentID SERIAL PRIMARY KEY,
    MemberID INTEGER REFERENCES Members(MemberID),
    Amount DECIMAL(10, 2) DEFAULT 50.00,
    PaymentDate TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    Service VARCHAR(255) CHECK (Service IN ('Membership Fee', 'Personal Training', 'Group Class')),
    Status VARCHAR(255) DEFAULT 'Unprocessed'
);

-- MemberSchedule Table for personal training and group fitness classes
CREATE TABLE MemberSchedule (
    ScheduleID SERIAL PRIMARY KEY,
    MemberID INTEGER REFERENCES Members(MemberID),
    TrainerID INTEGER REFERENCES Trainers(TrainerID) NOT NULL,
    ClassID INTEGER REFERENCES FitnessClasses(ClassID) NOT NULL,
    StartTime TIMESTAMP,
    EndTime TIMESTAMP,
    Status VARCHAR(255) CHECK (Status IN ('Scheduled', 'Completed', 'Cancelled')),
    Type VARCHAR(255) CHECK (Type IN ('Personal Training', 'Group Fitness Class'))
);

CREATE TABLE TrainerUnavailability (
    UnavailabilityID SERIAL PRIMARY KEY,
    TrainerID INTEGER REFERENCES Trainers(TrainerID),
    StartTime TIME NOT NULL,
    EndTime TIME NOT NULL
);
