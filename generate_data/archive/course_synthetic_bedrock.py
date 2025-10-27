import pandas as pd
import mysql.connector
from mysql.connector import Error
import os
from dotenv import load_dotenv
import json
import boto3
import random
from typing import List, Dict, Any
import time
from botocore.exceptions import ClientError

# Load environment variables
load_dotenv()

# Database configuration
DB_CONFIG = {
    "host": os.getenv("DB_HOST"),
    "user": os.getenv("DB_USER"),
    "password": os.getenv("DB_PASSWORD"),
    "port": int(os.getenv("DB_PORT", "3306")),
}

# AWS Bedrock configuration
AWS_CONFIG = {
    "region_name": os.getenv("AWS_REGION", "us-east-1"),
    "aws_access_key_id": os.getenv("AWS_ACCESS_KEY_ID"),
    "aws_secret_access_key": os.getenv("AWS_SECRET_ACCESS_KEY"),
}

# Database names with their acronyms
DATABASES = [
    {"dbname": "Bishop_State_Community_College", "acronym": "AL"},
    {"dbname": "California_State_University_San_Bernardino", "acronym": "CSUSB"},
    {"dbname": "Kentucky_Community_and_Technical_College_System", "acronym": "KCTCS"},
    {"dbname": "Thomas_More_University_KY", "acronym": "KY"},
    {"dbname": "University_of_Akron_OH", "acronym": "OH"}
]

