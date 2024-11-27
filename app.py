from random import random
from flask import flash, Flask, render_template, request, redirect, url_for, session, jsonify
from flask_mysqldb import MySQL
from datetime import datetime
import random


app = Flask(__name__)

# MySQL configuration
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = 'Mysql@2024'
app.config['MYSQL_DB'] = 'RailwayManagement'
app.secret_key = 'BAD_SECRET_KEY'
# Initialize MySQL
mysql = MySQL(app)

@app.route('/')
def home():
    return render_template('index.html')


@app.route('/admin_login')
def admin_login():
    return render_template('Admin/admin_login.html')

@app.route('/admin_login', methods=['POST'])
def submit_login():
    # Get email and password from the form
    email = request.form['email']
    password = request.form['password']
    # Check if email and password are not empty
    if email and password:
        # Get the database connection using the Flask-MySQLdb extension
        conn = mysql.connection
        cursor = conn.cursor()

        # Query the database to check if the email exists and password matches
        cursor.execute("SELECT * FROM admin WHERE mail = %s and pass=%s", (email,password))
        user = cursor.fetchone()
        cursor.close()
        if user and user[-1] == password:  # user[2] corresponds to the password field
            session['admin_id'] = user[0]
            return redirect(url_for('admin_dashboard'))  # Redirect to dashboard if login is successful
        else:
            return render_template('Admin/admin_login.html', error="Invalid email or password.")
    else:
        return render_template('Admin/admin_login.html', error="Please enter both email and password.")

@app.route('/admin_dashboard')
def admin_dashboard():
    admin_id=session.get('admin_id')
    if admin_id:
        return render_template('Admin/admin_dashboard.html')
    else:
        return redirect(url_for('admin_login'))

@app.route('/add_departments')
def view_departments():
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM department")
    departments = cur.fetchall()  # Fetch all records from the table
    cur.close()
    return render_template('Admin/add_department.html',departments=departments)

@app.route('/add_departments', methods=['POST'])
def add_departments():
    admin_id = session.get('admin_id')
    if not admin_id:
        return redirect(url_for('admin_login'))  # Redirect if no admin is logged in
    if request.method == 'POST':
        department_id = request.form['departmentId']
        dept_name = request.form['dept_name']
        cur = mysql.connection.cursor()
        try:
            # Check if department name already exists
            cur.execute("SELECT department_id FROM department WHERE dept_name = %s", (dept_name,))
            existing_deptname = cur.fetchone()
            if existing_deptname:
                departments = cur.fetchall()
                return render_template('Admin/add_department.html',departments=departments,error="Department name already exists. Please choose another name.")

            # Check if department ID already exists
            cur.execute("SELECT department_id FROM department WHERE department_id = %s", (department_id,))
            existing_dept_id = cur.fetchone()
            if existing_dept_id:
                departments = cur.fetchall()
                return render_template('Admin/add_department.html',departments=departments,error="Department ID already exists. Please choose another ID.")

            # Insert the new department into the database
            cur.execute("INSERT INTO department(department_id, dept_name, admin_id) VALUES (%s, %s, %s)",(department_id, dept_name, admin_id))
            mysql.connection.commit()
            return redirect(url_for('view_departments'))  # Redirect to the departments list
        except Exception as e:
            mysql.connection.rollback()  # Rollback if there is any error
            return f"Error: {str(e)}"
        finally:
            cur.close()
    return render_template('Admin/add_department.html')

@app.route('/edit_department', methods=['POST'])
def edit_departments():
    admin_id = session.get('admin_id')
    if not admin_id:
        return redirect(url_for('admin_login'))
    if request.method == 'POST':
        editDeptName = request.form['editDeptName']
        editDeptId = request.form['editDeptId']
        if not editDeptName or not editDeptId:
            return render_template('Admin/add_department.html', error="Please provide both department name and department ID.")
        try:
            editDeptId = int(editDeptId)  # Ensure it's an integer if required
        except ValueError:
            return render_template('Admin/add_department.html', error="Invalid department ID. Please enter a valid number.")
        cur = mysql.connection.cursor()
        try:
            cur.execute("SELECT * FROM department WHERE dept_name = %s;", (editDeptName,))
            existing_dept = cur.fetchone()  # Fetch one record if it exists
            cur.execute("SELECT * FROM department")
            departments = cur.fetchall()

            if existing_dept:
                return render_template('Admin/add_department.html',departments=departments, error="This department name already exists. Try a different name.")

            # Update the department in the database
            cur.execute("UPDATE department SET dept_name = %s, admin_id = %s WHERE department_id = %s;",(editDeptName, admin_id, editDeptId))
            mysql.connection.commit()
            return redirect(url_for('view_departments'))  # Redirect to view departments
        except Exception as e:
            mysql.connection.rollback()  # Rollback if there is any error
            return f"Error: {str(e)}"
        finally:
            cur.close()
    return render_template('Admin/add_department.html')

@app.route('/delete_department', methods=['POST'])
def delete_department():
    if request.method == 'POST':
        department_id = request.form['department_id']
        cur = mysql.connection.cursor()
        try:
            # Check if the department exists
            cur.execute("SELECT * FROM department WHERE department_id = %s", (department_id,))
            department = cur.fetchone()

            if department is None:
                return render_template('Admin/departments.html', error="Department not found.")

            # Delete the department
            cur.execute("DELETE FROM department WHERE department_id = %s", (department_id,))
            mysql.connection.commit()
            return redirect(url_for('view_departments'))  # Redirect after success
        except Exception as e:
            mysql.connection.rollback()  # Rollback in case of an error
            return f"Error: {str(e)}"
        finally:
            cur.close()
    else:
        return redirect(url_for('admin_login'))

@app.route('/add_employees')
def view_employees():
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM employee")
    employees = cur.fetchall()
    cur.execute("SELECT * FROM department")
    departments = cur.fetchall()# Fetch all records from the table
    cur.close()
    return render_template('Admin/add_employee.html',departments=departments,employees=employees)

@app.route('/add_employees', methods=['POST'])
def add_employees():
    admin_id=session.get('admin_id')
    if admin_id:
        if request.method == 'POST':
            #employee_id = request.form['employee_id']
            employee_name = request.form['employee_name']
            mail = request.form['mail']
            mobileNumber = request.form['mobileNumber']
            role = request.form['role']
            address = request.form['address']
            city = request.form['city']
            state = request.form['state']
            country = request.form['country']
            zipcode = request.form['zipcode']
            emp_password = request.form['emp_password']
            emp_status = request.form['emp_status']
            salary = request.form['salary']
            department_id = request.form['department_id']

            cur = mysql.connection.cursor()
            try:
                # Inserting data into the database
                cur.execute("INSERT INTO employee(department_id,salary,emp_status,emp_password,zipcode,country,employee_name,mail,mobileNumber,role,address,city,state) VALUES(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s, %s, %s)",
                            (department_id,salary,emp_status,emp_password,zipcode,country,employee_name,mail,mobileNumber,role,address,city,state))
                mysql.connection.commit()
                return redirect(url_for('view_employees'))  # Redirect after success
            except Exception as e:
                mysql.connection.rollback()  # Rollback in case of an error
                return f"Error: {str(e)}"
            finally:
                cur.close()

        return render_template('Admin/add_employee.html')
    else:
        return redirect(url_for('admin_login'))


