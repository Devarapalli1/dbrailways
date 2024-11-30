import math
from random import random
from flask import flash, Flask, render_template, request, redirect, url_for, session, jsonify
from flask_mysqldb import MySQL
from datetime import datetime, timedelta
import random
import decimal


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
    cur.execute("SELECT * FROM department where dept_name!='None'")
    departments = cur.fetchall()  # Fetch all records from the table
    cur.close()
    return render_template('Admin/add_department.html',departments=departments)

@app.route('/add_departments', methods=['POST'])
def add_departments():
    admin_id = session.get('admin_id')
    if not admin_id:
        return redirect(url_for('admin_login'))
    if request.method == 'POST':
        dept_name = request.form['dept_name']
        cur = mysql.connection.cursor()
        try:
            cur.execute("SELECT department_id FROM department WHERE dept_name = %s", (dept_name,))
            existing_deptname = cur.fetchone()
            if existing_deptname:
                cur.execute("SELECT * FROM department where dept_name!='None'")
                departments = cur.fetchall()
                return render_template('Admin/add_department.html',departments=departments,error="Department name already exists. Please choose another name.")

            # Insert the new department into the database
            cur.execute("INSERT INTO department(dept_name, admin_id) VALUES ( %s, %s)",(dept_name, admin_id))
            mysql.connection.commit()
            return redirect(url_for('view_departments'))
        except Exception as e:
            mysql.connection.rollback()
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
        cur = mysql.connection.cursor()
        try:
            cur.execute("SELECT * FROM department WHERE dept_name = %s and department_id != %s;", (editDeptName,editDeptId,))
            existing_dept = cur.fetchone()  # Fetch one record if it exists
            cur.execute("SELECT * FROM department where dept_name!='None'")
            departments = cur.fetchall()
            if existing_dept:
                return render_template('Admin/add_department.html',departments=departments, error="This department name already exists. Try a different name.")
            cur.execute("UPDATE department SET dept_name = %s, admin_id = %s WHERE department_id = %s;",(editDeptName, admin_id, editDeptId))
            mysql.connection.commit()
            return render_template('Admin/add_department.html',departments=departments, error="Updated Successfully")
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
        cur.execute("SELECT * FROM department")
        departments = cur.fetchall()
        try:
            cur.execute("SELECT * FROM department WHERE department_id = %s", (department_id,))
            department = cur.fetchone()

            if department is None:
                return render_template('Admin/departments.html', error="Department not found.")
            cur.execute("SELECT department_id FROM department WHERE dept_name = 'None'")
            id=cur.fetchone()[0]
            cur.execute("UPDATE employee SET department_id= %s WHERE department_id = %s", (id,department_id,))
            cur.execute("DELETE FROM department WHERE department_id = %s", (department_id,))
            mysql.connection.commit()
            flash("Successfully deleted department")
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
    cur.execute("SELECT * FROM department where dept_name!='None'")
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
            emp_status = "Active"
            salary = request.form['salary']
            department_id = request.form['department_id']
            cur = mysql.connection.cursor()
            try:
                cur.execute("INSERT INTO employee(department_id,salary,emp_status,emp_password,zipcode,country,employee_name,mail,mobileNumber,role,address,city,state) VALUES(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)",
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
            emp_password = request.form['editPassword']
            emp_status = request.form['editStatus']
            salary = request.form['editSalary']
            department_id = request.form['editDepartmentId']
            print(request.form)
            cur = mysql.connection.cursor()
            try:
                cur.execute(""" UPDATE employee SET department_id = %s,salary = %s,emp_status = %s,emp_password = %s,zipcode = %s,country = %s,employee_name = %s,mail = %s,
                            mobileNumber = %s,role = %s, address = %s,city = %s,state = %s WHERE employee_id = %s""", (department_id, salary, emp_status, emp_password, zipcode, country, editEmployeeName, mail, mobileNumber, role, address, city, state, employee_id))
                mysql.connection.commit()
                flash("Updated employee details successfully")
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
            cur.execute("DELETE from employee_shifts where employee_id = %s", (employee_id,))
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
    cur.execute("SELECT * FROM train")
    trains = cur.fetchall()  # Fetch all records from the table
    cur.close()
    return render_template('Admin/maintanace_schedule.html',maintenances=maintenances, trains=trains)

@app.route('/add_maintenance', methods=['POST'])
def add_maintenanceschedule():
    admin_id=session.get('admin_id')
    if admin_id:
        if request.method == 'POST':
            train_id = request.form['train_id']
            maintenance_date = request.form['maintenance_date']
            main_description = request.form['main_description']
            main_status = 'In Progress'
            cur = mysql.connection.cursor()
            cur.execute("SELECT * FROM maintenanceschedule")
            maintenances = cur.fetchall()  # Fetch all records from the table
            cur.execute("SELECT * FROM train")
            trains = cur.fetchall()
            try:
                cur.execute("""
                    SELECT * FROM schedules WHERE train_id = %s AND start_date >= %s AND status != 'Cancelled'""", (train_id, maintenance_date))
                conflicting_schedule = cur.fetchone()
                if conflicting_schedule:
                    return render_template('Admin/maintanace_schedule.html',trains=trains, maintenances=maintenances,error="This train is already scheduled for this date or after the maintenance date.")

                cur.execute("""SELECT * FROM maintenanceschedule WHERE train_id = %s AND maintenance_date = %s """, (train_id, maintenance_date))
                existing_record = cur.fetchone()  # Fetch the first record if exists

                if existing_record:
                    return render_template('Admin/maintanace_schedule.html',trains=trains, maintenances=maintenances,error='Record already exists for this train ID and maintenance date')  # Or any other page

                cur.execute("""SELECT * FROM maintenanceschedule WHERE train_id = %s AND main_status = 'In Progress'""", (train_id,))
                existing1_record = cur.fetchone()

                if existing1_record:
                    return render_template('Admin/maintanace_schedule.html',trains=trains, maintenances=maintenances,error='Train is already in maintenanace for this train')  # Or any other page

                else:
                    cur.execute("""INSERT INTO maintenanceschedule(train_id, maintenance_date, main_description, main_status) VALUES(%s, %s, %s, %s)""", (train_id, maintenance_date, main_description, main_status))
                    mysql.connection.commit()  # Commit the changes to the database
                    return render_template('Admin/maintanace_schedule.html',trains=trains, maintenances=maintenances,error='Maintenance schedule added successfully!')  # Or any other page
            except Exception as e:
                mysql.connection.rollback()  # Rollback in case of an error
                flash(f"Error: {str(e)}")
                return redirect(url_for("view_maintenanceschedule"))
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
            main_status = 'Completed'

            cur = mysql.connection.cursor()
            try:
                # Inserting data into the database
                cur.execute("""UPDATE maintenanceschedule SET maintenance_id=%s, maintenance_date = %s, main_description = %s, main_status = %s WHERE train_id = %s""",
                            (maintanance_id,maintenance_date, main_description, main_status, train_id))

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
    s.seats_available,s.train_id, st_start.name AS start_station_name, st_end.name AS end_station_name,rs.route_id FROM schedules s 
    JOIN stations st_start ON s.start_point = st_start.station_id
    JOIN stations st_end ON s.end_point = st_end.station_id
    JOIN route_schedules rs ON s.schedule_id = rs.schedule_id; """)
    schedules = cur.fetchall()
    cur.execute(""" SELECT s.schedule_id, s.start_date, s.departure_time, s.end_date, s.arrival_time, s.status, s.price,
    s.seats_available,s.train_id, st_start.name AS start_station_name, st_end.name AS end_station_name FROM schedules s 
    JOIN stations st_start ON s.start_point = st_start.station_id
    JOIN stations st_end ON s.end_point = st_end.station_id where s.status!='Cancelled'; """)
    active_schedules = cur.fetchall()
    print(active_schedules)
    cur.execute("SELECT * FROM train")
    trains = cur.fetchall()
    cur.execute("SELECT * FROM stations")
    stations = cur.fetchall()
    cur.execute("SELECT * FROM route")
    routes = cur.fetchall()
    cur.close()
    return render_template('Admin/train_schedule.html',active_schedules=active_schedules,routes=routes,stations=stations,trains=trains,schedules=schedules)

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

            cur.execute(""" SELECT s.schedule_id, s.start_date, s.departure_time, s.end_date, s.arrival_time, s.status, s.price,
            s.seats_available,s.train_id, st_start.name AS start_station_name, st_end.name AS end_station_name,rs.route_id FROM schedules s 
            JOIN stations st_start ON s.start_point = st_start.station_id
            JOIN stations st_end ON s.end_point = st_end.station_id
            JOIN route_schedules rs ON s.schedule_id = rs.schedule_id; """)
            schedules = cur.fetchall()
            cur.execute(""" SELECT s.schedule_id, s.start_date, s.departure_time, s.end_date, s.arrival_time, s.status, s.price,
            s.seats_available,s.train_id, st_start.name AS start_station_name, st_end.name AS end_station_name FROM schedules s 
            JOIN stations st_start ON s.start_point = st_start.station_id
            JOIN stations st_end ON s.end_point = st_end.station_id where s.status!='Cancelled'; """)
            active_schedules = cur.fetchall()
            print(active_schedules)
            cur.execute("SELECT * FROM train")
            trains = cur.fetchall()
            cur.execute("SELECT * FROM stations")
            stations = cur.fetchall()
            cur.execute("SELECT * FROM route")
            routes = cur.fetchall()
            cur.execute("""SELECT * FROM maintenanceschedule WHERE train_id = %s and main_status='In Progress' """, (train_id,))
            result=cur.fetchone()
            if result:
                return render_template('Admin/train_schedule.html',error='This train is under maintenanance you cant add schedules',active_schedules=active_schedules,routes=routes,stations=stations,trains=trains,schedules=schedules)
            else:
                try:
                    cur.execute("""SELECT COUNT(*) FROM schedules WHERE train_id = %s AND start_date = %s AND departure_time = %s """, (train_id, start_date[0:10], start_date[11:16]))
                    if cur.fetchone()[0] > 0:
                        return render_template('Admin/train_schedule.html',error="This train is already scheduled for this date and time.")

                    start_datetime = f"{start_date[0:10]} {start_date[11:16]}"
                    end_datetime = f"{end_date[0:10]} {end_date[11:16]}"
                    cur.execute("""SELECT COUNT(*) FROM schedules  WHERE train_id = %s AND (
                    (CONCAT(start_date, ' ', departure_time) BETWEEN %s AND %s) OR
                    (CONCAT(end_date, ' ', arrival_time) BETWEEN %s AND %s) OR
                    (CONCAT(start_date, ' ', departure_time) <= %s AND CONCAT(end_date, ' ', arrival_time) >= %s))""",
                    (train_id, start_datetime, end_datetime, start_datetime, end_datetime, start_datetime, end_datetime))
                    if cur.fetchone()[0] > 0:
                        flash("This train is already scheduled for this date range.")
                        return redirect(url_for('view_trainschedule'))
                    cur.execute("""SELECT COUNT(*) FROM schedules WHERE train_id = %s AND start_date = %s AND departure_time = %s """, (train_id, start_date[0:10], start_date[11:16]))
                    if cur.fetchone()[0] > 0:
                        flash("This train is already scheduled for this date and time.")
                        return redirect(url_for('view_trainschedule'))

                    cur.execute("""SELECT COUNT(*) FROM schedules s JOIN route_schedules rs ON s.schedule_id = rs.schedule_id WHERE rs.route_id = %s AND s.start_date = %s""", (route_id, start_date))
                    if cur.fetchone()[0] > 0:
                        flash("This route is already assigned to another train on the same date.")
                        return redirect(url_for('view_trainschedule'))

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
                    flash("Schedule added successfully")
                    return redirect(url_for('view_trainschedule'))
                except Exception as e:
                    mysql.connection.rollback()  # Rollback in case of an error
                    flash(f"Error: {str(e)}")
                finally:
                    cur.close()
        return render_template('Admin/train_schedule.html')
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
            cur.execute("SELECT * FROM maintenanceschedule where train_id =%s and main_status='In Progress'; ",(train_id,))
            main = cur.fetchall()

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
    stations = cur.fetchall()
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
            cur.execute("INSERT INTO stations( name,address,city,state,country,zipcode) VALUES( %s,%s,%s, %s,%s,%s)",
                            (name,address,city,state,country,zipcode))
            mysql.connection.commit()
            flash("Station details added successfully")
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
            flash("Updated station details successfully")
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
            cur.execute("SELECT * FROM stations WHERE station_id = %s", (station_id,))
            station = cur.fetchone()
            if station is None:
                return render_template('Admin/stations.html', error="Station not found.")
            cur.execute("DELETE FROM stations WHERE station_id = %s", (station_id,))
            mysql.connection.commit()
            flash("Deleted station details successfully")
            return redirect(url_for('view_stations'))  # Redirect after success
        except Exception as e:
            mysql.connection.rollback()  # Rollback in case of an error
            return f"Error: {str(e)}"
        finally:
            cur.close()
        return redirect(url_for('view_stations'))
    else:
        return redirect(url_for('admin_login'))


@app.route('/add_routes')
def view_routes():
    cur = mysql.connection.cursor()
    cur.execute("""SELECT r.route_id, r.num_of_stationstops, r.distance, s1.name AS start_station, s2.name AS end_station, s1.station_id AS start_station_id, s2.station_id AS end_station_id FROM route r
                    JOIN stations s1 ON r.start_station = s1.station_id
                    JOIN stations s2 ON r.end_station = s2.station_id;""")
    routes = cur.fetchall()
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
            cur.execute(
                "INSERT INTO route (num_of_stationstops, distance, start_station, end_station) VALUES (%s, %s, %s, %s)",
                (2, distance, start_station, end_station))
            route_id = cur.lastrowid

            # Insert into the route_station table
            cur.execute(
                "INSERT INTO route_stations (route_id, station_id, order_id, stoptime) VALUES (%s, %s, %s, %s)",
                (route_id, start_station, 0, 10)  # Adjust 'stop_time' value as needed
            )
            cur.execute(
                "INSERT INTO route_stations (route_id, station_id, order_id, stoptime) VALUES (%s, %s, %s, %s)",
                (route_id, end_station, 1, 10)  # Adjust 'stop_time' value as needed
            )

            mysql.connection.commit()
            flash("routes added successfully")
            return redirect(url_for('view_routes'))
        except Exception as e:
            mysql.connection.rollback()
            flash(f"Error: {str(e)}")
        finally:
            cur.close()
        return render_template('Admin/routes.html')
    else:
        return redirect(url_for('admin_login'))

@app.route('/get_stations_for_route/<int:route_id>', methods=['GET'])
def get_stations_for_route(route_id):
    cursor = mysql.connection.cursor()
    try:
        query = """
            SELECT s.name
            FROM route_stations rs
            JOIN stations s ON rs.station_id = s.station_id
            WHERE rs.route_id = %s
            ORDER BY rs.order_id
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

        cursor.execute("""
            SELECT station_id, order_id FROM route_stations 
            WHERE route_id = %s
            ORDER BY order_id desc limit 1;
        """, (route_id))
        last_station = cursor.fetchone()

        # Insert the station into the route
        cursor.execute(
            "INSERT INTO route_stations (route_id, station_id, order_id) VALUES (%s, %s, %s)",
            (route_id, station[0], last_station[1])
        )

        cursor.execute(
            "UPDATE route_stations SET order_id = %s WHERE route_id = %s AND station_id = %s",
            (last_station[1]+1, route_id, last_station[0])
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
    cur.execute("""SELECT employee_id FROM employee where emp_status="Active" """)
    active_employees = cur.fetchall()

    cur.execute("""SELECT e.employee_id, e.employee_name, s.shift_name, s.shift_id
    FROM employee_shifts es JOIN shifts s ON es.shift_id = s.shift_id
    JOIN employee e ON es.employee_id = e.employee_id
    """)
    employee_shifts = cur.fetchall()
    cur.execute("""SELECT * from shifts""")
    shifts=cur.fetchall()
    cur.close()
    return render_template('Admin/employee_shifts.html',shifts=shifts,employee_shifts=employee_shifts, active_employees=active_employees)

@app.route('/assignemployee_shifts', methods=['POST'])
def assignemployee_shifts():
    admin_id = session.get('admin_id')
    if admin_id:
        if request.method == 'POST':
            employee_id = request.form['employee_id']
            shift_id = request.form['shift_id']
            cur = mysql.connection.cursor()
            try:
                cur.execute("SELECT * FROM employee_shifts WHERE employee_id = %s AND shift_id = %s",
                            (employee_id, shift_id))
                existing_entry = cur.fetchone()
                if existing_entry:
                    flash("This employee is already assigned to this shift.")
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
            new_shift_id = request.form['editShiftId']
            cur = mysql.connection.cursor()
            cur.execute("""SELECT * from shifts""")
            shifts=cur.fetchall()
            try:
                cur.execute("""SELECT shift_id FROM employee_shifts WHERE employee_id = %s""", (editEmployeeId,))
                existing_shifts = cur.fetchone()

                if new_shift_id in existing_shifts:
                    cur.execute("""SELECT employee_id FROM employee where emp_status="Active" """)
                    active_employees = cur.fetchall()

                    cur.execute("""SELECT e.employee_id, e.employee_name, s.shift_id, s.shift_name FROM employee_shifts es 
                    JOIN shifts s ON es.shift_id = s.shift_id
                    JOIN employee e ON es.employee_id = e.employee_id""")
                    employee_shifts = cur.fetchall()
                    cur.execute("""SELECT * from shifts""")
                    shifts=cur.fetchall()
                    return render_template('Admin/employee_shifts.html',
                                           error="This employee is already assigned to this shift.",shifts=shifts,employee_shifts=employee_shifts, active_employees=active_employees)
                cur.execute("""UPDATE employee_shifts SET shift_id = %s WHERE employee_id = %s""", (new_shift_id, editEmployeeId))
                mysql.connection.commit()
                flash("Updated employee shift successfully")
                return redirect(url_for('view_employeesshifts'))

            except Exception as e:
                mysql.connection.rollback()
                flash(f"Error: {str(e)}")
            finally:
                cur.close()

        return render_template('Admin/employee_shifts.html')
    else:
        return redirect(url_for('admin_login'))

@app.route('/deleteemployee_shifts', methods=['POST'])
def deleteemployee_shifts():
    admin_id = session.get('admin_id')
    shift_id = request.form['shift_id']

    if admin_id:
        cur = mysql.connection.cursor()
        try:
            cur.execute("DELETE FROM employee_shifts WHERE shift_id = %s", (shift_id,))
            mysql.connection.commit()

        except Exception as e:
            mysql.connection.rollback()
            flash(f"Error: {str(e)}")
        finally:
            cur.close()
        flash("Deleted the shift for an employee successfully")
        return redirect(url_for('view_employeesshifts'))
    else:
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
                    sl_seats = math.ceil(train_capacity * 0.4)  # 40% for SL
                    cc_seats = math.ceil(train_capacity * 0.3)  # 30% for CC
                    seats_2s = math.ceil(train_capacity * 0.3)  # 30% for 2S
                    total_seats = sl_seats + cc_seats + seats_2s
                    if total_seats > train_capacity:
                        excess_seats = total_seats - train_capacity
                        if sl_seats >= cc_seats and sl_seats >= seats_2s:
                            sl_seats -= excess_seats
                        elif cc_seats >= sl_seats and cc_seats >= seats_2s:
                            cc_seats -= excess_seats
                        else:
                            seats_2s -= excess_seats
                    seat_distribution = {
                        'SL': sl_seats,
                        'CC': cc_seats,
                        '2S': seats_2s
                    }
                    seat_number = 1
                    for class_type, num_seats in seat_distribution.items():
                        for i in range(num_seats):
                            seat_identifier = f"{class_type}{i + 1}"
                            cur.execute("INSERT INTO seats (seat_number, class, price, train_id) VALUES (%s, %s, %s, %s)",
                                        (seat_identifier, class_type, prices[class_type], train_id))
                    mysql.connection.commit()
                    flash("Train details added successfully")
                    return redirect(url_for('view_train'))  # Redirect after success
            except Exception as e:
                mysql.connection.rollback()
                flash(f"Error: {str(e)}")
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
                    flash("Updated train details successfully")
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
    admin_id = session.get('admin_id')
    if admin_id:
        if request.method == 'POST':
            shift_name = request.form['shift_name']
            start_time = request.form['start_time']

            end_time = request.form['end_time']
            if not shift_name or not start_time or not end_time:
                flash("All fields are required.")
                return redirect(url_for('add_shifts'))  # Redirect back to the form

            # Check if start_time is earlier than end_time
            try:
                start_time_obj = datetime.strptime(start_time, "%H:%M")
                end_time_obj = datetime.strptime(end_time, "%H:%M")
                if start_time_obj >= end_time_obj:
                    flash("Start time must be earlier than end time.")
                    return redirect(url_for('add_shifts'))
            except ValueError:
                flash("Invalid time format. Please use HH:MM format.")
                return redirect(url_for('add_shifts'))
            cur = mysql.connection.cursor()
            try:
                cur.execute("""SELECT * FROM shifts WHERE start_time = %s AND end_time = %s""",
                            (start_time, end_time))
                existing_shift = cur.fetchone()
                if existing_shift:
                    flash("This shift already exists with the same time.")
                    return redirect(url_for('add_shifts'))
                cur.execute("""INSERT INTO shifts(shift_name, start_time, end_time) VALUES(%s, %s, %s)""",
                            (shift_name, start_time, end_time))
                mysql.connection.commit()
                flash("Shift added successfully!")
                return redirect(url_for('view_shifts'))

            except Exception as e:
                mysql.connection.rollback()
                flash(f"Error: {str(e)}")
                return redirect(url_for('add_shifts'))
            finally:
                cur.close()
        return render_template('Admin/add_shifts.html')
    else:
        return redirect(url_for('admin_login'))

@app.route('/edit_shifts', methods=['POST'])
def edit_shifts():
    admin_id = session.get('admin_id')
    if admin_id:
        if request.method == 'POST':
            editShiftId=request.form['editShiftId']
            shift_name = request.form['shift_name']
            start_time = request.form['start_time'].strip()
            end_time = request.form['end_time'].strip()
            print(start_time, type(start_time))

            if not shift_name or not start_time or not end_time:
                flash("All fields are required.")
                return redirect(url_for('view_shifts'))  # Redirect back to the form
            cur = mysql.connection.cursor()
            try:
                cur.execute("""SELECT * FROM shifts WHERE start_time = %s AND end_time = %s""",
                            (start_time, end_time))
                existing_shift = cur.fetchone()
                if existing_shift:
                    flash("This shift already exists with the same time.")
                    return redirect(url_for('view_shifts'))
                cur.execute("""UPDATE shifts SET shift_name=%s, start_time=%s, end_time=%s WHERE shift_id=%s""",
                            (shift_name, start_time, end_time, editShiftId))
                mysql.connection.commit()
                flash("Shift details updated successfully!")
                return redirect(url_for('view_shifts'))  #
            except Exception as e:
                mysql.connection.rollback()
                flash(f"Error: {str(e)}")
                return redirect(url_for('view_shifts'))
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
    cur.execute("SELECT * FROM schedules where status!='Cancelled'")
    schedules = cur.fetchall()  # Fetch all records from the table
    cur.close()
    return render_template('Admin/cancellations.html',schedules=schedules,cancellations=cancellations)

@app.route('/add_cancellations', methods=['POST'])
def add_cancellations():
    admin_id=session.get('admin_id')
    if admin_id:
        if request.method == 'POST':
            schedule_id = request.form['schedule_id']
            reason = request.form['reason']
            cur = mysql.connection.cursor()
            now = datetime.now()
            cancellation_date = now.strftime("%Y-%m-%d")
            try:
                # Inserting data into the database
                cur.execute("INSERT INTO cancellations(schedule_id, cancellation_date, reason) VALUES(%s, %s, %s)",
                            (schedule_id, cancellation_date, reason))

                cur.execute("UPDATE schedules SET status = 'Cancelled' WHERE schedule_id = %s;", (schedule_id,))

                cur.execute("UPDATE ticket SET status='Cancelled' WHERE schedule_id = %s;", (schedule_id,))
                cur.execute("""UPDATE booking b JOIN ticket t ON t.booking_id = b.booking_id SET b.status = 'Cancelled'
                    WHERE t.schedule_id = %s;""", (schedule_id,))
                cur.execute("""UPDATE payment p JOIN ticket t ON p.booking_id = t.booking_id SET p.pay_status = 'refunded'WHERE t.schedule_id = %s;
                """, (schedule_id,))

                mysql.connection.commit()
                flash("schedule cancellation successfully")
                return redirect(url_for('view_trainschedule'))  # Redirect after success
            except Exception as e:
                flash(f"Error: {str(e)}")
                flash("updated details successfully")
                return redirect(url_for('view_trainschedule'))
            finally:
                cur.close()
        return redirect(url_for('view_trainschedule'))
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
                cur.execute("INSERT INTO delay(schedule_id, duration, reason) VALUES(%s, %s, %s)",
                            (schedule_id, duration, reason))
                cur.execute("UPDATE schedules SET status = 'Delayed' WHERE schedule_id = %s;", (schedule_id,))
                mysql.connection.commit()
                flash("Delay updated successfully")
                return redirect(url_for('view_trainschedule'))  # Redirect after success
            except Exception as e:
                mysql.connection.rollback()  # Rollback in case of an error
                flash(f"Error: {str(e)}")
                return redirect(url_for('view_trainschedule'))
            finally:
                cur.close()
        return render_template('Admin/train_schedule.html')
    else:
        return redirect(url_for('admin_login'))

@app.route('/add_notifications')
def view_notificatons():
    cur = mysql.connection.cursor()
    cur.execute("""SELECT N.* , UN.user_id
    FROM notifications N
    JOIN user_notifications UN
    on N.notification_id = UN.notification_id
    """)
    notifications = cur.fetchall()
    cur.execute("SELECT * FROM user")
    users = cur.fetchall()
    cur.close()
    return render_template('Admin/add_notifications.html',users=users,notifications=notifications)

@app.route('/add_notifications', methods=['POST'])
def add_notifications():
    admin_id=session.get('admin_id')
    if admin_id:
        if request.method == 'POST':
            noti_description = request.form['noti_description']
            now = datetime.now()
            noti_date = now.strftime('%Y-%m-%d')
            noti_time = now.strftime('%H:%M:%S')
            user_id=request.form['user_id']
            cur = mysql.connection.cursor()
            try:
                # Inserting data into the database
                cur.execute("INSERT INTO notifications(noti_description, noti_date, noti_time,admin_id) VALUES(%s, %s, %s,%s)",
                            (noti_description, noti_date, noti_time,admin_id))
                mysql.connection.commit()
                notification_id = cur.lastrowid
                cur.execute("INSERT INTO user_notifications(notification_id, user_id) VALUES(%s,%s)",
                            (notification_id, user_id))
                mysql.connection.commit()
                return redirect(url_for('view_notificatons'))  # Redirect after success
            except Exception as e:
                mysql.connection.rollback()  # Rollback in case of an error
                return f"Error: {str(e)}"
            finally:
                cur.close()
        return redirect(url_for('view_notificatons'))
    else:
        return redirect(url_for('admin_login'))

@app.route('/user_reviews')
def user_reviews():
    cur = mysql.connection.cursor()
    query = """SELECT f.feedback_id, f.feed_description, f.feed_date, f.feed_time, u.user_id, u.name AS user_name
            FROM feedback f JOIN user u ON f.user_id = u.user_id """
    cur.execute(query)
    feedbacks = cur.fetchall()
    cur.close()
    return render_template('Admin/user_reviews.html',feedbacks=feedbacks)


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
            flash("Registered successfully")
            return redirect(url_for("user_login"))

        except Exception as e:
            mysql.connection.rollback()
            flash(f"Error: {str(e)}")
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
        journey_start_date = request.form['journey_start_date']
        source = request.form['source']
        destination = request.form['destination']
        cur = mysql.connection.cursor()
        cur.execute("SELECT * FROM stations")
        stations = cur.fetchall()
        try:
            cur.execute("""
               SELECT t.train_id, 
       t.train_name, 
       t.train_type, 
       t.train_capacity, 
       t.numOfCoaches, 
       t.admin_id,
       s.schedule_id, 
       s.start_date, 
       sp.name AS start_station_name,  -- Start station name
       s.departure_time, 
       ep.name AS end_station_name,    -- End station name
       s.end_point, 
       s.end_date, 
       s.arrival_time, 
       s.status, 
       s.price, 
       s.seats_available,
       COUNT(CASE WHEN st.class = 'SL' AND ss.availability_status = 'Available' THEN 1 END) AS economy_seat_count,
       COUNT(CASE WHEN st.class = 'CC' AND ss.availability_status = 'Available' THEN 1 END) AS business_seat_count,
       COUNT(CASE WHEN st.class = '2S' AND ss.availability_status = 'Available' THEN 1 END) AS first_class_seat_count
FROM train t
JOIN schedules s ON t.train_id = s.train_id
LEFT JOIN route_schedules rss ON rss.schedule_id = s.schedule_id
LEFT JOIN route_stations rs_start ON rs_start.route_id = rss.route_id AND rs_start.station_id = %s  -- Source station in route
LEFT JOIN route_stations rs_end ON rs_end.route_id = rss.route_id AND rs_end.station_id = %s  -- Destination station in route
LEFT JOIN stations sp ON s.start_point = sp.station_id  -- Join for start station
LEFT JOIN stations ep ON s.end_point = ep.station_id    -- Join for end station
LEFT JOIN seats st ON t.train_id = st.train_id          -- Join for seats
LEFT JOIN scheduleseats ss ON s.schedule_id = ss.schedule_id AND st.seat_id = ss.seat_id  -- Join for schedule seats
WHERE rs_start.route_id IS NOT NULL  -- Ensure source station is part of the route
  AND rs_end.route_id IS NOT NULL    -- Ensure destination station is part of the route
  AND rs_start.order_id < rs_end.order_id  -- Ensure the source station comes before the destination station in the route
  AND s.start_date = %s  -- Journey start date
GROUP BY t.train_id, t.train_name, t.train_type, t.train_capacity, t.numOfCoaches, t.admin_id,
         s.schedule_id, s.start_date, sp.name, s.departure_time, ep.name, s.end_point, 
         s.end_date, s.arrival_time, s.status, s.price, s.seats_available;
""", (source, destination, journey_start_date))

            details = cur.fetchall()

            if details:
                return render_template('User/search_booking.html',stations=stations,details=details)
                #return redirect(url_for('search_booktrainsview', details=details))
            else:
                return render_template('User/search_booking.html',stations=stations,error ="No schedule for trains in this date")
                #return redirect(url_for('search_booktrainsview', error ="No schedule for trains in this date"))

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
            jour_price = journey_price[1]
            journey_seats=journey_price[2]
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

        total_price = len(dependents_data) * (jour_price + seat_price)
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
                availableseats=journey_price[2]
                availseats=availableseats-len(dependents_data)
                print(availseats,type(journey_price[2]))
                cur.execute("""UPDATE schedules SET seats_available =%s  WHERE schedule_id = %s """,(availseats,schedule_id))
                mysql.connection.commit()

                # Insert payment details into the database
                cur.execute("""INSERT INTO payment (total_price,pay_date, payment_type, address, city, state, country, zipcode, cardNumber, pay_status, booking_id) 
                            VALUES (%s,%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)""",
                            (total_price,pay_date, payment_type, address, city, state, country, zipcode, cardNumber, 'Confirmed', booking_id))
                mysql.connection.commit()

                flash('Payment processed and booking successful!', 'success')
                return redirect(url_for('booking_confirmation', booking_id=booking_id))

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
    cur.execute("""SELECT distinct b.booking_id, b.date AS booking_date, b.status AS booking_status,t.train_id AS train_number,t.train_name,
                s.start_date AS journey_date,s.departure_time AS journey_time FROM booking b
                JOIN ticket tk ON b.booking_id = tk.booking_id
                JOIN schedules s ON tk.schedule_id = s.schedule_id
                JOIN train t ON s.train_id = t.train_id
                WHERE b.user_id = %s;""", (user_id,))
    bookings = cur.fetchall()
    print(bookings)
    cur.close()
    return  render_template('User/booking_history.html',bookings=bookings)

@app.route('/booking_confirmation/<int:booking_id>', methods=['GET'])
def booking_confirmation(booking_id):
    user_id = session.get('user_id')
    if not user_id:
        flash("You must be logged in to view your booking", 'danger')
        return redirect(url_for('user_login'))

    cur = mysql.connection.cursor()

    query = """
    SELECT
        booking_id,
        date AS booking_date,
        status AS booking_status
    FROM booking
    WHERE booking_id = %s;
    """
    cur.execute(query, (booking_id,))
    booking_details = cur.fetchone()

    if not booking_details:
        flash("Booking not found or you don't have access to it.", 'danger')
        return redirect(url_for('user_dashboard'))

    # Fetch the ticket details
    cur.execute("""
    SELECT 
    t.ticket_number, s.seat_number, d.dependent_name 
    FROM ticket t JOIN seats s ON t.seat_id = s.seat_id
    JOIN dependents d ON t.dependent_id = d.dependent_id
    WHERE t.booking_id = %s;""", (booking_id,))
    tickets = cur.fetchall()

    if not tickets:
        flash("No tickets found for this booking.", 'danger')
        return redirect(url_for('user_dashboard'))

    # Fetch the ticket details
    cur.execute("""
    SELECT 
    p.total_price, p.pay_status, p.payment_type 
    FROM payment p 
    WHERE booking_id = %s;""", (booking_id,))
    payment = cur.fetchone()

    if not tickets:
        flash("No tickets found for this booking.", 'danger')
        return redirect(url_for('user_dashboard'))
    cur.close()

    return render_template('User/booking_confirmation.html', booking=booking_details, tickets=tickets, payment=payment)

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
        now = datetime.now()
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
    SELECT distinct 
        b.booking_id,
        p.payment_type,
        b.date AS booking_date,
        s1.name AS start_point,    
        s2.name AS end_point,
        p.total_price
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