"""
Delete existing Kentucky data and regenerate with institution hierarchy.
Creates 16 child campuses and generates ~30k students distributed across them.
"""
import sys
import os
from pathlib import Path
import random
from datetime import datetime, timedelta

# Add parent directory to path for imports
sys.path.append(str(Path(__file__).parent.parent))

from shared.config import get_db_connection, SCHOOLS

# Map acronyms to database names
DATABASES = {school['acronym']: school['dbname'] for school in SCHOOLS.values()}

# Kentucky parent and child configuration
KENTUCKY_SYSTEM_ID = 86753094
KENTUCKY_CHILD_START_ID = 86753100

KENTUCKY_CAMPUSES = [
    {'id': 86753100, 'name': 'Ashland Community and Technical College', 'code': 'ACTC'},
    {'id': 86753101, 'name': 'Big Sandy Community and Technical College', 'code': 'BSCTC'},
    {'id': 86753102, 'name': 'Bluegrass Community and Technical College', 'code': 'BCTC'},
    {'id': 86753103, 'name': 'Elizabethtown Community and Technical College', 'code': 'ECTC'},
    {'id': 86753104, 'name': 'Gateway Community and Technical College', 'code': 'GCTC'},
    {'id': 86753105, 'name': 'Hazard Community and Technical College', 'code': 'HCTC'},
    {'id': 86753106, 'name': 'Henderson Community College', 'code': 'HCC'},
    {'id': 86753107, 'name': 'Hopkinsville Community College', 'code': 'HCC2'},
    {'id': 86753108, 'name': 'Jefferson Community and Technical College', 'code': 'JCTC'},
    {'id': 86753109, 'name': 'Madisonville Community College', 'code': 'MCC'},
    {'id': 86753110, 'name': 'Maysville Community and Technical College', 'code': 'MCTC'},
    {'id': 86753111, 'name': 'Owensboro Community and Technical College', 'code': 'OCTC'},
    {'id': 86753112, 'name': 'Somerset Community College', 'code': 'SCC'},
    {'id': 86753113, 'name': 'Southcentral Kentucky Community and Technical College', 'code': 'SKYCTC'},
    {'id': 86753114, 'name': 'Southeast Kentucky Community and Technical College', 'code': 'SEKCTC'},
    {'id': 86753115, 'name': 'West Kentucky Community and Technical College', 'code': 'WKCTC'},
]

# Target student counts per campus (totaling ~30k)
CAMPUS_STUDENT_TARGETS = {
    86753100: 1500,   # Ashland
    86753101: 1400,   # Big Sandy
    86753102: 3500,   # Bluegrass (largest - Lexington area)
    86753103: 2200,   # Elizabethtown
    86753104: 2000,   # Gateway
    86753105: 1300,   # Hazard
    86753106: 1600,   # Henderson
    86753107: 1500,   # Hopkinsville
    86753108: 4500,   # Jefferson (largest - Louisville area)
    86753109: 1400,   # Madisonville
    86753110: 1200,   # Maysville
    86753111: 2000,   # Owensboro
    86753112: 1600,   # Somerset
    86753113: 1800,   # Southcentral
    86753114: 1500,   # Southeast
    86753115: 2000,   # West Kentucky
}  # Total: 30,000


def delete_existing_kentucky_data(cursor):
    """Delete all existing Kentucky data from fact tables (both old system and new campuses)."""
    print("Deleting existing Kentucky data...")
    
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
    
    return cohort_deleted, course_deleted, financial_deleted


def create_institution_table(cursor):
    """Create the institution dimension table."""
    print("\nCreating institution table...")
    
    create_table_sql = """
    CREATE TABLE IF NOT EXISTS institution (
        Institution_ID BIGINT(20) NOT NULL PRIMARY KEY,
        Name VARCHAR(255) NOT NULL,
        Code VARCHAR(50),
        Institution_Type ENUM('system', 'institution') NOT NULL DEFAULT 'institution',
        Parent_Institution_ID BIGINT(20) NULL,
        State VARCHAR(50),
        Active BOOLEAN DEFAULT TRUE,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
        
        INDEX idx_parent_institution (Parent_Institution_ID),
        INDEX idx_institution_type (Institution_Type)
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
    """
    
    cursor.execute(create_table_sql)
    print("  ✓ Institution table created")


