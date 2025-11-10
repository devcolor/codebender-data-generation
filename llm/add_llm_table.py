"""
Add llm_recommendations table to existing databases.
"""

import sys
import os

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import mysql.connector
from mysql.connector import Error
from dboperations.db_setup import DB_CONFIG, DATABASES


def add_llm_table(database_name: str):
    """Add llm_recommendations table to a database."""
    config = DB_CONFIG.copy()
    config["database"] = database_name
    
    try:
        conn = mysql.connector.connect(**config)
        cursor = conn.cursor()
        
        create_table_sql = """
        CREATE TABLE IF NOT EXISTS llm_recommendations (
            id BIGINT AUTO_INCREMENT PRIMARY KEY,
            Student_GUID VARCHAR(58) NOT NULL,
            Institution_ID BIGINT,
            Cohort VARCHAR(57),
            Cohort_Term VARCHAR(56),
            Academic_Year VARCHAR(57),
            school VARCHAR(10),
            recommendation_type VARCHAR(50) NOT NULL,
            readiness_score DECIMAL(5,4),
            readiness_level VARCHAR(20),
            rationale TEXT,
            risk_factors JSON,
            suggested_actions JSON,
            inputs_snapshot JSON,
            course_summaries JSON,
            prompt_version VARCHAR(50) NOT NULL,
            model_name VARCHAR(100) NOT NULL,
            model_version VARCHAR(100),
            input_hash CHAR(64) NOT NULL,
            status VARCHAR(20) NOT NULL DEFAULT 'ok',
            error_message TEXT,
            generated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            INDEX idx_student_rec_time (Student_GUID, recommendation_type, generated_at),
            INDEX idx_school (school),
            UNIQUE KEY unique_recommendation (Student_GUID, recommendation_type, prompt_version, input_hash)
        )
        """
        
        cursor.execute(create_table_sql)
        conn.commit()
        print(f"✓ Created llm_recommendations table in {database_name}")
        
        cursor.close()
        conn.close()
        
    except Error as e:
        print(f"✗ Error creating table in {database_name}: {e}")


def main():
    print("Adding llm_recommendations table to all databases...\n")
    
    for db in DATABASES:
        dbname = db["dbname"]
        print(f"Processing {dbname}...")
        add_llm_table(dbname)
    
    print("\nDone!")


if __name__ == "__main__":
    main()
