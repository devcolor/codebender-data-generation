import mysql.connector
from mysql.connector import Error
from dotenv import load_dotenv
import os

def get_connection():
    """Create and return a database connection."""
    config = {
        "host": os.getenv("DB_HOST"),
        "user": os.getenv("DB_USER"),
        "password": os.getenv("DB_PASSWORD"),
        "port": int(os.getenv("DB_PORT", "3306")),
    }
    return mysql.connector.connect(**config)

def list_databases(connection):
    """List all databases."""
    cursor = connection.cursor()
    cursor.execute("SHOW DATABASES")
    databases = [db[0] for db in cursor.fetchall()]
    cursor.close()
    return databases

def main():
    """Main function to list all databases."""
    load_dotenv()
    connection = None
    
    try:
        print("Connecting to the database...")
        connection = get_connection()
        
        if connection.is_connected():
            print(f"\nConnected to MariaDB Server version: {connection.server_info}")
            
            # List all databases
            print("\nAvailable Databases:")
            print("-" * 30)
            databases = list_databases(connection)
            
            for i, db in enumerate(databases, 1):
                print(f"{i:2d}. {db}")
    
    except Error as e:
        print(f"Error: {e}")
    finally:
        if connection and connection.is_connected():
            connection.close()
            print("\nConnection closed.")

if __name__ == "__main__":
    main()
