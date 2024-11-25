import mysql

from dbconnection import seed_sql_filedata, execute_schema_file, create_or_use_database, drop_database

DB_CONFIG = {
    "host": "localhost",
    "user": "root",
    "password": "Akhi0312"
}

def get_database_name():
    choice = input("The assignment uses a default database name 'rms'. "
                   "Would you like to continue with the default (1) or create a database with a new name (2)? ")
    while True:
        if choice.strip() == '1':
            db_name = 'rms'
            break

        elif choice.strip() == '2':
            db_name = input("Enter the new database name: ").strip()
            while db_name == "":
                db_name = input("Invalid database name, please enter a valid database name: ").strip()
            break
        else:
            choice = input("Invalid choice, please enter 1 to continue with the default or 2 to create a new database: ")
    return db_name

def create_connection(db_name=None):
    config = DB_CONFIG.copy()
    if db_name:
        config["database"] = db_name
    return mysql.connector.connect(**config)

if __name__ == "__main__":
    print("Welcome to Assignment 2 - Adi Vishnu Madhuri Devarapalli(11818524)")
    db_name = get_database_name()

    # Establish the connection without specifying a database
    connection = create_connection()

    drop_database(connection, db_name)
    create_or_use_database(connection, db_name)

    connection_with_db_name = create_connection(db_name)

    schema_file = 'database/config/DDL.sql'
    print(f"Creating tables using default config - {schema_file}")
    execute_schema_file(connection_with_db_name, schema_file)

    seed_data_file = 'database/config/smallRelationsInsertFile.sql'
    print(f"Putting seed data into tables using file - {seed_data_file}")
    seed_sql_filedata(connection_with_db_name, seed_data_file)
