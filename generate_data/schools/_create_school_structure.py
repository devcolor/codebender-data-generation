"""
Helper script to create school-specific generation scripts for all remaining schools.
This creates the folder structure and scripts for CSUSB, KCTCS, KY, and OH.
"""
import os

# School configurations (excluding AL which is already created)
SCHOOLS_TO_CREATE = [
    {"code": "CSUSB", "name": "California State University San Bernardino"},
    {"code": "KCTCS", "name": "Kentucky Community and Technical College System"},
    {"code": "KY", "name": "Thomas More University"},
    {"code": "OH", "name": "University of Akron"}
]

# Template for cohort.py
COHORT_TEMPLATE = '''"""
Cohort data generation for {school_name} ({school_code})
"""
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))

from schools.shared.config import get_db_connection, add_school_column_if_not_exists, SCHOOLS
import random
from typing import List, Dict
from datetime import datetime

SCHOOL_CODE = "{school_code}"
SCHOOL_INFO = SCHOOLS[SCHOOL_CODE]

def generate_cohort_data(num_records: int = 50) -> List[Dict]:
    """Generate synthetic cohort data for {school_code}."""
    print(f"Generating {{num_records}} cohort records for {{SCHOOL_INFO['name']}}...")
    
    # Cohort name patterns
    cohort_types = ["Fall", "Spring", "Summer", "Winter"]
    years = list(range(2020, 2026))
    programs = ["Engineering", "Business", "Liberal Arts", "Sciences", "Nursing", "Education"]
    
    synthetic_data = []
    
    for i in range(num_records):
        cohort_type = random.choice(cohort_types)
        year = random.choice(years)
        program = random.choice(programs)
        
        # Generate start and end dates
        if cohort_type == "Fall":
            start_month, start_day = 8, random.randint(15, 31)
            end_month, end_day = 12, random.randint(15, 20)
        elif cohort_type == "Spring":
            start_month, start_day = 1, random.randint(15, 31)
            end_month, end_day = 5, random.randint(15, 31)
        elif cohort_type == "Summer":
            start_month, start_day = 6, random.randint(1, 15)
            end_month, end_day = 8, random.randint(1, 15)
        else:  # Winter
            start_month, start_day = 12, random.randint(15, 31)
            end_month, end_day = 1, random.randint(15, 31)
            if end_month == 1:
                year += 1
        
        start_date = datetime(year, start_month, start_day)
        end_date = datetime(year, end_month, end_day)
        
        cohort = {{
            'name': f"{{cohort_type}} {{year}} {{program}} Cohort",
            'start_date': start_date.strftime('%Y-%m-%d'),
            'end_date': end_date.strftime('%Y-%m-%d')
        }}
        
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
        print(f"✓ Inserted {{len(cohort_data)}} cohort records for {{SCHOOL_INFO['acronym']}}")
        
    except Exception as e:
        print(f"✗ Error inserting cohort data: {{e}}")
        connection.rollback()
    finally:
        cursor.close()

def main():
    """Main function to generate cohort data for {school_code}."""
    print(f"\\n{{'='*60}}")
    print(f"Cohort Data Generation - {{SCHOOL_INFO['name']}}")
    print(f"{{'='*60}}\\n")
    
    # Generate data
    synthetic_data = generate_cohort_data(num_records=50)
    
    # Connect to database
    connection = get_db_connection(SCHOOL_INFO['dbname'])
    if not connection:
        print(f"✗ Could not connect to database: {{SCHOOL_INFO['dbname']}}")
        return
    
    try:
        # Add school column if needed
        add_school_column_if_not_exists(connection, 'cohort')
        
        # Insert data
        insert_cohort_data(connection, synthetic_data)
        
        print(f"\\n✓ Successfully populated {{SCHOOL_INFO['acronym']}} cohort table")
        
    finally:
        connection.close()

if __name__ == "__main__":
    main()
'''

# Template for course.py
COURSE_TEMPLATE = '''"""
Course data generation for {school_name} ({school_code})
"""
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))

from schools.shared.config import get_db_connection, add_school_column_if_not_exists, SCHOOLS
import random
from typing import List, Dict

SCHOOL_CODE = "{school_code}"
SCHOOL_INFO = SCHOOLS[SCHOOL_CODE]

def generate_course_data(num_records: int = 200) -> List[Dict]:
    """Generate synthetic course data for {school_code}."""
    print(f"Generating {{num_records}} course records for {{SCHOOL_INFO['name']}}...")
    
    # Course generation patterns
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
        print(f"✓ Inserted {{len(course_data)}} course records for {{SCHOOL_INFO['acronym']}}")
        
    except Exception as e:
        print(f"✗ Error inserting course data: {{e}}")
        connection.rollback()
    finally:
        cursor.close()

def main():
    """Main function to generate course data for {school_code}."""
    print(f"\\n{{'='*60}}")
    print(f"Course Data Generation - {{SCHOOL_INFO['name']}}")
    print(f"{{'='*60}}\\n")
    
    # Generate data
    synthetic_data = generate_course_data(num_records=200)
    
    # Connect to database
    connection = get_db_connection(SCHOOL_INFO['dbname'])
    if not connection:
        print(f"✗ Could not connect to database: {{SCHOOL_INFO['dbname']}}")
        return
    
    try:
        # Add school column if needed
        add_school_column_if_not_exists(connection, 'course')
        
        # Insert data
        insert_course_data(connection, synthetic_data)
        
        print(f"\\n✓ Successfully populated {{SCHOOL_INFO['acronym']}} course table")
        
    finally:
        connection.close()

if __name__ == "__main__":
    main()
'''