@app.route('/edit_employees', methods=['POST'])
def edit_employees():
    admin_id=session.get('admin_id')
    if admin_id:
        if request.method == 'POST':
            print(request.form)
            employee_id=request.form['editEmployeeId']
            editEmployeeName = request.form['editEmployeeName']
            mail = request.form['editEmail']
            mobileNumber = request.form['editMobile']
            role = request.form['editRole']
            address = request.form['editAddress']
            city = request.form['editCity']
            state = request.form['editState']
            country = request.form['editCountry']
            zipcode = request.form['editZipcode']
            emp_password = request.form['emp_password']
            emp_status = request.form['editStatus']
            salary = request.form['editSalary']
            department_id = request.form['editDepartmentId']
            print(request.form)
            cur = mysql.connection.cursor()
            try:
                cur.execute(""" UPDATE employee SET department_id = %s,salary = %s,emp_status = %s,emp_password = %s,zipcode = %s,country = %s,employee_name = %s,mail = %s,
                            mobileNumber = %s,role = %s, address = %s,city = %s,state = %s WHERE employee_id = %s""", (department_id, salary, emp_status, emp_password, zipcode, country, editEmployeeName, mail, mobileNumber, role, address, city, state, employee_id))
                mysql.connection.commit()
                return redirect(url_for('view_employees'))  # Redirect after success
            except Exception as e:
                mysql.connection.rollback()  # Rollback in case of an error
                return f"Error: {str(e)}"
            finally:
                cur.close()

        return render_template('Admin/add_employee.html')
    else:
        return redirect(url_for('admin_login'))

@app.route('/delete_employee', methods=['POST'])
def delete_employee():
    admin_id = session.get('admin_id')
    if admin_id:
        employee_id = request.form['employee_id']
        cur = mysql.connection.cursor()
        try:
            cur.execute("UPDATE employee SET emp_status='Inactive' WHERE employee_id = %s", (employee_id,))
            mysql.connection.commit()
            return redirect(url_for('view_employees'))  # Redirect after success
        except Exception as e:
            mysql.connection.rollback()  # Rollback in case of an error
            return f"Error: {str(e)}"
        finally:
            cur.close()
    else:
        return redirect(url_for('admin_login'))


@app.route('/add_maintenance')
def view_maintenanceschedule():
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM maintenanceschedule")
    maintenances = cur.fetchall()  # Fetch all records from the table
    cur.close()
    return render_template('Admin/maintanace_schedule.html',maintenances=maintenances)

@app.route('/add_maintenance', methods=['POST'])
def add_maintenanceschedule():
    admin_id=session.get('admin_id')
    if admin_id:
        if request.method == 'POST':
            train_id = request.form['train_id']
            maintenance_date = request.form['maintenance_date']
            main_description = request.form['main_description']
            main_status = request.form['main_status']

            cur = mysql.connection.cursor()
            try:
                # Inserting data into the database
                cur.execute("""SELECT * FROM maintenanceschedule WHERE train_id = %s AND maintenance_date = %s """, (train_id, maintenance_date))
                existing_record = cur.fetchone()  # Fetch the first record if exists

                if existing_record:
                    flash("Record already exists for this train ID and maintenance date", "error")
                    return redirect(url_for('view_maintenanceschedule'))  # Or any other page

                else:
                    cur.execute("""INSERT INTO maintenanceschedule(train_id, maintenance_date, main_description, main_status) VALUES(%s, %s, %s, %s)""", (train_id, maintenance_date, main_description, main_status))

                    mysql.connection.commit()  # Commit the changes to the database
                    flash("Maintenance schedule added successfully!", "success")
                    return redirect(url_for('view_maintenanceschedule')) # Redirect after success
            except Exception as e:
                mysql.connection.rollback()  # Rollback in case of an error
                return f"Error: {str(e)}"
            finally:
                cur.close()

        return render_template('Admin/maintanace_schedule.html')
    else:
        return redirect(url_for('admin_login'))

@app.route('/edit_maintenance', methods=['POST'])
def edit_maintenanceschedule():
    admin_id=session.get('admin_id')
    if admin_id:
        if request.method == 'POST':
            maintanance_id = request.form['editMaintenanceId']
            train_id = request.form['train_id']
            maintenance_date = request.form['maintenance_date']
            main_description = request.form['main_description']
            main_status = request.form['main_status']

            cur = mysql.connection.cursor()
            try:
                # Inserting data into the database
                cur.execute("""UPDATE maintenanceschedule SET maintenance_date = %s, main_description = %s, main_status = % WHERE train_id = %s""",
                            (maintenance_date, main_description, main_status, train_id))

                mysql.connection.commit()
                return redirect(url_for('view_maintenanceschedule'))  # Redirect after success
            except Exception as e:
                mysql.connection.rollback()  # Rollback in case of an error
                return f"Error: {str(e)}"
            finally:
                cur.close()

        return render_template('Admin/maintanace_schedule.html')
    else:
        return redirect(url_for('admin_login'))


@app.route('/delete_maintenance/<int:maintenance_id>', methods=['POST'])
def delete_maintenanceschedule(maintenance_id):
    admin_id = session.get('admin_id')
    if admin_id:
        cur = mysql.connection.cursor()
        try:
            # Check if the maintenance record exists
            cur.execute("SELECT * FROM maintenanceschedule WHERE id = %s", (maintenance_id,))
            existing_record = cur.fetchone()

            if existing_record:
                # Delete the record from the database
                cur.execute("DELETE FROM maintenanceschedule WHERE id = %s", (maintenance_id,))
                mysql.connection.commit()  # Commit the changes to the database
                flash("Maintenance schedule deleted successfully!", "success")
            else:
                flash("No record found with the provided ID.", "error")

            return redirect(url_for('view_maintenanceschedule'))  # Redirect after success
        except Exception as e:
            mysql.connection.rollback()  # Rollback in case of an error
            return f"Error: {str(e)}"
        finally:
            cur.close()
    else:
        return redirect(url_for('admin_login'))

@app.route('/add_schedules')
def view_trainschedule():
    cur = mysql.connection.cursor()
    cur.execute(""" SELECT s.schedule_id, s.start_date, s.departure_time, s.end_date, s.arrival_time, s.status, s.price,
    s.seats_available,s.train_id, st_start.name AS start_station_name, st_end.name AS end_station_name FROM schedules s 
    JOIN stations st_start ON s.start_point = st_start.station_id
    JOIN stations st_end ON s.end_point = st_end.station_id;""")
    schedules = cur.fetchall()
    cur.execute("SELECT * FROM train")
    trains = cur.fetchall()
    cur.execute("SELECT * FROM stations")
    stations = cur.fetchall()
    cur.execute("SELECT * FROM route")
    routes = cur.fetchall()
    cur.close()
    return render_template('Admin/train_schedule.html',routes=routes,stations=stations,trains=trains,schedules=schedules)

