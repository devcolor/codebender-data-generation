"""
Verify analysis_ready_all table was populated correctly
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
    "database": "Bishop_State_Community_College"
}

def main():
    print("="*80)
    print("VERIFYING ANALYSIS_READY_ALL TABLE")
    print("="*80)
    
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        cursor = conn.cursor()
        
        # Check table structure
        print("\n1. TABLE STRUCTURE:")
        cursor.execute("DESCRIBE analysis_ready_all")
        columns = cursor.fetchall()
        for field, type_info, null_info, key_info, default, extra in columns:
            print(f"   {field:<40} {type_info:<20}")
        
        # Count records
        print("\n2. RECORD COUNT:")
        cursor.execute("SELECT COUNT(*) FROM analysis_ready_all WHERE school = 'AL'")
        count = cursor.fetchone()[0]
        print(f"   Total AL records: {count}")
        
        # Check unique student IDs
        print("\n3. STUDENT ID CHECK:")
        cursor.execute("SELECT COUNT(DISTINCT student_id) FROM analysis_ready_all WHERE school = 'AL'")
        unique_students = cursor.fetchone()[0]
        print(f"   Unique student IDs: {unique_students}")
        
        # Verify student IDs match cohort table
        print("\n4. MATCHING WITH COHORT TABLE:")
        cursor.execute("""
            SELECT COUNT(DISTINCT c.Student_GUID) 
            FROM cohort c 
            WHERE c.school = 'AL'
        """)
        cohort_students = cursor.fetchone()[0]
        print(f"   Student IDs in cohort: {cohort_students}")
        
        cursor.execute("""
            SELECT COUNT(DISTINCT ara.student_id)
            FROM analysis_ready_all ara
            INNER JOIN cohort c ON ara.student_id = c.Student_GUID
            WHERE ara.school = 'AL' AND c.school = 'AL'
        """)
        matching_students = cursor.fetchone()[0]
        print(f"   Matching student IDs: {matching_students}")
        print(f"   Match rate: {(matching_students/cohort_students*100):.1f}%")
        
        # Sample data
        print("\n5. SAMPLE DATA (first 3 records):")
        cursor.execute("""
            SELECT student_id, years_to_bachelors_cohort, naspa_first_gen, 
                   recent_assoc_cert_other_state, school
            FROM analysis_ready_all 
            WHERE school = 'AL'
            LIMIT 3
        """)
        rows = cursor.fetchall()
        print(f"   {'Student ID':<15} {'Years Bach':<12} {'NASPA FG':<10} {'State':<10} {'School':<8}")
        print("   " + "-"*65)
        for row in rows:
            print(f"   {str(row[0]):<15} {str(row[1]):<12} {str(row[2]):<10} {str(row[3]):<10} {str(row[4]):<8}")
        
        print("\n" + "="*80)
        print("✓ VERIFICATION COMPLETE")
        print("="*80)
        
        cursor.close()
        conn.close()
        
    except Error as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    main()
