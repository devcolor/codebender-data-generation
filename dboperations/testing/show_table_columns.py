"""
Display the exact column structure for all 3 tables in the databases.
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

def get_db_connection(database_name: str = None):
    """Create database connection."""
    config = DB_CONFIG.copy()
    if database_name:
        config["database"] = database_name

    try:
        return mysql.connector.connect(**config)
    except Error as e:
        print(f"[ERROR] Error connecting to database: {e}")
        return None

def show_table_structure(connection, table_name: str):
    """Display complete table structure."""
    cursor = connection.cursor()

    try:
        cursor.execute(f"DESCRIBE {table_name}")
        columns = cursor.fetchall()

        print(f"\n{table_name.upper()} TABLE - {len(columns)} COLUMNS:")
        print("=" * 80)
        print(f"{'#':<3} {'Column Name':<40} {'Type':<20} {'Null':<5} {'Key':<5} {'Default':<10}")
        print("-" * 80)

        for i, (field, type_info, null_info, key_info, default, extra) in enumerate(columns, 1):
            print(f"{i:<3} {field:<40} {type_info:<20} {null_info:<5} {key_info:<5} {str(default):<10}")

        return len(columns)

    except Error as e:
        print(f"Error getting structure for {table_name}: {e}")
        return 0
    finally:
        cursor.close()

def main():
    """Main function to display all table structures."""
    print("="*80)
    print("COMPLETE DATABASE TABLE STRUCTURE")
    print("="*80)

    # Connect to first school database to get structure
    connection = get_db_connection("Bishop_State_Community_College")

    if connection:
        try:
            # Show structure for all 3 tables
            cohort_cols = show_table_structure(connection, 'cohort')
            course_cols = show_table_structure(connection, 'course')
            financial_cols = show_table_structure(connection, 'financial_aid')

            print(f"\n{'='*80}")
            print("SUMMARY:")
            print(f"  - COHORT TABLE: {cohort_cols} columns")
            print(f"  - COURSE TABLE: {course_cols} columns")
            print(f"  - FINANCIAL_AID TABLE: {financial_cols} columns")
            print(f"  - TOTAL COLUMNS: {cohort_cols + course_cols + financial_cols}")
            print("="*80)

        finally:
            connection.close()
    else:
        print("Could not connect to database")

if __name__ == "__main__":
    main()