@app.route('/add_schedules', methods=['POST'])
def add_trainschedule():
    admin_id = session.get('admin_id')
    if admin_id:
        if request.method == 'POST':
            train_id = request.form['train_id']
            route_id = request.form['route_id']
            start_date = request.form['start_dt']
            end_date = request.form['end_dt']
            price = request.form['price']
            status = "Scheduled"
            cur = mysql.connection.cursor()
            try:

                start_datetime = f"{start_date[0:10]} {start_date[11:16]}"
                end_datetime = f"{end_date[0:10]} {end_date[11:16]}"
                cur.execute("""SELECT COUNT(*) FROM schedules  WHERE train_id = %s AND (
                (CONCAT(start_date, ' ', departure_time) BETWEEN %s AND %s) OR
                (CONCAT(end_date, ' ', arrival_time) BETWEEN %s AND %s) OR
                (CONCAT(start_date, ' ', departure_time) <= %s AND CONCAT(end_date, ' ', arrival_time) >= %s))""",
                (train_id, start_datetime, end_datetime, start_datetime, end_datetime, start_datetime, end_datetime))

                if cur.fetchone()[0] > 0:
                    flash("This train is already scheduled for this date range.", 'danger')
                    return render_template('Admin/train_schedule.html')

                cur.execute("""SELECT COUNT(*) FROM schedules WHERE train_id = %s AND start_date = %s AND departure_time = %s """, (train_id, start_date[0:10], start_date[11:16]))
                if cur.fetchone()[0] > 0:
                    flash("This train is already scheduled for this date and time.", 'danger')
                    return render_template('Admin/train_schedule.html')


                cur.execute("""SELECT COUNT(*) FROM schedules s JOIN route_schedules rs ON s.schedule_id = rs.schedule_id WHERE rs.route_id = %s AND s.start_date = %s""", (route_id, start_date))

                if cur.fetchone()[0] > 0:
                    flash("This route is already assigned to another train on the same date.", 'danger')
                    return render_template('Admin/train_schedule.html')  # Re-render the form with the flash message


                cur.execute("SELECT COUNT(*) AS seats_available FROM seats WHERE train_id = %s", (train_id,))
                seats_available = cur.fetchone()[0]
                cur.execute("""SELECT start_station, end_station FROM route WHERE route_id = %s """, (route_id,))
                routes_info=cur.fetchone()
                cur.execute("""INSERT INTO schedules (start_date, start_point,end_point,departure_time, end_date, arrival_time, status, price, seats_available, train_id)
                    VALUES ( %s, %s, %s, %s, %s, %s, %s, %s,%s,%s)
                """, (start_date[0:10],routes_info[0], routes_info[1],start_date[11:16], end_date[0:10], end_date[11:16], status, price, seats_available, train_id))
                mysql.connection.commit()
                cur.execute("SELECT LAST_INSERT_ID()")
                schedule_id = cur.fetchone()[0]
                cur.execute("""INSERT INTO route_schedules (route_id, schedule_id) VALUES (%s, %s) """, (route_id, schedule_id))
                mysql.connection.commit()
                cur.execute("""INSERT INTO train_schedules (train_id, schedule_id) VALUES (%s, %s)""", (train_id, schedule_id))
                mysql.connection.commit()
                cur.execute("""SELECT seat_id FROM seats WHERE train_id = %s """, (train_id,))
                seats = cur.fetchall()
                for seat in seats:
                    seat_id = seat[0]
                    cur.execute("""INSERT INTO scheduleseats (schedule_id, seat_id, availability_status) VALUES (%s, %s, %s)""", (schedule_id, seat_id, 'Available'))
                    mysql.connection.commit()
                return redirect(url_for('view_trainschedule'))  # Redirect after success
            except Exception as e:
                mysql.connection.rollback()  # Rollback in case of an error
                return f"Error: {str(e)}"
            finally:
                cur.close()

        return render_template('Admin/train_schedule.html')  # Render the schedule form page
    else:
        return redirect(url_for('admin_login'))  # Redirect to login page if admin is not logged in


@app.route('/edit_schedules', methods=['POST'])
def edit_trainschedule():
    admin_id=session.get('admin_id')
    if admin_id:
        if request.method == 'POST':
            schedule_id=request.form['schedule_id']
            start_date = request.form['start_date']
            start_point = request.form['start_point']
            departure_time = request.form['departure_time']
            end_point = request.form['end_point']
            end_date = request.form['end_date']
            arrival_time = request.form['arrival_time']
            status = request.form['status']
            price = request.form['price']
            seats_available = request.form['seats_available']
            train_id = request.form['train_id']

            cur = mysql.connection.cursor()
            try:
                # Inserting data into the database
                cur.execute("""UPDATE schedules SET start_date = %s, start_point = %s, departure_time = %s, end_point = %s,end_date = %s,arrival_time = %s,status = %s,price = %s,seats_available = %s,train_id = %s
                    WHERE schedule_id = %s""",
                            (start_date, start_point, departure_time, end_point, end_date, arrival_time, status, price, seats_available, train_id,schedule_id))
                mysql.connection.commit()
                return redirect(url_for('view_trainschedule'))  # Redirect after success
            except Exception as e:
                mysql.connection.rollback()  # Rollback in case of an error
                return f"Error: {str(e)}"
            finally:
                cur.close()


        return render_template('Admin/train_schedule.html')
    else:
        return redirect(url_for('admin_login'))



@app.route('/add_stations')
def view_stations():
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM stations")
    stations = cur.fetchall()  # Fetch all records from the table
    return render_template('Admin/stations.html',stations=stations)

@app.route('/add_stations', methods=['POST'])
def add_stations():
    if request.method == 'POST':
        name = request.form['name']
        address = request.form['address']
        city = request.form['city']
        state = request.form['state']
        country = request.form['country']
        zipcode = request.form['zipcode']
        cur = mysql.connection.cursor()
        try:
            cur.execute("SELECT COUNT(*) FROM stations WHERE name = %s OR address= %s ", (name,address,))
            result = cur.fetchone()

            cur.execute("SELECT * FROM stations")
            stations = cur.fetchall()

            if result[0] > 0:
                return render_template('Admin/stations.html',stations=stations,error="Station name or Station address already exists, please use a different name")
            # Inserting data into the database
                # Inserting data into the database
            cur.execute("INSERT INTO stations( name,address,city,state,country,zipcode) VALUES( %s,%s,%s, %s,%s,%s)",
                            (name,address,city,state,country,zipcode))
            mysql.connection.commit()
            return redirect(url_for('view_stations'))  # Redirect after success
        except Exception as e:
            mysql.connection.rollback()  # Rollback in case of an error
            return f"Error: {str(e)}"
        finally:
            cur.close()
        return render_template('Admin/stations.html')
    else:
        return redirect(url_for('admin_login'))

