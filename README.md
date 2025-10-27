# DevColor Data Generation

This project contains scripts for setting up MariaDB databases and generating synthetic data for educational institutions using local or cloud-based LLMs.

## Prerequisites

### 1. Choose Your LLM Provider (Ollama or AWS Bedrock)

#### Option 1: Ollama (Recommended for local development)
**Installation:**
- **Windows:**
  1. Go to [ollama.ai](https://ollama.ai) and download the Windows installer
  2. Run the installer and follow setup instructions
  3. Alternative: `winget install Ollama.Ollama`

**Start Ollama Service:**
```bash
ollama serve
```

**Install Mistral Model:**
```bash
ollama pull mistral
```

**System Requirements:**
- RAM: At least 8GB (16GB recommended)
- Storage: 4-8GB for model files
- CPU: Any modern CPU (more cores = faster generation)

#### Option 2: AWS Bedrock (For production use)
**Requirements:**
- AWS account with Bedrock access
- IAM user with `bedrock:InvokeModel` permissions
- AWS CLI configured with valid credentials

**Environment Variables:**
```
AWS_ACCESS_KEY_ID=your_access_key
AWS_SECRET_ACCESS_KEY=your_secret_key
AWS_DEFAULT_REGION=your_region
```

### 2. Python Environment Setup

**Create virtual environment:**
```bash
python -m venv venv
.\venv\Scripts\Activate.ps1
```

**Install required packages:**
```bash
pip install -r requirements.txt
```

**Configure database connection in `.env`:**
```
DB_HOST=your_database_host
DB_USER=your_username
DB_PASSWORD=your_password
DB_PORT=3306
```

## Database Structure

Each database in this project contains the following three tables:
- `financial_aid`: Contains financial aid information for students
- `course`: Contains course-related data
- `cohort`: Contains cohort information for tracking student groups

## Database Setup

### 1. Create Databases and Tables
```bash
python db_setup.py
```

This creates 5 databases with 3 tables each:
- Bishop_State_Community_College (AL)
- California_State_University_San_Bernardino (CSUSB)
- Kentucky_Community_and_Technical_College_System (KCTCS)
- Thomas_More_University (KY)
- University_of_Akron (OH)

### 2. Test Database Connection
```bash
python test_db_connection.py
```

## Data Generation (School-Based Structure)

The data generation scripts are organized by school in the `generate_data/schools/` directory:

```
generate_data/schools/
├── shared/config.py              # Shared configuration and utilities
├── AL/                           # Bishop State Community College
│   ├── cohort.py
│   ├── course.py
│   ├── financial_aid.py
│   └── generate_all.py
├── CSUSB/                        # California State University San Bernardino
├── KCTCS/                        # Kentucky Community and Technical College System
├── KY/                           # Thomas More University
├── OH/                           # University of Akron
└── generate_all_schools.py       # Master script for all schools
```

### Generate Data for All Schools
```bash
cd generate_data/schools
python generate_all_schools.py
```
This generates all data types for all 5 schools (1,750 total records).

### Generate Data for a Specific School
```bash
cd generate_data/schools/AL
python generate_all.py
```
This generates all data types for one school (350 records).

### Generate Specific Data Type for a School
```bash
cd generate_data/schools/AL
python cohort.py           # 50 cohort records
python course.py           # 200 course records
python financial_aid.py    # 100 financial aid records
```

### Count Records
```bash
python count_records.py
```

### Generate Excel Summary
```bash
python generate_db_summary.py
```

## Data Summary

**Per Database:**
- Course Records: 200
- Cohort Records: 50
- Financial Aid Records: 100
- Total per school: 350 records

**Grand Total: 1,750 records across all databases**

## Table Structures

### Course Table
- `id` (AUTO_INCREMENT PRIMARY KEY)
- `code` (VARCHAR(50))
- `title` (VARCHAR(255))
- `credits` (INT)
- `description` (TEXT)
- `school` (VARCHAR(10)) - School acronym
- `created_at` (TIMESTAMP)

### Cohort Table
- `id` (AUTO_INCREMENT PRIMARY KEY)
- `name` (VARCHAR(255))
- `start_date` (DATE)
- `end_date` (DATE)
- `school` (VARCHAR(10)) - School acronym
- `created_at` (TIMESTAMP)

### Financial Aid Table
- `id` (AUTO_INCREMENT PRIMARY KEY)
- `student_id` (VARCHAR(50))
- `aid_type` (VARCHAR(100))
- `amount` (DECIMAL(10,2))
- `semester` (VARCHAR(20))
- `academic_year` (VARCHAR(20))
- `school` (VARCHAR(10)) - School acronym
- `created_at` (TIMESTAMP)

## Join-Ready Structure

All tables include a `school` column with matching acronyms (AL, CSUSB, KCTCS, KY, OH) for easy joins across:
- course <-> cohort <-> financial_aid

**Table Relationships:**
- Each table has an auto-incrementing `id` field (PRIMARY KEY) for unique record identification
- Tables can be joined using the `school` column to relate data across institutions
- The `id` fields serve as primary keys for referential integrity when creating relationships
- Example join: `SELECT * FROM course c JOIN cohort co ON c.school = co.school WHERE c.school = 'AL'`

## Fallback Generation

If Ollama is not available or fails, scripts automatically use rule-based synthetic data generation to ensure data is always created.

## Files Structure

```
devcolor-data-gen/
├── .env                          # Database configuration
├── requirements.txt              # Python dependencies
├── db_setup.py                  # Creates databases and tables
├── test_db_connection.py        # Tests database connection
├── count_records.py             # Counts records in all tables
├── generate_db_summary.py       # Generates Excel summary of databases
├── rename_databases.py          # Utility to rename databases
├── data/                        # Seed data files
│   └── course_analysis_ready_file_template_Identified_01_27_25.xlsx
└── generate_data/               # Synthetic data generation scripts
    ├── schools/                 # School-based generation scripts
    │   ├── shared/config.py     # Shared configuration
    │   ├── AL/                  # Bishop State Community College
    │   ├── CSUSB/               # California State University San Bernardino
    │   ├── KCTCS/               # Kentucky Community and Technical College System
    │   ├── KY/                  # Thomas More University
    │   ├── OH/                  # University of Akron
    │   └── generate_all_schools.py
    └── archive/                 # Old data-type-based scripts (for reference)
```
