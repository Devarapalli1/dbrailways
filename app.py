from flask import flash, Flask, render_template, request, redirect, url_for,session
from flask_mysqldb import MySQL
import datetime
from dotenv import load_dotenv
import os

load_dotenv()

app = Flask(__name__)

# MySQL configuration
app.config['MYSQL_HOST'] = os.getenv("MYSQL_HOST")
app.config['MYSQL_USER'] = os.getenv("MYSQL_USER")
app.config['MYSQL_PASSWORD'] = os.getenv("MYSQL_PASSWORD")
app.config['MYSQL_DB'] = os.getenv("MYSQL_DB")
app.secret_key = os.getenv("SECRET_KEY")
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



@app.route('/add_trainschedule')
def view_trainschedule():
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM schedules")
    schedules = cur.fetchall()  # Fetch all records from the table
    cur.close()
    return render_template('Admin/train_schedule.html',schedules=schedules)

@app.route('/add_trainschedule', methods=['POST'])
def add_trainschedule():
    admin_id=session.get('admin_id')
    if admin_id:
        if request.method == 'POST':
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
                cur.execute("INSERT INTO schedules(start_date, start_point,departure_time,end_point,end_date,arrival_time,status,price,seats_available,train_id) VALUES(%s, %s, %s, %s,%s,%s,%s,%s,%s,%s)",
                            (start_date, start_point,departure_time,end_point,end_date,arrival_time,status,price,seats_available,train_id))
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

@app.route('/add_routes')
def view_routes():
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM route")
    routes = cur.fetchall()
    print(routes)# Fetch all records from the table
    cur.execute("SELECT * FROM stations")
    stations = cur.fetchall()
    cur.close()
    return render_template('Admin/routes.html',stations=stations,routes=routes)

@app.route('/add_routes', methods=['POST'])
def add_routes():
    if request.method == 'POST':
        #employee_id = request.form['employee_id']
        num_of_stationstops = request.form['num_of_stationstops']
        distance = request.form['distance']
        start_station = request.form['start_station']
        end_station = request.form['end_station']
        cur = mysql.connection.cursor()
        try:
            # Inserting data into the database
            cur.execute("INSERT INTO route( num_of_stationstops,distance,start_station,end_station) VALUES( %s,%s,%s,%s)",
                        (num_of_stationstops,distance,start_station,end_station))
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


@app.route('/assignemployee_shifts')
def view_employeesshifts():
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM employee_shifts")
    employee_shifts = cur.fetchall()  # Fetch all records from the table
    cur.close()
    return render_template('Admin/employee_shifts.html',error="This employee is already assigned to this shift.",employee_shifts=employee_shifts)

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


@app.route('/add_train')
def view_train():
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM train")
    trains = cur.fetchall()  # Fetch all records from the table
    cur.close()
    return render_template('Admin/add_train.html',trains=trains)

@app.route('/add_train', methods=['POST'])
def add_train():
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
                cur.execute("SELECT COUNT(*) FROM train WHERE train_name = %s", (train_name,))
                result = cur.fetchone()
                cur.execute("SELECT COUNT(*) FROM train WHERE train_id= %s", (train_id,))
                result_id = cur.fetchone()
                cur.execute("SELECT * FROM train")
                trains = cur.fetchall()

                if result[0] > 0:
                    return render_template('Admin/add_train.html',trains=trains,error="Train name already exists, please use a different name")
                # Inserting data into the database
                elif result_id[0] > 0:
                        return render_template('Admin/add_train.html',trains=trains,error="Train Id already exists, please use a different name")
                # Inserting data into the database
                else:
                    cur.execute("INSERT INTO train(train_id, train_name, train_type, train_capacity, numOfCoaches,admin_id) VALUES(%s, %s, %s, %s, %s,%s)",
                                (train_id, train_name, train_type, train_capacity, numOfCoaches,admin_id))
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
                # Inserting data into the database
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
                # Inserting data into the database
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
                cur.execute("INSERT INTO seats(schedule_id, cancellation_date, reason) VALUES(%s, %s, %s)",
                            (schedule_id, cancellation_date, reason))

                cur.execute("UPDATE schedules SET status = 'Canceled' WHERE schedule_id = %s;", (schedule_id,))
                mysql.connection.commit()
                return redirect(url_for('view_cancellations'))  # Redirect after success
            except Exception as e:
                mysql.connection.rollback()  # Rollback in case of an error
                return f"Error: {str(e)}"
            finally:
                cur.close()
        return render_template('Admin/cancellations.html')
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
                return redirect(url_for('view_delays'))  # Redirect after success
            except Exception as e:
                mysql.connection.rollback()  # Rollback in case of an error
                return f"Error: {str(e)}"
            finally:
                cur.close()
        return render_template('Admin/delay.html')
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

@app.route('/searchtrains')
def searchtrains():
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM stations")
    stations = cur.fetchall()
    cur.close()
    return  render_template('User/search_booking.html',stations=stations)

@app.route('/searchtrains', methods=['POST'])
def searchbooktrains():
    if request.method == 'POST':
        train_id = request.form['train_id']
        journey_start_date = request.form['journey_start_date']
        source = request.form['source']
        destination = request.form['destination']
        cur = mysql.connection.cursor()
        try:
            # Check if the email already exists
            cur.execute("SELECT * FROM schedules WHERE source = %s AND destination= %s AND journey_start_date= %s", (source,destination,journey_start_date))
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

if __name__ == '__main__':
    app.run(debug=True)
