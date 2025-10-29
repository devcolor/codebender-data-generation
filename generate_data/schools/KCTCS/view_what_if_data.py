"""
View what_if_data predictions for Kentucky students.
"""

import sys
import os
from pathlib import Path
import json

# Add parent directory to path
sys.path.append(str(Path(__file__).parent.parent))
from shared.config import get_db_connection

DATABASE = "Kentucky_Community_and_Technical_College_System"


def view_what_if_data(limit=10, filter_industry=None, filter_job=None, show_llm=False):
    """View what_if_data records."""
    conn = get_db_connection(DATABASE)
    cursor = conn.cursor(dictionary=True)
    
    try:
        # Build query
        query = """
            SELECT 
                Student_GUID,
                primary_program,
                gpa_cumulative,
                total_credits_earned,
                internship_completed,
                work_experience_years,
                technical_skills,
                soft_skills,
                certifications_earned,
                pred_top_industry,
                pred_industry_confidence,
                pred_top_job_category,
                pred_job_confidence,
                pred_job_placement_probability,
                pred_salary_range_low,
                pred_salary_range_high,
                pred_salary_median,
                pred_industry_readiness_score,
                pred_skill_match_percentage,
                pred_time_to_employment_months,
                stated_career_interest,
                llm_career_summary,
                llm_strengths,
                llm_skill_gaps,
                llm_recommended_actions,
                llm_career_pathway,
                llm_salary_justification
            FROM what_if_data
            WHERE 1=1
        """
        
        params = []
        if filter_industry:
            query += " AND pred_top_industry = %s"
            params.append(filter_industry)
        
        if filter_job:
            query += " AND pred_top_job_category = %s"
            params.append(filter_job)
        
        query += " ORDER BY pred_job_placement_probability DESC LIMIT %s"
        params.append(limit)
        
        cursor.execute(query, params)
        results = cursor.fetchall()
        
        if not results:
            print("No records found")
            return
        
        print(f"\n{'='*100}")
        print(f"WHAT-IF DATA PREDICTIONS - KENTUCKY")
        print(f"{'='*100}\n")
        
        for i, rec in enumerate(results, 1):
            print(f"[{i}] Student: {rec['Student_GUID']}")
            print(f"    Program: {rec['primary_program']}")
            print(f"    GPA: {rec['gpa_cumulative']:.2f} | Credits: {rec['total_credits_earned']}")
            print(f"    Internship: {rec['internship_completed']} | Work Experience: {rec['work_experience_years']} years")
            
            # Technical skills
            tech_skills = json.loads(rec['technical_skills']) if rec['technical_skills'] else []
            print(f"\n    Technical Skills: {', '.join(tech_skills[:5])}")
            
            # Certifications
            certs = json.loads(rec['certifications_earned']) if rec['certifications_earned'] else []
            if certs:
                print(f"    Certifications: {', '.join(certs)}")
            
            print(f"\n    === PREDICTIONS ===")
            print(f"    Industry: {rec['pred_top_industry']} (confidence: {rec['pred_industry_confidence']:.1%})")
            print(f"    Job: {rec['pred_top_job_category']} (confidence: {rec['pred_job_confidence']:.1%})")
            print(f"    Job Placement Probability: {rec['pred_job_placement_probability']:.1%}")
            print(f"    Salary Range: ${rec['pred_salary_range_low']:,} - ${rec['pred_salary_range_high']:,} (median: ${rec['pred_salary_median']:,})")
            print(f"    Industry Readiness: {rec['pred_industry_readiness_score']:.1%}")
            print(f"    Skill Match: {rec['pred_skill_match_percentage']:.1%}")
            print(f"    Est. Time to Employment: {rec['pred_time_to_employment_months']} months")
            print(f"    Student's Career Interest: {rec['stated_career_interest']}")
            
            # Show LLM insights if available and requested
            if show_llm and rec.get('llm_career_summary'):
                print(f"\n    === LLM CAREER INSIGHTS ===")
                print(f"    Summary: {rec['llm_career_summary']}")
                
                if rec.get('llm_strengths'):
                    strengths = json.loads(rec['llm_strengths'])
                    print(f"\n    Strengths:")
                    for strength in strengths:
                        print(f"      ✓ {strength}")
                
                if rec.get('llm_skill_gaps'):
                    gaps = json.loads(rec['llm_skill_gaps'])
                    print(f"\n    Skill Gaps to Address:")
                    for gap in gaps:
                        print(f"      ⚠ {gap}")
                
                if rec.get('llm_recommended_actions'):
                    actions = json.loads(rec['llm_recommended_actions'])
                    print(f"\n    Recommended Actions:")
                    for action in actions:
                        print(f"      → {action}")
                
                if rec.get('llm_career_pathway'):
                    print(f"\n    Career Pathway: {rec['llm_career_pathway']}")
                
                if rec.get('llm_salary_justification'):
                    print(f"\n    Salary Justification: {rec['llm_salary_justification']}")
            
            print(f"\n{'-'*100}\n")
        
    finally:
        cursor.close()
        conn.close()


