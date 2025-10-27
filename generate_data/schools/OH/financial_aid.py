"""
Financial Aid data generation for University of Akron (OH)
"""
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))

from schools.shared.config import get_db_connection, add_school_column_if_not_exists, SCHOOLS
import random
from typing import List, Dict
from decimal import Decimal

SCHOOL_CODE = "OH"
SCHOOL_INFO = SCHOOLS[SCHOOL_CODE]

def generate_financial_aid_data(num_records: int = 100) -> List[Dict]:
    """Generate synthetic financial aid data for OH."""
    print(f"Generating {num_records} financial aid records for {SCHOOL_INFO['name']}...")
    
    aid_types = [
        "Pell Grant", "Federal Direct Loan", "State Grant", "Institutional Grant",
        "Work Study", "Scholarship", "SEOG", "Parent PLUS Loan", "Private Loan",
        "Merit Scholarship", "Need-based Grant", "Athletic Scholarship"
    ]
    
    semesters = ["Fall", "Spring", "Summer", "Winter"]
    academic_years = ["2020-21", "2021-22", "2022-23", "2023-24", "2024-25", "2025-26"]
    
    synthetic_data = []
    
    for i in range(num_records):
        student_id = f"{SCHOOL_INFO['acronym']}{random.randint(100000, 999999)}"
        
        aid_type = random.choice(aid_types)
        
        if "Grant" in aid_type or "Scholarship" in aid_type:
            amount = round(random.uniform(500, 6000), 2)
        elif "Loan" in aid_type:
            amount = round(random.uniform(1000, 12000), 2)
        elif "Work Study" in aid_type:
            amount = round(random.uniform(800, 3000), 2)
        else:
            amount = round(random.uniform(300, 5000), 2)
        
        financial_aid = {
            'student_id': student_id,
            'aid_type': aid_type,
            'amount': Decimal(str(amount)),
            'semester': random.choice(semesters),
            'academic_year': random.choice(academic_years)
        }
        
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
        print(f"[OK] Inserted {len(financial_aid_data)} financial aid records for {SCHOOL_INFO['acronym']}")
        
    except Exception as e:
        print(f"[ERROR] Error inserting financial aid data: {e}")
        connection.rollback()
    finally:
        cursor.close()

def main():
    """Main function to generate financial aid data for OH."""
    print(f"\n{'='*60}")
    print(f"Financial Aid Data Generation - {SCHOOL_INFO['name']}")
    print(f"{'='*60}\n")
    
    synthetic_data = generate_financial_aid_data(num_records=100)
    
    connection = get_db_connection(SCHOOL_INFO['dbname'])
    if not connection:
        print(f"[ERROR] Could not connect to database: {SCHOOL_INFO['dbname']}")
        return
    
    try:
        add_school_column_if_not_exists(connection, 'financial_aid')
        insert_financial_aid_data(connection, synthetic_data)
        print(f"\n[OK] Successfully populated {SCHOOL_INFO['acronym']} financial aid table")
    finally:
        connection.close()

if __name__ == "__main__":
    main()
