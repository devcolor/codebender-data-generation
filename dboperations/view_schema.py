#!/usr/bin/env python3
"""
Database Schema Viewer

This script connects to each database and displays the complete schema information
including tables, columns, data types, and relationships.

Usage:
    python dboperations/view_schema.py                    # View all databases
    python dboperations/view_schema.py --database AL     # View specific database
    python dboperations/view_schema.py --table cohort    # View specific table across all databases
"""

import mysql.connector
from mysql.connector import Error
import argparse
import sys
import os
from typing import List, Dict, Optional

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from dboperations.db_setup import DB_CONFIG, DATABASES


def get_connection(database_name: str) -> Optional[mysql.connector.connection.MySQLConnection]:
    """Create a connection to the specified database."""
    config = DB_CONFIG.copy()
    config["database"] = database_name
    
    try:
        conn = mysql.connector.connect(**config)
        return conn
    except Error as e:
        print(f"Error connecting to database {database_name}: {e}")
        return None


def get_table_schema(conn: mysql.connector.connection.MySQLConnection, table_name: str) -> List[Dict]:
    """Get detailed schema information for a specific table."""
    cursor = conn.cursor(dictionary=True)
    
    try:
        # Get column information
        cursor.execute(f"DESCRIBE {table_name}")
        columns = cursor.fetchall()
        
        # Get additional column information
        cursor.execute(f"""
            SELECT 
                COLUMN_NAME,
                DATA_TYPE,
                IS_NULLABLE,
                COLUMN_DEFAULT,
                EXTRA,
                COLUMN_COMMENT
            FROM INFORMATION_SCHEMA.COLUMNS 
            WHERE TABLE_SCHEMA = DATABASE() 
            AND TABLE_NAME = '{table_name}'
            ORDER BY ORDINAL_POSITION
        """)
        detailed_info = cursor.fetchall()
        
        # Merge the information
        schema_info = []
        for i, col in enumerate(columns):
            detailed = detailed_info[i] if i < len(detailed_info) else {}
            schema_info.append({
                'Field': col['Field'],
                'Type': col['Type'],
                'Null': col['Null'],
                'Key': col['Key'],
                'Default': col['Default'],
                'Extra': col['Extra'],
                'Comment': detailed.get('COLUMN_COMMENT', '')
            })
        
        return schema_info
        
    except Error as e:
        print(f"Error getting schema for table {table_name}: {e}")
        return []
    finally:
        cursor.close()


def get_table_indexes(conn: mysql.connector.connection.MySQLConnection, table_name: str) -> List[Dict]:
    """Get index information for a specific table."""
    cursor = conn.cursor(dictionary=True)
    
    try:
        cursor.execute(f"SHOW INDEX FROM {table_name}")
        indexes = cursor.fetchall()
        return indexes
    except Error as e:
        print(f"Error getting indexes for table {table_name}: {e}")
        return []
    finally:
        cursor.close()


def get_table_count(conn: mysql.connector.connection.MySQLConnection, table_name: str) -> int:
    """Get record count for a specific table."""
    cursor = conn.cursor()
    
    try:
        cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
        count = cursor.fetchone()[0]
        return count
    except Error as e:
        print(f"Error getting count for table {table_name}: {e}")
        return 0
    finally:
        cursor.close()


