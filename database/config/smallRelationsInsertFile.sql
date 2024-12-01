SET FOREIGN_KEY_CHECKS = 0;
TRUNCATE TABLE employee_shifts;
TRUNCATE TABLE maintenanceschedule;
TRUNCATE TABLE scheduleseats;
TRUNCATE TABLE train_schedules;
TRUNCATE TABLE employee;
TRUNCATE TABLE department;
TRUNCATE TABLE admin;
TRUNCATE TABLE train;
TRUNCATE TABLE shifts;
TRUNCATE TABLE route_stations
TRUNCATE TABLE stations;
TRUNCATE TABLE route;
TRUNCATE TABLE schedules;
TRUNCATE TABLE seats;
TRUNCATE TABLE dependents;
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
    (101, 'CH Express', 'Express', 5, 2, 3),
    (102, 'HC Express', 'Local', 5, 2, 3);


INSERT INTO maintenanceschedule (maintenance_date, main_description, main_status, train_id)
VALUES
    ('2024-12-01', 'Routine Maintenance', 'In Progress', 102);

INSERT INTO stations (name, address, city, state, country, zipcode)
VALUES
    ('MGR central', 'Grand Western Trunk Road', 'Chennai', 'Tamil Nadu', 'India', '600003'),
    ('Hyderabad Deccan', 'Public Garden Rd, Devi Bagh, Red Hills', 'Hyderabad', 'Telangana', 'India', '500001'),
    ('Piduguralla Station', 'Piduguralla', 'Piduguralla', 'Andhra Pradesh', 'India', '522413'),
    ('Vijayawada Station', 'Vinchipeta', 'Vijayawada', 'Andhra Pradesh', 'India', '520001');


    INSERT INTO route (num_of_stationstops, distance, start_station, end_station)
VALUES
    (2, 1000.00, 1, 2),
    (3, 700.00, 1, 2);

INSERT INTO schedules (start_date, start_point, departure_time, end_point, end_date, arrival_time, status, price, seats_available, train_id)
VALUES
    ('2024-12-08', 1, '13:59:00', 2, '2024-12-10', '13:59:00', 'Delayed', 100.00, 4, 101),
    ('2024-12-05', 1, '14:12:00', 2, '2024-12-06', '14:12:00', 'Cancelled', 50.00, 4, 101);

INSERT INTO train_schedules (train_id, schedule_id)
VALUES
    (101, 1),
    (101, 2);


INSERT INTO route_stations (route_id, station_id, order_id, stoptime)
VALUES
    (1, 1, 0,10),
    (1, 2, 1, 10),
    (1, 3, 1, 10),
    (2, 1, 0, 10),
    (2, 2, 1, 10),
    (2, 4, 1, 10);

INSERT INTO route_schedules (route_id, schedule_id)
VALUES
    (1, 1),
    (2, 2);

INSERT INTO seats (seat_number, class, price, train_id)
VALUES
    (SL1, 'SL', 100.00, 101),
    (CC1, 'CC', 75.00, 101),
    (CC2, 'CC', 75.00, 101),
    (2S1, '2S', 50.00, 101),
    (2S2, '2S', 50.00, 101),
    (SL1, 'SL', 100.00, 102),
    (CC1, 'CC', 75.00, 102),
    (CC2, 'CC', 75.00, 102),
    (2S1, '2S', 50.00, 102),
    (2S2, '2S', 50.00, 102);


INSERT INTO scheduleseats (schedule_id, seat_id,availability_status)
VALUES
    (1, 1,'Available'),
    (1, 2, 'Booked'),
    (1, 3, 'Available'),
    (1, 4, 'Available'),
    (1, 5,'Available'),
    (2, 1,'Booked'),
    (2, 2, 'Available'),
    (2, 3, 'Available'),
    (2, 4, 'Available'),
    (2, 5,'Available');

INSERT INTO cancellations (schedule_id, cancellation_date, reason)
VALUES
    (2, '2024-11-3', 'engine failure');

INSERT INTO delay (schedule_id, duration, reason)
VALUES
    (1, '00:10:00', 'crossing');

INSERT INTO user (name, mail, mobileNumber, address, city, state, country, zipcode, user_password)
VALUES
    ('Madhuri', 'avm122@gmail.com', '1234567891', '1101 Avenue', 'Piduguralla', 'Andhra Pradesh', 'India', '522413', '123');

INSERT INTO booking (user_id, date, booking_time, status)
VALUES
    (1, '2024-11-10', '14:32:58', 'Confirmed'),
    (1, '2024-11-10', '15:02:41', 'Confirmed');

INSERT INTO dependents (dependent_name, mail, mobileNumber, age, user_id, booking_id)
VALUES
    ('Madhuri', 'avm122@gmail.com', '1234567891', 25, 1, 1),
    ('Adi', 'avm@gmail.com', '9010901010', 26, 1, 2);

INSERT INTO feedback (feed_description, feed_date, feed_time, user_id)
VALUES
    ('Seats are very comfortable', '2024-11-30', '14:51:08', 1);

INSERT INTO ticket (ticket_number, booking_id, seat_id, schedule_id, issue_date, status, user_id,dependent_id)
VALUES
    ('TICKET4630', 1, 1, 2, '2024-11-30', 'Cancelled', 1,1),
    ('TICKET3867', 2, 2, 1, '2024-11-30', 'Issued', 1,2)

INSERT INTO notifications (noti_description, noti_date, noti_time, admin_id)
VALUES
    ('added food system inside train for ordering', '2024-11-30', '14:55:36', 3);

INSERT INTO user_notifications (user_id, notification_id)
VALUES
    (1, 1);

INSERT INTO payment (payment_type, address, city, state, country, zipcode, cardNumber, pay_status, pay_date, total_price, booking_id)
VALUES
    ('Creditcard', '1101 Avenue', 'Piduguralla', 'Andhra Pradesh', 'India', '522413', '123456', 'refunded', '2024-11-30 14:32:00', '150.00', 1),
    ('debitcard', '11111 era', 'Hyderabad', 'Telangana', 'India', '522001', '1234567890', 'Confirmed', '2024-11-30 15:02:41', '175.00', 2);

