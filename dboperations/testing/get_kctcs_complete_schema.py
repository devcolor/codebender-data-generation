"""
Export KCTCS database schema to JSON format for specific tables.
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
                "default": str(col['Default']) if col['Default'] is not None else None,
                "extra": col['Extra']
            }
            schema["columns"].append(column_info)
        
        schema["total_columns"] = len(columns)
        return schema
    except Error as e:
        return {"table_name": table_name, "error": str(e), "columns": [], "total_columns": 0}
    finally:
        cursor.close()

def main():
    """Main function to export schemas."""
    # Updated to use ar_kctcs instead of analysis_ready
    requested_tables = [
        'course',
        'cohort',
        'llm_recommendations',
        'ar_kctcs'  # This is the AR (Analysis Ready) table for KCTCS
    ]
    
    try:
        connection = mysql.connector.connect(**DB_CONFIG)
        
        schemas = {
            "database": "Kentucky_Community_and_Technical_College_System",
            "description": "Schema for KCTCS database tables",
            "tables": {}
        }
        
        for table in requested_tables:
            schema = get_table_schema(connection, table)
            schemas["tables"][table] = schema
            if "error" not in schema:
                print(f"✓ Retrieved schema for {table} ({schema.get('total_columns', 0)} columns)", flush=True)
            else:
                print(f"✗ Error with {table}: {schema['error']}", flush=True)
        
        # Write to file
        output_file = "data/predictions/kctcs_db_schema.json"
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(schemas, indent=2, fp=f)
        
        print(f"\n✓ Schema exported to {output_file}", flush=True)
        print(f"\nSummary:")
        print(f"  - course: {schemas['tables']['course']['total_columns']} columns")
        print(f"  - cohort: {schemas['tables']['cohort']['total_columns']} columns")
        print(f"  - llm_recommendations: {schemas['tables']['llm_recommendations']['total_columns']} columns")
        print(f"  - ar_kctcs: {schemas['tables']['ar_kctcs']['total_columns']} columns")
        
        connection.close()
        
    except Error as e:
        print(json.dumps({"error": str(e)}, indent=2), flush=True)

if __name__ == "__main__":
    main()
