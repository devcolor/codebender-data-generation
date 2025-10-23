import mysql.connector
from mysql.connector import Error
import os
from dotenv import load_dotenv
import random
from typing import List, Dict
import time
from decimal import Decimal

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

def add_school_column_to_financial_aid(connection):
    """Add school column to existing financial_aid table if it doesn't exist."""
    cursor = connection.cursor()
    
    try:
        # Add school column if it doesn't exist
        cursor.execute("ALTER TABLE financial_aid ADD COLUMN school VARCHAR(10)")
        connection.commit()
        print("Added school column to financial_aid table")
    except Error as e:
        if "Duplicate column name" in str(e):
            print("School column already exists in financial_aid table")
        else:
            print(f"Error adding school column: {e}")
    finally:
        cursor.close()

def generate_financial_aid_data(num_records: int, school_acronym: str) -> List[Dict]:
    """Generate synthetic financial aid data."""
    print(f"Generating synthetic financial aid data for {school_acronym}...")
    
    # Financial aid types
    aid_types = [
        "Pell Grant", "Federal Direct Loan", "State Grant", "Institutional Grant",
        "Work Study", "Scholarship", "SEOG", "Parent PLUS Loan", "Private Loan",
        "Merit Scholarship", "Need-based Grant", "Athletic Scholarship"
    ]
    
    # Semesters and academic years
    semesters = ["Fall", "Spring", "Summer", "Winter"]
    academic_years = ["2020-21", "2021-22", "2022-23", "2023-24", "2024-25", "2025-26"]
    
    synthetic_data = []
    
    for i in range(num_records):
        # Generate student ID (format: school acronym + random number)
        student_id = f"{school_acronym}{random.randint(100000, 999999)}"
        
        # Select aid type and determine appropriate amount range
        aid_type = random.choice(aid_types)
        
        if "Grant" in aid_type or "Scholarship" in aid_type:
            # Grants and scholarships: $500 - $6000
            amount = round(random.uniform(500, 6000), 2)
        elif "Loan" in aid_type:
            # Loans: $1000 - $12000
            amount = round(random.uniform(1000, 12000), 2)
        elif "Work Study" in aid_type:
            # Work study: $800 - $3000
            amount = round(random.uniform(800, 3000), 2)
        else:
            # Other aid: $300 - $5000
            amount = round(random.uniform(300, 5000), 2)
        
        financial_aid = {
            'student_id': student_id,
            'aid_type': aid_type,
            'amount': Decimal(str(amount)),
            'semester': random.choice(semesters),
            'academic_year': random.choice(academic_years)
        }
        
        synthetic_data.append(financial_aid)
    
    return synthetic_data

def insert_financial_aid_data(connection, financial_aid_data: List[Dict], school_acronym: str):
    """Insert financial aid data into the database."""
    cursor = connection.cursor()
    
    # Insert statement matching actual table columns
    insert_sql = """
    INSERT INTO financial_aid (student_id, aid_type, amount, semester, academic_year, school)
    VALUES (%s, %s, %s, %s, %s, %s)
    """
    
    try:
        for aid in financial_aid_data:
            values = (
                aid['student_id'],
                aid['aid_type'],
                aid['amount'],
                aid['semester'],
                aid['academic_year'],
                school_acronym
            )
            
            cursor.execute(insert_sql, values)
        
        connection.commit()
        print(f"Inserted {len(financial_aid_data)} financial aid records for {school_acronym}")
        
    except Error as e:
        print(f"Error inserting financial aid data: {e}")
        connection.rollback()
    finally:
        cursor.close()

def main():
    """Main function to generate and distribute synthetic financial aid data."""
    
    # Generate synthetic data for each database (100 records each = 500 total)
    records_per_db = 100
    
    for db_info in DATABASES:
        db_name = db_info["dbname"]
        school_acronym = db_info["acronym"]
        
        print(f"\nProcessing database: {db_name} ({school_acronym})")
        
        # Generate synthetic data
        synthetic_data = generate_financial_aid_data(records_per_db, school_acronym)
        
        # Connect to database
        connection = get_db_connection(db_name)
        if not connection:
            print(f"Could not connect to database: {db_name}")
            continue
        
        try:
            # Add school column
            add_school_column_to_financial_aid(connection)
            
            # Insert data
            insert_financial_aid_data(connection, synthetic_data, school_acronym)
            
            print(f"Successfully populated {db_name} with {len(synthetic_data)} financial aid records")
            
        finally:
            connection.close()
        
        # Small delay between databases
        time.sleep(1)
    
    print("\nFinancial aid synthetic data generation completed!")

if __name__ == "__main__":
    main()
