import mysql.connector
from mysql.connector import Error
import os
from dotenv import load_dotenv
import random
from typing import List, Dict
import time
from datetime import datetime, timedelta

# Load environment variables
load_dotenv()

# Database configuration
DB_CONFIG = {
    "host": os.getenv("DB_HOST"),
    "user": os.getenv("DB_USER"),
    "password": os.getenv("DB_PASSWORD"),
    "port": int(os.getenv("DB_PORT", "3306")),
}

# Database names with their acronyms (updated names)
DATABASES = [
    {"dbname": "Bishop_State_Community_College", "acronym": "AL"},
    {"dbname": "California_State_University_San_Bernardino", "acronym": "CSUSB"},
    {"dbname": "Kentucky_Community_and_Technical_College_System", "acronym": "KCTCS"},
    {"dbname": "Thomas_More_University", "acronym": "KY"},
    {"dbname": "University_of_Akron", "acronym": "OH"}
]

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

def add_school_column_to_cohort(connection):
    """Add school column to existing cohort table if it doesn't exist."""
    cursor = connection.cursor()
    
    try:
        # Add school column if it doesn't exist
        cursor.execute("ALTER TABLE cohort ADD COLUMN school VARCHAR(10)")
        connection.commit()
        print("Added school column to cohort table")
    except Error as e:
        if "Duplicate column name" in str(e):
            print("School column already exists in cohort table")
        else:
            print(f"Error adding school column: {e}")
    finally:
        cursor.close()

def generate_cohort_data(num_records: int, school_acronym: str) -> List[Dict]:
    """Generate synthetic cohort data."""
    print(f"Generating synthetic cohort data for {school_acronym}...")
    
    # Cohort name patterns
    cohort_types = ["Fall", "Spring", "Summer", "Winter"]
    years = list(range(2020, 2026))
    programs = ["Engineering", "Business", "Liberal Arts", "Sciences", "Nursing", "Education"]
    
    synthetic_data = []
    
    for i in range(num_records):
        cohort_type = random.choice(cohort_types)
        year = random.choice(years)
        program = random.choice(programs)
        
        # Generate start and end dates
        if cohort_type == "Fall":
            start_month, start_day = 8, random.randint(15, 31)
            end_month, end_day = 12, random.randint(15, 20)
        elif cohort_type == "Spring":
            start_month, start_day = 1, random.randint(15, 31)
            end_month, end_day = 5, random.randint(15, 31)
        elif cohort_type == "Summer":
            start_month, start_day = 6, random.randint(1, 15)
            end_month, end_day = 8, random.randint(1, 15)
        else:  # Winter
            start_month, start_day = 12, random.randint(15, 31)
            end_month, end_day = 1, random.randint(15, 31)
            if end_month == 1:
                year += 1
        
        start_date = datetime(year, start_month, start_day)
        end_date = datetime(year, end_month, end_day)
        
        cohort = {
            'name': f"{cohort_type} {year} {program} Cohort",
            'start_date': start_date.strftime('%Y-%m-%d'),
            'end_date': end_date.strftime('%Y-%m-%d')
        }
        
        synthetic_data.append(cohort)
    
    return synthetic_data

def insert_cohort_data(connection, cohort_data: List[Dict], school_acronym: str):
    """Insert cohort data into the database."""
    cursor = connection.cursor()
    
    # Insert statement matching actual table columns
    insert_sql = """
    INSERT INTO cohort (name, start_date, end_date, school)
    VALUES (%s, %s, %s, %s)
    """
    
    try:
        for cohort in cohort_data:
            values = (
                cohort['name'],
                cohort['start_date'],
                cohort['end_date'],
                school_acronym
            )
            
            cursor.execute(insert_sql, values)
        
        connection.commit()
        print(f"Inserted {len(cohort_data)} cohort records for {school_acronym}")
        
    except Error as e:
        print(f"Error inserting cohort data: {e}")
        connection.rollback()
    finally:
        cursor.close()

def main():
    """Main function to generate and distribute synthetic cohort data."""
    
    # Generate synthetic data for each database (50 records each = 250 total)
    records_per_db = 50
    
    for db_info in DATABASES:
        db_name = db_info["dbname"]
        school_acronym = db_info["acronym"]
        
        print(f"\nProcessing database: {db_name} ({school_acronym})")
        
        # Generate synthetic data
        synthetic_data = generate_cohort_data(records_per_db, school_acronym)
        
        # Connect to database
        connection = get_db_connection(db_name)
        if not connection:
            print(f"Could not connect to database: {db_name}")
            continue
        
        try:
            # Add school column
            add_school_column_to_cohort(connection)
            
            # Insert data
            insert_cohort_data(connection, synthetic_data, school_acronym)
            
            print(f"Successfully populated {db_name} with {len(synthetic_data)} cohort records")
            
        finally:
            connection.close()
        
        # Small delay between databases
        time.sleep(1)
    
    print("\nCohort synthetic data generation completed!")

if __name__ == "__main__":
    main()
