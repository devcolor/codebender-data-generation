"""
Analysis Ready All data generation for Bishop State Community College (AL)
Populates analysis_ready_all table with AR fields not in cohort, using student IDs from cohort table
"""
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))

from schools.shared.config import get_db_connection, add_school_column_if_not_exists, SCHOOLS
import pandas as pd
import random
from typing import List, Dict

SCHOOL_CODE = "AL"
SCHOOL_INFO = SCHOOLS[SCHOOL_CODE]
AR_TABLE_NAME = f"ar_{SCHOOL_CODE.lower()}"

# AR seed file path
AR_SEED_FILE = "data/seed_data01/cohort_AR_data_mock_A.csv"

def get_student_ids_from_cohort(connection) -> List[str]:
    """Get all student IDs from the cohort table for this school."""
    cursor = connection.cursor()
    try:
        query = "SELECT DISTINCT Student_GUID FROM cohort WHERE school = %s"
        cursor.execute(query, (SCHOOL_INFO['acronym'],))
        student_ids = [row[0] for row in cursor.fetchall()]
        return student_ids
    finally:
        cursor.close()

def load_ar_seed_data() -> pd.DataFrame:
    """Load AR seed data from CSV."""
    print(f"Loading AR seed data from {AR_SEED_FILE}...")
    df = pd.read_csv(AR_SEED_FILE)
    print(f"Loaded {len(df)} records from AR seed file")
    return df

def generate_analysis_ready_data(student_ids: List[str], ar_df: pd.DataFrame) -> List[Dict]:
    """
    Generate analysis_ready_all records for student IDs from cohort table.
    Uses AR seed data as reference for realistic values.
    """
    print(f"Generating analysis_ready_all records for {len(student_ids)} students...")
    
    synthetic_data = []
    
    # Column mapping from AR file to database fields
    ar_columns = {
        'Years to Bachelors at cohort inst.': 'years_to_bachelors_cohort',
        'Years to Associates or Certificate at cohort inst.': 'years_to_assoc_cert_cohort',
        'Years to Bachelor at other inst.': 'years_to_bachelor_other',
        'Years to Associates or Certificate at other inst.': 'years_to_assoc_cert_other',
        'NASPA First-Generation': 'naspa_first_gen',
        'First Year to Bachelors at cohort inst.': 'first_year_bachelors_cohort',
        'First Year to Associates or Certificate at cohort inst.': 'first_year_assoc_cert_cohort',
        'First Year to Bachelor at other inst.': 'first_year_bachelor_other',
        'First Year to Associates or Certificate at other inst.': 'first_year_assoc_cert_other',
        'Most Recent Associates or Certificate at Other Institution STATE': 'recent_assoc_cert_other_state',
        'Most Recent Associates or Certificate at Other Institution CARNEGIE': 'recent_assoc_cert_other_carnegie',
        'First Associates or Certificate at Other Institution CARNEGIE': 'first_assoc_cert_other_carnegie',
        'Most Recent Associates or Certificate at Other Institution LOCALE': 'recent_assoc_cert_other_locale'
    }
    
    # Get unique values from AR seed data for each column (for sampling)
    ar_value_pools = {}
    for ar_col, db_col in ar_columns.items():
        if ar_col in ar_df.columns:
            # Get non-null values
            values = ar_df[ar_col].dropna().unique().tolist()
            if values:
                ar_value_pools[db_col] = values
            else:
                ar_value_pools[db_col] = [None]
        else:
            ar_value_pools[db_col] = [None]
    
    # Generate record for each student ID
    for student_id in student_ids:
        record = {'student_id': student_id}
        
        # Sample values from AR seed data for each field
        for db_col, value_pool in ar_value_pools.items():
            record[db_col] = random.choice(value_pool)
        
        synthetic_data.append(record)
    
    return synthetic_data

def insert_analysis_ready_data(connection, data: List[Dict]):
    """Insert AR data into the database."""
    cursor = connection.cursor()
    
    insert_sql = f"""
    INSERT INTO {AR_TABLE_NAME} (
        student_id,
        years_to_bachelors_cohort,
        years_to_assoc_cert_cohort,
        years_to_bachelor_other,
        years_to_assoc_cert_other,
        naspa_first_gen,
        first_year_bachelors_cohort,
        first_year_assoc_cert_cohort,
        first_year_bachelor_other,
        first_year_assoc_cert_other,
        recent_assoc_cert_other_state,
        recent_assoc_cert_other_carnegie,
        first_assoc_cert_other_carnegie,
        recent_assoc_cert_other_locale,
        school
    ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
    """
    
    try:
        for record in data:
            values = (
                record['student_id'],
                record.get('years_to_bachelors_cohort'),
                record.get('years_to_assoc_cert_cohort'),
                record.get('years_to_bachelor_other'),
                record.get('years_to_assoc_cert_other'),
                record.get('naspa_first_gen'),
                record.get('first_year_bachelors_cohort'),
                record.get('first_year_assoc_cert_cohort'),
                record.get('first_year_bachelor_other'),
                record.get('first_year_assoc_cert_other'),
                record.get('recent_assoc_cert_other_state'),
                record.get('recent_assoc_cert_other_carnegie'),
                record.get('first_assoc_cert_other_carnegie'),
                record.get('recent_assoc_cert_other_locale'),
                SCHOOL_INFO['acronym']
            )
            cursor.execute(insert_sql, values)
        
        connection.commit()
        print(f"✓ Inserted {len(data)} {AR_TABLE_NAME} records for {SCHOOL_INFO['acronym']}")
        
    except Exception as e:
        print(f"✗ Error inserting {AR_TABLE_NAME} data: {e}")
        connection.rollback()
        raise
    finally:
        cursor.close()

def main():
    """Main function to generate analysis_ready_all data for AL."""
    print(f"\n{'='*60}")
    print(f"Analysis Ready All Data Generation - {SCHOOL_INFO['name']}")
    print(f"{'='*60}\n")
    
    # Connect to database
    connection = get_db_connection(SCHOOL_INFO['dbname'])
    if not connection:
        print(f"✗ Could not connect to database: {SCHOOL_INFO['dbname']}")
        return
    
    try:
        # Get student IDs from cohort table
        student_ids = get_student_ids_from_cohort(connection)
        if not student_ids:
            print(f"✗ No student IDs found in cohort table for {SCHOOL_INFO['acronym']}")
            print("  Make sure cohort data has been generated first!")
            return
        
        print(f"Found {len(student_ids)} unique student IDs in cohort table")
        
        # Load AR seed data
        ar_df = load_ar_seed_data()
        
        # Generate data
        synthetic_data = generate_analysis_ready_data(student_ids, ar_df)
        
        # Insert data
        insert_analysis_ready_data(connection, synthetic_data)
        
        print(f"\n✓ Successfully populated {SCHOOL_INFO['acronym']} analysis_ready_all table")
        print(f"  Total records: {len(synthetic_data)}")
        
    finally:
        connection.close()

if __name__ == "__main__":
    main()