# Template for financial_aid.py
FINANCIAL_AID_TEMPLATE = '''"""
Financial Aid data generation for {school_name} ({school_code})
"""
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))

from schools.shared.config import get_db_connection, add_school_column_if_not_exists, SCHOOLS
import random
from typing import List, Dict
from decimal import Decimal

SCHOOL_CODE = "{school_code}"
SCHOOL_INFO = SCHOOLS[SCHOOL_CODE]

def generate_financial_aid_data(num_records: int = 100) -> List[Dict]:
    """Generate synthetic financial aid data for {school_code}."""
    print(f"Generating {{num_records}} financial aid records for {{SCHOOL_INFO['name']}}...")
    
    # Financial aid types
    aid_types = [
        "Pell Grant", "Federal Direct Loan", "State Grant", "Institutional Grant",
        "Work Study", "Scholarship", "SEOG", "Parent PLUS Loan", "Private Loan",
        "Merit Scholarship", "Need-based Grant", "Athletic Scholarship"
    ]
    
    # Semesters and academic years
    semesters = ["Fall", "Spring", "Summer", "Winter"]
    academic_years = ["2020-21", "2021-22", "2022-23", "2023-24", "2024-25", "2025-26"]
    
    synthetic_data = []
    
    for i in range(num_records):
        # Generate student ID (format: school acronym + random number)
        student_id = f"{{SCHOOL_INFO['acronym']}}{{random.randint(100000, 999999)}}"
        
        # Select aid type and determine appropriate amount range
        aid_type = random.choice(aid_types)
        
        if "Grant" in aid_type or "Scholarship" in aid_type:
            # Grants and scholarships: $500 - $6000
            amount = round(random.uniform(500, 6000), 2)
        elif "Loan" in aid_type:
            # Loans: $1000 - $12000
            amount = round(random.uniform(1000, 12000), 2)
        elif "Work Study" in aid_type:
            # Work study: $800 - $3000
            amount = round(random.uniform(800, 3000), 2)
        else:
            # Other aid: $300 - $5000
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
        print(f"✓ Inserted {{len(financial_aid_data)}} financial aid records for {{SCHOOL_INFO['acronym']}}")
        
    except Exception as e:
        print(f"✗ Error inserting financial aid data: {{e}}")
        connection.rollback()
    finally:
        cursor.close()

def main():
    """Main function to generate financial aid data for {school_code}."""
    print(f"\\n{{'='*60}}")
    print(f"Financial Aid Data Generation - {{SCHOOL_INFO['name']}}")
    print(f"{{'='*60}}\\n")
    
    # Generate data
    synthetic_data = generate_financial_aid_data(num_records=100)
    
    # Connect to database
    connection = get_db_connection(SCHOOL_INFO['dbname'])
    if not connection:
        print(f"✗ Could not connect to database: {{SCHOOL_INFO['dbname']}}")
        return
    
    try:
        # Add school column if needed
        add_school_column_if_not_exists(connection, 'financial_aid')
        
        # Insert data
        insert_financial_aid_data(connection, synthetic_data)
        
        print(f"\\n✓ Successfully populated {{SCHOOL_INFO['acronym']}} financial aid table")
        
    finally:
        connection.close()

if __name__ == "__main__":
    main()
'''

# Template for generate_all.py
GENERATE_ALL_TEMPLATE = '''"""
Generate all data types for {school_name} ({school_code})
"""
import cohort
import course
import financial_aid

def main():
    """Run all data generation scripts for {school_code}."""
    print("\\n" + "="*70)
    print("GENERATING ALL DATA FOR {school_name_upper} ({school_code})")
    print("="*70)
    
    # Generate cohort data
    cohort.main()
    
    # Generate course data
    course.main()
    
    # Generate financial aid data
    financial_aid.main()
    
    print("\\n" + "="*70)
    print("✓ ALL DATA GENERATION COMPLETED FOR {school_code}")
    print("="*70 + "\\n")

if __name__ == "__main__":
    main()
'''

def create_school_files(school_code, school_name):
    """Create all files for a specific school."""
    # Create school directory
    school_dir = os.path.join(os.path.dirname(__file__), school_code)
    os.makedirs(school_dir, exist_ok=True)
    
    # Create cohort.py
    with open(os.path.join(school_dir, 'cohort.py'), 'w') as f:
        f.write(COHORT_TEMPLATE.format(school_code=school_code, school_name=school_name))
    
    # Create course.py
    with open(os.path.join(school_dir, 'course.py'), 'w') as f:
        f.write(COURSE_TEMPLATE.format(school_code=school_code, school_name=school_name))
    
    # Create financial_aid.py
    with open(os.path.join(school_dir, 'financial_aid.py'), 'w') as f:
        f.write(FINANCIAL_AID_TEMPLATE.format(school_code=school_code, school_name=school_name))
    
    # Create generate_all.py
    with open(os.path.join(school_dir, 'generate_all.py'), 'w') as f:
        f.write(GENERATE_ALL_TEMPLATE.format(
            school_code=school_code, 
            school_name=school_name,
            school_name_upper=school_name.upper()
        ))
    
    print(f"✓ Created files for {school_code} - {school_name}")

def main():
    """Create all school directories and files."""
    print("Creating school-specific generation scripts...")
    print("="*70)
    
    for school in SCHOOLS_TO_CREATE:
        create_school_files(school['code'], school['name'])
    
    print("="*70)
    print("✓ All school structures created successfully!")

if __name__ == "__main__":
    main()
