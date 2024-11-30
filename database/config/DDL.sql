CREATE TABLE admin (
    admin_id INT PRIMARY KEY AUTO_INCREMENT,
    admin_name VARCHAR(100),
    mail VARCHAR(100) UNIQUE,
    mobile_number VARCHAR(15),
    address VARCHAR(255),
    city VARCHAR(100),
    state VARCHAR(100),
    country VARCHAR(100),
    zipcode VARCHAR(10),
    pass VARCHAR(100) NOT NULL
);

CREATE TABLE department (
    department_id INT PRIMARY KEY AUTO_INCREMENT,
    dept_name VARCHAR(100),
    admin_id INT,
    FOREIGN KEY (admin_id) REFERENCES admin(admin_id)
);

CREATE TABLE employee (
    employee_id INT PRIMARY KEY AUTO_INCREMENT,
    employee_name VARCHAR(100),
    mail VARCHAR(100),
    mobileNumber VARCHAR(15),
    role VARCHAR(50),
    address VARCHAR(255),
    city VARCHAR(100),
    state VARCHAR(100),
    country VARCHAR(100),
    zipcode VARCHAR(10),
    emp_password VARCHAR(100) NOT NULL,
    emp_status VARCHAR (10),
    salary numeric(8, 0),
    department_id INT,
    FOREIGN KEY (department_id) REFERENCES department(department_id)
);

CREATE TABLE shifts (
    shift_id INT PRIMARY KEY AUTO_INCREMENT,
    start_time TIME,
    end_time TIME,
    shift_name VARCHAR(50)
);

CREATE TABLE employee_shifts (
    employee_id INT,
    shift_id INT,
    PRIMARY KEY (employee_id, shift_id),
    FOREIGN KEY (employee_id) REFERENCES employee(employee_id),
    FOREIGN KEY (shift_id) REFERENCES shifts(shift_id)
);

CREATE TABLE train (
    train_id INT PRIMARY KEY,
    train_name VARCHAR(100),
    train_type VARCHAR(50),
    train_capacity INT,
    numOfCoaches INT,
    admin_id INT,
    FOREIGN KEY (admin_id) REFERENCES admin(admin_id)
);

CREATE TABLE maintenanceschedule (
    maintenance_id INT PRIMARY KEY AUTO_INCREMENT,
    maintenance_date DATE,
    main_description VARCHAR(120),
    main_status VARCHAR(50),
    train_id INT,
    FOREIGN KEY (train_id) REFERENCES train(train_id)
);

CREATE TABLE stations (
    station_id INT PRIMARY KEY AUTO_INCREMENT,
    name VARCHAR(100),
    address VARCHAR(255),
    city VARCHAR(100),
    state VARCHAR(100),
    country VARCHAR(100),
    zipcode VARCHAR(10)
);

CREATE TABLE route (
    route_id INT PRIMARY KEY AUTO_INCREMENT,
    num_of_stationstops INT,
    distance DECIMAL(10, 2),
    start_station INT,
    end_station INT,
    FOREIGN KEY (start_station) REFERENCES stations(station_id),
    FOREIGN KEY (end_station) REFERENCES stations(station_id)
);

CREATE TABLE schedules (
    schedule_id INT PRIMARY KEY AUTO_INCREMENT,
    start_date DATE,
    start_point INT,
    departure_time TIME,
    end_point INT,
    end_date DATE,
    arrival_time TIME,
    status VARCHAR(50),
    price DECIMAL(10, 2),
    seats_available INT,
    train_id INT,
    FOREIGN KEY (train_id) REFERENCES train(train_id),
    UNIQUE (start_date, departure_time, train_id)
);

CREATE TABLE train_schedules (
    train_id INT,
    schedule_id INT,
    PRIMARY KEY (train_id, schedule_id),
    FOREIGN KEY (train_id) REFERENCES train(train_id),
    FOREIGN KEY (schedule_id) REFERENCES schedules(schedule_id)
);

CREATE TABLE route_stations (
    route_id INT,
    station_id INT,
    order_id INT,
    stoptime INT,
    PRIMARY KEY (route_id, station_id),
    FOREIGN KEY (route_id) REFERENCES route(route_id),
    FOREIGN KEY (station_id) REFERENCES stations(station_id)
);

CREATE TABLE route_schedules (
    route_id INT,
    schedule_id INT,
    PRIMARY KEY (route_id, schedule_id),
    FOREIGN KEY (route_id) REFERENCES route(route_id) ,
    FOREIGN KEY (schedule_id) REFERENCES schedules(schedule_id)
);

