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
        return {"table_name": table_name, "error": str(e), "columns": []}
    finally:
        cursor.close()

def get_all_tables(connection):
    """Get list of all tables in the database."""
    cursor = connection.cursor()
    try:
        cursor.execute("SHOW TABLES")
        tables = [table[0] for table in cursor.fetchall()]
        return tables
    except Error as e:
        print(f"Error getting tables: {e}")
        return []
    finally:
        cursor.close()

def main():
    """Main function to export schemas."""
    requested_tables = [
        'course',
        'cohort',
        'llm_recommendations',
        'analysis_ready'
    ]
    
    try:
        connection = mysql.connector.connect(**DB_CONFIG)
        
        # Get all available tables
        all_tables = get_all_tables(connection)
        print(f"Available tables in database: {all_tables}\n", flush=True)
        
        schemas = {
            "database": "Kentucky_Community_and_Technical_College_System",
            "tables": {}
        }
        
        for table in requested_tables:
            if table in all_tables:
                schema = get_table_schema(connection, table)
                schemas["tables"][table] = schema
                print(f"✓ Retrieved schema for {table} ({schema.get('total_columns', 0)} columns)", flush=True)
            else:
                schemas["tables"][table] = {
                    "table_name": table,
                    "error": f"Table '{table}' does not exist in database",
                    "columns": []
                }
                print(f"✗ Table {table} not found", flush=True)
        
        # Write to file
        output_file = "data/predictions/kctcs_db_schema.json"
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(schemas, indent=2, fp=f)
        
        print(f"\n✓ Schema exported to {output_file}", flush=True)
        
        connection.close()
        
    except Error as e:
        print(json.dumps({"error": str(e)}, indent=2), flush=True)

if __name__ == "__main__":
    main()
