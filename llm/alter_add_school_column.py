"""
Add school column to existing llm_recommendations tables.
"""

import sys
import os

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import mysql.connector
from mysql.connector import Error
from db_setup import DB_CONFIG, DATABASES


def add_school_column(database_name: str):
    """Add school column to llm_recommendations table."""
    config = DB_CONFIG.copy()
    config["database"] = database_name
    
    try:
        conn = mysql.connector.connect(**config)
        cursor = conn.cursor()
        
        # Try to add the column (will fail if it already exists, which is fine)
        try:
            alter_sql = """
            ALTER TABLE llm_recommendations 
            ADD COLUMN school VARCHAR(10) AFTER Academic_Year
            """
            cursor.execute(alter_sql)
            
            # Add index
            index_sql = "CREATE INDEX idx_school ON llm_recommendations(school)"
            cursor.execute(index_sql)
            
            conn.commit()
            print(f"✓ Added school column to {database_name}")
        except Error as e:
            if "Duplicate column name" in str(e):
                print(f"  School column already exists in {database_name}")
            else:
                print(f"✗ Error adding column to {database_name}: {e}")
        
        cursor.close()
        conn.close()
        
    except Error as e:
        print(f"✗ Error connecting to {database_name}: {e}")


def main():
    print("Adding school column to llm_recommendations tables...\n")
    
    for db in DATABASES:
        dbname = db["dbname"]
        print(f"Processing {dbname}...")
        add_school_column(dbname)
    
    print("\nDone!")


if __name__ == "__main__":
    main()
