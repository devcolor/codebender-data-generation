import pandas as pd
import mysql.connector
from mysql.connector import Error
import os
from dotenv import load_dotenv
import json
import requests
import random
from typing import List, Dict, Any
import time

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
    {"dbname": "Thomas_More_University_KY", "acronym": "KY"},
    {"dbname": "University_of_Akron_OH", "acronym": "OH"}
]

class OllamaSyntheticDataGenerator:
    def __init__(self, model_name="mistral"):
        self.model_name = model_name
        self.base_url = "http://localhost:11434/api/generate"
        
    def generate_course_data(self, seed_data: pd.DataFrame, num_records: int = 200, school_acronym: str = "") -> List[Dict]:
        """Generate synthetic course data using Ollama Mistral."""
        
        # Prepare seed data sample for the prompt
        seed_sample = seed_data.head(5).to_dict('records')
        
        prompt = f"""
        Based on the following sample course data, generate {num_records} new realistic course records for {school_acronym} school.
        Each record should follow the same structure and data patterns.
        
        Sample data:
        {json.dumps(seed_sample, indent=2, default=str)}
        
        Generate diverse but realistic course data including:
        - Course codes (like MATH101, ENG201, etc.)
        - Course titles
        - Credit hours (typically 1-4)
        - Departments
        - Prerequisites
        - Course descriptions
        
        Return the data as a JSON array of objects with the same field names as the sample.
        Only return the JSON array, no additional text.
        """
        
        try:
            response = requests.post(
                self.base_url,
                json={
                    "model": self.model_name,
                    "prompt": prompt,
                    "stream": False,
                    "options": {
                        "temperature": 0.8,
                        "top_p": 0.9
                    }
                },
                timeout=300
            )
            
            if response.status_code == 200:
                result = response.json()
                generated_text = result.get('response', '')
                
                # Try to extract JSON from the response
                try:
                    # Find JSON array in the response
                    start_idx = generated_text.find('[')
                    end_idx = generated_text.rfind(']') + 1
                    
                    if start_idx != -1 and end_idx != 0:
                        json_str = generated_text[start_idx:end_idx]
                        return json.loads(json_str)
                    else:
                        print("Could not find JSON array in response")
                        return []
                        
                except json.JSONDecodeError as e:
                    print(f"Error parsing JSON: {e}")
                    print(f"Response: {generated_text[:500]}...")
                    return []
            else:
                print(f"Error from Ollama: {response.status_code}")
                return []
                
        except requests.exceptions.RequestException as e:
            print(f"Error connecting to Ollama: {e}")
            return []

def load_and_clean_seed_data(file_path: str) -> pd.DataFrame:
    """Load Excel file and remove rows 12 and beyond."""
    try:
        # Read the Excel file
        df = pd.read_excel(file_path)
        
        # Remove rows 12 and beyond (keeping rows 0-11, which is 12 rows)
        cleaned_df = df.iloc[:11].copy()
        
        print(f"Original data shape: {df.shape}")
        print(f"Cleaned data shape: {cleaned_df.shape}")
        
        return cleaned_df
        
    except Exception as e:
        print(f"Error loading seed data: {e}")
        return pd.DataFrame()

def get_db_connection(database_name: str = None):
    """Create database connection."""
    config = DB_CONFIG.copy()
    if database_name:
        config["database"] = database_name
    
    try:
        return mysql.connector.connect(**config)
    except Error as e:
        print(f"Error connecting to database: {e}")
        return None

def create_course_table(connection):
    """Add school column to existing course table if it doesn't exist."""
    cursor = connection.cursor()
    
    try:
        # Add school column if it doesn't exist
        cursor.execute("ALTER TABLE course ADD COLUMN school VARCHAR(10)")
        connection.commit()
        print("Added school column to course table")
    except Error as e:
        if "Duplicate column name" in str(e):
            print("School column already exists in course table")
        else:
            print(f"Error adding school column: {e}")
    finally:
        cursor.close()

