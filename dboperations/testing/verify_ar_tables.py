"""
Verify school-specific AR tables (ar_al, ar_csusb, ar_kctcs, ar_ky, ar_oh)
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
}

SCHOOLS = [
    {"dbname": "Bishop_State_Community_College", "shortname": "AL"},
    {"dbname": "California_State_University_San_Bernardino", "shortname": "CSUSB"},
    {"dbname": "Kentucky_Community_and_Technical_College_System", "shortname": "KCTCS"},
    {"dbname": "Thomas_More_University", "shortname": "KY"},
    {"dbname": "University_of_Akron", "shortname": "OH"}
]

def check_ar_table(dbname, shortname):
    """Check if AR table exists and show basic info"""
    ar_table = f"ar_{shortname.lower()}"
    
    try:
        config = DB_CONFIG.copy()
        config["database"] = dbname
        conn = mysql.connector.connect(**config)
        cursor = conn.cursor()
        
        # Check if table exists
        cursor.execute("SHOW TABLES LIKE %s", (ar_table,))
        exists = cursor.fetchone()
        
        if exists:
            # Get record count
            cursor.execute(f"SELECT COUNT(*) FROM {ar_table}")
            count = cursor.fetchone()[0]
            
            print(f"  ✓ {ar_table:<15} - {count:>5} records")
        else:
            print(f"  ✗ {ar_table:<15} - Table does not exist")
        
        cursor.close()
        conn.close()
        
    except Error as e:
        print(f"  ✗ {ar_table:<15} - Error: {e}")

def main():
    print("="*80)
    print("VERIFYING SCHOOL-SPECIFIC AR TABLES")
    print("="*80)
    
    for school in SCHOOLS:
        print(f"\n{school['dbname']}:")
        check_ar_table(school['dbname'], school['shortname'])
    
    print("\n" + "="*80)
    print("✓ VERIFICATION COMPLETE")
    print("="*80)

if __name__ == "__main__":
    main()
