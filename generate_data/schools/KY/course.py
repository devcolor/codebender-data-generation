"""
Course data generation for Thomas More University (KY)
"""
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))

from schools.shared.config import get_db_connection, add_school_column_if_not_exists, SCHOOLS
import random
from typing import List, Dict

SCHOOL_CODE = "KY"
SCHOOL_INFO = SCHOOLS[SCHOOL_CODE]

def generate_course_data(num_records: int = 200) -> List[Dict]:
    """Generate synthetic course data for KY."""
    print(f"Generating {num_records} course records for {SCHOOL_INFO['name']}...")
    
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
        
        course = {
            'course_code': f"{code_prefix}{course_num}",
            'course_title': f"{title_prefix} {subject}",
            'credits': random.randint(1, 4),
            'department': random.choice(sample_subjects),
            'prerequisites': random.choice(['', f"{code_prefix}{random.randint(100, 299)}", 'None']),
            'description': f"This course covers {subject.lower()} concepts and applications."
        }
        
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
                course.get('course_code', f"COURSE{random.randint(100, 999)}"),
                course.get('course_title', course.get('title', 'Unknown Course')),
                course.get('credits', random.randint(1, 4)),
                course.get('description', ''),
                SCHOOL_INFO['acronym']
            )
            cursor.execute(insert_sql, values)
        
        connection.commit()
        print(f"[OK] Inserted {len(course_data)} course records for {SCHOOL_INFO['acronym']}")
        
    except Exception as e:
        print(f"[ERROR] Error inserting course data: {e}")
        connection.rollback()
    finally:
        cursor.close()

def main():
    """Main function to generate course data for KY."""
    print(f"\n{'='*60}")
    print(f"Course Data Generation - {SCHOOL_INFO['name']}")
    print(f"{'='*60}\n")
    
    synthetic_data = generate_course_data(num_records=200)
    
    connection = get_db_connection(SCHOOL_INFO['dbname'])
    if not connection:
        print(f"[ERROR] Could not connect to database: {SCHOOL_INFO['dbname']}")
        return
    
    try:
        add_school_column_if_not_exists(connection, 'course')
        insert_course_data(connection, synthetic_data)
        print(f"\n[OK] Successfully populated {SCHOOL_INFO['acronym']} course table")
    finally:
        connection.close()

if __name__ == "__main__":
    main()