def insert_course_data(connection, course_data: List[Dict], school_acronym: str):
    """Insert course data into the database."""
    cursor = connection.cursor()
    
    # Updated insert statement with school field - matching actual table columns
    insert_sql = """
    INSERT INTO course (code, title, credits, description, school)
    VALUES (%s, %s, %s, %s, %s)
    """
    
    try:
        for course in course_data:
            # Map the generated data to your table columns
            # Adjust these field names based on your actual Excel columns
            values = (
                course.get('course_code', f"COURSE{random.randint(100, 999)}"),
                course.get('course_title', course.get('title', 'Unknown Course')),
                course.get('credits', random.randint(1, 4)),
                course.get('description', ''),
                school_acronym
            )
            
            cursor.execute(insert_sql, values)
        
        connection.commit()
        print(f"Inserted {len(course_data)} course records for {school_acronym}")
        
    except Error as e:
        print(f"Error inserting course data: {e}")
        connection.rollback()
    finally:
        cursor.close()

def fallback_data_generation(seed_data: pd.DataFrame, num_records: int, school_acronym: str) -> List[Dict]:
    """Generate synthetic data without LLM if Ollama is not available."""
    print(f"Generating fallback synthetic data for {school_acronym}...")
    
    # Get sample values from seed data
    sample_codes = ["MATH", "ENG", "SCI", "HIST", "ART", "BUS", "CS", "PHYS", "CHEM", "BIO"]
    sample_titles = [
        "Introduction to", "Advanced", "Principles of", "Fundamentals of",
        "Applied", "Modern", "Classical", "Contemporary", "Research in"
    ]
    sample_subjects = [
        "Mathematics", "English", "Science", "History", "Art", "Business",
        "Computer Science", "Physics", "Chemistry", "Biology", "Psychology",
        "Sociology", "Economics", "Philosophy", "Literature"
    ]
    
    synthetic_data = []
    
    for i in range(num_records):
        code_prefix = random.choice(sample_codes)
        course_num = random.randint(100, 499)
        title_prefix = random.choice(sample_titles)
        subject = random.choice(sample_subjects)
        
        course = {
            'course_code': f"{code_prefix}{course_num}",
            'course_title': f"{title_prefix} {subject}",
            'credits': random.randint(1, 4),
            'department': random.choice(sample_subjects),
            'prerequisites': random.choice(['', f"{code_prefix}{random.randint(100, 299)}", 'None']),
            'description': f"This course covers {subject.lower()} concepts and applications."
        }
        
        synthetic_data.append(course)
    
    return synthetic_data

def main():
    """Main function to generate and distribute synthetic data."""
    
    # Load and clean seed data
    seed_file_path = "data/course_analysis_ready_file_template_Identified_01_27_25.xlsx"
    
    if not os.path.exists(seed_file_path):
        print(f"Seed data file not found: {seed_file_path}")
        return
    
    seed_data = load_and_clean_seed_data(seed_file_path)
    
    if seed_data.empty:
        print("No seed data available")
        return
    
    print("Seed data columns:", seed_data.columns.tolist())
    print("Sample seed data:")
    print(seed_data.head())
    
    # Initialize synthetic data generator
    generator = OllamaSyntheticDataGenerator()
    
    # Generate synthetic data for each database (200 records each = 1000 total)
    records_per_db = 200
    
    for db_info in DATABASES:
        db_name = db_info["dbname"]
        school_acronym = db_info["acronym"]
        
        print(f"\nProcessing database: {db_name} ({school_acronym})")
        
        # Generate synthetic data
        print(f"Generating synthetic course data for {school_acronym}...")
        synthetic_data = generator.generate_course_data(seed_data, records_per_db, school_acronym)
        
        # Fallback if Ollama generation fails
        if not synthetic_data:
            print("Ollama generation failed, using fallback method...")
            synthetic_data = fallback_data_generation(seed_data, records_per_db, school_acronym)
        
        # Connect to database
        connection = get_db_connection(db_name)
        if not connection:
            print(f"Could not connect to database: {db_name}")
            continue
        
        try:
            # Create table
            create_course_table(connection)
            
            # Insert data
            insert_course_data(connection, synthetic_data, school_acronym)
            
            print(f"Successfully populated {db_name} with {len(synthetic_data)} records")
            
        finally:
            connection.close()
        
        # Small delay between databases
        time.sleep(1)
    
    print("\nSynthetic data generation completed!")

if __name__ == "__main__":
    main()
