"""
FINAL VERSION: Create database tables matching EXACT seed data structure
and populate with realistic data for all 5 schools.

COHORT: 85 columns
COURSE: 35 columns  
FINANCIAL_AID: 21 columns

Fixed: MySQL column name limits + data type conversions
"""

import mysql.connector
from mysql.connector import Error
import pandas as pd
import numpy as np
import os
from dotenv import load_dotenv
import random
from typing import List, Dict, Any
import hashlib

# Load environment variables
load_dotenv()

# Database configuration
DB_CONFIG = {
    "host": os.getenv("DB_HOST"),
    "user": os.getenv("DB_USER"),
    "password": os.getenv("DB_PASSWORD"),
    "port": int(os.getenv("DB_PORT", "3306")),
}

# School configurations
SCHOOLS = [
    {"dbname": "Bishop_State_Community_College", "acronym": "AL", "name": "Bishop State Community College"},
    {"dbname": "California_State_University_San_Bernardino", "acronym": "CSUSB", "name": "California State University San Bernardino"},
    {"dbname": "Kentucky_Community_and_Technical_College_System", "acronym": "KCTCS", "name": "Kentucky Community and Technical College System"},
    {"dbname": "Thomas_More_University", "acronym": "KY", "name": "Thomas More University"},
    {"dbname": "University_of_Akron", "acronym": "OH", "name": "University of Akron"}
]

def get_db_connection(database_name: str = None):
    """Create database connection."""
    config = DB_CONFIG.copy()
    if database_name:
        config["database"] = database_name
    
    try:
        return mysql.connector.connect(**config)
    except Error as e:
        print(f"[ERROR] Error connecting to database: {e}")
        return None

def clean_column_name(col_name: str) -> str:
    """Clean and truncate column names for MySQL compatibility."""
    # Replace problematic characters
    clean_name = col_name.replace(' ', '_').replace('(', '').replace(')', '').replace('-', '_')
    clean_name = clean_name.replace('/', '_').replace('&', 'and').replace(',', '').replace("'", '')
    clean_name = clean_name.replace('.', '_').replace('#', 'num').replace('%', 'pct')
    
    # Remove multiple underscores
    while '__' in clean_name:
        clean_name = clean_name.replace('__', '_')
    
    # Truncate to 60 characters (leave room for suffixes)
    if len(clean_name) > 60:
        # Keep first 50 chars + hash of full name for uniqueness
        hash_suffix = hashlib.md5(col_name.encode()).hexdigest()[:8]
        clean_name = clean_name[:50] + '_' + hash_suffix
    
    return clean_name

def convert_value_for_mysql(value: Any) -> Any:
    """Convert pandas/numpy values to MySQL-compatible types."""
    if pd.isna(value):
        return None
    elif isinstance(value, (np.int64, np.int32, np.int16, np.int8)):
        return int(value)
    elif isinstance(value, (np.float64, np.float32)):
        return float(value)
    elif isinstance(value, np.bool_):
        return bool(value)
    elif isinstance(value, bytes):
        return value.decode('utf-8', errors='ignore')
    else:
        return value

def analyze_seed_data():
    """Load and analyze seed data structure."""
    print("Loading and analyzing seed data structure...")
    
    # Load seed data
    cohort_df = pd.read_csv('data/seed_data01/cohort_AR_data_mock_A.csv')
    course_df = pd.read_csv('data/seed_data01/course_AR_data_mock.csv')
    financial_df = pd.read_excel('data/seed_data01/financialaid_analysis_ready_file_template.xlsx')
    
    # Create column mappings
    cohort_column_mapping = {col: clean_column_name(col) for col in cohort_df.columns}
    course_column_mapping = {col: clean_column_name(col) for col in course_df.columns}
    financial_column_mapping = {col: clean_column_name(col) for col in financial_df.columns}
    
    return (cohort_df, course_df, financial_df,
            cohort_column_mapping, course_column_mapping, financial_column_mapping)

