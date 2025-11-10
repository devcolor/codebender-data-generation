# Database Operations

This folder contains all database-related utilities and scripts for the devcolor-data-gen project.

## Structure

```
dboperations/
├── db_setup.py                      # Database setup and configuration
├── count_records.py                 # Count records across all databases
├── generate_db_summary.py           # Generate database summary reports
├── create_complete_seed_structure.py # Create seed data structure
├── llm/                             # LLM-related database operations
│   ├── add_llm_table.py            # Add LLM recommendations table
│   ├── alter_add_school_column.py  # Add school column to tables
│   ├── check_progress.py           # Check LLM recommendation progress
│   ├── llm_student_readiness.py    # Generate student readiness recommendations
│   └── view_recommendations.py     # View LLM recommendations
└── testing/                         # Database testing and verification
    ├── test_db_connection.py       # Test database connections
    ├── verify_*.py                 # Various verification scripts
    ├── get_kctcs_*.py             # KCTCS schema scripts
    └── ...                         # Other testing utilities
```

## Core Scripts

### db_setup.py
Sets up all school databases with required tables (cohort, course, financial_aid, ar_*, llm_recommendations).

**Usage:**
```bash
python dboperations/db_setup.py
```

### count_records.py
Counts records in all tables across all school databases.

**Usage:**
```bash
python dboperations/count_records.py
```

### generate_db_summary.py
Generates an Excel summary of all databases with table structures and record counts.

**Usage:**
```bash
python dboperations/generate_db_summary.py
```

## LLM Operations

Scripts in `llm/` handle LLM-related database operations:

- **add_llm_table.py**: Creates llm_recommendations table in all databases
- **llm_student_readiness.py**: Generates student readiness recommendations using LLM
- **view_recommendations.py**: View stored recommendations
- **check_progress.py**: Monitor recommendation generation progress

## Testing Scripts

Scripts in `testing/` verify database integrity and test connections:

- **test_db_connection.py**: Test database connectivity
- **verify_*.py**: Various verification scripts for data integrity
- **display_schema.py**: Display database schemas
- **analyze_*.py**: Data analysis utilities

## Configuration

All scripts use the shared database configuration from `db_setup.py`:

```python
from dboperations.db_setup import DB_CONFIG, DATABASES
```

Database credentials are loaded from `.env` file in the project root.
