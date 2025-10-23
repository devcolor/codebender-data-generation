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

def get_connection():
    """Create database connection."""
    try:
        return mysql.connector.connect(**DB_CONFIG)
    except Error as e:
        print(f"Error connecting to database: {e}")
        return None

def rename_database(connection, old_name, new_name):
    """Rename a database by creating new one and copying data."""
    cursor = connection.cursor()
    
    try:
        # Create new database
        cursor.execute(f"CREATE DATABASE IF NOT EXISTS `{new_name}`")
        print(f"Created new database: {new_name}")
        
        # Get all tables from old database
        cursor.execute(f"USE `{old_name}`")
        cursor.execute("SHOW TABLES")
        tables = [table[0] for table in cursor.fetchall()]
        
        # Copy each table to new database
        for table in tables:
            print(f"Copying table: {table}")
            cursor.execute(f"CREATE TABLE `{new_name}`.`{table}` LIKE `{old_name}`.`{table}`")
            cursor.execute(f"INSERT INTO `{new_name}`.`{table}` SELECT * FROM `{old_name}`.`{table}`")
        
        # Drop old database
        cursor.execute(f"DROP DATABASE `{old_name}`")
        print(f"Dropped old database: {old_name}")
        
        connection.commit()
        print(f"Successfully renamed {old_name} to {new_name}")
        
    except Error as e:
        print(f"Error renaming database {old_name} to {new_name}: {e}")
        connection.rollback()
    finally:
        cursor.close()

def main():
    """Main function to rename databases."""
    connection = get_connection()
    if not connection:
        return
    
    try:
        # Rename the databases
        rename_database(connection, "Thomas_More_University_KY", "Thomas_More_University")
        rename_database(connection, "University_of_Akron_OH", "University_of_Akron")
        
    finally:
        connection.close()
        print("Database renaming completed!")

if __name__ == "__main__":
    main()
