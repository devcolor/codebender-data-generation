"""
Generate what_if_data table for Kentucky students with industry readiness and job predictions.
Includes mock data for columns not in course/cohort tables.
"""

import sys
import os
from pathlib import Path
import random
from decimal import Decimal
from datetime import datetime

# Add parent directory to path
sys.path.append(str(Path(__file__).parent.parent))
from shared.config import get_db_connection

# Database name
DATABASE = "Kentucky_Community_and_Technical_College_System"

# Industry and job mappings based on common community college programs
PROGRAM_INDUSTRY_MAP = {
    # Healthcare
    "Nursing": ["Healthcare", "Medical Services", "Long-term Care"],
    "Medical Assisting": ["Healthcare", "Medical Services", "Clinical Services"],
    "Dental Hygiene": ["Healthcare", "Dental Services"],
    "Radiologic Technology": ["Healthcare", "Medical Imaging", "Diagnostic Services"],
    "Respiratory Therapy": ["Healthcare", "Critical Care", "Medical Services"],
    
    # Technology
    "Computer Science": ["Information Technology", "Software Development", "Tech Services"],
    "Information Technology": ["Information Technology", "IT Support", "Cybersecurity"],
    "Cybersecurity": ["Information Technology", "Cybersecurity", "Network Security"],
    "Web Development": ["Information Technology", "Software Development", "Digital Media"],
    
    # Business
    "Business Administration": ["Business Services", "Management", "Finance"],
    "Accounting": ["Finance", "Business Services", "Tax Services"],
    "Marketing": ["Marketing", "Business Services", "Sales"],
    "Management": ["Business Services", "Management", "Operations"],
    
    # Skilled Trades
    "Welding": ["Manufacturing", "Construction", "Industrial Services"],
    "HVAC": ["Construction", "Building Services", "Maintenance"],
    "Electrical Technology": ["Construction", "Electrical Services", "Industrial Services"],
    "Automotive Technology": ["Automotive Services", "Transportation", "Repair Services"],
    "Diesel Technology": ["Transportation", "Automotive Services", "Heavy Equipment"],
    
    # Education & Social Services
    "Early Childhood Education": ["Education", "Childcare Services", "Social Services"],
    "Social Work": ["Social Services", "Healthcare", "Community Services"],
    "Human Services": ["Social Services", "Community Services", "Healthcare"],
    
    # Other
    "Criminal Justice": ["Public Safety", "Law Enforcement", "Corrections"],
    "Fire Science": ["Public Safety", "Emergency Services", "Fire Protection"],
    "Culinary Arts": ["Hospitality", "Food Services", "Restaurant Management"],
    "General Studies": ["Various Industries", "Business Services", "Public Services"]
}

JOB_CATEGORIES_BY_INDUSTRY = {
    "Healthcare": ["Registered Nurse", "Medical Assistant", "Healthcare Technician", "Clinical Coordinator", "Patient Care Specialist"],
    "Medical Services": ["Medical Assistant", "Clinical Support Specialist", "Healthcare Administrator", "Medical Records Technician"],
    "Information Technology": ["IT Support Specialist", "Network Administrator", "Software Developer", "Systems Analyst", "Database Administrator"],
    "Software Development": ["Junior Developer", "Web Developer", "Application Developer", "Software Engineer", "Full Stack Developer"],
    "Business Services": ["Business Analyst", "Administrative Manager", "Operations Coordinator", "Project Manager", "Account Manager"],
    "Finance": ["Accountant", "Financial Analyst", "Bookkeeper", "Tax Preparer", "Auditor"],
    "Manufacturing": ["Production Technician", "Quality Control Inspector", "Manufacturing Engineer", "Welder", "Machine Operator"],
    "Construction": ["Electrician", "HVAC Technician", "Construction Manager", "Building Inspector", "Project Coordinator"],
    "Education": ["Teacher", "Educational Assistant", "Childcare Director", "Curriculum Coordinator", "Student Services Coordinator"],
    "Public Safety": ["Police Officer", "Corrections Officer", "Emergency Dispatcher", "Security Manager", "Fire Fighter"],
    "Hospitality": ["Chef", "Restaurant Manager", "Catering Manager", "Food Service Director", "Culinary Supervisor"]
}