def insert_kentucky_hierarchy(cursor):
    """Insert Kentucky system and 16 child campuses."""
    print("\nInserting Kentucky institution hierarchy...")
    
    # Insert parent system
    insert_sql = """
    INSERT INTO institution (
        Institution_ID, Name, Code, Institution_Type, Parent_Institution_ID, State
    ) VALUES (
        %s, %s, %s, %s, %s, %s
    )
    ON DUPLICATE KEY UPDATE
        Name = VALUES(Name),
        Code = VALUES(Code),
        Institution_Type = VALUES(Institution_Type),
        State = VALUES(State)
    """
    
    cursor.execute(insert_sql, (
        KENTUCKY_SYSTEM_ID,
        'Kentucky Community and Technical College System',
        'KCTCS',
        'system',
        None,
        'Kentucky'
    ))
    print(f"  ✓ Kentucky system parent (ID: {KENTUCKY_SYSTEM_ID})")
    
    # Insert 16 child campuses
    for campus in KENTUCKY_CAMPUSES:
        cursor.execute(insert_sql, (
            campus['id'],
            campus['name'],
            campus['code'],
            'institution',
            KENTUCKY_SYSTEM_ID,
            'Kentucky'
        ))
    print(f"  ✓ All 16 child campuses inserted")


def generate_student_guid():
    """Generate a random student GUID."""
    return f"KY-{random.randint(100000, 999999)}-{random.randint(1000, 9999)}"


