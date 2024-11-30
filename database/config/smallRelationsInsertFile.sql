SET FOREIGN_KEY_CHECKS = 0;
TRUNCATE TABLE employee_shifts;
TRUNCATE TABLE maintenanceschedule;
TRUNCATE TABLE scheduleseats;
TRUNCATE TABLE employee;
TRUNCATE TABLE department;
TRUNCATE TABLE admin;
TRUNCATE TABLE train;
TRUNCATE TABLE shifts;
TRUNCATE TABLE stations;
TRUNCATE TABLE route;
TRUNCATE TABLE schedules;
TRUNCATE TABLE seats;
TRUNCATE TABLE user;
TRUNCATE TABLE ticket;
TRUNCATE TABLE booking;
TRUNCATE TABLE feedback;
TRUNCATE TABLE notifications;
TRUNCATE TABLE cancellations;
TRUNCATE TABLE delay;
TRUNCATE TABLE payment;
SET FOREIGN_KEY_CHECKS = 1;

INSERT INTO admin (admin_name, mail, mobile_number, address, city, state, country, zipcode, pass)
VALUES
    ('John Doe', 'john.doe@example.com', '1234567890', '123 Admin Street', 'Admin City', 'Admin State', 'CountryX', '12345', 'securepass1'),
    ('Jane Smith', 'jane.smith@example.com', '0987654321', '456 Admin Lane', 'Admin Town', 'Admin State', 'CountryY', '67890', 'securepass2'),
    ('Train Admin', 'admin@gmail.com', '0987654321', '456 Admin Lane', 'Admin Town', 'Admin State', 'CountryY', '67890', '123');

INSERT INTO department (dept_name, admin_id)
VALUES
    ('Engineering', 1),
    ('Operations', 2),
    ('None', 3);

INSERT INTO employee (employee_id, employee_name, mail, mobileNumber, role, address, city, state, country, zipcode, emp_password, emp_status, salary, department_id)
VALUES
    (1001, 'Alice Johnson', 'alice.j@example.com', '1231231234', 'Engineer', '12 Elm Street', 'CityA', 'StateA', 'CountryA', '45678', 'password123', 'Active', 50000, 1),
    (1002, 'Bob Brown', 'bob.b@example.com', '9879879876', 'Operator', '34 Pine Street', 'CityB', 'StateB', 'CountryB', '12345', 'password456', 'Inactive', 45000, 2);

INSERT INTO shifts (start_time, end_time, shift_name)
VALUES
    ('08:00:00', '16:00:00', 'Morning Shift'),
    ('16:00:00', '00:00:00', 'Evening Shift');

INSERT INTO employee_shifts (employee_id, shift_id)
VALUES
    (1001, 1),
    (1002, 2);

INSERT INTO train (train_id, train_name, train_type, train_capacity, numOfCoaches, admin_id)
VALUES
    (1, 'Express 101', 'Express', 500, 10, 1),
    (2, 'Local 202', 'Local', 300, 6, 2);

INSERT INTO maintenanceschedule (maintenance_date, main_description, main_status, train_id)
VALUES
    ('2024-11-30', 'Routine Maintenance', 'Scheduled', 1),
    ('2024-12-15', 'Brake Check', 'Scheduled', 2);

INSERT INTO stations (name, address, city, state, country, zipcode)
VALUES
    ('Central Station', '123 Main St', 'Metro City', 'StateX', 'CountryZ', '11111'),
    ('East Station', '456 East Blvd', 'Metro City', 'StateX', 'CountryZ', '22222');

INSERT INTO route (num_of_stationstops, distance, start_station, end_station)
VALUES
    (2, 120.5, 1, 2),
    (2, 115, 1, 2);