def create_table_from_dataframe(connection, table_name: str, df: pd.DataFrame, column_mapping: Dict[str, str]):
    """Create table based on DataFrame structure."""
    cursor = connection.cursor()
    
    try:
        # Drop existing table
        cursor.execute(f"DROP TABLE IF EXISTS {table_name}")
        
        # Start CREATE TABLE statement
        sql = f"CREATE TABLE {table_name} (\n"
        sql += "    id BIGINT AUTO_INCREMENT PRIMARY KEY,\n"
        
        # Add columns based on DataFrame
        for original_col, clean_col in column_mapping.items():
            dtype = str(df[original_col].dtype)
            
            if dtype == 'object':
                # String columns
                max_len = df[original_col].astype(str).str.len().max()
                if pd.isna(max_len) or max_len == 0:
                    max_len = 50
                
                if max_len <= 255:
                    sql += f"    `{clean_col}` VARCHAR({min(max_len + 50, 255)}),\n"
                else:
                    sql += f"    `{clean_col}` TEXT,\n"
            
            elif dtype in ['int64', 'int32']:
                sql += f"    `{clean_col}` BIGINT,\n"
            elif dtype in ['float64', 'float32']:
                sql += f"    `{clean_col}` DECIMAL(15,2),\n"
            else:
                sql += f"    `{clean_col}` VARCHAR(255),\n"
        
        # Add standard columns
        sql += "    school VARCHAR(10),\n"
        sql += "    dataset_type VARCHAR(1) DEFAULT 'S',\n"
        sql += "    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP\n"
        sql += ")"
        
        cursor.execute(sql)
        connection.commit()
        print(f"  - Created {table_name} table with {len(column_mapping)} columns")
        
    except Error as e:
        print(f"  - Error creating {table_name} table: {e}")
        connection.rollback()
        raise
    finally:
        cursor.close()

def generate_cohort_data(school_acronym: str, cohort_df: pd.DataFrame, 
                        cohort_column_mapping: Dict[str, str], num_students: int = 1800) -> List[Dict]:
    """Generate cohort data matching seed structure."""
    print(f"    Generating {num_students} cohort records for {school_acronym}...")
    
    synthetic_data = []
    
    # Get cohort distribution from seed data
    cohort_distribution = cohort_df['Cohort'].value_counts()
    
    student_counter = 0
    for cohort_name, base_count in cohort_distribution.items():
        # Calculate proportional students for this cohort
        proportion = base_count / len(cohort_df)
        cohort_students = int(num_students * proportion)
        
        # Get template rows for this cohort
        cohort_templates = cohort_df[cohort_df['Cohort'] == cohort_name]
        
        for i in range(cohort_students):
            # Use random template from this cohort
            template_row = cohort_templates.sample(n=1).iloc[0]
            
            record = {}
            for original_col, clean_col in cohort_column_mapping.items():
                if original_col == 'Student GUID':
                    record[clean_col] = f"{school_acronym}_STU{student_counter:05d}"
                elif original_col == 'Institution ID':
                    # Use school-specific institution ID
                    institution_ids = {'AL': 86753091, 'CSUSB': 86753092, 'KCTCS': 86753093, 'KY': 86753094, 'OH': 86753095}
                    record[clean_col] = institution_ids[school_acronym]
                else:
                    # Convert value for MySQL compatibility
                    value = template_row[original_col]
                    record[clean_col] = convert_value_for_mysql(value)
            
            record['school'] = school_acronym
            record['dataset_type'] = 'S'
            synthetic_data.append(record)
            student_counter += 1
    
    return synthetic_data