@app.route('/edit_stations', methods=['POST'])
def edit_stations():
    if request.method == 'POST':
        station_id=request.form['station_id']
        name = request.form['name']
        address = request.form['address']
        city = request.form['city']
        state = request.form['state']
        country = request.form['country']
        zipcode = request.form['zipcode']
        cur = mysql.connection.cursor()
        try:

            cur.execute("SELECT name, address FROM stations WHERE station_id = %s", (station_id,))
            current_station = cur.fetchone()
            cur.execute("SELECT * FROM stations")
            stations = cur.fetchall()

        # Check if name has been modified (name != current_name)
            if name != current_station[0]:
                cur.execute("SELECT COUNT(*) FROM stations WHERE name = %s", (name,))
                result = cur.fetchone()
                if result[0] > 0:
                    return render_template('Admin/stations.html', stations=stations, error="Station name already exists, please use a different name")

            # Check if address has been modified (address != current_address)
            if address != current_station[1]:
                cur.execute("SELECT COUNT(*) FROM stations WHERE address = %s", (address,))
                result1 = cur.fetchone()
                if result1[0] > 0:
                    return render_template('Admin/stations.html', stations=stations, error="Station address already exists, please use a different address")
            cur.execute("""UPDATE stations SET name = %s, address = %s, city = %s, state = %s, country = %s,zipcode = %s WHERE station_id = %s """, (name, address, city, state, country, zipcode, station_id))

            mysql.connection.commit()
            return redirect(url_for('view_stations'))  # Redirect after success
        except Exception as e:
            mysql.connection.rollback()  # Rollback in case of an error
            return f"Error: {str(e)}"
        finally:
            cur.close()
        return render_template('Admin/stations.html')
    else:
        return redirect(url_for('admin_login'))

@app.route('/delete_station', methods=['POST'])
def delete_station():
    if request.method == 'POST':
        station_id = request.form['station_id']
        cur = mysql.connection.cursor()
        try:
            # Check if the station exists
            cur.execute("SELECT * FROM stations WHERE station_id = %s", (station_id,))
            station = cur.fetchone()

            if station is None:
                return render_template('Admin/stations.html', error="Station not found.")

            # Delete the station
            cur.execute("DELETE FROM stations WHERE station_id = %s", (station_id,))
            mysql.connection.commit()
            return redirect(url_for('view_stations'))  # Redirect after success
        except Exception as e:
            mysql.connection.rollback()  # Rollback in case of an error
            return f"Error: {str(e)}"
        finally:
            cur.close()
    else:
        return redirect(url_for('admin_login'))


@app.route('/add_routes')
def view_routes():
    cur = mysql.connection.cursor()
    cur.execute("""SELECT r.route_id, r.num_of_stationstops, r.distance, s1.name AS start_station, s2.name AS end_station, s1.station_id AS start_station_id, s2.station_id AS end_station_id FROM route r
                    JOIN stations s1 ON r.start_station = s1.station_id
                    JOIN stations s2 ON r.end_station = s2.station_id;""")

    routes = cur.fetchall()
    print(routes)# Fetch all records from the table
    cur.execute("SELECT * FROM stations")
    stations = cur.fetchall()
    cur.close()
    return render_template('Admin/routes.html',stations=stations,routes=routes)

@app.route('/add_routes', methods=['POST'])
def add_routes():
    if request.method == 'POST':
        distance = request.form['distance']
        start_station = request.form['start_station']
        end_station = request.form['end_station']

        cur = mysql.connection.cursor()
        try:
            # Insert into the route table
            cur.execute(
                "INSERT INTO route (num_of_stationstops, distance, start_station, end_station) VALUES (%s, %s, %s, %s)",
                (2, distance, start_station, end_station)
            )
            # Get the route_id of the inserted route
            route_id = cur.lastrowid

            # Insert into the route_station table
            cur.execute(
                "INSERT INTO route_stations (route_id, station_id, stoptime) VALUES (%s, %s, %s)",
                (route_id, start_station, 10)  # Adjust 'stop_time' value as needed
            )
            cur.execute(
                "INSERT INTO route_stations (route_id, station_id, stoptime) VALUES (%s, %s, %s)",
                (route_id, end_station, 10)  # Adjust 'stop_time' value as needed
            )

            mysql.connection.commit()
            return redirect(url_for('view_routes'))  # Redirect after success
        except Exception as e:
            mysql.connection.rollback()  # Rollback in case of an error
            return f"Error: {str(e)}"
        finally:
            cur.close()

        return render_template('Admin/routes.html')
    else:
        return redirect(url_for('admin_login'))

@app.route('/get_stations_for_route/<int:route_id>', methods=['GET'])
def get_stations_for_route(route_id):
    """
    Endpoint to fetch stations for a given route ID.
    """
    cursor = mysql.connection.cursor()

    try:
        # Query to get all stations for the given route ID
        query = """
            SELECT s.name 
            FROM route_stations rs
            JOIN stations s ON rs.station_id = s.station_id
            WHERE rs.route_id = %s
            ORDER BY rs.station_id
        """
        cursor.execute(query, (route_id,))
        stations = cursor.fetchall()

        # Format the result as a JSON response
        station_list = [{"name": station[0]} for station in stations]
        return jsonify({"stations": station_list})

    except Exception as e:
        # Handle exceptions and return an error response
        return jsonify({"error": str(e)}), 500

    finally:
        # Ensure the connection is closed
        cursor.close()

@app.route('/add_station_to_route', methods=['POST'])
def add_station_to_route():
    route_id = request.form.get('route_id')
    station_name = request.form.get('station_name')

    if not route_id or not station_name:
        flash("Both Route ID and Station Name are required.", "error")
        return redirect('/add_routes')  # Replace with your relevant route

    cursor = mysql.connection.cursor()

    try:
        # Check if the route exists
        cursor.execute("SELECT route_id FROM route WHERE route_id = %s", (route_id,))
        route = cursor.fetchone()
        if not route:
            flash("Route ID does not exist.", "error")
            return redirect('/add_routes')

        # Check if the station exists
        cursor.execute("SELECT station_id FROM stations WHERE name = %s", (station_name,))
        station = cursor.fetchone()
        if not station:
            flash("Station does not exist.", "error")
            return redirect('/add_routes')

        # Check if the station is already part of the route
        cursor.execute("""
            SELECT COUNT(*) FROM route_stations 
            WHERE route_id = %s AND station_id = %s
        """, (route_id, station[0]))
        station_exists = cursor.fetchone()[0]

        if station_exists:
            flash("This station is already part of the route.", "error")
            return redirect('/add_routes')

        # Insert the station into the route
        cursor.execute(
            "INSERT INTO route_stations (route_id, station_id) VALUES (%s, %s)",
            (route_id, station[0])
        )

        # Increase the number of station stops in the route
        update_route_query = """
            UPDATE route
            SET num_of_stationstops = num_of_stationstops + 1
            WHERE route_id = %s
        """
        cursor.execute(update_route_query, (route_id,))
        mysql.connection.commit()
        flash("Station successfully added to the route.", "success")

    except Exception as e:
        flash(f"An error occurred: {e}", "error")

    finally:
        cursor.close()

    return redirect('/add_routes')  # Replace with your relevant route