INSERT INTO schedules (start_date, start_point, departure_time, end_point, end_date, arrival_time, status, price, seats_available, train_id)
VALUES
    ('2024-12-01', 1, '09:00:00', 2, '2024-12-01', '12:00:00', 'On Time', 50.00, 200, 1),
    ('2024-12-02', 1, '10:00:00', 2, '2024-12-02', '13:00:00', 'On Time', 45.00, 250, 2);

INSERT INTO train_schedules (train_id, schedule_id)
VALUES
    (1, 1),
    (2, 2);

INSERT INTO route_stations (route_id, station_id, order_id, stoptime)
VALUES
    (1, 1, 0,10),
    (1, 2, 1, 20),
    (2, 2, 0, 15),
    (2, 1, 1, 25);

INSERT INTO route_schedules (route_id, schedule_id)
VALUES
    (1, 1),
    (2, 2);

INSERT INTO seats (seat_number, class, price, train_id)
VALUES
    (1, '2S', 25.00, 1),
    (2, 'SL', 50.00, 1),
    (3, '2S', 20.00, 2),
    (4, 'SL', 40.00, 2);

INSERT INTO scheduleseats (schedule_id, seat_id)
VALUES
    (1, 1),
    (1, 2),
    (2, 3),
    (2, 4);

INSERT INTO cancellations (schedule_id, cancellation_date, reason)
VALUES
    (1, '2024-11-01', 'Technical Issues'),
    (2, '2024-11-15', 'Low Ticket Sales');

INSERT INTO delay (schedule_id, duration, reason)
VALUES
    (1, '00:30:00', 'Weather Conditions'),
    (2, '01:00:00', 'Mechanical Issues');

INSERT INTO user (name, mail, mobileNumber, address, city, state, country, zipcode, user_password)
VALUES
    ('Tom Hanks', 'tom.h@example.com', '5555555555', '789 Maple St', 'CityX', 'StateY', 'CountryZ', '99999', 'userpass1'),
    ('Emma Watson', 'emma.w@example.com', '4444444444', '101 Oak St', 'CityY', 'StateZ', 'CountryX', '88888', 'userpass2');

INSERT INTO booking (user_id, date, booking_time, status)
VALUES
    (1, '2024-12-01', '08:30:00', 'Confirmed'),
    (2, '2024-12-02', '09:15:00', 'Pending');

INSERT INTO dependents (dependent_name, mail, mobileNumber, age, user_id, booking_id)
VALUES
    ('Charlie Green', 'charlie.green@example.com', '5551234567', 15, 1, 1),
    ('Diana White', 'diana.white@example.com', '4449876543', 18, 2, 2);

INSERT INTO feedback (feed_description, feed_date, feed_time, user_id)
VALUES
    ('Great service!', '2024-11-01', '14:00:00', 1),
    ('Delayed train, but comfortable ride.', '2024-11-02', '16:00:00', 2);

INSERT INTO ticket (ticket_number, booking_id, seat_id, schedule_id, issue_date, status, user_id)
VALUES
    ('T12345', 1, 1, 1, '2024-12-01', 'Issued', 1),
    ('T12346', 2, 2, 2, '2024-12-02', 'Issued', 2);

INSERT INTO notifications (noti_description, noti_date, noti_time, admin_id)
VALUES
    ('Train 1 delayed by 30 minutes.', '2024-11-01', '09:00:00', 1),
    ('Train 2 maintenance scheduled.', '2024-11-05', '08:00:00', 2);

INSERT INTO user_notifications (user_id, notification_id)
VALUES
    (1, 1),
    (2, 2);

INSERT INTO payment (payment_type, address, city, state, country, zipcode, cardNumber, pay_status, pay_date, total_price, booking_id)
VALUES
    ('Credit Card', '123 Main St', 'San Francisco', 'CA', 'USA', '94101', '1234567812345678', 'Completed', '2024-11-01 10:30:00', '100', 1),
    ('Debit Card', '456 Elm St', 'Dallas', 'TX', 'USA', '75201', '8765432187654321', 'Refunded', '2024-11-02 10:30:00', '200', 2);
