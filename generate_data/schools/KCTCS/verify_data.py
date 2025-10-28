"""Quick verification script to check if Kentucky data was regenerated."""
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent.parent))
from shared.config import get_db_connection, SCHOOLS

KENTUCKY_SYSTEM_ID = 86753094
KENTUCKY_CHILD_START_ID = 86753100

def verify_kentucky_data():
    """Verify the Kentucky data exists."""
    db_name = SCHOOLS['KCTCS']['dbname']
    
    try:
        connection = get_db_connection(db_name)
        if not connection:
            print("Failed to connect to database")
            return
        
        cursor = connection.cursor()
        
        # Check institution table
        cursor.execute("""
            SELECT COUNT(*) 
            FROM institution 
            WHERE Institution_ID = %s OR Parent_Institution_ID = %s
        """, (KENTUCKY_SYSTEM_ID, KENTUCKY_SYSTEM_ID))
        inst_count = cursor.fetchone()[0]
        print(f"Institution records: {inst_count} (expected: 17)")
        
        # Check cohort table
        cursor.execute("""
            SELECT COUNT(*) 
            FROM cohort 
            WHERE Institution_ID BETWEEN %s AND %s
        """, (KENTUCKY_CHILD_START_ID, KENTUCKY_CHILD_START_ID + 15))
        cohort_count = cursor.fetchone()[0]
        print(f"Cohort records: {cohort_count} (expected: ~31000)")
        
        # Check course table
        cursor.execute("""
            SELECT COUNT(*) 
            FROM course 
            WHERE Institution_ID BETWEEN %s AND %s
        """, (KENTUCKY_CHILD_START_ID, KENTUCKY_CHILD_START_ID + 15))
        course_count = cursor.fetchone()[0]
        print(f"Course records: {course_count} (expected: ~120000-180000)")
        
        # Check financial_aid table
        cursor.execute("""
            SELECT COUNT(*) 
            FROM financial_aid 
            WHERE Institution_ID BETWEEN %s AND %s
        """, (KENTUCKY_CHILD_START_ID, KENTUCKY_CHILD_START_ID + 15))
        financial_count = cursor.fetchone()[0]
        print(f"Financial aid records: {financial_count} (expected: ~21000)")
        
        # Check views
        cursor.execute("SHOW TABLES LIKE 'v_%'")
        views = cursor.fetchall()
        print(f"\nViews created: {len(views)}")
        for view in views:
            print(f"  - {view[0]}")
        
        cursor.close()
        connection.close()
        
        print("\n✓ Verification complete")
        
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    verify_kentucky_data()