@app.route('/delete_station_from_route', methods=['POST'])
def delete_station_from_route():
    route_id = request.form['route_id']
    station_name = request.form.get('station_name')

    cursor = mysql.connection.cursor()
    try:
        # Check if the route exists
        cursor.execute("SELECT route_id FROM route WHERE route_id = %s", (route_id,))
        route = cursor.fetchone()
        if not route:
            flash("Route ID does not exist.", "error")
            return redirect('/add_routes')

        # Check if the station exists
        cursor.execute("SELECT station_id FROM stations WHERE name = %s", (station_name,))
        station = cursor.fetchone()
        if not station:
            flash("Station does not exist.", "error")
            return redirect('/add_routes')

        station_id = station[0]

        # Check if the station is the start or end station
        start_end_check_query = """
            SELECT start_station, end_station
            FROM route 
            WHERE route_id = %s
        """
        cursor.execute(start_end_check_query, (route_id,))
        route_data = cursor.fetchone()

        if route_data:
            start_station_id, end_station_id = route_data
            if station_id == start_station_id or station_id == end_station_id:
                flash("Cannot delete the station because it is the start or end station of the route.", "error")
                return redirect('/add_routes')

        # Check if the station is part of the route (in route_stations table)
        cursor.execute("""
            SELECT COUNT(*) FROM route_stations 
            WHERE route_id = %s AND station_id = %s
        """, (route_id, station_id))
        station_in_route = cursor.fetchone()[0]

        if station_in_route == 0:
            flash("This station is not part of the route.", "error")
            return redirect('/add_routes')

        # Delete the station from the route in the database
        query = """
            DELETE FROM route_stations
            WHERE route_id = %s AND station_id = %s
        """
        cursor.execute(query, (route_id, station[0]))

        # Decrease the number of station stops in the route
        update_route_query = """
            UPDATE route
            SET num_of_stationstops = num_of_stationstops - 1
            WHERE route_id = %s
        """
        cursor.execute(update_route_query, (route_id,))
        mysql.connection.commit();

        flash("Station successfully deleted from the route.", "success")
    except Exception as e:
        flash(f"An error occurred: {e}", "error")
    return redirect('/add_routes')

@app.route('/assignemployee_shifts')
def view_employeesshifts():
    cur = mysql.connection.cursor()
    cur.execute("""SELECT e.employee_id, e.employee_name, s.shift_name FROM employee_shifts es JOIN shifts s ON es.shift_id = s.shift_id
        JOIN employee e ON es.employee_id = e.employee_id
    """)
    employee_shifts = cur.fetchall()
    cur.execute("""SELECT * from shifts""")
    shifts=cur.fetchall()
    print(shifts)
     # Fetch all records from the table
    cur.close()
    return render_template('Admin/employee_shifts.html',shifts=shifts,employee_shifts=employee_shifts)

@app.route('/assignemployee_shifts', methods=['POST'])
def assignemployee_shifts():
    admin_id = session.get('admin_id')
    if admin_id:
        if request.method == 'POST':
            employee_id = request.form['employee_id']
            shift_id = request.form['shift_id']
            cur = mysql.connection.cursor()
            try:
                # Check if the combination already exists
                cur.execute("SELECT * FROM employee_shifts WHERE employee_id = %s AND shift_id = %s",
                            (employee_id, shift_id))
                existing_entry = cur.fetchone()


                if existing_entry:
                    return redirect(url_for('view_employeesshifts'))
                    # Inserting data into the database
                cur.execute("INSERT INTO employee_shifts(employee_id, shift_id) VALUES(%s, %s)",
                            (employee_id, shift_id))
                mysql.connection.commit()
                return redirect(url_for('view_employeesshifts'))  # Redirect after success
            except Exception as e:
                mysql.connection.rollback()  # Rollback in case of an error
                return f"Error: {str(e)}"
            finally:
                cur.close()

        return render_template('Admin/employee_shifts.html')
    else:
        return redirect(url_for('admin_login'))

@app.route('/editemployee_shifts', methods=['POST'])
def editemployee_shifts():
    admin_id = session.get('admin_id')

    if admin_id:
        if request.method == 'POST':
            editEmployeeId = request.form['editEmployeeId']
            new_shift_id = request.form['editShiftName']
            cur = mysql.connection.cursor()
            cur.execute("""SELECT * from shifts""")
            shifts=cur.fetchall()

            try:
                # Step 1: Check if the new shift assignment already exists
                cur.execute("""SELECT * FROM employee_shifts WHERE employee_id = %s AND shift_id = %s""", (editEmployeeId, new_shift_id))

                existing_shift = cur.fetchone()  # If this returns a row, it means the combination exists

                if existing_shift:
                    # If the combination already exists, send an error message
                    return render_template('Admin/employee_shifts.html',
                                           error="This employee is already assigned to this shift.",shifts=shifts)

                # Step 2: Proceed to update the shift if combination doesn't exist
                cur.execute("""UPDATE employee_shifts SET shift_id = %s WHERE employee_id = %s""", (new_shift_id, editEmployeeId))

                # Commit the changes to the database
                mysql.connection.commit()

                # Redirect to the employee shifts view page after the update
                return redirect(url_for('view_employeesshifts'))

            except Exception as e:
                # Rollback in case of an error
                mysql.connection.rollback()
                return f"Error: {str(e)}"

            finally:
                cur.close()

        # Render the template if it's a GET request or after POST processing
        return render_template('Admin/employee_shifts.html')

    else:
        # Redirect to login page if no admin_id in session
        return redirect(url_for('admin_login'))



@app.route('/add_train')
def view_train():
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM train")
    trains = cur.fetchall()  # Fetch all records from the table
    cur.close()
    return render_template('Admin/add_train.html',trains=trains)

@app.route('/add_train', methods=['POST'])
def add_train():
    admin_id = session.get('admin_id')
    if admin_id:
        if request.method == 'POST':
            train_id = request.form['train_id']
            train_name = request.form['train_name']
            train_type = request.form['train_type']
            train_capacity = int(request.form['train_capacity'])
            numOfCoaches = request.form['numOfCoaches']
            cur = mysql.connection.cursor()
            try:
                cur.execute("SELECT COUNT(*) FROM train WHERE train_name = %s", (train_name,))
                result = cur.fetchone()
                cur.execute("SELECT COUNT(*) FROM train WHERE train_id = %s", (train_id,))
                result_id = cur.fetchone()
                cur.execute("SELECT * FROM train")
                trains = cur.fetchall()
                if result[0] > 0:
                    return render_template('Admin/add_train.html', trains=trains, error="Train name already exists, please use a different name")

                elif result_id[0] > 0:
                    return render_template('Admin/add_train.html', trains=trains, error="Train ID already exists, please use a different ID")

                else:
                    cur.execute("INSERT INTO train(train_id, train_name, train_type, train_capacity, numOfCoaches, admin_id) VALUES(%s, %s, %s, %s, %s, %s)",
                                (train_id, train_name, train_type, train_capacity, numOfCoaches, admin_id))
                    mysql.connection.commit()
                    prices = {
                        'SL': 100.00,  # Class A price
                        'CC': 75.00,   # Class B price
                        '2S': 50.00    # Class C price
                    }
                    seat_distribution = {
                        'SL': int(train_capacity * 0.4),  # 40% for Class A
                        'CC': int(train_capacity * 0.3),  # 30% for Class B
                        '2S': int(train_capacity * 0.3)   # 30% for Class C
                    }

                    seat_number = 1
                    for class_type, num_seats in seat_distribution.items():
                        for i in range(num_seats):
                            seat_identifier = f"{class_type}{i + 1}"
                            cur.execute("INSERT INTO seats (seat_number, class, price, train_id) VALUES (%s, %s, %s, %s)",
                                        (seat_identifier, class_type, prices[class_type], train_id))
                    mysql.connection.commit()  # Commit the seat inserts
                    return redirect(url_for('view_train'))  # Redirect after success
            except Exception as e:
                mysql.connection.rollback()  # Rollback in case of an error
                return f"Error: {str(e)}"
            finally:
                cur.close()
        return render_template('Admin/add_train.html')

    else:
        return redirect(url_for('admin_login'))


