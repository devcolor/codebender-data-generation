"""
FAST VERSION: Generate what_if_data using batch processing and parallel execution.
Uses bulk queries and multiprocessing to dramatically speed up generation.
"""

import sys
import os
from pathlib import Path
import random
from decimal import Decimal
from datetime import datetime
import json
from multiprocessing import Pool, cpu_count
from functools import partial

# Add parent directory to path
sys.path.append(str(Path(__file__).parent.parent))
from shared.config import get_db_connection

# Import all the mappings and functions from the original script
from what_if_data import (
    PROGRAM_INDUSTRY_MAP, JOB_CATEGORIES_BY_INDUSTRY, TECHNICAL_SKILLS_BY_PROGRAM,
    SOFT_SKILLS, CERTIFICATIONS_BY_PROGRAM, KENTUCKY_INDUSTRY_DEMAND, SALARY_RANGES,
    get_program_from_cip, calculate_predictions
)

DATABASE = "Kentucky_Community_and_Technical_College_System"


def fetch_all_data_bulk():
    """Fetch ALL student data in bulk - much faster than individual queries."""
    print("Fetching all student data in bulk...")
    conn = get_db_connection(DATABASE)
    cursor = conn.cursor(dictionary=True)
    
    try:
        # Get all cohort data at once
        print("  Loading cohort data...")
        cursor.execute("SELECT * FROM cohort WHERE Student_GUID IS NOT NULL")
        cohort_data = cursor.fetchall()
        cohort_dict = {row['Student_GUID']: row for row in cohort_data}
        print(f"    ✓ Loaded {len(cohort_dict):,} cohort records")
        
        # Get all course data at once
        print("  Loading course data...")
        cursor.execute("""
            SELECT Student_GUID, Course_CIP, Grade, Number_of_Credits_Earned
            FROM course 
            WHERE Student_GUID IS NOT NULL
        """)
        course_data = cursor.fetchall()
        
        # Group courses by student
        course_dict = {}
        for row in course_data:
            student_guid = row['Student_GUID']
            if student_guid not in course_dict:
                course_dict[student_guid] = []
            course_dict[student_guid].append(row)
        print(f"    ✓ Loaded {len(course_data):,} course records for {len(course_dict):,} students")
        
        return cohort_dict, course_dict
        
    finally:
        cursor.close()
        conn.close()