def generate_student_data(campus_id, num_students):
    """Generate complete student data (cohort, courses, financial aid) for a campus."""
    cohorts = ['2020', '2021', '2022', '2023', '2024']
    terms = ['Fall', 'Spring', 'Summer']
    races = ['White', 'Black or African American', 'Hispanic/Latino', 'Asian', 'Two or more races']
    genders = ['Male', 'Female', 'Non-binary']
    ethnicities = ['Hispanic or Latino', 'Not Hispanic or Latino']
    
    # Course data
    course_prefixes = ['ENG', 'MATH', 'HIST', 'BIO', 'CHEM', 'PSY', 'SOC', 'ART', 'MUS', 'PE']
    course_names = {
        'ENG': ['English Composition I', 'English Composition II', 'Literature'],
        'MATH': ['College Algebra', 'Calculus I', 'Statistics'],
        'HIST': ['US History I', 'US History II', 'World History'],
        'BIO': ['General Biology', 'Anatomy & Physiology', 'Microbiology'],
        'CHEM': ['General Chemistry', 'Organic Chemistry', 'Biochemistry'],
        'PSY': ['Introduction to Psychology', 'Developmental Psychology', 'Abnormal Psychology'],
        'SOC': ['Introduction to Sociology', 'Social Problems', 'Cultural Anthropology'],
        'ART': ['Art Appreciation', 'Drawing I', 'Painting I'],
        'MUS': ['Music Appreciation', 'Music Theory', 'Applied Music'],
        'PE': ['Physical Education', 'Wellness', 'Team Sports']
    }
    grades = ['A', 'A-', 'B+', 'B', 'B-', 'C+', 'C', 'C-', 'D', 'F', 'W']
    
    students_data = {
        'cohort': [],
        'courses': [],
        'financial_aid': []
    }
    
    for i in range(num_students):
        # Generate consistent student info
        student_guid = generate_student_guid()
        student_id = random.randint(100000, 999999)
        cohort_year = random.choice(cohorts)
        cohort_term = random.choice(terms)
        academic_year = f"{cohort_year}-{int(cohort_year)+1}"
        age = random.randint(18, 45)
        race = random.choice(races)
        ethnicity = random.choice(ethnicities)
        gender = random.choice(genders)
        first_name = f"Student{i}"
        last_name = f"LastName{i}"
        
        # Cohort record
        cohort_record = {
            'Institution_ID': campus_id,
            'Cohort': cohort_year,
            'Student_GUID': student_guid,
            'Cohort_Term': cohort_term,
            'Student_Age': age,
            'Race': race,
            'Ethnicity': ethnicity,
            'Gender': gender,
            'Enrollment_Type': random.choice(['First-time', 'Transfer', 'Continuing']),
            'Pell_Status_First_Year': random.choice(['Yes', 'No']),
            'GPA_Group_Year_1': round(random.uniform(2.0, 4.0), 2),
            'Retention': random.choice([0, 1]),
            'Persistence': random.choice([0, 1]),
            'school': 'KY',
            'dataset_type': 'S',
            'created_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }
        students_data['cohort'].append(cohort_record)
        
        # Generate 3-6 course records per student
        num_courses = random.randint(3, 6)
        for _ in range(num_courses):
            prefix = random.choice(course_prefixes)
            course_number = random.randint(100, 499)
            section_id = random.randint(1, 20)
            course_name = random.choice(course_names[prefix])
            credits = random.choice([3, 4])
            grade = random.choice(grades)
            credits_earned = credits if grade not in ['F', 'W'] else 0
            
            course_record = {
                'Student_GUID': student_guid,
                'Student_Age': age,
                'Race': race,
                'Ethnicity': ethnicity,
                'Gender': gender,
                'Institution_ID': campus_id,
                'Cohort': cohort_year,
                'Cohort_Term': cohort_term,
                'Academic_Year': academic_year,
                'Academic_Term': random.choice(terms),
                'Course_Prefix': prefix,
                'Course_Number': course_number,
                'Section_ID': section_id,
                'Course_Name': course_name,
                'Course_Type': random.choice(['Core', 'Elective', 'Major']),
                'Grade': grade,
                'Number_of_Credits_Attempted': credits,
                'Number_of_Credits_Earned': credits_earned,
                'Delivery_Method': random.choice(['In-Person', 'Online', 'Hybrid']),
                'school': 'KY',
                'dataset_type': 'S',
                'created_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            }
            students_data['courses'].append(course_record)
        
        # Financial aid record (not all students have financial aid)
        if random.random() < 0.7:  # 70% of students have financial aid
            cost_of_attendance = random.randint(8000, 15000)
            efc = random.randint(0, 10000)
            total_grants = random.randint(2000, 8000)
            unmet_need = max(0, cost_of_attendance - efc - total_grants)
            net_price = cost_of_attendance - total_grants
            
            financial_record = {
                'Student_ID': student_id,
                'Institution_ID': campus_id,
                'Cohort': cohort_year,
                'Cohort_Term': cohort_term,
                'Academic_Year': academic_year,
                'First_Name': first_name,
                'Last_Name': last_name,
                'Student_Age': age,
                'Dependency_Status': random.choice(['Dependent', 'Independent']),
                'Housing_Status': random.choice(['On-Campus', 'Off-Campus', 'With Parents']),
                'Cost_of_Attendance': cost_of_attendance,
                'EFC': efc,
                'Total_Institutional_Grants': random.randint(0, 3000),
                'Total_State_Grants': random.randint(0, 2000),
                'Total_Federal_Grants': random.randint(1000, 6000),
                'Unmet_Need': unmet_need,
                'Net_Price': net_price,
                'Applied_Aid': random.choice(['Yes', 'No']),
                'school': 'KY',
                'dataset_type': 'S',
                'created_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            }
            students_data['financial_aid'].append(financial_record)
    
    return students_data


def insert_campus_data(cursor, campus_id, campus_name, num_students):
    """Insert cohort, course, and financial aid data for a campus."""
    print(f"  Generating {num_students} students for {campus_name}...")
    
    # Generate all data for this campus
    data = generate_student_data(campus_id, num_students)
    
    # Insert cohort records
    cohort_sql = """
    INSERT INTO cohort (
        Institution_ID, Cohort, Student_GUID, Cohort_Term, Student_Age,
        Race, Ethnicity, Gender, Enrollment_Type, Pell_Status_First_Year,
        GPA_Group_Year_1, Retention, Persistence, school, dataset_type, created_at
    ) VALUES (
        %(Institution_ID)s, %(Cohort)s, %(Student_GUID)s, %(Cohort_Term)s, %(Student_Age)s,
        %(Race)s, %(Ethnicity)s, %(Gender)s, %(Enrollment_Type)s, %(Pell_Status_First_Year)s,
        %(GPA_Group_Year_1)s, %(Retention)s, %(Persistence)s, %(school)s, %(dataset_type)s, %(created_at)s
    )
    """
    cursor.executemany(cohort_sql, data['cohort'])
    print(f"    ✓ Inserted {len(data['cohort'])} cohort records")
    
    # Insert course records
    course_sql = """
    INSERT INTO course (
        Student_GUID, Student_Age, Race, Ethnicity, Gender,
        Institution_ID, Cohort, Cohort_Term, Academic_Year, Academic_Term,
        Course_Prefix, Course_Number, Section_ID, Course_Name, Course_Type,
        Grade, Number_of_Credits_Attempted, Number_of_Credits_Earned,
        Delivery_Method, school, dataset_type, created_at
    ) VALUES (
        %(Student_GUID)s, %(Student_Age)s, %(Race)s, %(Ethnicity)s, %(Gender)s,
        %(Institution_ID)s, %(Cohort)s, %(Cohort_Term)s, %(Academic_Year)s, %(Academic_Term)s,
        %(Course_Prefix)s, %(Course_Number)s, %(Section_ID)s, %(Course_Name)s, %(Course_Type)s,
        %(Grade)s, %(Number_of_Credits_Attempted)s, %(Number_of_Credits_Earned)s,
        %(Delivery_Method)s, %(school)s, %(dataset_type)s, %(created_at)s
    )
    """
    cursor.executemany(course_sql, data['courses'])
    print(f"    ✓ Inserted {len(data['courses'])} course records")
    
    # Insert financial aid records
    if data['financial_aid']:
        financial_sql = """
        INSERT INTO financial_aid (
            Student_ID, Institution_ID, Cohort, Cohort_Term, Academic_Year,
            First_Name, Last_Name, Student_Age,
            Dependency_Status, Housing_Status,
            Cost_of_Attendance, EFC, Total_Institutional_Grants, Total_State_Grants,
            Total_Federal_Grants, Unmet_Need, Net_Price, Applied_Aid,
            school, dataset_type, created_at
        ) VALUES (
            %(Student_ID)s, %(Institution_ID)s, %(Cohort)s, %(Cohort_Term)s, %(Academic_Year)s,
            %(First_Name)s, %(Last_Name)s, %(Student_Age)s,
            %(Dependency_Status)s, %(Housing_Status)s,
            %(Cost_of_Attendance)s, %(EFC)s, %(Total_Institutional_Grants)s, %(Total_State_Grants)s,
            %(Total_Federal_Grants)s, %(Unmet_Need)s, %(Net_Price)s, %(Applied_Aid)s,
            %(school)s, %(dataset_type)s, %(created_at)s
        )
        """
        cursor.executemany(financial_sql, data['financial_aid'])
        print(f"    ✓ Inserted {len(data['financial_aid'])} financial aid records")
    
    return {
        'students': len(data['cohort']),
        'courses': len(data['courses']),
        'financial_aid': len(data['financial_aid'])
    }


def generate_all_data(cursor):
    """Generate data for all 16 campuses."""
    print("\nGenerating synthetic data for all campuses...")
    
    totals = {
        'students': 0,
        'courses': 0,
        'financial_aid': 0
    }
    
    for campus in KENTUCKY_CAMPUSES:
        campus_id = campus['id']
        campus_name = campus['name']
        num_students = CAMPUS_STUDENT_TARGETS[campus_id]
        
        stats = insert_campus_data(cursor, campus_id, campus_name, num_students)
        totals['students'] += stats['students']
        totals['courses'] += stats['courses']
        totals['financial_aid'] += stats['financial_aid']
    
    print(f"\n✓ Total records generated:")
    print(f"  - Students: {totals['students']}")
    print(f"  - Course enrollments: {totals['courses']}")
    print(f"  - Financial aid records: {totals['financial_aid']}")
    
    return totals


def create_views(cursor):
    """Create views for system-level reporting."""
    print("\nCreating reporting views...")
    
    # Institution hierarchy view
    view_hierarchy_sql = """
    CREATE OR REPLACE VIEW v_institution_hierarchy AS
    SELECT 
        i.Institution_ID,
        i.Name AS Institution_Name,
        i.Code AS Institution_Code,
        i.Institution_Type,
        i.State,
        i.Parent_Institution_ID,
        p.Name AS System_Name,
        p.Code AS System_Code,
        COALESCE(p.Institution_ID, i.Institution_ID) AS Reporting_Institution_ID,
        COALESCE(p.Name, i.Name) AS Reporting_Institution_Name
    FROM institution i
    LEFT JOIN institution p ON i.Parent_Institution_ID = p.Institution_ID
    """
    cursor.execute(view_hierarchy_sql)
    print("  ✓ v_institution_hierarchy created")
    
    # Cohort with system view
    view_cohort_sql = """
    CREATE OR REPLACE VIEW v_cohort_with_system AS
    SELECT 
        c.*,
        ih.Institution_Name,
        ih.System_Name,
        ih.System_Code,
        ih.Reporting_Institution_ID,
        ih.Reporting_Institution_Name
    FROM cohort c
    LEFT JOIN v_institution_hierarchy ih ON c.Institution_ID = ih.Institution_ID
    """
    cursor.execute(view_cohort_sql)
    print("  ✓ v_cohort_with_system created")
    
    # Course with system view
    view_course_sql = """
    CREATE OR REPLACE VIEW v_course_with_system AS
    SELECT 
        cr.*,
        ih.Institution_Name,
        ih.System_Name,
        ih.System_Code,
        ih.Reporting_Institution_ID,
        ih.Reporting_Institution_Name
    FROM course cr
    LEFT JOIN v_institution_hierarchy ih ON cr.Institution_ID = ih.Institution_ID
    """
    cursor.execute(view_course_sql)
    print("  ✓ v_course_with_system created")
    
    # Financial aid with system view
    view_financial_aid_sql = """
    CREATE OR REPLACE VIEW v_financial_aid_with_system AS
    SELECT 
        fa.*,
        ih.Institution_Name,
        ih.System_Name,
        ih.System_Code,
        ih.Reporting_Institution_ID,
        ih.Reporting_Institution_Name
    FROM financial_aid fa
    LEFT JOIN v_institution_hierarchy ih ON fa.Institution_ID = ih.Institution_ID
    """
    cursor.execute(view_financial_aid_sql)
    print("  ✓ v_financial_aid_with_system created")


def verify_data(cursor):
    """Verify the generated data."""
    print("\n" + "="*60)
    print("VERIFICATION")
    print("="*60)
    
    # Check institution hierarchy
    cursor.execute("""
        SELECT 
            Institution_Type,
            COUNT(*) as Count
        FROM institution
        WHERE Institution_ID = %s OR Parent_Institution_ID = %s
        GROUP BY Institution_Type
    """, (KENTUCKY_SYSTEM_ID, KENTUCKY_SYSTEM_ID))
    
    print("\nInstitution hierarchy:")
    for row in cursor.fetchall():
        print(f"  {row[0]}: {row[1]}")
    
    # Check student distribution in cohort
    cursor.execute("""
        SELECT 
            i.Institution_ID,
            i.Name AS Campus_Name,
            COUNT(DISTINCT c.Student_GUID) AS Student_Count
        FROM cohort c
        JOIN institution i ON c.Institution_ID = i.Institution_ID
        WHERE i.Parent_Institution_ID = %s
        GROUP BY i.Institution_ID, i.Name
        ORDER BY Student_Count DESC
    """, (KENTUCKY_SYSTEM_ID,))
    
    print("\nStudent distribution across campuses (cohort table):")
    total_students = 0
    for row in cursor.fetchall():
        inst_id, campus_name, student_count = row
        total_students += student_count
        target = CAMPUS_STUDENT_TARGETS[inst_id]
        print(f"  {campus_name}: {student_count} students (target: {target})")
    
    print(f"\n✓ Total Kentucky students: {total_students}")
    
    # Check course enrollments
    cursor.execute("""
        SELECT COUNT(*) as course_count
        FROM course
        WHERE Institution_ID BETWEEN %s AND %s
    """, (KENTUCKY_CHILD_START_ID, KENTUCKY_CHILD_START_ID + 15))
    
    course_count = cursor.fetchone()[0]
    print(f"\n✓ Total course enrollments: {course_count}")
    
    # Check financial aid records
    cursor.execute("""
        SELECT COUNT(*) as financial_count
        FROM financial_aid
        WHERE Institution_ID BETWEEN %s AND %s
    """, (KENTUCKY_CHILD_START_ID, KENTUCKY_CHILD_START_ID + 15))
    
    financial_count = cursor.fetchone()[0]
    print(f"✓ Total financial aid records: {financial_count}")
    
    # Verify data consistency - check if Student_GUIDs match across tables
    cursor.execute("""
        SELECT 
            COUNT(DISTINCT c.Student_GUID) as cohort_students,
            COUNT(DISTINCT cr.Student_GUID) as course_students
        FROM cohort c
        LEFT JOIN course cr ON c.Student_GUID = cr.Student_GUID
        WHERE c.Institution_ID BETWEEN %s AND %s
    """, (KENTUCKY_CHILD_START_ID, KENTUCKY_CHILD_START_ID + 15))
    
    consistency = cursor.fetchone()
    print(f"\n✓ Data consistency check:")
    print(f"  - Unique students in cohort: {consistency[0]}")
    print(f"  - Unique students in courses: {consistency[1]}")
    
    print("="*60)


def run_regeneration(database='KY'):
    """Run the complete data regeneration."""
    print("="*60)
    print("KENTUCKY DATA REGENERATION WITH HIERARCHY")
    print("="*60)
    print(f"Database: {database}")
    print(f"Parent System ID: {KENTUCKY_SYSTEM_ID}")
    print(f"Child Campus IDs: {KENTUCKY_CHILD_START_ID} - {KENTUCKY_CHILD_START_ID + 15}")
    print(f"Target Students: {sum(CAMPUS_STUDENT_TARGETS.values())}")
    print("="*60 + "\n")
    
    # Get actual database name from acronym
    if database in DATABASES:
        db_name = DATABASES[database]
        print(f"Connecting to database: {db_name}\n")
    else:
        db_name = database
    
    try:
        with get_db_connection(db_name) as connection:
            cursor = connection.cursor()
            
            # Step 1: Delete existing data
            delete_existing_kentucky_data(cursor)
            
            # Step 2: Create institution table
            create_institution_table(cursor)
            
            # Step 3: Insert Kentucky hierarchy
            insert_kentucky_hierarchy(cursor)
            
            # Step 4: Generate new data
            generate_all_data(cursor)
            
            # Step 5: Create views
            create_views(cursor)
            
            # Commit all changes
            connection.commit()
            print("\n✓ All changes committed")
            
            # Verify
            verify_data(cursor)
            
            print("\n" + "="*60)
            print("REGENERATION COMPLETED SUCCESSFULLY")
            print("="*60)
        
    except Exception as e:
        print(f"\n✗ Error occurred: {e}")
        print("Changes have been rolled back automatically.")
        import traceback
        traceback.print_exc()
        raise


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description='Regenerate Kentucky data with institution hierarchy')
    parser.add_argument(
        '--database',
        default='KY',
        help='Database to run regeneration on (default: KY)'
    )
    parser.add_argument(
        '--dry-run',
        action='store_true',
        help='Print what would be done without making changes'
    )
    parser.add_argument(
        '--yes',
        action='store_true',
        help='Skip confirmation prompt and proceed automatically'
    )
    
    args = parser.parse_args()
    
    if args.dry_run:
        print("DRY RUN MODE - No changes will be made")
        print("\nThis script will:")
        print("1. Delete all existing Kentucky data (Institution_ID = 86753094)")
        print("2. Create institution dimension table")
        print("3. Insert Kentucky system parent + 16 child campuses")
        print("4. Generate ~30,000 new synthetic students distributed across campuses")
        print("5. Create reporting views")
        print("\nCampus distribution:")
        for campus in KENTUCKY_CAMPUSES:
            target = CAMPUS_STUDENT_TARGETS[campus['id']]
            print(f"  {campus['name']}: {target} students")
        print(f"\nTotal: {sum(CAMPUS_STUDENT_TARGETS.values())} students")
    else:
        if args.yes:
            run_regeneration(args.database)
        else:
            confirm = input(f"\n⚠️  WARNING: This will DELETE all existing Kentucky data and regenerate it.\nContinue with database '{args.database}'? (yes/no): ")
            if confirm.lower() == 'yes':
                run_regeneration(args.database)
            else:
                print("Regeneration cancelled")