@app.route('/update_train', methods=['POST'])
def update_train():
    admin_id=session.get('admin_id')
    if admin_id:
        if request.method == 'POST':
            train_id = request.form['train_id']
            train_name = request.form['train_name']
            train_type = request.form['train_type']
            train_capacity = request.form['train_capacity']
            numOfCoaches = request.form['numOfCoaches']

            cur = mysql.connection.cursor()
            try:
                cur.execute("SELECT * FROM train")
                trains = cur.fetchall()
                cur.execute("SELECT COUNT(*) FROM train WHERE train_name = %s", (train_name,))
                result = cur.fetchone()
                if result[0] > 0:
                    return render_template('Admin/add_train.html',trains=trains,error="Train name already exists, please use a different name")
                else:
                    cur.execute("""UPDATE train SET train_name = %s,train_type = %s,train_capacity = %s,numOfCoaches = %s,admin_id = %s WHERE train_id = %s;""", (train_name, train_type, train_capacity, numOfCoaches, admin_id, train_id))
                    mysql.connection.commit()
                    return redirect(url_for('view_train'))  # Redirect after success
            except Exception as e:
                mysql.connection.rollback()  # Rollback in case of an error
                return f"Error: {str(e)}"
            finally:
                cur.close()

        return render_template('Admin/add_train.html')
    else:
        return redirect(url_for('admin_login'))


@app.route('/add_shifts')
def view_shifts():
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM shifts")
    shifts = cur.fetchall()  # Fetch all records from the table
    cur.close()
    return render_template('Admin/add_shifts.html',shifts=shifts)

@app.route('/add_shifts', methods=['POST'])
def add_shifts():
    admin_id=session.get('admin_id')
    if admin_id:
        if request.method == 'POST':
            shift_name = request.form['shift_name']
            start_time = request.form['start_time']
            end_time = request.form['end_time']
            cur = mysql.connection.cursor()
            try:
                cur.execute("INSERT INTO shifts(shift_name, start_time, end_time) VALUES(%s, %s, %s)",
                            (shift_name, start_time, end_time))
                mysql.connection.commit()
                return redirect(url_for('view_shifts'))  # Redirect after success
            except Exception as e:
                mysql.connection.rollback()  # Rollback in case of an error
                return f"Error: {str(e)}"
            finally:
                cur.close()
        return render_template('Admin/add_shifts.html')
    else:
        return redirect(url_for('admin_login'))

@app.route('/add_seats')
def view_seats():
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM seats")
    seats = cur.fetchall()
    cur.execute("SELECT * FROM train")
    trains = cur.fetchall()  # Fetch all records from the table
    cur.close()
    return render_template('Admin/seats.html',seats=seats,trains=trains)

@app.route('/add_seats', methods=['POST'])
def add_seats():
    admin_id=session.get('admin_id')
    if admin_id:
        if request.method == 'POST':
            seat_number = request.form['seat_number']
            class1 = request.form['class1']
            price = request.form['price']
            cur = mysql.connection.cursor()
            try:
                # Inserting data into the database
                cur.execute("INSERT INTO seats(seat_number, class, price) VALUES(%s, %s, %s)",
                            (seat_number, class1, price))
                mysql.connection.commit()
                return redirect(url_for('view_seats'))  # Redirect after success
            except Exception as e:
                mysql.connection.rollback()  # Rollback in case of an error
                return f"Error: {str(e)}"
            finally:
                cur.close()
        return render_template('Admin/seats.html')
    else:
        return redirect(url_for('admin_login'))

@app.route('/add_cancellations')
def view_cancellations():
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM cancellations")
    cancellations = cur.fetchall()
    cur.execute("SELECT * FROM schedules")
    schedules = cur.fetchall()  # Fetch all records from the table
    cur.close()
    return render_template('Admin/cancellations.html',schedules=schedules,cancellations=cancellations)

@app.route('/add_cancellations', methods=['POST'])
def add_cancellations():
    admin_id=session.get('admin_id')
    if admin_id:
        if request.method == 'POST':
            schedule_id = request.form['schedule_id']
            cancellation_date = request.form['cancellation_date']
            reason = request.form['reason']
            cur = mysql.connection.cursor()
            try:
                # Inserting data into the database
                cur.execute("INSERT INTO cancellations(schedule_id, cancellation_date, reason) VALUES(%s, %s, %s)",
                            (schedule_id, cancellation_date, reason))

                cur.execute("UPDATE schedules SET status = 'Canceled' WHERE schedule_id = %s;", (schedule_id,))
                mysql.connection.commit()
                return redirect(url_for('view_trainschedule'))  # Redirect after success
            except Exception as e:
                mysql.connection.rollback()  # Rollback in case of an error
                return f"Error: {str(e)}"
            finally:
                cur.close()
        return render_template('Admin/train_schedule.html')
    else:
        return redirect(url_for('admin_login'))

@app.route('/add_delays')
def view_delays():
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM delay")
    delays = cur.fetchall()
    cur.execute("SELECT * FROM schedules")
    schedules = cur.fetchall()  # Fetch all records from the table
    cur.close()
    return render_template('Admin/delay.html',delays=delays,schedules=schedules)

@app.route('/add_delays', methods=['POST'])
def add_delays():
    admin_id=session.get('admin_id')
    if admin_id:
        if request.method == 'POST':
            schedule_id = request.form['schedule_id']
            duration = request.form['duration']
            reason = request.form['reason']
            cur = mysql.connection.cursor()
            try:
                # Inserting data into the database
                cur.execute("INSERT INTO delay(schedule_id, duration, reason) VALUES(%s, %s, %s)",
                            (schedule_id, duration, reason))

                cur.execute("UPDATE schedules SET status = 'Delayed' WHERE schedule_id = %s;", (schedule_id,))
                mysql.connection.commit()
                return redirect(url_for('view_trainschedule'))  # Redirect after success
            except Exception as e:
                mysql.connection.rollback()  # Rollback in case of an error
                return f"Error: {str(e)}"
            finally:
                cur.close()
        return render_template('Admin/train_schedule.html')
    else:
        return redirect(url_for('admin_login'))


@app.route('/user_login')
def user_login():
    return render_template('User/user_login.html')

@app.route('/user_login', methods=['POST'])
def usersubmit_login():
    # Get email and password from the form
    mail = request.form['mail']
    user_password = request.form['user_password']
    # Check if email and password are not empty
    if mail and user_password:
        # Get the database connection using the Flask-MySQLdb extension
        conn = mysql.connection
        cursor = conn.cursor()

        # Query the database to check if the email exists and password matches
        cursor.execute("SELECT * FROM user WHERE mail = %s and user_password=%s", (mail,user_password))
        user = cursor.fetchone()
        cursor.close()
        if user and user[-1] == user_password:  # user[2] corresponds to the password field
            session['user_id'] = user[0]
            return redirect(url_for('user_dashboard'))  # Redirect to dashboard if login is successful
        else:
            return render_template('User/user_login.html', error="Invalid email or password.")
    else:
        return render_template('Admin/user_login.html', error="Please enter both email and password.")