def generate_student_record(student_guid, cohort_dict, course_dict):
    """Generate what_if record for a single student (for parallel processing)."""
    try:
        cohort_data = cohort_dict.get(student_guid)
        course_data = course_dict.get(student_guid, [])
        
        if not cohort_data:
            return None
        
        # Determine program
        program_cip = None
        if course_data:
            cips = [c.get('Course_CIP') for c in course_data if c.get('Course_CIP')]
            if cips:
                program_cip = max(set(cips), key=cips.count)
        
        if not program_cip:
            program_cip = cohort_data.get('Program_of_Study_Year_1')
        
        program = get_program_from_cip(program_cip)
        
        # Calculate academic metrics
        total_credits_earned = cohort_data.get('Number_of_Credits_Earned_Year_1', 0) or 0
        total_credits_attempted = cohort_data.get('Number_of_Credits_Attempted_Year_1', 0) or 0
        
        for year in [2, 3, 4]:
            total_credits_earned += cohort_data.get(f'Number_of_Credits_Earned_Year_{year}', 0) or 0
            total_credits_attempted += cohort_data.get(f'Number_of_Credits_Attempted_Year_{year}', 0) or 0
        
        gpa = float(cohort_data.get('GPA_Group_Year_1', 0) or random.uniform(2.0, 3.8))
        
        # Generate skills
        technical_skills = TECHNICAL_SKILLS_BY_PROGRAM.get(program, ["General Skills", "Computer Literacy"])
        selected_technical = random.sample(technical_skills, min(len(technical_skills), random.randint(3, 5)))
        selected_soft = random.sample(SOFT_SKILLS, random.randint(4, 7))
        
        # Certifications
        cert_pool = CERTIFICATIONS_BY_PROGRAM.get(program, [])
        certs_earned = random.sample(cert_pool, min(len(cert_pool), random.randint(0, 2))) if cert_pool else []
        certs_in_progress = random.sample([c for c in cert_pool if c not in certs_earned], 
                                         min(len(cert_pool) - len(certs_earned), random.randint(0, 1))) if cert_pool else []
        
        # Experience
        internship_completed = random.choice(['Yes', 'No', 'No', 'In Progress'])
        internship_hours = random.randint(80, 400) if internship_completed == 'Yes' else 0
        work_experience_years = round(random.uniform(0, 5), 1)
        relevant_work = random.choice(['Yes', 'No', 'Partial'])
        
        # Activities
        activities = random.sample([
            "Student Government", "Honor Society", "Professional Club", "Volunteer Work",
            "Study Groups", "Peer Tutoring", "Campus Events", "Community Service"
        ], random.randint(0, 3))
        
        leadership = random.sample([
            "Club President", "Team Lead", "Volunteer Coordinator", "Peer Mentor"
        ], random.randint(0, 2)) if random.random() > 0.7 else []
        
        # Career interests
        job_categories = JOB_CATEGORIES_BY_INDUSTRY.get(
            PROGRAM_INDUSTRY_MAP.get(program, ["Business Services"])[0],
            ["Entry Level Position"]
        )
        stated_interest = random.choice(job_categories)
        interest_confidence = round(random.uniform(0.6, 0.95), 2)
        willing_relocate = random.choice(['Yes', 'No', 'Maybe'])
        work_env = random.choice(['Office', 'Remote', 'Hybrid', 'Field', 'Clinical', 'Industrial'])
        
        # Build student data dict
        student_data = {
            'gpa_cumulative': gpa,
            'total_credits_earned': total_credits_earned,
            'total_credits_attempted': total_credits_attempted,
            'internship_completed': internship_completed,
            'work_experience_years': work_experience_years
        }
        
        # Calculate predictions
        predictions = calculate_predictions(student_data, program)
        
        # Data quality score
        data_quality = round(random.uniform(0.75, 0.98), 2)
        
        return {
            'Student_GUID': student_guid,
            'Institution_ID': cohort_data.get('Institution_ID'),
            'Cohort': cohort_data.get('Cohort'),
            'Cohort_Term': cohort_data.get('Cohort_Term'),
            'school': 'KCTCS',
            'primary_program': program,
            'secondary_program': random.choice([None, "Business", "General Studies"]),
            'total_credits_earned': total_credits_earned,
            'total_credits_attempted': total_credits_attempted,
            'gpa_cumulative': gpa,
            'technical_skills': selected_technical,
            'soft_skills': selected_soft,
            'certifications_earned': certs_earned,
            'certifications_in_progress': certs_in_progress,
            'internship_completed': internship_completed,
            'internship_hours': internship_hours,
            'work_experience_years': work_experience_years,
            'relevant_work_experience': relevant_work,
            'extracurricular_activities': activities,
            'leadership_roles': leadership,
            'stated_career_interest': stated_interest,
            'career_interest_confidence': interest_confidence,
            'willing_to_relocate': willing_relocate,
            'preferred_work_environment': work_env,
            **predictions,
            'data_quality_score': data_quality
        }
        
    except Exception as e:
        print(f"Error processing {student_guid}: {e}")
        return None


