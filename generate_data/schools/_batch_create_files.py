"""
Batch create all remaining school files (KCTCS, KY, OH)
"""
import os

# School configurations
SCHOOLS_CONFIG = [
    {"code": "KCTCS", "name": "Kentucky Community and Technical College System"},
    {"code": "KY", "name": "Thomas More University"},
    {"code": "OH", "name": "University of Akron"}
]

# Base templates without special characters
COURSE_TEMPLATE = '''"""
Course data generation for {name} ({code})
"""
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))

from schools.shared.config import get_db_connection, add_school_column_if_not_exists, SCHOOLS
import random
from typing import List, Dict

SCHOOL_CODE = "{code}"
SCHOOL_INFO = SCHOOLS[SCHOOL_CODE]

def generate_course_data(num_records: int = 200) -> List[Dict]:
    """Generate synthetic course data for {code}."""
    print(f"Generating {{num_records}} course records for {{SCHOOL_INFO['name']}}...")
    
    sample_codes = ["MATH", "ENG", "SCI", "HIST", "ART", "BUS", "CS", "PHYS", "CHEM", "BIO"]
    sample_titles = [
        "Introduction to", "Advanced", "Principles of", "Fundamentals of",
        "Applied", "Modern", "Classical", "Contemporary", "Research in"
    ]
    sample_subjects = [
        "Mathematics", "English", "Science", "History", "Art", "Business",
        "Computer Science", "Physics", "Chemistry", "Biology", "Psychology",
        "Sociology", "Economics", "Philosophy", "Literature"
    ]
    
    synthetic_data = []
    
    for i in range(num_records):
        code_prefix = random.choice(sample_codes)
        course_num = random.randint(100, 499)
        title_prefix = random.choice(sample_titles)
        subject = random.choice(sample_subjects)
        
        course = {{
            'course_code': f"{{code_prefix}}{{course_num}}",
            'course_title': f"{{title_prefix}} {{subject}}",
            'credits': random.randint(1, 4),
            'department': random.choice(sample_subjects),
            'prerequisites': random.choice(['', f"{{code_prefix}}{{random.randint(100, 299)}}", 'None']),
            'description': f"This course covers {{subject.lower()}} concepts and applications."
        }}
        
        synthetic_data.append(course)
    
    return synthetic_data

def insert_course_data(connection, course_data: List[Dict]):
    """Insert course data into the database."""
    cursor = connection.cursor()
    
    insert_sql = """
    INSERT INTO course (code, title, credits, description, school)
    VALUES (%s, %s, %s, %s, %s)
    """
    
    try:
        for course in course_data:
            values = (
                course.get('course_code', f"COURSE{{random.randint(100, 999)}}"),
                course.get('course_title', course.get('title', 'Unknown Course')),
                course.get('credits', random.randint(1, 4)),
                course.get('description', ''),
                SCHOOL_INFO['acronym']
            )
            cursor.execute(insert_sql, values)
        
        connection.commit()
        print(f"[OK] Inserted {{len(course_data)}} course records for {{SCHOOL_INFO['acronym']}}")
        
    except Exception as e:
        print(f"[ERROR] Error inserting course data: {{e}}")
        connection.rollback()
    finally:
        cursor.close()

def main():
    """Main function to generate course data for {code}."""
    print(f"\\n{{'='*60}}")
    print(f"Course Data Generation - {{SCHOOL_INFO['name']}}")
    print(f"{{'='*60}}\\n")
    
    synthetic_data = generate_course_data(num_records=200)
    
    connection = get_db_connection(SCHOOL_INFO['dbname'])
    if not connection:
        print(f"[ERROR] Could not connect to database: {{SCHOOL_INFO['dbname']}}")
        return
    
    try:
        add_school_column_if_not_exists(connection, 'course')
        insert_course_data(connection, synthetic_data)
        print(f"\\n[OK] Successfully populated {{SCHOOL_INFO['acronym']}} course table")
    finally:
        connection.close()

if __name__ == "__main__":
    main()
'''