@app.route('/register')
def view_register():
    return  render_template('User/registration.html')

@app.route('/register', methods=['POST'])
def register():
    if request.method == 'POST':
        name = request.form['name']
        mail = request.form['mail']
        mobileNumber = request.form['mobileNumber']
        address = request.form['address']
        city = request.form['city']
        state = request.form['state']
        country = request.form['country']
        zipcode = request.form['zipcode']
        user_password = request.form['user_password']

        cur = mysql.connection.cursor()
        try:
            # Check if the email already exists
            cur.execute("SELECT * FROM user WHERE mail = %s", (mail,))
            existing_user = cur.fetchone()

            if existing_user:
                return render_template('User/registration.html',error= "Email already registered. Please use a different email.")

            # If email does not exist, insert the new user
            cur.execute("INSERT INTO user(name, mail, mobileNumber, address, city, state, country, zipcode, user_password) VALUES(%s, %s, %s, %s, %s, %s, %s, %s, %s)",
                        (name, mail, mobileNumber, address, city, state, country, zipcode, user_password))
            mysql.connection.commit()
            return render_template('User/user_dashboard.html')

        except Exception as e:
            mysql.connection.rollback()  # Rollback in case of an error
            return f"Error: {str(e)}"
        finally:
            cur.close()
    return render_template('User/registration.html')  # Ensure you return the registration form for GET requests


@app.route('/user_dashboard')
def user_dashboard():
    user_id=session.get('user_id')
    if user_id:
        return render_template('User/user_dashboard.html')
    else:
        return redirect(url_for('user_login'))

@app.route('/search_booktrains')
def search_booktrainsview():
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM stations")
    stations = cur.fetchall()
    cur.close()
    return  render_template('User/search_booking.html',stations=stations)

@app.route('/search_booktrains', methods=['POST'])
def search_booktrains():
    if request.method == 'POST':
        train_id = request.form['train_id']
        journey_start_date = request.form['journey_start_date']
        source = request.form['source']
        destination = request.form['destination']
        cur = mysql.connection.cursor()
        try:
            # Check if the email already exists
            cur.execute("""
               SELECT t.train_id, t.train_name, t.train_type, t.train_capacity, t.numOfCoaches, t.admin_id,
               s.schedule_id, s.start_date, 
               sp.name AS start_station_name,  -- Start station name
               s.departure_time, 
               ep.name AS end_station_name,    -- End station name
               s.end_point, s.end_date, 
               s.arrival_time, s.status, 
               s.price, s.seats_available
            FROM train t
            JOIN schedules s ON t.train_id = s.train_id
            LEFT JOIN stations sp ON s.start_point = sp.station_id  -- Join for start station
            LEFT JOIN stations ep ON s.end_point = ep.station_id    -- Join for end station
            WHERE s.start_point = %s AND s.end_point = %s AND s.start_date = %s""", (source, destination, journey_start_date))

            details = cur.fetchall()

            if details:
                return render_template('User/search_booking.html',details=details)
            else:
                return render_template('User/search_booking.html',error ="No schedule for trains in this date")

        except Exception as e:
            mysql.connection.rollback()  # Rollback in case of an error
            return f"Error: {str(e)}"
        finally:
            cur.close()
    return  render_template('User/search_booking.html')


@app.route('/book_ticket/<int:schedule_id>', methods=['GET'])
def book_ticket(schedule_id):
    user_id =session['user_id']
    cursor = mysql.connection.cursor()
    cursor.execute("SELECT * FROM schedules WHERE schedule_id = %s", (schedule_id,))
    schedule_train = cursor.fetchone()
    cursor.execute("SELECT DISTINCT class FROM seats")
    seats = cursor.fetchall()
    cursor.close()
    if schedule_train is None:
        return "Train not found", 404
    return render_template('User/book_tickets.html', seats=seats,schedule_id=schedule_id, schedule_train=schedule_train)

@app.route('/submit_payment/<int:schedule_id>', methods=['GET', 'POST'])
def submit_payment(schedule_id):
    if request.method == 'POST':
        user_id = session['user_id']
        dependents_data = []
        dependent_index = 1
        now = datetime.now()
        pay_date = now.strftime('%Y-%m-%d %H:%M:%S')
        booking_date = now.strftime('%Y-%m-%d')
        seatclass = request.form['seatclass']
        payment_type = request.form['payment_type']
        address = request.form['address']
        city = request.form['city']
        state = request.form['state']
        country = request.form['country']
        zipcode = request.form['zipcode']
        cardNumber = request.form['cardNumber']

        while f'dependent_name_{dependent_index}' in request.form:
            dependent_name = request.form.get(f'dependent_name_{dependent_index}')
            email = request.form.get(f'email_{dependent_index}')
            mobileNumber = request.form.get(f'mobileNumber_{dependent_index}')
            age = request.form.get(f'age_{dependent_index}')
            dependents_data.append((dependent_name, email, mobileNumber, age))
            dependent_index += 1

        cur = mysql.connection.cursor()
        cur.execute("""SELECT train_id, price,seats_available FROM schedules WHERE schedule_id=%s;""", (schedule_id,))
        journey_price = cur.fetchone()

        if journey_price:
            train_id = journey_price[0]
            journey_price = journey_price[1]
        else:
            flash('No schedule found with the given schedule_id.', 'danger')
            return redirect(url_for('payment', schedule_id=schedule_id))

        cur.execute("""SELECT price FROM seats WHERE train_id=%s AND class=%s;""", (train_id, seatclass))
        seat_price = cur.fetchone()

        if seat_price:
            seat_price = seat_price[0]
        else:
            flash('No seats found for the given train and class.', 'danger')
            return redirect(url_for('payment', schedule_id=schedule_id))

        total_price = len(dependents_data) * (journey_price + seat_price)
        print(f"Total Price for booking: ${total_price:.2f}")

        cur.execute("""SELECT COUNT(*) FROM scheduleseats ss JOIN seats s ON ss.seat_id = s.seat_id WHERE ss.schedule_id = %s AND ss.availability_status = 'Available' AND s.class = %s""",
                    (schedule_id, seatclass))
        available_seats_count = cur.fetchone()[0]
        if available_seats_count>=len(dependents_data):
            try:
                cur.execute("""INSERT INTO booking (user_id, date, status) VALUES (%s, %s, %s)""", (user_id, booking_date, 'Confirmed'))
                mysql.connection.commit()
                booking_id = cur.lastrowid

                dependent_ids = []
                for dependent_name, email, mobileNumber, age in dependents_data:
                    cur.execute("""INSERT INTO dependents (dependent_name, mail, mobileNumber, age, user_id, booking_id) 
                                VALUES (%s, %s, %s, %s, %s, %s)""",
                                (dependent_name, email, mobileNumber, age, user_id, booking_id))
                    mysql.connection.commit()
                    dependent_id = cur.lastrowid
                    dependent_ids.append(dependent_id)

                ticket_numbers = []
                for dependent_id in dependent_ids:
                    cur.execute("""SELECT ss.seat_id FROM scheduleseats ss 
                                   JOIN seats s ON ss.seat_id = s.seat_id 
                                   WHERE ss.schedule_id = %s AND ss.availability_status = 'Available' AND s.class = %s LIMIT 1""",
                                (schedule_id, seatclass))
                    seat = cur.fetchone()

                    if seat:
                        seat_id = seat[0]
                        ticket_number = f"TICKET{random.randint(1000, 9999)}"
                        while True:
                            cur.execute("SELECT COUNT(*) FROM ticket WHERE ticket_number = %s", (ticket_number,))
                            if cur.fetchone()[0] == 0:
                                break
                            ticket_number = f"TICKET{random.randint(1000, 9999)}"
                        cur.execute("""INSERT INTO ticket (ticket_number, booking_id, seat_id, schedule_id, issue_date, status, user_id, dependent_id) 
                                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s)""",
                                    (ticket_number, booking_id, seat_id, schedule_id, datetime.today().date(), 'Issued', user_id, dependent_id))
                        mysql.connection.commit()

                        cur.execute("""UPDATE scheduleseats SET availability_status = 'Booked' WHERE schedule_id = %s AND seat_id = %s""",
                            (schedule_id, seat_id))
                        mysql.connection.commit()

                availseats=journey_price[2]-len(dependents_data)
                cur.execute("""UPDATE schedules SET seats_available =%s  WHERE schedule_id = %s """,(availseats,schedule_id))
                mysql.connection.commit()

                # Insert payment details into the database
                cur.execute("""INSERT INTO payment (pay_date, payment_type, address, city, state, country, zipcode, cardNumber, pay_status, booking_id) 
                            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)""",
                            (pay_date, payment_type, address, city, state, country, zipcode, cardNumber, 'Confirmed', booking_id))
                mysql.connection.commit()

                flash('Payment processed and booking successful!', 'success')
                return render_template('User/confirmation.html',train_id=train_id, total_price=total_price, schedule_id=schedule_id, booking_id=booking_id)

            except Exception as e:
                # Rollback in case of an error
                mysql.connection.rollback()
                print(f"Error occurred: {e}")
                flash('An error occurred while processing your booking. Please try again.', 'danger')
                return redirect(url_for('submit_payment', schedule_id=schedule_id))

            finally:
                cur.close()
        else:
            return render_template('User/error.html')
    return redirect(url_for('user_login'))