def bulk_insert_records(records, cursor):
    """Insert multiple records at once using bulk insert."""
    if not records:
        return 0
    
    # Build bulk insert query
    placeholders = "(%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"
    
    sql = f"""
    INSERT INTO what_if_data (
        Student_GUID, Institution_ID, Cohort, Cohort_Term, school,
        primary_program, secondary_program, total_credits_earned, total_credits_attempted, gpa_cumulative,
        technical_skills, soft_skills, certifications_earned, certifications_in_progress,
        internship_completed, internship_hours, work_experience_years, relevant_work_experience,
        extracurricular_activities, leadership_roles,
        stated_career_interest, career_interest_confidence, willing_to_relocate, preferred_work_environment,
        pred_top_industry, pred_industry_confidence, pred_alternative_industries, pred_industry_growth_rate,
        pred_top_job_category, pred_job_confidence, pred_alternative_jobs, pred_job_placement_probability,
        pred_regional_demand_score, pred_salary_range_low, pred_salary_range_high, pred_salary_median,
        pred_industry_readiness_score, pred_skill_match_percentage, pred_experience_gap_years, pred_time_to_employment_months,
        data_quality_score
    ) VALUES {', '.join([placeholders] * len(records))}
    """
    
    # Flatten all values
    values = []
    for rec in records:
        values.extend([
            rec['Student_GUID'], rec['Institution_ID'], rec['Cohort'], rec['Cohort_Term'], rec['school'],
            rec['primary_program'], rec['secondary_program'], rec['total_credits_earned'], 
            rec['total_credits_attempted'], rec['gpa_cumulative'],
            json.dumps(rec['technical_skills']), json.dumps(rec['soft_skills']),
            json.dumps(rec['certifications_earned']), json.dumps(rec['certifications_in_progress']),
            rec['internship_completed'], rec['internship_hours'], rec['work_experience_years'],
            rec['relevant_work_experience'],
            json.dumps(rec['extracurricular_activities']), json.dumps(rec['leadership_roles']),
            rec['stated_career_interest'], rec['career_interest_confidence'],
            rec['willing_to_relocate'], rec['preferred_work_environment'],
            rec['pred_top_industry'], rec['pred_industry_confidence'],
            json.dumps(rec['pred_alternative_industries']), rec['pred_industry_growth_rate'],
            rec['pred_top_job_category'], rec['pred_job_confidence'],
            json.dumps(rec['pred_alternative_jobs']), rec['pred_job_placement_probability'],
            rec['pred_regional_demand_score'], rec['pred_salary_range_low'],
            rec['pred_salary_range_high'], rec['pred_salary_median'],
            rec['pred_industry_readiness_score'], rec['pred_skill_match_percentage'],
            rec['pred_experience_gap_years'], rec['pred_time_to_employment_months'],
            rec['data_quality_score']
        ])
    
    cursor.execute(sql, values)
    return len(records)


def create_table(cursor):
    """Create the what_if_data table."""
    drop_sql = "DROP TABLE IF EXISTS what_if_data"
    cursor.execute(drop_sql)
    
    create_sql = """
    CREATE TABLE what_if_data (
        id BIGINT AUTO_INCREMENT PRIMARY KEY,
        Student_GUID VARCHAR(58) NOT NULL,
        Institution_ID BIGINT,
        Cohort VARCHAR(57),
        Cohort_Term VARCHAR(56),
        school VARCHAR(10),
        primary_program VARCHAR(100),
        secondary_program VARCHAR(100),
        total_credits_earned INT,
        total_credits_attempted INT,
        gpa_cumulative DECIMAL(3,2),
        technical_skills JSON,
        soft_skills JSON,
        certifications_earned JSON,
        certifications_in_progress JSON,
        internship_completed VARCHAR(20),
        internship_hours INT,
        work_experience_years DECIMAL(3,1),
        relevant_work_experience VARCHAR(20),
        extracurricular_activities JSON,
        leadership_roles JSON,
        stated_career_interest VARCHAR(100),
        career_interest_confidence DECIMAL(3,2),
        willing_to_relocate VARCHAR(10),
        preferred_work_environment VARCHAR(50),
        pred_top_industry VARCHAR(100),
        pred_industry_confidence DECIMAL(5,4),
        pred_alternative_industries JSON,
        pred_industry_growth_rate DECIMAL(5,4),
        pred_top_job_category VARCHAR(100),
        pred_job_confidence DECIMAL(5,4),
        pred_alternative_jobs JSON,
        pred_job_placement_probability DECIMAL(5,4),
        pred_regional_demand_score DECIMAL(5,4),
        pred_salary_range_low INT,
        pred_salary_range_high INT,
        pred_salary_median INT,
        pred_industry_readiness_score DECIMAL(5,4),
        pred_skill_match_percentage DECIMAL(5,4),
        pred_experience_gap_years DECIMAL(3,1),
        pred_time_to_employment_months INT,
        llm_career_summary TEXT,
        llm_strengths JSON,
        llm_skill_gaps JSON,
        llm_recommended_actions JSON,
        llm_career_pathway TEXT,
        llm_salary_justification TEXT,
        prediction_model_version VARCHAR(50) DEFAULT 'v1',
        data_quality_score DECIMAL(3,2),
        last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        INDEX idx_student (Student_GUID),
        INDEX idx_school (school),
        INDEX idx_industry (pred_top_industry),
        INDEX idx_job (pred_top_job_category),
        UNIQUE KEY unique_student (Student_GUID)
    )
    """
    cursor.execute(create_sql)


