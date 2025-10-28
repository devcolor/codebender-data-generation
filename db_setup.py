import mysql.connector
from mysql.connector import Error
import os
from dotenv import load_dotenv
from typing import List, Dict, Any, Optional

# Load environment variables
load_dotenv()

# Database configuration
DB_CONFIG = {
    "host": os.getenv("DB_HOST"),
    "user": os.getenv("DB_USER"),
    "password": os.getenv("DB_PASSWORD"),
    "port": int(os.getenv("DB_PORT", "3306")),
    "database": "mysql"  # Default database to connect to first
}

# Database names and their short names
DATABASES = [
    {"dbname": "Bishop_State_Community_College", "shortname": "AL"},
    {"dbname": "California_State_University_San_Bernardino", "shortname": "CSUSB"},
    {"dbname": "Kentucky_Community_and_Technical_College_System", "shortname": "KCTCS"},
    {"dbname": "Thomas_More_University", "shortname": "KY"},
    {"dbname": "University_of_Akron", "shortname": "OH"}
]

def get_connection(dbname: str = None) -> mysql.connector.connection.MySQLConnection:
    """Create a database connection."""
    config = DB_CONFIG.copy()
    if dbname:
        config["database"] = dbname
    
    try:
        conn = mysql.connector.connect(**config)
        return conn
    except Error as e:
        print(f"Error connecting to database: {e}")
        raise

def create_database(conn: mysql.connector.connection.MySQLConnection, dbname: str) -> None:
    """Create a new database."""
    cursor = conn.cursor()
    try:
        # Check if database exists
        cursor.execute("SHOW DATABASES LIKE %s", (dbname,))
        if not cursor.fetchone():
            cursor.execute(f"CREATE DATABASE {dbname}")
            print(f"Created database: {dbname}")
        else:
            print(f"Database {dbname} already exists")
    except Error as e:
        print(f"Error creating database {dbname}: {e}")
        raise
    finally:
        cursor.close()

def create_tables(conn: mysql.connector.connection.MySQLConnection, shortname: str) -> None:
    """Create tables in the specified database."""
    ar_table_name = f"ar_{shortname.lower()}"
    
    commands = [
        """
        CREATE TABLE IF NOT EXISTS cohort (
            id INT AUTO_INCREMENT PRIMARY KEY,
            name VARCHAR(255) NOT NULL,
            start_date DATE,
            end_date DATE,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """,
        """
        CREATE TABLE IF NOT EXISTS course (
            id INT AUTO_INCREMENT PRIMARY KEY,
            code VARCHAR(50) NOT NULL,
            title VARCHAR(255) NOT NULL,
            credits INT,
            description TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """,
        """
        CREATE TABLE IF NOT EXISTS financial_aid (
            id INT AUTO_INCREMENT PRIMARY KEY,
            student_id VARCHAR(50) NOT NULL,
            aid_type VARCHAR(100) NOT NULL,
            amount DECIMAL(10, 2) NOT NULL,
            semester VARCHAR(20),
            academic_year VARCHAR(20),
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """,
        f"""
        CREATE TABLE IF NOT EXISTS {ar_table_name} (
            id INT AUTO_INCREMENT PRIMARY KEY,
            student_id VARCHAR(50) NOT NULL,
            years_to_bachelors_cohort VARCHAR(50),
            years_to_assoc_cert_cohort VARCHAR(50),
            years_to_bachelor_other VARCHAR(50),
            years_to_assoc_cert_other VARCHAR(50),
            naspa_first_gen VARCHAR(50),
            first_year_bachelors_cohort VARCHAR(50),
            first_year_assoc_cert_cohort VARCHAR(50),
            first_year_bachelor_other VARCHAR(50),
            first_year_assoc_cert_other VARCHAR(50),
            recent_assoc_cert_other_state VARCHAR(50),
            recent_assoc_cert_other_carnegie VARCHAR(50),
            first_assoc_cert_other_carnegie VARCHAR(50),
            recent_assoc_cert_other_locale VARCHAR(50),
            school VARCHAR(10),
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """
    ]
    
    cursor = conn.cursor()
    try:
        for command in commands:
            try:
                cursor.execute(command)
                print("Created table")
            except Error as e:
                print(f"Error creating table: {e}")
                conn.rollback()
                raise
        conn.commit()
    finally:
        cursor.close()

def setup_databases():
    """Main function to set up all databases and tables."""
    conn = None
    try:
        # Connect to default database to create other databases
        conn = get_connection()
        
        for db in DATABASES:
            dbname = db["dbname"]
            shortname = db["shortname"]
            print(f"\nSetting up database: {dbname}")
            
            # Create database
            create_database(conn, dbname)
            
            # Close current connection to switch databases
            conn.close()
            
            # Connect to the new database
            db_conn = get_connection(dbname)
            
            # Create tables
            create_tables(db_conn, shortname)
            
            # Close connection to this database
            db_conn.close()
            
            # Reconnect to default database for next iteration
            conn = get_connection()
            
            print(f"Completed setup for database: {dbname}")
            
    except Error as e:
        print(f"Error during database setup: {e}")
    finally:
        if conn and conn.is_connected():
            conn.close()

if __name__ == "__main__":
    print("Starting database setup...")
    setup_databases()
    print("\nDatabase setup completed!")
