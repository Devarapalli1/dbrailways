from mysql.connector import Error

def create_or_use_database(connection, db_name):
    cursor = connection.cursor()
    cursor.execute("SHOW DATABASES")
    databases = [db[0] for db in cursor.fetchall()]

    if db_name in databases:
        print(f"Database '{db_name}' already exists. Using existing database. Will continue to Drop Database and re-create!..")
    else:
        try:
            cursor.execute(f"CREATE DATABASE {db_name}")
            print(f"Database '{db_name}' created successfully")
        except Error as e:
            print(f"Failed to create database: {e}")
            cursor.close()
            exit()
    return

def create_database(connection, db_name):
    cursor = connection.cursor()
    try:
        cursor.execute("SHOW DATABASES")
        databases = cursor.fetchall()  # Fetch all results from the executed query
        print(databases)
        cursor.execute(f"CREATE DATABASE IF NOT EXISTS {db_name}")
        print(f"Database '{db_name}' created successfully")
    except Error as e:
        print(f"Failed to create database: {e}")
    finally:
        cursor.close()

def drop_database(connection, db_name):
    cursor = connection.cursor()
    try:
        # Check if the database exists
        cursor.execute("SHOW DATABASES")
        databases = [db[0] for db in cursor.fetchall()]  # Get database names in a list

        if db_name in databases:
            # Drop the database if it exists
            cursor.execute(f"DROP DATABASE IF EXISTS `{db_name}`")
            print(f"Database '{db_name}' dropped successfully")

    except Error as e:
        print(f"Failed to drop database: {e}")

    finally:
        cursor.close()

def table_exists(cursor, table_name):
    cursor.execute(f"""SELECT COUNT(*) FROM information_schema.tables WHERE table_schema = '{cursor._connection.database}' AND table_name = '{table_name}'""")
    return cursor.fetchone()[0] > 0

def execute_schema_file(connection, schema_file):
    cursor = connection.cursor()
    with open(schema_file, 'r') as file:
        schema = file.read()
        for command in schema.split(';'):
            command = command.strip()
            if command and command.lower().startswith("create table"):
                # Extract table name from the command
                table_name = command.split()[2]  # Assumes "CREATE TABLE table_name"
            if not table_exists(cursor, table_name):
                cursor.execute(command)
                print(f" '{table_name}' created.")
            else:
                print(f"'{table_name}' already exists.")

# First time loading the data into the table
def seed_sql_filedata(connection, file_path):
    cursor = connection.cursor()
    try:
        # Open and read the SQL file
        with open(file_path, 'r') as sql_file:
            sql_script = sql_file.read()

        # Split the script into individual SQL statements
        sql_commands = sql_script.split(';')

        # Execute each command
        for command in sql_commands:
            if command.strip():  # Skip empty lines
                cursor.execute(command)
                print(f"Executed: {command.strip()}")

        # Commit the changes
        connection.commit()
        print("SQL file executed successfully")

    except Error as e:
        print(f"Error: {e}")
    finally:
        cursor.close()