def generate_course_data(school_acronym: str, course_df: pd.DataFrame, 
                        course_column_mapping: Dict[str, str], student_guids: List[str]) -> List[Dict]:
    """Generate course data matching seed structure."""
    courses_per_student = 3
    print(f"    Generating ~{len(student_guids) * courses_per_student} course records for {school_acronym}...")
    
    synthetic_data = []
    
    for student_guid in student_guids:
        # Each student takes 2-5 courses
        num_courses = random.randint(2, 5)
        
        for _ in range(num_courses):
            # Use random template from seed data
            template_row = course_df.sample(n=1).iloc[0]
            
            record = {}
            for original_col, clean_col in course_column_mapping.items():
                if original_col == 'Student GUID':
                    record[clean_col] = student_guid
                elif original_col == 'Institution ID':
                    institution_ids = {'AL': 86753091, 'CSUSB': 86753092, 'KCTCS': 86753093, 'KY': 86753094, 'OH': 86753095}
                    record[clean_col] = institution_ids[school_acronym]
                else:
                    # Convert value for MySQL compatibility
                    value = template_row[original_col]
                    record[clean_col] = convert_value_for_mysql(value)
            
            record['school'] = school_acronym
            record['dataset_type'] = 'S'
            synthetic_data.append(record)
    
    return synthetic_data

def generate_financial_data(school_acronym: str, financial_df: pd.DataFrame, 
                           financial_column_mapping: Dict[str, str], student_guids: List[str]) -> List[Dict]:
    """Generate financial aid data matching seed structure."""
    print(f"    Generating {len(student_guids)} financial aid records for {school_acronym}...")
    
    synthetic_data = []
    
    for student_guid in student_guids:
        # Use random template from seed data
        template_row = financial_df.sample(n=1).iloc[0]
        
        record = {}
        for original_col, clean_col in financial_column_mapping.items():
            if original_col == 'Student ID':
                # Extract numeric part from student GUID
                record[clean_col] = int(student_guid.split('_STU')[1])
            elif original_col == 'Institution ID':
                institution_ids = {'AL': 86753091, 'CSUSB': 86753092, 'KCTCS': 86753093, 'KY': 86753094, 'OH': 86753095}
                record[clean_col] = institution_ids[school_acronym]
            else:
                # Convert value and add variation for financial amounts
                value = template_row[original_col]
                converted_value = convert_value_for_mysql(value)
                
                # Add variation to financial amounts
                if (converted_value is not None and isinstance(converted_value, (int, float)) and 
                    ('Cost' in original_col or 'EFC' in original_col or 'Grant' in original_col or 
                     'Need' in original_col or 'Price' in original_col)):
                    variation = random.uniform(0.8, 1.2)
                    record[clean_col] = int(converted_value * variation)
                else:
                    record[clean_col] = converted_value
        
        record['school'] = school_acronym
        record['dataset_type'] = 'S'
        synthetic_data.append(record)
    
    return synthetic_data

def insert_data_safely(connection, table_name: str, data: List[Dict], columns: List[str]):
    """Insert data with proper type conversion."""
    if not data:
        return
    
    cursor = connection.cursor()
    
    # Create column list with backticks
    escaped_columns = [f"`{col}`" for col in columns]
    placeholders = ", ".join(["%s"] * len(columns))
    
    insert_sql = f"INSERT INTO {table_name} ({', '.join(escaped_columns)}) VALUES ({placeholders})"
    
    try:
        batch_size = 500
        for i in range(0, len(data), batch_size):
            batch = data[i:i + batch_size]
            values = []
            
            for record in batch:
                row_values = []
                for col in columns:
                    value = record.get(col)
                    # Ensure proper type conversion
                    converted_value = convert_value_for_mysql(value)
                    row_values.append(converted_value)
                values.append(tuple(row_values))
            
            cursor.executemany(insert_sql, values)
            connection.commit()
            print(f"      Inserted batch {i//batch_size + 1} ({len(batch)} records)")
        
        print(f"    - Successfully inserted {len(data)} records into {table_name}")
        
    except Error as e:
        print(f"    - Error inserting data into {table_name}: {e}")
        connection.rollback()
        raise
    finally:
        cursor.close()

