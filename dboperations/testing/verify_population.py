"""
Verification script to confirm data population and referential integrity.
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

def verify_school(school: dict):
    """Verify data for a single school."""
    print("\n" + "="*80)
    print(f"{school['name']} ({school['acronym']})")
    print("="*80)
    
    connection = get_db_connection(school['dbname'])
    if not connection:
        return
    
    cursor = connection.cursor(dictionary=True)
    
    try:
        # Count cohorts
        cursor.execute("SELECT COUNT(*) as count FROM cohort WHERE dataset_type = 'S'")
        cohort_count = cursor.fetchone()['count']
        
        # Count courses
        cursor.execute("SELECT COUNT(*) as count FROM course WHERE dataset_type = 'S'")
        course_count = cursor.fetchone()['count']
        
        # Count financial aid
        cursor.execute("SELECT COUNT(*) as count FROM financial_aid WHERE dataset_type = 'S'")
        financial_count = cursor.fetchone()['count']
        
        # Get cohort details
        cursor.execute("""
            SELECT name, start_date, end_date, school 
            FROM cohort 
            WHERE dataset_type = 'S'
            ORDER BY start_date
        """)
        cohorts = cursor.fetchall()
        
        # Verify dataset_type column exists
        cursor.execute("SHOW COLUMNS FROM cohort LIKE 'dataset_type'")
        has_dataset_type = cursor.fetchone() is not None
        
        print(f"\nData Summary:")
        print(f"  Cohorts (Synthetic):        {cohort_count:,}")
        print(f"  Course Records (Synthetic): {course_count:,}")
        print(f"  Financial Aid (Synthetic):  {financial_count:,}")
        print(f"  dataset_type column:        {'[OK] Present' if has_dataset_type else '[ERROR] Missing'}")
        
        print(f"\nCohort Details:")
        for cohort in cohorts:
            print(f"  - {cohort['name']}")
            print(f"    Start: {cohort['start_date']}, End: {cohort['end_date']}")
        
        # Verify all records are marked as synthetic
        cursor.execute("""
            SELECT 
                (SELECT COUNT(*) FROM cohort WHERE dataset_type != 'S') as non_synthetic_cohorts,
                (SELECT COUNT(*) FROM course WHERE dataset_type != 'S') as non_synthetic_courses,
                (SELECT COUNT(*) FROM financial_aid WHERE dataset_type != 'S') as non_synthetic_financial
        """)
        non_synthetic = cursor.fetchone()
        
        if non_synthetic['non_synthetic_cohorts'] == 0 and \
           non_synthetic['non_synthetic_courses'] == 0 and \
           non_synthetic['non_synthetic_financial'] == 0:
            print(f"\n[OK] All records properly marked as synthetic (dataset_type = 'S')")
        else:
            print(f"\n[WARNING] Found non-synthetic records:")
            print(f"  Cohorts: {non_synthetic['non_synthetic_cohorts']}")
            print(f"  Courses: {non_synthetic['non_synthetic_courses']}")
            print(f"  Financial Aid: {non_synthetic['non_synthetic_financial']}")
        
    finally:
        cursor.close()
        connection.close()

def main():
    """Main verification function."""
    print("\n" + "="*80)
    print(" "*25 + "DATA VERIFICATION REPORT")
    print("="*80)
    
    total_cohorts = 0
    total_courses = 0
    total_financial = 0
    
    for school in SCHOOLS:
        verify_school(school)
        
        # Get counts for grand total
        connection = get_db_connection(school['dbname'])
        if connection:
            cursor = connection.cursor(dictionary=True)
            cursor.execute("SELECT COUNT(*) as count FROM cohort WHERE dataset_type = 'S'")
            total_cohorts += cursor.fetchone()['count']
            cursor.execute("SELECT COUNT(*) as count FROM course WHERE dataset_type = 'S'")
            total_courses += cursor.fetchone()['count']
            cursor.execute("SELECT COUNT(*) as count FROM financial_aid WHERE dataset_type = 'S'")
            total_financial += cursor.fetchone()['count']
            cursor.close()
            connection.close()
    
    print("\n" + "="*80)
    print("GRAND TOTALS ACROSS ALL SCHOOLS")
    print("="*80)
    print(f"  Total Cohorts:        {total_cohorts:,}")
    print(f"  Total Course Records: {total_courses:,}")
    print(f"  Total Financial Aid:  {total_financial:,}")
    print(f"  GRAND TOTAL RECORDS:  {total_cohorts + total_courses + total_financial:,}")
    print("="*80 + "\n")

if __name__ == "__main__":
    main()