def show_statistics():
    """Show aggregate statistics."""
    conn = get_db_connection(DATABASE)
    cursor = conn.cursor(dictionary=True)
    
    try:
        print(f"\n{'='*100}")
        print(f"WHAT-IF DATA STATISTICS")
        print(f"{'='*100}\n")
        
        # Total records
        cursor.execute("SELECT COUNT(*) as count FROM what_if_data")
        total = cursor.fetchone()['count']
        print(f"Total Records: {total:,}\n")
        
        # Top industries
        print("Top Predicted Industries:")
        cursor.execute("""
            SELECT pred_top_industry, COUNT(*) as count,
                   AVG(pred_job_placement_probability) as avg_placement
            FROM what_if_data
            GROUP BY pred_top_industry
            ORDER BY count DESC
            LIMIT 10
        """)
        for row in cursor.fetchall():
            print(f"  {row['pred_top_industry']:30} {row['count']:5} students (avg placement: {row['avg_placement']:.1%})")
        
        # Top jobs
        print("\nTop Predicted Jobs:")
        cursor.execute("""
            SELECT pred_top_job_category, COUNT(*) as count,
                   AVG(pred_salary_median) as avg_salary
            FROM what_if_data
            GROUP BY pred_top_job_category
            ORDER BY count DESC
            LIMIT 10
        """)
        for row in cursor.fetchall():
            print(f"  {row['pred_top_job_category']:35} {row['count']:5} students (avg salary: ${row['avg_salary']:,.0f})")
        
        # Readiness distribution
        print("\nIndustry Readiness Distribution:")
        cursor.execute("""
            SELECT 
                CASE 
                    WHEN pred_industry_readiness_score >= 0.8 THEN 'High (0.8+)'
                    WHEN pred_industry_readiness_score >= 0.6 THEN 'Medium (0.6-0.8)'
                    ELSE 'Low (<0.6)'
                END as readiness_level,
                COUNT(*) as count
            FROM what_if_data
            GROUP BY readiness_level
            ORDER BY readiness_level DESC
        """)
        for row in cursor.fetchall():
            print(f"  {row['readiness_level']:20} {row['count']:5} students")
        
        # Average metrics
        print("\nAverage Metrics:")
        cursor.execute("""
            SELECT 
                AVG(gpa_cumulative) as avg_gpa,
                AVG(total_credits_earned) as avg_credits,
                AVG(pred_job_placement_probability) as avg_placement,
                AVG(pred_salary_median) as avg_salary,
                AVG(pred_industry_readiness_score) as avg_readiness
            FROM what_if_data
        """)
        metrics = cursor.fetchone()
        print(f"  GPA: {metrics['avg_gpa']:.2f}")
        print(f"  Credits Earned: {metrics['avg_credits']:.0f}")
        print(f"  Job Placement Probability: {metrics['avg_placement']:.1%}")
        print(f"  Median Salary: ${metrics['avg_salary']:,.0f}")
        print(f"  Industry Readiness: {metrics['avg_readiness']:.1%}")
        
        print(f"\n{'='*100}\n")
        
    finally:
        cursor.close()
        conn.close()


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="View what_if_data predictions")
    parser.add_argument("--limit", type=int, default=10, help="Number of records to show")
    parser.add_argument("--industry", help="Filter by industry")
    parser.add_argument("--job", help="Filter by job category")
    parser.add_argument("--stats", action="store_true", help="Show statistics only")
    parser.add_argument("--llm", action="store_true", help="Show LLM-generated insights")
    
    args = parser.parse_args()
    
    if args.stats:
        show_statistics()
    else:
        view_what_if_data(limit=args.limit, filter_industry=args.industry, filter_job=args.job, show_llm=args.llm)
