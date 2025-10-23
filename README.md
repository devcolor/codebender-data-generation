# Data Generation Scripts

This folder contains scripts for generating synthetic data for the database project.

## Scripts

### `course_synthetic.py`
- Generates synthetic course data using Ollama Mistral LLM
- Reads seed data from `../data/course_analysis_ready_file_template_Identified_01_27_25.xlsx`
- Removes rows 12+ from seed data (keeps first 11 rows as clean seed data)
- Generates 200 records per database (1000 total)
- Adds school acronym to each record
- Has fallback generation if Ollama is not available

**Database Distribution:**
- Bishop_State_Community_College (AL) - 200 records
- California_State_University_San_Bernardino (CSUSB) - 200 records  
- Kentucky_Community_and_Technical_College_System (KCTCS) - 200 records
- Thomas_More_University_KY (KY) - 200 records
- University_of_Akron_OH (OH) - 200 records

### `test_ollama.py`
- Tests if Ollama is running and accessible
- Checks if Mistral model is available
- Performs a test generation to verify functionality

## Usage

1. **Test Ollama first:**
   ```bash
   cd generate_data
   python test_ollama.py
   ```

2. **Generate course data:**
   ```bash
   python course_synthetic.py
   ```

## Requirements

- Ollama running with Mistral model
- Database connection configured in `.env`
- Required Python packages (see `../requirements.txt`)

## Table Structure

The course table includes:
- `id` (AUTO_INCREMENT PRIMARY KEY)
- `course_code` (VARCHAR(20))
- `course_title` (VARCHAR(255))
- `credits` (INT)
- `department` (VARCHAR(100))
- `prerequisites` (TEXT)
- `description` (TEXT)
- `school` (VARCHAR(10)) - School acronym
- `created_at` (TIMESTAMP)