class BedrockClaudeSyntheticDataGenerator:
    def __init__(self, model_id="anthropic.claude-3-sonnet-20240229-v1:0"):
        """
        Initialize AWS Bedrock client for Claude API.
        
        Key differences from self-hosted Ollama:
        1. Requires AWS credentials and internet connection
        2. Pay-per-use pricing model vs free self-hosted
        3. Higher rate limits and better performance
        4. No local setup required
        5. Enterprise-grade security and compliance
        """
        self.model_id = model_id
        
        try:
            # Initialize AWS Bedrock client
            self.bedrock_client = boto3.client(
                service_name='bedrock-runtime',
                region_name=AWS_CONFIG["region_name"],
                aws_access_key_id=AWS_CONFIG["aws_access_key_id"],
                aws_secret_access_key=AWS_CONFIG["aws_secret_access_key"]
            )
            print("AWS Bedrock client initialized successfully")
        except Exception as e:
            print(f"Error initializing AWS Bedrock client: {e}")
            self.bedrock_client = None
    
    def generate_course_data(self, seed_data: pd.DataFrame, num_records: int = 200, school_acronym: str = "") -> List[Dict]:
        """
        Generate synthetic course data using AWS Bedrock Claude API.
        
        API-based advantages:
        - No local model storage (4-8GB saved)
        - Faster response times
        - More consistent output quality
        - Automatic scaling
        
        API-based considerations:
        - Requires internet connection
        - Usage costs (typically $0.003-0.015 per 1K tokens)
        - Rate limits (but usually higher than self-hosted)
        - Data sent to external service
        """
        
        if not self.bedrock_client:
            print("Bedrock client not available, falling back to synthetic generation")
            return self._fallback_generation(seed_data, num_records, school_acronym)
        
        # Prepare seed data sample for the prompt
        seed_sample = seed_data.head(3).to_dict('records')  # Smaller sample to reduce token usage
        
        # Claude-optimized prompt structure
        prompt = f"""You are a data generation expert. Generate {num_records} realistic course records for {school_acronym} educational institution.

Based on this sample data structure:
{json.dumps(seed_sample, indent=2, default=str)}

Requirements:
- Generate diverse but realistic course data
- Include course codes (MATH101, ENG201, etc.)
- Vary credit hours (1-4 typically)
- Create appropriate course titles and descriptions
- Use realistic department names
- Some courses should have prerequisites, others none

Return ONLY a valid JSON array with the same field structure as the sample. No additional text or formatting."""

        try:
            # Prepare the request body for Claude
            request_body = {
                "anthropic_version": "bedrock-2023-05-31",
                "max_tokens": 4000,  # Adjust based on your needs
                "temperature": 0.7,
                "messages": [
                    {
                        "role": "user",
                        "content": prompt
                    }
                ]
            }
            
            # Make the API call to Bedrock
            print(f"Calling AWS Bedrock Claude API for {school_acronym}...")
            response = self.bedrock_client.invoke_model(
                modelId=self.model_id,
                body=json.dumps(request_body),
                contentType='application/json'
            )
            
            # Parse the response
            response_body = json.loads(response['body'].read())
            generated_text = response_body['content'][0]['text']
            
            print(f"Received response from Claude API ({len(generated_text)} characters)")
            
            # Extract JSON from Claude's response
            try:
                # Find JSON array in the response
                start_idx = generated_text.find('[')
                end_idx = generated_text.rfind(']') + 1
                
                if start_idx != -1 and end_idx != 0:
                    json_str = generated_text[start_idx:end_idx]
                    parsed_data = json.loads(json_str)
                    
                    print(f"Successfully parsed {len(parsed_data)} course records")
                    return parsed_data
                else:
                    print("Could not find JSON array in Claude response")
                    return self._fallback_generation(seed_data, num_records, school_acronym)
                    
            except json.JSONDecodeError as e:
                print(f"Error parsing JSON from Claude: {e}")
                print(f"Response preview: {generated_text[:200]}...")
                return self._fallback_generation(seed_data, num_records, school_acronym)
                
        except ClientError as e:
            error_code = e.response['Error']['Code']
            error_message = e.response['Error']['Message']
            
            if error_code == 'ThrottlingException':
                print("API rate limit exceeded, waiting and retrying...")
                time.sleep(5)
                return self._fallback_generation(seed_data, num_records, school_acronym)
            elif error_code == 'ValidationException':
                print(f"Invalid request: {error_message}")
                return self._fallback_generation(seed_data, num_records, school_acronym)
            else:
                print(f"AWS Bedrock error ({error_code}): {error_message}")
                return self._fallback_generation(seed_data, num_records, school_acronym)
                
        except Exception as e:
            print(f"Unexpected error calling Bedrock: {e}")
            return self._fallback_generation(seed_data, num_records, school_acronym)
    
    def _fallback_generation(self, seed_data: pd.DataFrame, num_records: int, school_acronym: str) -> List[Dict]:
        """Generate synthetic data without API if Bedrock is not available."""
        print(f"Generating fallback synthetic data for {school_acronym}...")
        
        # Enhanced fallback with more realistic data
        departments = ["Mathematics", "English", "Computer Science", "Biology", "Chemistry", 
                      "Physics", "History", "Psychology", "Business", "Art", "Music", 
                      "Philosophy", "Sociology", "Economics", "Political Science"]
        
        course_prefixes = ["MATH", "ENG", "CS", "BIO", "CHEM", "PHYS", "HIST", "PSYC", 
                          "BUS", "ART", "MUS", "PHIL", "SOC", "ECON", "POLS"]
        
        title_prefixes = ["Introduction to", "Advanced", "Principles of", "Fundamentals of",
                         "Applied", "Modern", "Classical", "Contemporary", "Research in",
                         "Topics in", "Survey of", "Methods in"]
        
        synthetic_data = []
        
        for i in range(num_records):
            dept_idx = random.randint(0, len(departments) - 1)
            department = departments[dept_idx]
            prefix = course_prefixes[dept_idx]
            
            course_num = random.randint(100, 499)
            title_prefix = random.choice(title_prefixes)
            
            # Generate prerequisites based on course level
            prereq = ""
            if course_num >= 200:
                prereq_num = random.randint(100, course_num - 50)
                if random.random() < 0.6:  # 60% chance of having prereq for upper level
                    prereq = f"{prefix}{prereq_num}"
            
            course = {
                'course_code': f"{prefix}{course_num}",
                'course_title': f"{title_prefix} {department}",
                'credits': random.choices([1, 2, 3, 4], weights=[5, 15, 60, 20])[0],  # Weighted towards 3 credits
                'department': department,
                'prerequisites': prereq,
                'description': f"This course provides comprehensive coverage of {department.lower()} concepts, theories, and practical applications."
            }
            
            synthetic_data.append(course)
        
        return synthetic_data

