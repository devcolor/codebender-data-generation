"""
Verify the KCTCS prediction tables were created correctly.
"""

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
    "database": "Kentucky_Community_and_Technical_College_System"
}

def get_connection() -> mysql.connector.connection.MySQLConnection:
    """Create a database connection."""
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        return conn
    except Error as e:
        print(f"Error connecting to database: {e}")
        raise

def verify_table(conn, table_name):
    """Verify table structure."""
    cursor = conn.cursor()
    
    try:
        print(f"\n{'='*80}")
        print(f"Table: {table_name}")
        print(f"{'='*80}")
        
        # Check if table exists
        cursor.execute(f"SHOW TABLES LIKE '{table_name}'")
        if not cursor.fetchone():
            print(f"✗ Table {table_name} does not exist")
            return
        
        print(f"✓ Table exists")
        
        # Get column count
        cursor.execute(f"""
            SELECT COUNT(*) 
            FROM information_schema.COLUMNS 
            WHERE TABLE_SCHEMA = 'Kentucky_Community_and_Technical_College_System'
            AND TABLE_NAME = '{table_name}'
        """)
        col_count = cursor.fetchone()[0]
        print(f"  - Total columns: {col_count}")
        
        # Get some sample columns
        cursor.execute(f"""
            SELECT COLUMN_NAME, COLUMN_TYPE, IS_NULLABLE, COLUMN_KEY
            FROM information_schema.COLUMNS 
            WHERE TABLE_SCHEMA = 'Kentucky_Community_and_Technical_College_System'
            AND TABLE_NAME = '{table_name}'
            ORDER BY ORDINAL_POSITION
            LIMIT 20
        """)
        
        print(f"\n  First 20 columns:")
        print(f"  {'Column Name':<50} {'Type':<25} {'Null':<6} {'Key':<6}")
        print(f"  {'-'*90}")
        
        for col in cursor.fetchall():
            col_name, col_type, nullable, key = col
            print(f"  {col_name:<50} {col_type:<25} {nullable:<6} {key:<6}")
        
        # Get indexes
        cursor.execute(f"SHOW INDEXES FROM {table_name}")
        indexes = cursor.fetchall()
        
        # Group by index name
        index_dict = {}
        for idx in indexes:
            idx_name = idx[2]
            if idx_name not in index_dict:
                index_dict[idx_name] = {
                    'columns': [],
                    'unique': idx[1] == 0
                }
            index_dict[idx_name]['columns'].append(idx[4])
        
        print(f"\n  Indexes ({len(index_dict)}):")
        for idx_name, idx_info in index_dict.items():
            unique_str = "UNIQUE" if idx_info['unique'] else "INDEX"
            cols_str = ", ".join(idx_info['columns'])
            print(f"    {unique_str:<10} {idx_name:<35} ({cols_str})")
        
        # Get row count
        cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
        row_count = cursor.fetchone()[0]
        print(f"\n  - Total rows: {row_count}")
        
    except Error as e:
        print(f"✗ Error verifying {table_name}: {e}")
    finally:
        cursor.close()

def main():
    """Verify both prediction tables."""
    print("Verifying KCTCS prediction tables...\n")
    
    try:
        conn = get_connection()
        
        verify_table(conn, "course_predictions")
        verify_table(conn, "student_predictions")
        
        conn.close()
        
        print(f"\n{'='*80}")
        print("✓ Verification complete!")
        print(f"{'='*80}")
        
    except Error as e:
        print(f"\n✗ Error: {e}")

if __name__ == "__main__":
    main()
