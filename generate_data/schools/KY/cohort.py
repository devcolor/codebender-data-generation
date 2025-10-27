"""
Cohort data generation for Thomas More University (KY)
"""
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))

from schools.shared.config import get_db_connection, add_school_column_if_not_exists, SCHOOLS
import random
from typing import List, Dict
from datetime import datetime

SCHOOL_CODE = "KY"
SCHOOL_INFO = SCHOOLS[SCHOOL_CODE]

def generate_cohort_data(num_records: int = 50) -> List[Dict]:
    """Generate synthetic cohort data for KY."""
    print(f"Generating {num_records} cohort records for {SCHOOL_INFO['name']}...")
    
    cohort_types = ["Fall", "Spring", "Summer", "Winter"]
    years = list(range(2020, 2026))
    programs = ["Engineering", "Business", "Liberal Arts", "Sciences", "Nursing", "Education"]
    
    synthetic_data = []
    
    for i in range(num_records):
        cohort_type = random.choice(cohort_types)
        year = random.choice(years)
        program = random.choice(programs)
        
        if cohort_type == "Fall":
            start_month, start_day = 8, random.randint(15, 31)
            end_month, end_day = 12, random.randint(15, 20)
        elif cohort_type == "Spring":
            start_month, start_day = 1, random.randint(15, 31)
            end_month, end_day = 5, random.randint(15, 31)
        elif cohort_type == "Summer":
            start_month, start_day = 6, random.randint(1, 15)
            end_month, end_day = 8, random.randint(1, 15)
        else:
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

def insert_cohort_data(connection, cohort_data: List[Dict]):
    """Insert cohort data into the database."""
    cursor = connection.cursor()
    
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
                SCHOOL_INFO['acronym']
            )
            cursor.execute(insert_sql, values)
        
        connection.commit()
        print(f"[OK] Inserted {len(cohort_data)} cohort records for {SCHOOL_INFO['acronym']}")
        
    except Exception as e:
        print(f"[ERROR] Error inserting cohort data: {e}")
        connection.rollback()
    finally:
        cursor.close()

def main():
    """Main function to generate cohort data for KY."""
    print(f"\n{'='*60}")
    print(f"Cohort Data Generation - {SCHOOL_INFO['name']}")
    print(f"{'='*60}\n")
    
    synthetic_data = generate_cohort_data(num_records=50)
    
    connection = get_db_connection(SCHOOL_INFO['dbname'])
    if not connection:
        print(f"[ERROR] Could not connect to database: {SCHOOL_INFO['dbname']}")
        return
    
    try:
        add_school_column_if_not_exists(connection, 'cohort')
        insert_cohort_data(connection, synthetic_data)
        print(f"\n[OK] Successfully populated {SCHOOL_INFO['acronym']} cohort table")
    finally:
        connection.close()

if __name__ == "__main__":
    main()