@app.route('/booking_history')
def booking_history():
    user_id =session['user_id']
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM booking where user_id =%s",(user_id,))
    bookings = cur.fetchall()
    print(bookings)
    cur.close()
    return  render_template('User/booking_history.html',bookings=bookings)

@app.route('/notifications')
def user_notifications():
    user_id =session['user_id']
    cur = mysql.connection.cursor()
    cur.execute("SELECT notifications.noti_description,notifications.noti_date,notifications.noti_time FROM user_notifications  LEFT JOIN notifications ON user_notifications.notification_id= notifications.notification_id where user_notifications.user_id =%s",(user_id,))
    notification_ids = cur.fetchall()
    print(notification_ids)
    cur.close()
    return  render_template('User/notifications.html',notification_ids=notification_ids)

@app.route('/user_feedback')
def user_feedback():
    user_id =session['user_id']
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM feedback where user_id =%s",(user_id,))
    feedbacks = cur.fetchall()
    print(feedbacks)
    cur.close()
    return  render_template('User/feedback.html',feedbacks=feedbacks)


@app.route('/user_feedback', methods=['POST'])
def add_feedback():
    if request.method=='POST':
        user_id =session['user_id']
        feed_description=request.form['feed_description']
        now = datetime.datetime.now()
        formatted_date_time = now.strftime("%Y-%m-%d %H:%M:%S")
        cur = mysql.connection.cursor()
        cur.execute("INSERT INTO feedback(feed_description, feed_date,feed_time, user_id) VALUES(%s,%s, %s, %s)",
                    (feed_description, formatted_date_time[0:10],formatted_date_time[11:], user_id))
        mysql.connection.commit()
        cur.close()
        return redirect(url_for('user_feedback'))
    else:
        return render_template('User/feedback.html')

@app.route('/payments')
def payments():
    user_id =session['user_id']
    cur = mysql.connection.cursor()
    query = """
    SELECT 
        p.payment_id,
        p.payment_type,
        p.address,
        p.city,
        p.state,
        p.country,
        p.zipcode,
        p.cardNumber,
        p.pay_status,
        b.booking_id,
        b.date AS booking_date,
        t.ticket_id,
        t.ticket_number,
        s1.name AS start_point,    
        s2.name AS end_point,      
        s1.address AS start_address,
        s2.address AS end_address
    FROM 
        payment p
    JOIN 
        booking b ON p.booking_id = b.booking_id
    JOIN 
        ticket t ON b.booking_id = t.booking_id
    JOIN 
        schedules sc ON t.schedule_id = sc.schedule_id
    JOIN 
        stations s1 ON sc.start_point = s1.station_id    
    JOIN 
        stations s2 ON sc.end_point = s2.station_id      
    WHERE 
        b.user_id = %s;
    """

    # Execute the query with the user_id
    cur.execute(query, (user_id,))
    # Fetch the results
    payment_details = cur.fetchall()
    print(payment_details)
    cur.close()
    return render_template('User/payments.html',payment_details=payment_details)

@app.route('/forgot_password')
def forgot_password():
    return "Forgot Password Page (Under Construction)"

@app.route('/user_booking')
def user_booking():
    # Here you can render the user booking page, or just return a placeholder for now
    return render_template('User/user_login.html')

@app.route('/delete_cancellation', methods=['POST'])
def delete_cancellation():
    if request.method == 'POST':
        cancellation_id = request.form['cancellation_id']
        cur = mysql.connection.cursor()
        try:
            cur.execute("DELETE FROM cancellations WHERE cancellation_id = %s", (cancellation_id,))
            mysql.connection.commit()
            flash("Cancellation deleted successfully!", "success")
            return redirect(url_for('add_cancellations'))
        except Exception as e:
            mysql.connection.rollback()
            flash(f"Error: {str(e)}", "error")
            return redirect(url_for('add_cancellations'))
        finally:
            cur.close()
    else:
        return redirect(url_for('admin_login'))

@app.route('/delete_delay', methods=['POST'])
def delete_delay():
    if request.method == 'POST':
        delay_id = request.form['delay_id']
        cur = mysql.connection.cursor()
        try:
            cur.execute("DELETE FROM delay WHERE delay_id = %s", (delay_id,))
            mysql.connection.commit()
            flash("Delay deleted successfully!", "success")
            return redirect(url_for('add_delays'))  # Redirect to the view delays page after deletion
        except Exception as e:
            mysql.connection.rollback()
            flash(f"Error: {str(e)}", "error")
            return redirect(url_for('add_delays'))  # Redirect to the view delays page if an error occurs
        finally:
            cur.close()
    else:
        return redirect(url_for('admin_login'))  # Redirect to login if the request is not POST


@app.route('/ulogout')
def ulogout():
    session.clear()
    flash('You have been logged out successfully!', 'info')
    return redirect(url_for('home'))  # Redirect to the login page after logout

@app.route('/alogout')
def alogout():
    session.clear()
    flash('You have been logged out successfully!', 'info')
    return redirect(url_for('home'))  # Redirect to the login page after logout

if __name__ == '__main__':
    app.run(debug=True)