TECHNICAL_SKILLS_BY_PROGRAM = {
    "Nursing": ["Patient Care", "Medical Terminology", "Clinical Procedures", "Medication Administration", "Electronic Health Records"],
    "Computer Science": ["Programming", "Data Structures", "Algorithms", "Database Management", "Software Engineering"],
    "Information Technology": ["Network Administration", "System Configuration", "Troubleshooting", "Cybersecurity", "Cloud Computing"],
    "Business Administration": ["Financial Analysis", "Project Management", "Business Strategy", "Operations Management", "Data Analysis"],
    "Welding": ["MIG Welding", "TIG Welding", "Blueprint Reading", "Metal Fabrication", "Safety Procedures"],
    "HVAC": ["HVAC Systems", "Refrigeration", "Electrical Systems", "Troubleshooting", "Building Codes"],
    "Accounting": ["Financial Reporting", "Tax Preparation", "Bookkeeping", "Auditing", "QuickBooks"],
    "Culinary Arts": ["Food Preparation", "Menu Planning", "Food Safety", "Kitchen Management", "Nutrition"],
    "Criminal Justice": ["Law Enforcement", "Criminal Law", "Investigation", "Report Writing", "Crisis Management"],
    "Early Childhood Education": ["Child Development", "Curriculum Planning", "Classroom Management", "Assessment", "Family Engagement"]
}

SOFT_SKILLS = [
    "Communication", "Teamwork", "Problem Solving", "Critical Thinking", "Time Management",
    "Leadership", "Adaptability", "Attention to Detail", "Customer Service", "Conflict Resolution",
    "Organization", "Work Ethic", "Interpersonal Skills", "Decision Making", "Creativity"
]

CERTIFICATIONS_BY_PROGRAM = {
    "Nursing": ["RN License", "BLS Certification", "ACLS Certification", "Specialty Certifications"],
    "Information Technology": ["CompTIA A+", "CompTIA Network+", "CompTIA Security+", "CCNA", "Microsoft Certified"],
    "Welding": ["AWS Certification", "ASME Certification", "State Welding License"],
    "HVAC": ["EPA 608 Certification", "NATE Certification", "State HVAC License"],
    "Accounting": ["CPA License", "CMA Certification", "QuickBooks Certified"],
    "Culinary Arts": ["ServSafe Certification", "Food Handler License", "Sommelier Certification"],
    "Business Administration": ["PMP Certification", "Six Sigma", "Business Analytics Certificate"]
}

# Regional demand scores by industry for Kentucky
KENTUCKY_INDUSTRY_DEMAND = {
    "Healthcare": 0.92,
    "Medical Services": 0.88,
    "Manufacturing": 0.85,
    "Business Services": 0.78,
    "Information Technology": 0.82,
    "Construction": 0.80,
    "Education": 0.75,
    "Public Safety": 0.70,
    "Transportation": 0.77,
    "Hospitality": 0.65
}

# Salary ranges by job category (Kentucky market)
SALARY_RANGES = {
    "Registered Nurse": (52000, 68000),
    "Medical Assistant": (28000, 38000),
    "IT Support Specialist": (38000, 52000),
    "Software Developer": (55000, 75000),
    "Accountant": (42000, 58000),
    "Welder": (35000, 50000),
    "HVAC Technician": (38000, 55000),
    "Teacher": (38000, 48000),
    "Police Officer": (40000, 55000),
    "Chef": (32000, 48000),
    "Business Analyst": (48000, 65000),
    "Network Administrator": (50000, 70000),
    "Healthcare Technician": (32000, 45000),
    "Electrician": (42000, 60000),
    "Default": (30000, 45000)
}


