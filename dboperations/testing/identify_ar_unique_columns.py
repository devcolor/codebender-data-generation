"""
Identify columns in AR file that don't exist in cohort table
"""
import pandas as pd
import mysql.connector
from mysql.connector import Error
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Database configuration
DB_CONFIG = {
    "host": os.getenv("DB_HOST"),
    "user": os.getenv("DB_USER"),
    "password": os.getenv("DB_PASSWORD"),
    "port": int(os.getenv("DB_PORT", "3306")),
    "database": "Bishop_State_Community_College"
}

def get_cohort_columns():
    """Get column names from cohort table"""
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        cursor = conn.cursor()
        cursor.execute("DESCRIBE cohort")
        columns = [row[0] for row in cursor.fetchall()]
        cursor.close()
        conn.close()
        return columns
    except Error as e:
        print(f"Error: {e}")
        return []

def get_ar_columns():
    """Get column names from AR seed file"""
    df = pd.read_csv('data/seed_data01/cohort_AR_data_mock_A.csv')
    return list(df.columns)

def main():
    print("="*80)
    print("IDENTIFYING UNIQUE AR COLUMNS")
    print("="*80)
    
    # Get columns from both sources
    cohort_cols = get_cohort_columns()
    ar_cols = get_ar_columns()
    
    print(f"\nCohort table columns: {len(cohort_cols)}")
    print(f"AR file columns: {len(ar_cols)}")
    
    # Normalize column names for comparison (handle case and underscores)
    cohort_cols_normalized = {col.lower().replace('_', ' ') for col in cohort_cols}
    
    # Find AR columns not in cohort
    unique_ar_cols = []
    for ar_col in ar_cols:
        ar_col_normalized = ar_col.lower().replace('_', ' ')
        if ar_col_normalized not in cohort_cols_normalized:
            unique_ar_cols.append(ar_col)
    
    print(f"\n{'='*80}")
    print(f"UNIQUE AR COLUMNS (not in cohort table): {len(unique_ar_cols)}")
    print(f"{'='*80}")
    
    for i, col in enumerate(unique_ar_cols, 1):
        print(f"{i:3}. {col}")
    
    # Also show which AR columns ARE in cohort (for reference)
    matching_cols = [col for col in ar_cols if col.lower().replace('_', ' ') in cohort_cols_normalized]
    print(f"\n{'='*80}")
    print(f"AR COLUMNS THAT MATCH COHORT: {len(matching_cols)}")
    print(f"{'='*80}")
    for i, col in enumerate(matching_cols, 1):
        print(f"{i:3}. {col}")

if __name__ == "__main__":
    main()
