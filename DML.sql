-- Insert default admin (Password will be set upon first login)
INSERT INTO AdministrativeStaff (Password) VALUES (NULL);

-- Insert default trainers (Passwords will be set upon first login)
INSERT INTO Trainers (FirstName, LastName, Email, Password, Specialization)
VALUES
('Sydney', 'Doe', 'sydney.doe@hfc.com', NULL, 'Weight Loss'),
('Alex', 'Smith', 'alex.smith@hfc.com', NULL, 'Strength'),
('Elsa', 'Johnson', 'elsa.johnson@hfc.com', NULL, 'Cardio'),
('Vivian', 'Lee', 'vivian.lee@hfc.com', NULL, 'Yoga'),
('Max', 'Davis', 'max.davis@hfc.com', NULL, 'Swimming'),
('Kane', 'Brown', 'kane.brown@hfc.com', NULL, 'Rehab'),
('Jerome', 'Miller', 'jerome.miller@hfc.com', NULL, 'Health');

-- Insert default rooms
INSERT INTO Rooms (RoomName, RoomType, Capacity)
VALUES
('Aqua Center', 'Swimming', 5),
('Yoga Studio', 'Yoga', 5),
('Cardio Room', 'Cardio', 5),
('Strength Room', 'Strength', 5);

-- Inserting initial values for Equipment Maintenance (Assuming a future date for demo purposes)
INSERT INTO EquipmentMaintenance (MaintenanceSchedule, Status)
VALUES
('2024-12-01 10:00:00', 'Scheduled'),
('2024-12-02 10:00:00', 'Scheduled');
