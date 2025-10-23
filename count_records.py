import mysql.connector
from mysql.connector import Error
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()

# Database configuration
DB_CONFIG = {
    "host": os.getenv("DB_HOST"),
    "user": os.getenv("DB_USER"),
    "password": os.getenv("DB_PASSWORD"),
    "port": int(os.getenv("DB_PORT", "3306")),
}

# Database names with their acronyms
DATABASES = [
    {"dbname": "Bishop_State_Community_College", "acronym": "AL"},
    {"dbname": "California_State_University_San_Bernardino", "acronym": "CSUSB"},
    {"dbname": "Kentucky_Community_and_Technical_College_System", "acronym": "KCTCS"},
    {"dbname": "Thomas_More_University", "acronym": "KY"},
    {"dbname": "University_of_Akron", "acronym": "OH"}
]

def get_connection(database_name: str = None):
    """Create and return a database connection."""
    config = DB_CONFIG.copy()
    if database_name:
        config["database"] = database_name
    
    try:
        return mysql.connector.connect(**config)
    except Error as e:
        print(f"Error connecting to database: {e}")
        return None

def count_records_in_table(connection, table_name):
    """Count records in a specific table."""
    cursor = connection.cursor()
    try:
        cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
        count = cursor.fetchone()[0]
        return count
    except Error as e:
        print(f"Error counting records in {table_name}: {e}")
        return 0
    finally:
        cursor.close()

def main():
    """Main function to count records in all databases."""
    
    print("📊 Data Summary by School")
    print("=" * 60)
    
    total_courses = 0
    total_cohorts = 0
    total_financial_aid = 0
    
    for db_info in DATABASES:
        db_name = db_info["dbname"]
        school_acronym = db_info["acronym"]
        
        print(f"\n🏫 {school_acronym} - {db_name}")
        print("-" * 50)
        
        # Connect to database
        connection = get_connection(db_name)
        if not connection:
            print(f"❌ Could not connect to database: {db_name}")
            continue
        
        try:
            # Count records in each table
            course_count = count_records_in_table(connection, "course")
            cohort_count = count_records_in_table(connection, "cohort")
            financial_aid_count = count_records_in_table(connection, "financial_aid")
            
            print(f"  📚 Course Records:      {course_count:,}")
            print(f"  👥 Cohort Records:      {cohort_count:,}")
            print(f"  💰 Financial Aid Records: {financial_aid_count:,}")
            print(f"  📊 Total Records:       {course_count + cohort_count + financial_aid_count:,}")
            
            # Add to totals
            total_courses += course_count
            total_cohorts += cohort_count
            total_financial_aid += financial_aid_count
            
        finally:
            connection.close()
    
    # Print grand totals
    print("\n" + "=" * 60)
    print("🎯 GRAND TOTALS ACROSS ALL SCHOOLS")
    print("=" * 60)
    print(f"📚 Total Course Records:      {total_courses:,}")
    print(f"👥 Total Cohort Records:      {total_cohorts:,}")
    print(f"💰 Total Financial Aid Records: {total_financial_aid:,}")
    print(f"📊 GRAND TOTAL RECORDS:       {total_courses + total_cohorts + total_financial_aid:,}")
    
    print(f"\n📈 Average per school:")
    print(f"  📚 Courses: {total_courses // 5:,} records per school")
    print(f"  👥 Cohorts: {total_cohorts // 5:,} records per school")
    print(f"  💰 Financial Aid: {total_financial_aid // 5:,} records per school")

if __name__ == "__main__":
    main()
