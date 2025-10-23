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

def list_tables(connection, database):
    """List all tables in a specific database."""
    cursor = connection.cursor()
    try:
        cursor.execute(f"USE `{database}`")
        cursor.execute("SHOW TABLES")
        tables = [table[0] for table in cursor.fetchall()]
        return tables
    except Error as e:
        print(f"Error listing tables in {database}: {e}")
        return []
    finally:
        cursor.close()

def describe_table(connection, database, table):
    """Show the structure of a specific table."""
    cursor = connection.cursor(dictionary=True)
    try:
        cursor.execute(f"USE `{database}`")
        cursor.execute(f"DESCRIBE `{table}`")
        return cursor.fetchall()
    except Error as e:
        print(f"Error describing table {database}.{table}: {e}")
        return []
    finally:
        cursor.close()

def main():
    """Main function to list all databases and their tables."""
    load_dotenv()
    connection = None
    
    try:
        print("Connecting to the database...")
        connection = get_connection()
        
        if connection.is_connected():
            print(f"\nConnected to: {connection.get_server_info()}")
            
            # List all databases
            print("\n=== Databases ===")
            databases = list_databases(connection)
            
            for db in databases:
                print(f"\nDatabase: {db}")
                print("-" * (len(db) + 10))
                
                # List all tables in the database
                tables = list_tables(connection, db)
                if not tables:
                    print("  No tables found")
                    continue
                    
                for table in tables:
                    print(f"  Table: {table}")
                    
                    # Show table structure
                    columns = describe_table(connection, db, table)
                    if columns:
                        print("    Columns:")
                        for col in columns:
                            print(f"      - {col['Field']} ({col['Type']}) {'NULL' if col['Null'] == 'YES' else 'NOT NULL'} {col.get('Key', '')} {col.get('Default', '')} {col.get('Extra', '')}".strip())
    
    except Error as e:
        print(f"Error: {e}")
    finally:
        if connection and connection.is_connected():
            connection.close()
            print("\nConnection closed.")

if __name__ == "__main__":
    main()
