"""Check for duplicate data and clean if necessary."""
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent.parent))
from shared.config import get_db_connection, SCHOOLS

KENTUCKY_SYSTEM_ID = 86753094
KENTUCKY_CHILD_START_ID = 86753100

def check_data():
    """Check the current state of Kentucky data."""
    db_name = SCHOOLS['KCTCS']['dbname']
    
    try:
        connection = get_db_connection(db_name)
        if not connection:
            print("Failed to connect to database")
            return
        
        cursor = connection.cursor()
        
        # Check for old system data
        cursor.execute("""
            SELECT COUNT(*) 
            FROM cohort 
            WHERE Institution_ID = %s
        """, (KENTUCKY_SYSTEM_ID,))
        old_cohort = cursor.fetchone()[0]
        print(f"Old system cohort records (ID={KENTUCKY_SYSTEM_ID}): {old_cohort}")
        
        # Check for new campus data
        cursor.execute("""
            SELECT Institution_ID, COUNT(*) as count
            FROM cohort 
            WHERE Institution_ID BETWEEN %s AND %s
            GROUP BY Institution_ID
            ORDER BY Institution_ID
        """, (KENTUCKY_CHILD_START_ID, KENTUCKY_CHILD_START_ID + 15))
        
        print("\nCampus data distribution:")
        total = 0
        for row in cursor.fetchall():
            inst_id, count = row
            total += count
            print(f"  Institution {inst_id}: {count} students")
        print(f"  Total: {total}")
        
        # Check for duplicates by Student_GUID
        cursor.execute("""
            SELECT Student_GUID, COUNT(*) as count
            FROM cohort
            WHERE Institution_ID BETWEEN %s AND %s
            GROUP BY Student_GUID
            HAVING count > 1
            LIMIT 10
        """, (KENTUCKY_CHILD_START_ID, KENTUCKY_CHILD_START_ID + 15))
        
        duplicates = cursor.fetchall()
        if duplicates:
            print(f"\n⚠️  Found {len(duplicates)} duplicate Student_GUIDs (showing first 10):")
            for guid, count in duplicates:
                print(f"  {guid}: {count} occurrences")
        else:
            print("\n✓ No duplicate Student_GUIDs found")
        
        cursor.close()
        connection.close()
        
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    check_data()
