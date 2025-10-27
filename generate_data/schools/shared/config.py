"""
Shared configuration and utilities for data generation across all schools.
"""
import mysql.connector
from mysql.connector import Error
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Database configuration
DB_CONFIG = {
    "host": os.getenv("DB_HOST"),
    "user": os.getenv("DB_USER"),
    "password": os.getenv("DB_PASSWORD"),
    "port": int(os.getenv("DB_PORT", "3306")),
}

# School configurations
SCHOOLS = {
    "AL": {
        "name": "Bishop State Community College",
        "dbname": "Bishop_State_Community_College",
        "acronym": "AL"
    },
    "CSUSB": {
        "name": "California State University San Bernardino",
        "dbname": "California_State_University_San_Bernardino",
        "acronym": "CSUSB"
    },
    "KCTCS": {
        "name": "Kentucky Community and Technical College System",
        "dbname": "Kentucky_Community_and_Technical_College_System",
        "acronym": "KCTCS"
    },
    "KY": {
        "name": "Thomas More University",
        "dbname": "Thomas_More_University",
        "acronym": "KY"
    },
    "OH": {
        "name": "University of Akron",
        "dbname": "University_of_Akron",
        "acronym": "OH"
    }
}

def get_db_connection(database_name: str = None):
    """Create database connection."""
    config = DB_CONFIG.copy()
    if database_name:
        config["database"] = database_name
    
    try:
        return mysql.connector.connect(**config)
    except Error as e:
        print(f"Error connecting to database: {e}")
        return None

def add_school_column_if_not_exists(connection, table_name: str):
    """Add school column to a table if it doesn't exist."""
    cursor = connection.cursor()
    
    try:
        cursor.execute(f"ALTER TABLE {table_name} ADD COLUMN school VARCHAR(10)")
        connection.commit()
        print(f"Added school column to {table_name} table")
    except Error as e:
        if "Duplicate column name" in str(e):
            print(f"School column already exists in {table_name} table")
        else:
            print(f"Error adding school column to {table_name}: {e}")
    finally:
        cursor.close()
