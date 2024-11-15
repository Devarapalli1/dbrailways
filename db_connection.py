import pymysql
from flask import current_app

def get_db_connection():
    """
    Establishes and returns a connection to the MySQL database using PyMySQL.
    """
    conn = pymysql.connect(
        host=current_app.config['MYSQL_HOST'],
        user=current_app.config['MYSQL_USER'],
        password=current_app.config['MYSQL_PASSWORD'],
        db=current_app.config['MYSQL_DB']
    )
    return conn
