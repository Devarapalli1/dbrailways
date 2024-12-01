import mysql

from config import Config
from dbconnection import seed_sql_filedata, execute_schema_file, create_or_use_database, drop_database

DB_CONFIG = {
    "host": Config.MYSQL_HOST,
    "user": Config.MYSQL_USER,
    "password": Config.MYSQL_PASSWORD
}

config = DB_CONFIG.copy()

def create_connection(db_name=None):
    if db_name:
        config["database"] = db_name
    return mysql.connector.connect(**config)

if __name__ == "__main__":
    print("Welcome to Railway Management Service Project")
    db_name = Config.MYSQL_DB

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
