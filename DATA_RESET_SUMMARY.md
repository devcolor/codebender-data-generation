# Database Reset and Population Summary

## Execution Date
**Completed:** October 26, 2025

## Overview
Successfully reset and repopulated all 5 university databases with new synthetic data derived from seed_data01 folder.

## Changes Made

### 1. Schema Updates
- **Added `dataset_type` column** to all tables (cohort, course, financial_aid)
  - Type: VARCHAR(1)
  - Default: 'S' (Synthetic)
  - Purpose: Distinguish between synthetic ('S') and real ('R') data

### 2. Data Reset
- **Deleted all existing records** from all 5 databases
- Tables cleared: financial_aid, course, cohort (in that order for FK integrity)

### 3. New Data Generation

#### Data Source
- **Seed Data:** `data/seed_data01/`
  - `cohort_AR_data_mock_A.csv` (5,457 rows, 85 columns)
  - `course_AR_data_mock.csv` (30,137 rows, 35 columns)
  - `financialaid_analysis_ready_file_template.xlsx` (5 rows, 21 columns)

#### Generation Rules Applied
- Each university has 3-5 distinct cohorts
- Each cohort contains 500-1,500 students (randomized)
- Each student enrolled in 4-6 courses
- Each student has one financial aid record
- All records marked with `dataset_type = 'S'`

## Results by University

### Bishop State Community College (AL)
- **Cohorts:** 4
- **Total Students:** 3,845
- **Course Enrollments:** 19,203
- **Financial Aid Records:** 3,845

**Cohort Details:**
1. 2019-20 - SPRING (Start: 2021-06-08, End: 2021-09-06)
2. 2017-18 - WINTER (Start: 2022-06-15, End: 2022-09-13)
3. 2016-17 - WINTER (Start: 2023-06-01, End: 2023-08-30)
4. 2020-21 - SPRING (Start: 2024-06-10, End: 2024-09-08)

### California State University San Bernardino (CSUSB)
- **Cohorts:** 5
- **Total Students:** 4,754
- **Course Enrollments:** 23,731
- **Financial Aid Records:** 4,754

**Cohort Details:**
1. 2020-21 - SPRING (Start: 2020-06-04, End: 2020-09-02)
2. 2019-20 - SUMMER (Start: 2020-06-07, End: 2020-09-05)
3. 2020-21 - WINTER (Start: 2020-06-08, End: 2020-09-06)
4. 2019-20 - SUMMER (Start: 2021-06-02, End: 2021-08-31)
5. 2020-21 - SPRING (Start: 2022-06-03, End: 2022-09-01)

### Kentucky Community and Technical College System (KCTCS)
- **Cohorts:** 5
- **Total Students:** 4,522
- **Course Enrollments:** 22,677
- **Financial Aid Records:** 4,522

**Cohort Details:**
1. 2017-18 - SUMMER (Start: 2020-06-05, End: 2020-09-03)
2. 2018-19 - FALL (Start: 2020-06-11, End: 2020-09-09)
3. 2020-21 - SPRING (Start: 2021-06-03, End: 2021-09-01)
4. 2018-19 - SPRING (Start: 2024-06-03, End: 2024-09-01)
5. 2019-20 - SPRING (Start: 2024-06-06, End: 2024-09-04)

### Thomas More University (KY)
- **Cohorts:** 4
- **Total Students:** 4,372
- **Course Enrollments:** 21,922
- **Financial Aid Records:** 4,372

**Cohort Details:**
1. 2016-17 - SUMMER (Start: 2020-06-08, End: 2020-09-06)
2. 2020-21 - FALL (Start: 2021-06-02, End: 2021-08-31)
3. 2020-21 - FALL (Start: 2021-06-15, End: 2021-09-13)
4. 2019-20 - FALL (Start: 2023-06-12, End: 2023-09-10)

### University of Akron (OH)
- **Cohorts:** 3
- **Total Students:** 3,660
- **Course Enrollments:** 18,193
- **Financial Aid Records:** 3,660

**Cohort Details:**
1. 2018-19 - FALL (Start: 2022-06-04, End: 2022-09-02)
2. 2017-18 - FALL (Start: 2022-06-07, End: 2022-09-05)
3. 2017-18 - SUMMER (Start: 2024-06-01, End: 2024-08-30)

## Grand Totals

| Metric | Count |
|--------|-------|
| **Total Cohorts** | 21 |
| **Total Students** | 21,153 |
| **Total Course Enrollments** | 105,726 |
| **Total Financial Aid Records** | 21,153 |
| **GRAND TOTAL RECORDS** | **126,900** |

## Data Integrity Verification

✓ All records properly marked as synthetic (dataset_type = 'S')
✓ Referential integrity maintained
✓ Student cohort sizes within specified range (500-1,500)
✓ Course enrollments properly distributed (4-6 per student)
✓ Financial aid records match student count (1:1 ratio)

## Database Schema

### Cohort Table
- id (AUTO_INCREMENT PRIMARY KEY)
- name (VARCHAR(255))
- start_date (DATE)
- end_date (DATE)
- school (VARCHAR(10))
- **dataset_type (VARCHAR(1))** ← NEW
- created_at (TIMESTAMP)

### Course Table
- id (AUTO_INCREMENT PRIMARY KEY)
- code (VARCHAR(50))
- title (VARCHAR(255))
- credits (INT)
- description (TEXT)
- school (VARCHAR(10))
- **dataset_type (VARCHAR(1))** ← NEW
- created_at (TIMESTAMP)

### Financial Aid Table
- id (AUTO_INCREMENT PRIMARY KEY)
- student_id (VARCHAR(50))
- aid_type (VARCHAR(100))
- amount (DECIMAL(10,2))
- semester (VARCHAR(20))
- academic_year (VARCHAR(20))
- school (VARCHAR(10))
- **dataset_type (VARCHAR(1))** ← NEW
- created_at (TIMESTAMP)

## Scripts Used

1. **reset_and_populate_databases.py** - Main script for reset and population
2. **verify_population.py** - Verification and reporting script
3. **examine_seed_data.py** - Seed data analysis script

## Future Considerations

- When real data becomes available, it should be marked with `dataset_type = 'R'`
- The system can now support mixed synthetic and real data
- Queries can filter by dataset_type to distinguish between data sources
- Example query: `SELECT * FROM cohort WHERE dataset_type = 'S'` (synthetic only)
- Example query: `SELECT * FROM cohort WHERE dataset_type = 'R'` (real only)

## Verification Commands

To verify the data at any time, run:
```bash
python verify_population.py
```

To count records:
```bash
python count_records.py
```

To generate Excel summary:
```bash
python generate_db_summary.py
```
