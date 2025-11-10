"""
Export KCTCS database schema to JSON format.
"""

import mysql.connector
from mysql.connector import Error
import os
import json
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

def get_table_schema(connection, table_name: str):
    """Get schema for a specific table."""
    cursor = connection.cursor(dictionary=True)
    schema = {
        "table_name": table_name,
        "columns": []
    }
    
    try:
        cursor.execute(f"DESCRIBE {table_name}")
        columns = cursor.fetchall()
        
        for col in columns:
            column_info = {
                "field": col['Field'],
                "type": col['Type'],
                "null": col['Null'],
                "key": col['Key'],
                "default": col['Default'],
                "extra": col['Extra']
            }
            schema["columns"].append(column_info)
        
        return schema
    except Error as e:
        return {"table_name": table_name, "error": str(e)}
    finally:
        cursor.close()

def main():
    """Main function to export schemas."""
    tables = [
        'course',
        'cohort',
        'llm_student_readiness',
        'analysis_ready',
        'llm_recommendations'
    ]
    
    try:
        connection = mysql.connector.connect(**DB_CONFIG)
        
        schemas = {}
        for table in tables:
            schema = get_table_schema(connection, table)
            schemas[table] = schema
        
        # Output as JSON
        print(json.dumps(schemas, indent=2, default=str))
        
        connection.close()
        
    except Error as e:
        print(json.dumps({"error": str(e)}, indent=2))

if __name__ == "__main__":
    main()