def display_table_schema(conn: mysql.connector.connection.MySQLConnection, table_name: str, database_name: str):
    """Display complete schema information for a table."""
    print(f"\n{'='*80}")
    print(f"TABLE: {table_name} (Database: {database_name})")
    print(f"{'='*80}")
    
    # Get record count
    count = get_table_count(conn, table_name)
    print(f"Records: {count:,}")
    
    # Get schema
    schema = get_table_schema(conn, table_name)
    if not schema:
        print("No schema information available")
        return
    
    print(f"\nCOLUMNS ({len(schema)} total):")
    print("-" * 80)
    print(f"{'Field':<25} {'Type':<20} {'Null':<8} {'Key':<8} {'Default':<15} {'Extra':<15}")
    print("-" * 80)
    
    for col in schema:
        field = col['Field'][:24]
        col_type = col['Type'][:19]
        null_val = col['Null'][:7]
        key_val = col['Key'][:7]
        default = str(col['Default'])[:14] if col['Default'] is not None else 'NULL'
        extra = col['Extra'][:14]
        
        print(f"{field:<25} {col_type:<20} {null_val:<8} {key_val:<8} {default:<15} {extra:<15}")
    
    # Get indexes
    indexes = get_table_indexes(conn, table_name)
    if indexes:
        print(f"\nINDEXES:")
        print("-" * 60)
        index_groups = {}
        for idx in indexes:
            key_name = idx['Key_name']
            if key_name not in index_groups:
                index_groups[key_name] = {
                    'columns': [],
                    'unique': not idx['Non_unique'],
                    'type': idx['Index_type']
                }
            index_groups[key_name]['columns'].append(idx['Column_name'])
        
        for key_name, info in index_groups.items():
            unique_str = "UNIQUE " if info['unique'] else ""
            columns_str = ", ".join(info['columns'])
            print(f"  {unique_str}{key_name}: ({columns_str}) [{info['type']}]")


def list_tables(conn: mysql.connector.connection.MySQLConnection) -> List[str]:
    """Get list of all tables in the database."""
    cursor = conn.cursor()
    
    try:
        cursor.execute("SHOW TABLES")
        tables = [table[0] for table in cursor.fetchall()]
        return tables
    except Error as e:
        print(f"Error listing tables: {e}")
        return []
    finally:
        cursor.close()


def display_database_overview(database_info: Dict):
    """Display overview of a database."""
    database_name = database_info['dbname']
    shortname = database_info['shortname']
    
    print(f"\n{database_name} ({shortname})")
    print("=" * (len(database_name) + len(shortname) + 4))
    
    conn = get_connection(database_name)
    if not conn:
        return
    
    try:
        tables = list_tables(conn)
        if not tables:
            print("No tables found")
            return
        
        print(f"Tables: {len(tables)}")
        
        # Get record counts for each table
        total_records = 0
        table_info = []
        
        for table in tables:
            count = get_table_count(conn, table)
            total_records += count
            table_info.append((table, count))
        
        print(f"Total Records: {total_records:,}")
        print(f"\nTable Summary:")
        print("-" * 40)
        
        for table, count in sorted(table_info, key=lambda x: x[1], reverse=True):
            print(f"  {table:<25} {count:>10,} records")
        
    finally:
        conn.close()


def main():
    parser = argparse.ArgumentParser(description="View database schema information")
    parser.add_argument("--database", "-d", 
                       choices=[db['shortname'] for db in DATABASES] + [db['dbname'] for db in DATABASES],
                       help="Specific database to view (shortname or full name)")
    parser.add_argument("--table", "-t", 
                       help="Specific table to view across all databases")
    parser.add_argument("--overview", "-o", action="store_true",
                       help="Show overview only (no detailed schema)")
    
    args = parser.parse_args()
    
    print("Database Schema Viewer")
    print("=" * 50)
    
    # Filter databases if specific one requested
    databases_to_check = DATABASES
    if args.database:
        databases_to_check = [db for db in DATABASES 
                             if db['shortname'] == args.database or db['dbname'] == args.database]
        if not databases_to_check:
            print(f"Database '{args.database}' not found")
            return
    
    # Show overview or detailed schema
    for db_info in databases_to_check:
        if args.overview:
            display_database_overview(db_info)
        else:
            database_name = db_info['dbname']
            conn = get_connection(database_name)
            if not conn:
                continue
            
            try:
                tables = list_tables(conn)
                
                # Filter tables if specific one requested
                if args.table:
                    tables = [t for t in tables if args.table.lower() in t.lower()]
                    if not tables:
                        print(f"Table '{args.table}' not found in {database_name}")
                        continue
                
                # Display overview first
                display_database_overview(db_info)
                
                # Display detailed schema for each table
                for table in tables:
                    display_table_schema(conn, table, database_name)
                
            finally:
                conn.close()
    
    print(f"\nSchema viewing completed!")


if __name__ == "__main__":
    main()
