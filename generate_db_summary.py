import mysql.connector
from mysql.connector import Error
from dotenv import load_dotenv
import os
import pandas as pd
from datetime import datetime

# Load environment variables
load_dotenv()

# Database configuration
DB_CONFIG = {
    "host": os.getenv("DB_HOST"),
    "user": os.getenv("DB_USER"),
    "password": os.getenv("DB_PASSWORD"),
    "port": int(os.getenv("DB_PORT", "3306")),
}

# Database names with their acronyms
DATABASES = [
    {"dbname": "Bishop_State_Community_College", "acronym": "AL"},
    {"dbname": "California_State_University_San_Bernardino", "acronym": "CSUSB"},
    {"dbname": "Kentucky_Community_and_Technical_College_System", "acronym": "KCTCS"},
    {"dbname": "Thomas_More_University", "acronym": "KY"},
    {"dbname": "University_of_Akron", "acronym": "OH"}
]

def get_connection(database_name: str = None):
    """Create and return a database connection."""
    config = DB_CONFIG.copy()
    if database_name:
        config["database"] = database_name
    
    try:
        return mysql.connector.connect(**config)
    except Error as e:
        print(f"Error connecting to database: {e}")
        return None

def get_table_info(connection, database_name):
    """Get table information for a database."""
    cursor = connection.cursor()
    tables_info = []
    
    try:
        # Get all tables
        cursor.execute("SHOW TABLES")
        tables = [table[0] for table in cursor.fetchall()]
        
        for table in tables:
            # Get table structure
            cursor.execute(f"DESCRIBE {table}")
            columns = cursor.fetchall()
            
            # Count records
            cursor.execute(f"SELECT COUNT(*) FROM {table}")
            record_count = cursor.fetchone()[0]
            
            # Get column details
            column_details = []
            for col in columns:
                column_details.append({
                    'column_name': col[0],
                    'data_type': col[1],
                    'nullable': col[2],
                    'key': col[3],
                    'default': col[4],
                    'extra': col[5]
                })
            
            tables_info.append({
                'database': database_name,
                'table': table,
                'record_count': record_count,
                'columns': column_details
            })
    
    except Error as e:
        print(f"Error getting table info for {database_name}: {e}")
    
    finally:
        cursor.close()
    
    return tables_info

def create_excel_summary():
    """Create Excel file with database and table summary."""
    
    # Lists to store data for different sheets
    database_summary = []
    table_summary = []
    column_details = []
    
    for db_info in DATABASES:
        db_name = db_info["dbname"]
        school_acronym = db_info["acronym"]
        
        print(f"Processing database: {db_name}")
        
        # Connect to database
        connection = get_connection(db_name)
        if not connection:
            continue
        
        try:
            # Get table information
            tables_info = get_table_info(connection, db_name)
            
            # Calculate totals for database summary
            total_records = sum(table['record_count'] for table in tables_info)
            table_count = len(tables_info)
            
            database_summary.append({
                'Database Name': db_name,
                'School Acronym': school_acronym,
                'Number of Tables': table_count,
                'Total Records': total_records
            })
            
            # Add to table summary
            for table_info in tables_info:
                table_summary.append({
                    'Database Name': db_name,
                    'School Acronym': school_acronym,
                    'Table Name': table_info['table'],
                    'Record Count': table_info['record_count']
                })
                
                # Add column details
                for col in table_info['columns']:
                    column_details.append({
                        'Database Name': db_name,
                        'School Acronym': school_acronym,
                        'Table Name': table_info['table'],
                        'Column Name': col['column_name'],
                        'Data Type': col['data_type'],
                        'Nullable': col['nullable'],
                        'Key': col['key'],
                        'Default': col['default'],
                        'Extra': col['extra']
                    })
        
        finally:
            connection.close()
    
    # Create DataFrames
    df_databases = pd.DataFrame(database_summary)
    df_tables = pd.DataFrame(table_summary)
    df_columns = pd.DataFrame(column_details)
    
    # Create Excel file with multiple sheets
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"database_summary_{timestamp}.xlsx"
    
    with pd.ExcelWriter(filename, engine='openpyxl') as writer:
        df_databases.to_excel(writer, sheet_name='Database Summary', index=False)
        df_tables.to_excel(writer, sheet_name='Table Summary', index=False)
        df_columns.to_excel(writer, sheet_name='Column Details', index=False)
        
        # Auto-adjust column widths
        for sheet_name in writer.sheets:
            worksheet = writer.sheets[sheet_name]
            for column in worksheet.columns:
                max_length = 0
                column_letter = column[0].column_letter
                for cell in column:
                    try:
                        if len(str(cell.value)) > max_length:
                            max_length = len(str(cell.value))
                    except:
                        pass
                adjusted_width = min(max_length + 2, 50)
                worksheet.column_dimensions[column_letter].width = adjusted_width
    
    print(f"\nExcel summary created: {filename}")
    
    # Print summary to console
    print("\nDatabase Summary:")
    print("=" * 80)
    for _, row in df_databases.iterrows():
        print(f"{row['School Acronym']} - {row['Database Name']}")
        print(f"  Tables: {row['Number of Tables']}, Total Records: {row['Total Records']:,}")
    
    print(f"\nGrand Total Records: {df_databases['Total Records'].sum():,}")
    
    return filename

if __name__ == "__main__":
    create_excel_summary()