def process_school(school: Dict, cohort_df, course_df, financial_df,
                  cohort_column_mapping, course_column_mapping, financial_column_mapping):
    """Process a single school with complete seed data structure."""
    print(f"\n{'='*80}")
    print(f"PROCESSING: {school['name']} ({school['acronym']})")
    print(f"{'='*80}")
    
    connection = get_db_connection(school['dbname'])
    if not connection:
        print(f"[ERROR] Could not connect to database: {school['dbname']}")
        return
    
    try:
        # Step 1: Create tables with full seed structure
        print("Step 1: Creating tables with full seed data structure...")
        create_table_from_dataframe(connection, 'cohort', cohort_df, cohort_column_mapping)
        create_table_from_dataframe(connection, 'course', course_df, course_column_mapping)
        create_table_from_dataframe(connection, 'financial_aid', financial_df, financial_column_mapping)
        
        # Step 2: Generate cohort data
        print("Step 2: Generating cohort data...")
        cohort_data = generate_cohort_data(school['acronym'], cohort_df, cohort_column_mapping, 1800)
        
        # Get student GUIDs
        student_guid_col = cohort_column_mapping['Student GUID']
        student_guids = [record[student_guid_col] for record in cohort_data]
        
        # Step 3: Generate course data
        print("Step 3: Generating course enrollment data...")
        course_data = generate_course_data(school['acronym'], course_df, course_column_mapping, student_guids)
        
        # Step 4: Generate financial aid data
        print("Step 4: Generating financial aid data...")
        financial_data = generate_financial_data(school['acronym'], financial_df, financial_column_mapping, student_guids)
        
        # Step 5: Insert all data
        print("Step 5: Inserting data into database...")
        
        cohort_columns = list(cohort_column_mapping.values()) + ['school', 'dataset_type']
        course_columns = list(course_column_mapping.values()) + ['school', 'dataset_type']
        financial_columns = list(financial_column_mapping.values()) + ['school', 'dataset_type']
        
        insert_data_safely(connection, 'cohort', cohort_data, cohort_columns)
        insert_data_safely(connection, 'course', course_data, course_columns)
        insert_data_safely(connection, 'financial_aid', financial_data, financial_columns)
        
        # Summary
        print(f"\n{'-'*80}")
        print("SUMMARY:")
        print(f"  - Cohort Records: {len(cohort_data):,} ({len(cohort_column_mapping)} seed columns)")
        print(f"  - Course Records: {len(course_data):,} ({len(course_column_mapping)} seed columns)")
        print(f"  - Financial Aid Records: {len(financial_data):,} ({len(financial_column_mapping)} seed columns)")
        print(f"  - Total Records: {len(cohort_data) + len(course_data) + len(financial_data):,}")
        print(f"{'-'*80}")
        
    finally:
        connection.close()

def main():
    """Main function to implement complete seed data structure."""
    print(f"\n{'='*80}")
    print(" "*10 + "COMPLETE SEED DATA STRUCTURE IMPLEMENTATION")
    print(" "*15 + "Using EXACT seed_data01 column structure")
    print(f"{'='*80}")
    
    # Load and analyze seed data
    (cohort_df, course_df, financial_df,
     cohort_column_mapping, course_column_mapping, financial_column_mapping) = analyze_seed_data()
    
    print(f"\nSeed data structure loaded:")
    print(f"  - COHORT: {len(cohort_column_mapping)} columns from seed data")
    print(f"  - COURSE: {len(course_column_mapping)} columns from seed data")
    print(f"  - FINANCIAL_AID: {len(financial_column_mapping)} columns from seed data")
    
    # Process each school
    for school in SCHOOLS:
        process_school(school, cohort_df, course_df, financial_df,
                      cohort_column_mapping, course_column_mapping, financial_column_mapping)
    
    print(f"\n{'='*80}")
    print(" "*5 + "SUCCESS! ALL 5 SCHOOLS POPULATED WITH FULL SEED STRUCTURE")
    print(" "*8 + "Each database now contains the complete 85/35/21 column structure")
    print(" "*15 + "with realistic data based on seed_data01!")
    print(f"{'='*80}\n")

if __name__ == "__main__":
    main()