FINANCIAL_AID_TEMPLATE = '''"""
Financial Aid data generation for {name} ({code})
"""
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))

from schools.shared.config import get_db_connection, add_school_column_if_not_exists, SCHOOLS
import random
from typing import List, Dict
from decimal import Decimal

SCHOOL_CODE = "{code}"
SCHOOL_INFO = SCHOOLS[SCHOOL_CODE]

def generate_financial_aid_data(num_records: int = 100) -> List[Dict]:
    """Generate synthetic financial aid data for {code}."""
    print(f"Generating {{num_records}} financial aid records for {{SCHOOL_INFO['name']}}...")
    
    aid_types = [
        "Pell Grant", "Federal Direct Loan", "State Grant", "Institutional Grant",
        "Work Study", "Scholarship", "SEOG", "Parent PLUS Loan", "Private Loan",
        "Merit Scholarship", "Need-based Grant", "Athletic Scholarship"
    ]
    
    semesters = ["Fall", "Spring", "Summer", "Winter"]
    academic_years = ["2020-21", "2021-22", "2022-23", "2023-24", "2024-25", "2025-26"]
    
    synthetic_data = []
    
    for i in range(num_records):
        student_id = f"{{SCHOOL_INFO['acronym']}}{{random.randint(100000, 999999)}}"
        
        aid_type = random.choice(aid_types)
        
        if "Grant" in aid_type or "Scholarship" in aid_type:
            amount = round(random.uniform(500, 6000), 2)
        elif "Loan" in aid_type:
            amount = round(random.uniform(1000, 12000), 2)
        elif "Work Study" in aid_type:
            amount = round(random.uniform(800, 3000), 2)
        else:
            amount = round(random.uniform(300, 5000), 2)
        
        financial_aid = {{
            'student_id': student_id,
            'aid_type': aid_type,
            'amount': Decimal(str(amount)),
            'semester': random.choice(semesters),
            'academic_year': random.choice(academic_years)
        }}
        
        synthetic_data.append(financial_aid)
    
    return synthetic_data

def insert_financial_aid_data(connection, financial_aid_data: List[Dict]):
    """Insert financial aid data into the database."""
    cursor = connection.cursor()
    
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
                SCHOOL_INFO['acronym']
            )
            cursor.execute(insert_sql, values)
        
        connection.commit()
        print(f"[OK] Inserted {{len(financial_aid_data)}} financial aid records for {{SCHOOL_INFO['acronym']}}")
        
    except Exception as e:
        print(f"[ERROR] Error inserting financial aid data: {{e}}")
        connection.rollback()
    finally:
        cursor.close()

def main():
    """Main function to generate financial aid data for {code}."""
    print(f"\\n{{'='*60}}")
    print(f"Financial Aid Data Generation - {{SCHOOL_INFO['name']}}")
    print(f"{{'='*60}}\\n")
    
    synthetic_data = generate_financial_aid_data(num_records=100)
    
    connection = get_db_connection(SCHOOL_INFO['dbname'])
    if not connection:
        print(f"[ERROR] Could not connect to database: {{SCHOOL_INFO['dbname']}}")
        return
    
    try:
        add_school_column_if_not_exists(connection, 'financial_aid')
        insert_financial_aid_data(connection, synthetic_data)
        print(f"\\n[OK] Successfully populated {{SCHOOL_INFO['acronym']}} financial aid table")
    finally:
        connection.close()

if __name__ == "__main__":
    main()
'''

GENERATE_ALL_TEMPLATE = '''"""
Generate all data types for {name} ({code})
"""
import cohort
import course
import financial_aid

def main():
    """Run all data generation scripts for {code}."""
    print("\\n" + "="*70)
    print("GENERATING ALL DATA FOR {name_upper} ({code})")
    print("="*70)
    
    cohort.main()
    course.main()
    financial_aid.main()
    
    print("\\n" + "="*70)
    print("[OK] ALL DATA GENERATION COMPLETED FOR {code}")
    print("="*70 + "\\n")

if __name__ == "__main__":
    main()
'''

def create_files_for_school(school_code, school_name):
    """Create all files for a school."""
    base_dir = os.path.dirname(__file__)
    school_dir = os.path.join(base_dir, school_code)
    
    # Create course.py
    with open(os.path.join(school_dir, 'course.py'), 'w', encoding='utf-8') as f:
        f.write(COURSE_TEMPLATE.format(code=school_code, name=school_name))
    
    # Create financial_aid.py
    with open(os.path.join(school_dir, 'financial_aid.py'), 'w', encoding='utf-8') as f:
        f.write(FINANCIAL_AID_TEMPLATE.format(code=school_code, name=school_name))
    
    # Create generate_all.py
    with open(os.path.join(school_dir, 'generate_all.py'), 'w', encoding='utf-8') as f:
        f.write(GENERATE_ALL_TEMPLATE.format(code=school_code, name=school_name, name_upper=school_name.upper()))
    
    print(f"Created files for {school_code}")

def main():
    """Create all files for remaining schools."""
    for school in SCHOOLS_CONFIG:
        create_files_for_school(school['code'], school['name'])
    print("All files created successfully!")

if __name__ == "__main__":
    main()