CREATE TABLE seats (
    seat_id INT PRIMARY KEY AUTO_INCREMENT,
    seat_number VARCHAR(10),
    class VARCHAR(50),
    price DECIMAL(10, 2),
    train_id INT,
    FOREIGN KEY (train_id) REFERENCES train(train_id)
);

CREATE TABLE scheduleseats (
    schedule_id INT,
    seat_id INT,
    availability_status varchar(20),
    PRIMARY KEY (schedule_id, seat_id),
    FOREIGN KEY (schedule_id) REFERENCES schedules(schedule_id),
    FOREIGN KEY (seat_id) REFERENCES seats(seat_id)
);

CREATE TABLE cancellations (
    cancellation_id INT PRIMARY KEY AUTO_INCREMENT,
    schedule_id INT,
    cancellation_date DATE,
    reason TEXT,
    FOREIGN KEY (schedule_id) REFERENCES schedules(schedule_id)
);

CREATE TABLE delay (
    delay_id INT PRIMARY KEY AUTO_INCREMENT,
    schedule_id INT,
    duration TIME,
    reason VARCHAR(255),
    FOREIGN KEY (schedule_id) REFERENCES schedules(schedule_id)
);

CREATE TABLE user (
    user_id INT PRIMARY KEY AUTO_INCREMENT,
    name VARCHAR(100),
    mail VARCHAR(100) UNIQUE,
    mobileNumber VARCHAR(15),
    address VARCHAR(255),
    city VARCHAR(100),
    state VARCHAR(100),
    country VARCHAR(100),
    zipcode VARCHAR(10),
    user_password VARCHAR(100)
);


CREATE TABLE booking (
    booking_id INT PRIMARY KEY AUTO_INCREMENT,
    user_id INT,
    date DATE,
    booking_time time,
    status VARCHAR(50),
    FOREIGN KEY (user_id) REFERENCES user(user_id)
);

CREATE TABLE dependents (
    dependent_id INT PRIMARY KEY AUTO_INCREMENT,
    dependent_name VARCHAR(100),
    mail VARCHAR(100),
    mobileNumber VARCHAR(15),
    age INT,
    user_id INT,
    booking_id INT,
    FOREIGN KEY (user_id) REFERENCES user(user_id),
    FOREIGN KEY (booking_id) REFERENCES booking(booking_id)
);

CREATE TABLE feedback (
    feedback_id INT PRIMARY KEY AUTO_INCREMENT,
    feed_description TEXT,
    feed_date DATE,
    feed_time TIME,
    user_id INT,
    FOREIGN KEY (user_id) REFERENCES user(user_id)
);

CREATE TABLE ticket (
    ticket_id INT PRIMARY KEY AUTO_INCREMENT,
    ticket_number VARCHAR(20),
    booking_id INT,
    seat_id INT,
    schedule_id INT,
    issue_date DATE,
    status VARCHAR(50),
    user_id INT,
    dependent_id INT,
    FOREIGN KEY (booking_id) REFERENCES booking(booking_id),
    FOREIGN KEY (seat_id) REFERENCES seats(seat_id),
    FOREIGN KEY (schedule_id) REFERENCES schedules(schedule_id),
    FOREIGN KEY (user_id) REFERENCES user(user_id),
    FOREIGN KEY (dependent_id) REFERENCES dependents(dependent_id)
);

CREATE TABLE notifications (
    notification_id INT PRIMARY KEY AUTO_INCREMENT,
    noti_description TEXT,
    noti_date DATE,
    noti_time TIME,
    admin_id INT,
    FOREIGN KEY (admin_id) REFERENCES admin(admin_id)
);

CREATE TABLE user_notifications (
    user_id INT,
    notification_id INT,
    FOREIGN KEY (user_id) REFERENCES user(user_id),
    FOREIGN KEY (notification_id) REFERENCES notifications(notification_id),
    PRIMARY KEY (user_id, notification_id)
);

CREATE TABLE payment (
    payment_id INT PRIMARY KEY AUTO_INCREMENT,
    payment_type VARCHAR(50),
    address VARCHAR(255),
    city VARCHAR(100),
    state VARCHAR(100),
    country VARCHAR(100),
    zipcode VARCHAR(10),
    cardNumber VARCHAR(16),
    pay_status VARCHAR(50),
    pay_date DATETIME,
    total_price DECIMAL(10,2),
    booking_id INT,
    FOREIGN KEY (booking_id) REFERENCES booking(booking_id)
);