def load_and_clean_seed_data(file_path: str) -> pd.DataFrame:
    """Load Excel file and remove rows 12 and beyond."""
    try:
        df = pd.read_excel(file_path)
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
    
    insert_sql = """
    INSERT INTO course (code, title, credits, description, school)
    VALUES (%s, %s, %s, %s, %s)
    """
    
    try:
        for course in course_data:
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

def main():
    """
    Main function demonstrating AWS Bedrock Claude API vs Self-hosted Ollama.
    
    Key Differences Summary:
    
    AWS Bedrock Claude (API-based):
    Pros:
    - No local setup or model downloads
    - Faster, more consistent responses
    - Enterprise-grade security
    - Automatic scaling
    - Latest model versions
    
    Cons:
    - Requires internet connection
    - Usage-based pricing (~$0.003-0.015 per 1K tokens)
    - Data sent to external service
    - Rate limits (though usually generous)
    
    Self-hosted Ollama:
    Pros:
    - Complete data privacy (local processing)
    - No usage costs after setup
    - Works offline
    - Full control over model and parameters
    
    Cons:
    - Requires 4-8GB local storage
    - Slower on consumer hardware
    - Manual model management
    - Potentially inconsistent quality
    """
    
    print("Starting AWS Bedrock Claude synthetic data generation...")
    print("\nConfiguration Check:")
    print(f"   AWS Region: {AWS_CONFIG['region_name']}")
    print(f"   AWS Access Key: {'Set' if AWS_CONFIG['aws_access_key_id'] else 'Missing'}")
    print(f"   AWS Secret Key: {'Set' if AWS_CONFIG['aws_secret_access_key'] else 'Missing'}")
    
    # Load and clean seed data
    seed_file_path = "data/course_analysis_ready_file_template_Identified_01_27_25.xlsx"
    
    if not os.path.exists(seed_file_path):
        print(f"Seed data file not found: {seed_file_path}")
        return
    
    seed_data = load_and_clean_seed_data(seed_file_path)
    
    if seed_data.empty:
        print("No seed data available")
        return
    
    print(f"\nSeed data columns: {seed_data.columns.tolist()}")
    print("Sample seed data:")
    print(seed_data.head(2))
    
    # Initialize Bedrock Claude generator
    generator = BedrockClaudeSyntheticDataGenerator()
    
    # Generate synthetic data for each database
    records_per_db = 50  # Reduced for testing - increase as needed
    total_estimated_cost = records_per_db * len(DATABASES) * 0.01  # Rough estimate
    
    print(f"\nEstimated API cost: ~${total_estimated_cost:.2f} (approximate)")
    print(f"Generating {records_per_db} records per database...")
    
    for db_info in DATABASES:
        db_name = db_info["dbname"]
        school_acronym = db_info["acronym"]
        
        print(f"\nProcessing database: {db_name} ({school_acronym})")
        
        # Generate synthetic data using Claude API
        start_time = time.time()
        synthetic_data = generator.generate_course_data(seed_data, records_per_db, school_acronym)
        generation_time = time.time() - start_time
        
        print(f"Generation time: {generation_time:.2f} seconds")
        
        if not synthetic_data:
            print(f"No data generated for {school_acronym}, skipping...")
            continue
        
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
        
        # Rate limiting - be respectful to the API
        time.sleep(2)
    
    print("\nAWS Bedrock Claude synthetic data generation completed!")
    print("\nNext steps:")
    print("   1. Check your AWS billing for usage costs")
    print("   2. Verify data quality in your databases")
    print("   3. Consider adjusting records_per_db for production use")

if __name__ == "__main__":
    main()
