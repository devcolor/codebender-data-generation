# DevColor Database Project

This project contains scripts for setting up MariaDB databases and generating synthetic data for educational institutions.

## Prerequisites

### 1. Install Ollama (Optional - for LLM-generated data)

**Windows:**
1. Go to https://ollama.ai and download the Windows installer
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

## Data Generation Scripts (in generate_data/ folder)

### `test_ollama.py`
- Tests if Ollama is running and accessible
- Checks if Mistral model is available
- Performs a test generation to verify functionality

### `course_synthetic.py`
- Generates synthetic course data using Ollama Mistral LLM
- Reads seed data from `data/course_analysis_ready_file_template_Identified_01_27_25.xlsx`
- Removes rows 12+ from seed data (keeps first 11 rows as clean seed data)
- Generates 200 records per database
- Adds school acronym to each record
- Has fallback generation if Ollama is not available

### `cohort_synthetic.py`
- Generates synthetic cohort data
- Creates cohort names with semester/year/program combinations
- Generates appropriate start/end dates
- Adds 50 records per database

### `financial_aid_synthetic.py`
- Generates synthetic financial aid data
- Creates realistic aid types (grants, loans, scholarships, work-study)
- Generates appropriate amounts based on aid type
- Adds 100 records per database

## Usage

### 1. Test Ollama connection (optional):
```bash
cd generate_data
python test_ollama.py
```

### 2. Generate synthetic data:
```bash
python course_synthetic.py
python cohort_synthetic.py
python financial_aid_synthetic.py
```

### 3. Count records (optional):
```bash
python count_records.py
```

### 4. Generate Excel summary (optional):
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
devcolor/
├── .env                          # Database configuration
├── requirements.txt              # Python dependencies
├── db_setup.py                  # Creates databases and tables
├── test_db_connection.py        # Tests database connection
├── count_records.py             # Counts records in all tables
├── rename_databases.py          # Utility to rename databases
├── data/                        # Seed data files
│   └── course_analysis_ready_file_template_Identified_01_27_25.xlsx
└── generate_data/               # Synthetic data generation scripts
    ├── test_ollama.py
    ├── course_synthetic.py
    ├── cohort_synthetic.py
    └── financial_aid_synthetic.py
```
