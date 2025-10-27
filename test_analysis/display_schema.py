"""
Display the complete schema for all 3 tables across all databases.
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
SCHOOLS = [
    {"dbname": "Bishop_State_Community_College", "acronym": "AL", "name": "Bishop State Community College"},
    {"dbname": "California_State_University_San_Bernardino", "acronym": "CSUSB", "name": "California State University San Bernardino"},
    {"dbname": "Kentucky_Community_and_Technical_College_System", "acronym": "KCTCS", "name": "Kentucky Community and Technical College System"},
    {"dbname": "Thomas_More_University", "acronym": "KY", "name": "Thomas More University"},
    {"dbname": "University_of_Akron", "acronym": "OH", "name": "University of Akron"}
]

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

def display_table_schema(connection, table_name: str, school_name: str):
    """Display schema for a specific table."""
    cursor = connection.cursor(dictionary=True)

    try:
        cursor.execute(f"DESCRIBE {table_name}")
        columns = cursor.fetchall()

        print(f"\n{school_name} - {table_name.upper()} TABLE SCHEMA")
        print("=" * 60)

        for col in columns:
            field = col['Field']
            type_info = col['Type']
            null_info = col['Null']
            key_info = col['Key']
            default = col['Default']
            extra = col['Extra']

            print(f"  {field"20"} | {type_info"15"} | {null_info"4"} | {key_info"6"} | {str(default)"10"} | {extra}")

        # Get sample data
        cursor.execute(f"SELECT * FROM {table_name} LIMIT 3")
        sample_data = cursor.fetchall()

        if sample_data:
            print("
SAMPLE DATA (first 3 rows):")
            print("-" * 40)
            # Get column names
            cursor.execute(f"DESCRIBE {table_name}")
            columns = cursor.fetchall()
            col_names = [col['Field'] for col in columns]
            print(f"  {' | '.join(col_names)}")
            print("-" * 40)

            for row in sample_data:
                values = []
                for col in col_names:
                    val = row[col]
                    if val is None:
                        values.append("NULL")
                    elif isinstance(val, str) and len(val) > 15:
                        values.append(f"{val[:12]}...")
                    else:
                        values.append(str(val))
                print(f"  {' | '.join(values)}")

    except Error as e:
        print(f"  Error getting schema for {table_name}: {e}")
    finally:
        cursor.close()

def main():
    """Main function to display all table schemas."""
    print("="*80)
    print("COMPLETE DATABASE SCHEMA - ALL TABLES")
    print("="*80)

    # Check one school to get the schema (all schools should have identical structure)
    school = SCHOOLS[0]  # Use first school
    connection = get_db_connection(school['dbname'])

    if connection:
        try:
            # Display schema for all 3 tables
            for table in ['cohort', 'course', 'financial_aid']:
                display_table_schema(connection, table, school['name'])

        finally:
            connection.close()
    else:
        print("Could not connect to database")

    print("\n" + "="*80)
    print("SCHEMA SUMMARY")
    print("="*80)
    print("""
COHORT TABLE:
- id (PRIMARY KEY, AUTO_INCREMENT)
- name (VARCHAR(255)) - Contains cohort name + student GUID
- start_date (DATE)
- end_date (DATE)
- school (VARCHAR(10))
- dataset_type (VARCHAR(1)) - 'S' for Synthetic, 'R' for Real
- created_at (TIMESTAMP)

COURSE TABLE:
- id (PRIMARY KEY, AUTO_INCREMENT)
- code (VARCHAR(50)) - Course code like 'ENG101'
- title (VARCHAR(255)) - Course title
- credits (INT) - Number of credits
- description (TEXT) - Course description
- school (VARCHAR(10))
- dataset_type (VARCHAR(1)) - 'S' for Synthetic, 'R' for Real
- created_at (TIMESTAMP)

FINANCIAL_AID TABLE:
- id (PRIMARY KEY, AUTO_INCREMENT)
- student_id (VARCHAR(50)) - Student GUID
- aid_type (VARCHAR(100)) - Type of financial aid
- amount (DECIMAL(10,2)) - Aid amount
- semester (VARCHAR(20)) - Academic semester
- academic_year (VARCHAR(20)) - Academic year
- school (VARCHAR(10))
- dataset_type (VARCHAR(1)) - 'S' for Synthetic, 'R' for Real
- created_at (TIMESTAMP)
""")

if __name__ == "__main__":
    main()
