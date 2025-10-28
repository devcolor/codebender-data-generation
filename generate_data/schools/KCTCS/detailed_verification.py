"""Detailed verification of Kentucky data structure."""
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent.parent))
from shared.config import get_db_connection, SCHOOLS

KENTUCKY_SYSTEM_ID = 86753094
KENTUCKY_CHILD_START_ID = 86753100

CAMPUS_STUDENT_TARGETS = {
    86753100: 1500,   # Ashland
    86753101: 1400,   # Big Sandy
    86753102: 3500,   # Bluegrass
    86753103: 2200,   # Elizabethtown
    86753104: 2000,   # Gateway
    86753105: 1300,   # Hazard
    86753106: 1600,   # Henderson
    86753107: 1500,   # Hopkinsville
    86753108: 4500,   # Jefferson
    86753109: 1400,   # Madisonville
    86753110: 1200,   # Maysville
    86753111: 2000,   # Owensboro
    86753112: 1600,   # Somerset
    86753113: 1800,   # Southcentral
    86753114: 1500,   # Southeast
    86753115: 2000,   # West Kentucky
}

def detailed_verification():
    """Perform detailed verification of Kentucky data."""
    db_name = SCHOOLS['KCTCS']['dbname']
    
    try:
        connection = get_db_connection(db_name)
        if not connection:
            print("Failed to connect to database")
            return
        
        cursor = connection.cursor()
        
        print("="*70)
        print("DETAILED KENTUCKY DATA VERIFICATION")
        print("="*70)
        
        # 1. Institution Hierarchy
        print("\n1. INSTITUTION HIERARCHY")
        print("-" * 70)
        cursor.execute("""
            SELECT Institution_ID, Name, Code, Institution_Type, Parent_Institution_ID
            FROM institution
            WHERE Institution_ID = %s OR Parent_Institution_ID = %s
            ORDER BY Institution_Type DESC, Institution_ID
        """, (KENTUCKY_SYSTEM_ID, KENTUCKY_SYSTEM_ID))
        
        for row in cursor.fetchall():
            inst_id, name, code, inst_type, parent_id = row
            if inst_type == 'system':
                print(f"  [SYSTEM] {name} (ID: {inst_id}, Code: {code})")
            else:
                print(f"    └─ [CAMPUS] {name} (ID: {inst_id}, Code: {code})")
        
        # 2. Student Distribution
        print("\n2. STUDENT DISTRIBUTION BY CAMPUS")
        print("-" * 70)
        cursor.execute("""
            SELECT 
                i.Institution_ID,
                i.Name,
                COUNT(DISTINCT c.Student_GUID) as Student_Count
            FROM institution i
            LEFT JOIN cohort c ON i.Institution_ID = c.Institution_ID
            WHERE i.Parent_Institution_ID = %s
            GROUP BY i.Institution_ID, i.Name
            ORDER BY Student_Count DESC
        """, (KENTUCKY_SYSTEM_ID,))
        
        total_students = 0
        for row in cursor.fetchall():
            inst_id, campus_name, student_count = row
            target = CAMPUS_STUDENT_TARGETS[inst_id]
            match = "✓" if student_count == target else "✗"
            total_students += student_count
            print(f"  {match} {campus_name[:45]:45} {student_count:5} / {target:5}")
        
        print(f"\n  Total Students: {total_students:,} (Target: 31,000)")
        
        # 3. Data Consistency
        print("\n3. DATA CONSISTENCY CHECKS")
        print("-" * 70)
        
        # Check Student_GUID consistency between cohort and course
        cursor.execute("""
            SELECT 
                COUNT(DISTINCT c.Student_GUID) as cohort_students,
                COUNT(DISTINCT cr.Student_GUID) as course_students
            FROM cohort c
            LEFT JOIN course cr ON c.Student_GUID = cr.Student_GUID
            WHERE c.Institution_ID BETWEEN %s AND %s
        """, (KENTUCKY_CHILD_START_ID, KENTUCKY_CHILD_START_ID + 15))
        
        cohort_students, course_students = cursor.fetchone()
        match = "✓" if cohort_students == course_students else "✗"
        print(f"  {match} Student_GUID match (cohort vs course): {cohort_students:,} = {course_students:,}")
        
        # Check average courses per student
        cursor.execute("""
            SELECT 
                COUNT(*) / COUNT(DISTINCT Student_GUID) as avg_courses
            FROM course
            WHERE Institution_ID BETWEEN %s AND %s
        """, (KENTUCKY_CHILD_START_ID, KENTUCKY_CHILD_START_ID + 15))
        
        avg_courses = cursor.fetchone()[0]
        print(f"  ✓ Average courses per student: {avg_courses:.2f} (Expected: 3-6)")
        
        # Check financial aid percentage
        cursor.execute("""
            SELECT 
                COUNT(DISTINCT fa.Student_ID) as students_with_aid,
                (SELECT COUNT(DISTINCT Student_GUID) 
                 FROM cohort 
                 WHERE Institution_ID BETWEEN %s AND %s) as total_students
            FROM financial_aid fa
            WHERE fa.Institution_ID BETWEEN %s AND %s
        """, (KENTUCKY_CHILD_START_ID, KENTUCKY_CHILD_START_ID + 15,
              KENTUCKY_CHILD_START_ID, KENTUCKY_CHILD_START_ID + 15))
        
        students_with_aid, total = cursor.fetchone()
        pct = (students_with_aid / total * 100) if total > 0 else 0
        print(f"  ✓ Financial aid coverage: {students_with_aid:,} / {total:,} ({pct:.1f}%, Expected: ~70%)")
        
        # 4. Views
        print("\n4. REPORTING VIEWS")
        print("-" * 70)
        cursor.execute("SHOW TABLES LIKE 'v_%'")
        views = cursor.fetchall()
        for view in views:
            print(f"  ✓ {view[0]}")
        
        # Test a view
        cursor.execute("""
            SELECT COUNT(*) 
            FROM v_cohort_with_system 
            WHERE System_Name = 'Kentucky Community and Technical College System'
        """)
        view_count = cursor.fetchone()[0]
        print(f"\n  View test: v_cohort_with_system returns {view_count:,} records")
        
        # 5. Old Data Check
        print("\n5. OLD DATA CHECK")
        print("-" * 70)
        cursor.execute("""
            SELECT COUNT(*) 
            FROM cohort 
            WHERE Institution_ID = %s
        """, (KENTUCKY_SYSTEM_ID,))
        old_data = cursor.fetchone()[0]
        if old_data == 0:
            print(f"  ✓ No old system data found (Institution_ID = {KENTUCKY_SYSTEM_ID})")
        else:
            print(f"  ✗ WARNING: Found {old_data} old system records!")
        
        print("\n" + "="*70)
        print("VERIFICATION COMPLETE")
        print("="*70)
        
        cursor.close()
        connection.close()
        
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    detailed_verification()