def create_what_if_data_table(cursor):
    """Create the what_if_data table."""
    print("Creating what_if_data table...")
    
    drop_sql = "DROP TABLE IF EXISTS what_if_data"
    cursor.execute(drop_sql)
    
    create_sql = """
    CREATE TABLE what_if_data (
        id BIGINT AUTO_INCREMENT PRIMARY KEY,
        
        -- Student Identifiers
        Student_GUID VARCHAR(58) NOT NULL,
        Institution_ID BIGINT,
        Cohort VARCHAR(57),
        Cohort_Term VARCHAR(56),
        school VARCHAR(10),
        
        -- Academic Profile (derived from existing data)
        primary_program VARCHAR(100),
        secondary_program VARCHAR(100),
        total_credits_earned INT,
        total_credits_attempted INT,
        gpa_cumulative DECIMAL(3,2),
        
        -- NEW: Skills Data (not in course/cohort)
        technical_skills JSON,
        soft_skills JSON,
        certifications_earned JSON,
        certifications_in_progress JSON,
        
        -- NEW: Experience & Activities (mock data)
        internship_completed VARCHAR(20),
        internship_hours INT,
        work_experience_years DECIMAL(3,1),
        relevant_work_experience VARCHAR(20),
        extracurricular_activities JSON,
        leadership_roles JSON,
        
        -- NEW: Career Interests (mock data)
        stated_career_interest VARCHAR(100),
        career_interest_confidence DECIMAL(3,2),
        willing_to_relocate VARCHAR(10),
        preferred_work_environment VARCHAR(50),
        
        -- PREDICTION: Industry Predictions
        pred_top_industry VARCHAR(100),
        pred_industry_confidence DECIMAL(5,4),
        pred_alternative_industries JSON,
        pred_industry_growth_rate DECIMAL(5,4),
        
        -- PREDICTION: Job Predictions
        pred_top_job_category VARCHAR(100),
        pred_job_confidence DECIMAL(5,4),
        pred_alternative_jobs JSON,
        pred_job_placement_probability DECIMAL(5,4),
        
        -- PREDICTION: Market Data
        pred_regional_demand_score DECIMAL(5,4),
        pred_salary_range_low INT,
        pred_salary_range_high INT,
        pred_salary_median INT,
        
        -- PREDICTION: Readiness Metrics
        pred_industry_readiness_score DECIMAL(5,4),
        pred_skill_match_percentage DECIMAL(5,4),
        pred_experience_gap_years DECIMAL(3,1),
        pred_time_to_employment_months INT,
        
        -- LLM: Generated Insights
        llm_career_summary TEXT,
        llm_strengths JSON,
        llm_skill_gaps JSON,
        llm_recommended_actions JSON,
        llm_career_pathway TEXT,
        llm_salary_justification TEXT,
        
        -- Metadata
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
    print("✓ Created what_if_data table")


def get_program_from_cip(cip_code):
    """Map CIP code to program name (simplified)."""
    if not cip_code:
        return "General Studies"
    
    cip_str = str(cip_code)
    
    # Healthcare (51.xxxx)
    if cip_str.startswith('51'):
        programs = ["Nursing", "Medical Assisting", "Dental Hygiene", "Radiologic Technology", "Respiratory Therapy"]
        return random.choice(programs)
    
    # Computer Science (11.xxxx)
    elif cip_str.startswith('11'):
        programs = ["Computer Science", "Information Technology", "Cybersecurity", "Web Development"]
        return random.choice(programs)
    
    # Business (52.xxxx)
    elif cip_str.startswith('52'):
        programs = ["Business Administration", "Accounting", "Marketing", "Management"]
        return random.choice(programs)
    
    # Engineering/Trades (15.xxxx, 46.xxxx, 47.xxxx, 48.xxxx)
    elif cip_str.startswith(('15', '46', '47', '48')):
        programs = ["Welding", "HVAC", "Electrical Technology", "Automotive Technology", "Diesel Technology"]
        return random.choice(programs)
    
    # Education (13.xxxx)
    elif cip_str.startswith('13'):
        return "Early Childhood Education"
    
    # Criminal Justice (43.xxxx)
    elif cip_str.startswith('43'):
        return random.choice(["Criminal Justice", "Fire Science"])
    
    # Culinary (12.xxxx)
    elif cip_str.startswith('12'):
        return "Culinary Arts"
    
    else:
        return "General Studies"


def calculate_predictions(student_data, program):
    """Calculate all prediction metrics for a student."""
    
    # Get industry predictions
    industries = PROGRAM_INDUSTRY_MAP.get(program, ["Various Industries", "Business Services"])
    top_industry = industries[0]
    
    # Base confidence on GPA and credits
    gpa = student_data.get('gpa_cumulative', 2.5)
    credits_earned = student_data.get('total_credits_earned', 0)
    credits_attempted = student_data.get('total_credits_attempted', 1)
    completion_rate = credits_earned / max(credits_attempted, 1)
    
    # Industry confidence (0.5 to 0.95)
    industry_confidence = min(0.95, 0.5 + (gpa / 4.0) * 0.3 + completion_rate * 0.15)
    
    # Get job predictions
    job_categories = JOB_CATEGORIES_BY_INDUSTRY.get(top_industry, ["Entry Level Position"])
    top_job = job_categories[0]
    
    # Job confidence slightly lower than industry
    job_confidence = industry_confidence * random.uniform(0.85, 0.95)
    
    # Job placement probability
    base_placement = 0.65
    gpa_factor = (gpa - 2.0) / 2.0 * 0.15  # Up to +15% for high GPA
    completion_factor = completion_rate * 0.10  # Up to +10% for completion
    experience_factor = 0.05 if student_data.get('internship_completed') == 'Yes' else 0
    
    placement_probability = min(0.95, base_placement + gpa_factor + completion_factor + experience_factor)
    
    # Regional demand
    regional_demand = KENTUCKY_INDUSTRY_DEMAND.get(top_industry, 0.70)
    
    # Salary range
    salary_range = SALARY_RANGES.get(top_job, SALARY_RANGES["Default"])
    salary_low = salary_range[0]
    salary_high = salary_range[1]
    salary_median = int((salary_low + salary_high) / 2)
    
    # Readiness score (0-1)
    readiness_score = (
        gpa / 4.0 * 0.30 +
        completion_rate * 0.25 +
        (1.0 if student_data.get('internship_completed') == 'Yes' else 0.5) * 0.20 +
        regional_demand * 0.15 +
        random.uniform(0.05, 0.10)  # Random factor
    )
    readiness_score = min(0.95, readiness_score)
    
    # Skill match percentage
    skill_match = readiness_score * random.uniform(0.85, 1.0)
    
    # Experience gap (0-3 years)
    if student_data.get('work_experience_years', 0) >= 1:
        experience_gap = random.uniform(0, 1.0)
    else:
        experience_gap = random.uniform(0.5, 2.5)
    
    # Time to employment (1-12 months)
    time_to_employment = int(12 * (1 - readiness_score) + random.randint(1, 3))
    
    # Growth rate
    growth_rate = random.uniform(0.02, 0.08)  # 2-8% annual growth
    
    return {
        'pred_top_industry': top_industry,
        'pred_industry_confidence': round(industry_confidence, 4),
        'pred_alternative_industries': industries[1:3] if len(industries) > 1 else [],
        'pred_industry_growth_rate': round(growth_rate, 4),
        'pred_top_job_category': top_job,
        'pred_job_confidence': round(job_confidence, 4),
        'pred_alternative_jobs': job_categories[1:4] if len(job_categories) > 1 else [],
        'pred_job_placement_probability': round(placement_probability, 4),
        'pred_regional_demand_score': round(regional_demand, 4),
        'pred_salary_range_low': salary_low,
        'pred_salary_range_high': salary_high,
        'pred_salary_median': salary_median,
        'pred_industry_readiness_score': round(readiness_score, 4),
        'pred_skill_match_percentage': round(skill_match, 4),
        'pred_experience_gap_years': round(experience_gap, 1),
        'pred_time_to_employment_months': time_to_employment
    }


def generate_mock_data_for_student(student_guid, cohort_data, course_data):
    """Generate all mock data for columns not in course/cohort."""
    
    # Determine program
    program_cip = None
    if course_data:
        # Get most common CIP from courses
        cips = [c.get('Course_CIP') for c in course_data if c.get('Course_CIP')]
        if cips:
            program_cip = max(set(cips), key=cips.count)
    
    if not program_cip and cohort_data:
        program_cip = cohort_data.get('Program_of_Study_Year_1')
    
    program = get_program_from_cip(program_cip)
    
    # Calculate academic metrics
    total_credits_earned = cohort_data.get('Number_of_Credits_Earned_Year_1', 0) or 0
    total_credits_attempted = cohort_data.get('Number_of_Credits_Attempted_Year_1', 0) or 0
    
    # Add year 2-4 if available
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


def insert_what_if_record(cursor, data):
    """Insert a what_if_data record."""
    import json
    
    sql = """
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
    ) VALUES (
        %s, %s, %s, %s, %s,
        %s, %s, %s, %s, %s,
        %s, %s, %s, %s,
        %s, %s, %s, %s,
        %s, %s,
        %s, %s, %s, %s,
        %s, %s, %s, %s,
        %s, %s, %s, %s,
        %s, %s, %s, %s,
        %s, %s, %s, %s,
        %s
    )
    """
    
    values = (
        data['Student_GUID'], data['Institution_ID'], data['Cohort'], data['Cohort_Term'], data['school'],
        data['primary_program'], data['secondary_program'], data['total_credits_earned'], 
        data['total_credits_attempted'], data['gpa_cumulative'],
        json.dumps(data['technical_skills']), json.dumps(data['soft_skills']),
        json.dumps(data['certifications_earned']), json.dumps(data['certifications_in_progress']),
        data['internship_completed'], data['internship_hours'], data['work_experience_years'],
        data['relevant_work_experience'],
        json.dumps(data['extracurricular_activities']), json.dumps(data['leadership_roles']),
        data['stated_career_interest'], data['career_interest_confidence'],
        data['willing_to_relocate'], data['preferred_work_environment'],
        data['pred_top_industry'], data['pred_industry_confidence'],
        json.dumps(data['pred_alternative_industries']), data['pred_industry_growth_rate'],
        data['pred_top_job_category'], data['pred_job_confidence'],
        json.dumps(data['pred_alternative_jobs']), data['pred_job_placement_probability'],
        data['pred_regional_demand_score'], data['pred_salary_range_low'],
        data['pred_salary_range_high'], data['pred_salary_median'],
        data['pred_industry_readiness_score'], data['pred_skill_match_percentage'],
        data['pred_experience_gap_years'], data['pred_time_to_employment_months'],
        data['data_quality_score']
    )
    
    cursor.execute(sql, values)


def generate_what_if_data(limit=None):
    """Main function to generate what_if_data for Kentucky students."""
    print(f"\n{'='*80}")
    print(f"GENERATING WHAT_IF_DATA FOR KENTUCKY")
    print(f"{'='*80}\n")
    
    conn = get_db_connection(DATABASE)
    cursor = conn.cursor(dictionary=True)
    
    try:
        # Create table
        create_what_if_data_table(cursor)
        conn.commit()
        
        # Get students from cohort
        print("\nFetching Kentucky students...")
        query = "SELECT DISTINCT Student_GUID, Institution_ID, Cohort, Cohort_Term FROM cohort WHERE Student_GUID IS NOT NULL"
        if limit:
            query += f" LIMIT {limit}"
        
        cursor.execute(query)
        students = cursor.fetchall()
        print(f"Found {len(students)} students to process")
        
        # Process each student with progress bar
        success_count = 0
        error_count = 0
        commit_batch_size = 5000
        
        print("\nProgress:")
        for i, student in enumerate(students, 1):
            student_guid = student['Student_GUID']
            
            try:
                # Get cohort data
                cursor.execute("""
                    SELECT * FROM cohort WHERE Student_GUID = %s LIMIT 1
                """, (student_guid,))
                cohort_data = cursor.fetchone()
                
                # Get course data
                cursor.execute("""
                    SELECT Course_CIP, Grade, Number_of_Credits_Earned
                    FROM course WHERE Student_GUID = %s
                """, (student_guid,))
                course_data = cursor.fetchall()
                
                # Generate mock data and predictions
                what_if_record = generate_mock_data_for_student(student_guid, cohort_data, course_data)
                
                # Insert record
                insert_what_if_record(cursor, what_if_record)
                success_count += 1
                
            except Exception as e:
                error_count += 1
                if error_count <= 5:  # Only print first few errors
                    print(f"\n  Error processing {student_guid}: {e}")
            
            # Progress bar and commit every 5000 records
            if i % commit_batch_size == 0:
                conn.commit()
                pct = (i / len(students)) * 100
                bar_length = 50
                filled = int(bar_length * i / len(students))
                bar = '█' * filled + '░' * (bar_length - filled)
                print(f"\r  [{bar}] {i:,}/{len(students):,} ({pct:.1f}%) - Committed to DB", end='', flush=True)
            elif i % 100 == 0:
                # Update progress bar every 100 records
                pct = (i / len(students)) * 100
                bar_length = 50
                filled = int(bar_length * i / len(students))
                bar = '█' * filled + '░' * (bar_length - filled)
                print(f"\r  [{bar}] {i:,}/{len(students):,} ({pct:.1f}%)", end='', flush=True)
        
        # Final commit
        conn.commit()
        print(f"\r  [{'█' * 50}] {len(students):,}/{len(students):,} (100.0%) - Complete!    ")
        
        # Summary
        print(f"\n{'='*80}")
        print(f"SUMMARY")
        print(f"{'='*80}")
        print(f"Total students: {len(students)}")
        print(f"Successfully generated: {success_count}")
        print(f"Errors: {error_count}")
        print(f"{'='*80}\n")
        
    finally:
        cursor.close()
        conn.close()


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Generate what_if_data for Kentucky students")
    parser.add_argument("--limit", type=int, help="Limit number of students to process")
    
    args = parser.parse_args()
    
    generate_what_if_data(limit=args.limit)