def generate_what_if_data_fast():
    """FAST generation using bulk queries and parallel processing."""
    print(f"\n{'='*80}")
    print(f"FAST WHAT_IF_DATA GENERATION FOR KENTUCKY")
    print(f"{'='*80}\n")
    
    # Fetch all data in bulk (2 queries instead of 65,600!)
    cohort_dict, course_dict = fetch_all_data_bulk()
    student_guids = list(cohort_dict.keys())
    total_students = len(student_guids)
    
    print(f"\nGenerating predictions for {total_students:,} students...")
    print(f"Using {cpu_count()} CPU cores for parallel processing\n")
    
    # Create table
    conn = get_db_connection(DATABASE)
    cursor = conn.cursor()
    
    try:
        print("Creating what_if_data table...")
        create_table(cursor)
        conn.commit()
        print("✓ Table created\n")
        
        # Process in parallel batches
        batch_size = 1000
        insert_batch_size = 500  # Insert 500 records at a time
        total_inserted = 0
        
        print("Progress:")
        for batch_start in range(0, total_students, batch_size):
            batch_end = min(batch_start + batch_size, total_students)
            batch_guids = student_guids[batch_start:batch_end]
            
            # Generate records in parallel
            with Pool(processes=cpu_count()) as pool:
                generate_func = partial(generate_student_record, cohort_dict=cohort_dict, course_dict=course_dict)
                batch_records = pool.map(generate_func, batch_guids)
            
            # Filter out None results
            batch_records = [r for r in batch_records if r is not None]
            
            # Insert in sub-batches
            for insert_start in range(0, len(batch_records), insert_batch_size):
                insert_end = min(insert_start + insert_batch_size, len(batch_records))
                insert_batch = batch_records[insert_start:insert_end]
                
                inserted = bulk_insert_records(insert_batch, cursor)
                total_inserted += inserted
            
            # Commit after each batch
            conn.commit()
            
            # Progress bar
            pct = (batch_end / total_students) * 100
            bar_length = 50
            filled = int(bar_length * batch_end / total_students)
            bar = '█' * filled + '░' * (bar_length - filled)
            print(f"\r  [{bar}] {batch_end:,}/{total_students:,} ({pct:.1f}%) - {total_inserted:,} records inserted", end='', flush=True)
        
        print(f"\n\n{'='*80}")
        print(f"COMPLETE!")
        print(f"{'='*80}")
        print(f"Total students processed: {total_students:,}")
        print(f"Records inserted: {total_inserted:,}")
        print(f"{'='*80}\n")
        
    finally:
        cursor.close()
        conn.close()


if __name__ == "__main__":
    import time
    start_time = time.time()
    
    generate_what_if_data_fast()
    
    elapsed = time.time() - start_time
    print(f"Total time: {elapsed:.1f} seconds ({elapsed/60:.1f} minutes)")
