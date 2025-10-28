"""Delete ALL Kentucky data (both old system and new campuses)."""
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent.parent))
from shared.config import get_db_connection, SCHOOLS

KENTUCKY_SYSTEM_ID = 86753094
KENTUCKY_CHILD_START_ID = 86753100

def delete_all_kentucky_data():
    """Delete all Kentucky data from all tables."""
    db_name = SCHOOLS['KCTCS']['dbname']
    
    try:
        connection = get_db_connection(db_name)
        if not connection:
            print("Failed to connect to database")
            return
        
        cursor = connection.cursor()
        
        print("Deleting ALL Kentucky data...")
        
        # Delete from cohort (old system + new campuses)
        cursor.execute("""
            DELETE FROM cohort 
            WHERE Institution_ID = %s 
               OR Institution_ID BETWEEN %s AND %s
        """, (KENTUCKY_SYSTEM_ID, KENTUCKY_CHILD_START_ID, KENTUCKY_CHILD_START_ID + 15))
        cohort_deleted = cursor.rowcount
        print(f"  ✓ Deleted {cohort_deleted} cohort records")
        
        # Delete from course (old system + new campuses)
        cursor.execute("""
            DELETE FROM course 
            WHERE Institution_ID = %s 
               OR Institution_ID BETWEEN %s AND %s
        """, (KENTUCKY_SYSTEM_ID, KENTUCKY_CHILD_START_ID, KENTUCKY_CHILD_START_ID + 15))
        course_deleted = cursor.rowcount
        print(f"  ✓ Deleted {course_deleted} course records")
        
        # Delete from financial_aid (old system + new campuses)
        cursor.execute("""
            DELETE FROM financial_aid 
            WHERE Institution_ID = %s 
               OR Institution_ID BETWEEN %s AND %s
        """, (KENTUCKY_SYSTEM_ID, KENTUCKY_CHILD_START_ID, KENTUCKY_CHILD_START_ID + 15))
        financial_deleted = cursor.rowcount
        print(f"  ✓ Deleted {financial_deleted} financial_aid records")
        
        # Commit changes
        connection.commit()
        print("\n✓ All Kentucky data deleted successfully")
        
        cursor.close()
        connection.close()
        
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
        if connection:
            connection.rollback()

if __name__ == "__main__":
    confirm = input("⚠️  WARNING: This will DELETE ALL Kentucky data. Continue? (yes/no): ")
    if confirm.lower() == 'yes':
        delete_all_kentucky_data()
    else:
        print("Deletion cancelled")
