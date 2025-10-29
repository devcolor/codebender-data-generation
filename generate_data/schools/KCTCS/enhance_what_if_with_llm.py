"""
Enhance what_if_data with LLM-generated insights using local Mistral via Ollama.
Populates llm_* columns with natural language career guidance.
"""

import sys
import os
from pathlib import Path
import json
import requests
import hashlib
from decimal import Decimal

# Add parent directory to path
sys.path.append(str(Path(__file__).parent.parent))
from shared.config import get_db_connection

DATABASE = "Kentucky_Community_and_Technical_College_System"
OLLAMA_URL = "http://localhost:11434"
MODEL_NAME = "mistral"


class DecimalEncoder(json.JSONEncoder):
    """Custom JSON encoder to handle Decimal types."""
    def default(self, obj):
        if isinstance(obj, Decimal):
            return float(obj)
        return super(DecimalEncoder, self).default(obj)


def test_ollama():
    """Test if Ollama is running and model is available."""
    try:
        response = requests.get(f"{OLLAMA_URL}/api/tags", timeout=5)
        if response.status_code == 200:
            models = response.json()
            model_names = [m.get('name', '') for m in models.get('models', [])]
            if any(MODEL_NAME in name.lower() for name in model_names):
                print(f"✓ Ollama is running with {MODEL_NAME} model")
                return True
            else:
                print(f"✗ {MODEL_NAME} model not found. Run: ollama pull {MODEL_NAME}")
                return False
        else:
            print(f"✗ Ollama responded with status: {response.status_code}")
            return False
    except requests.exceptions.ConnectionError:
        print(f"✗ Cannot connect to Ollama at {OLLAMA_URL}")
        print("  Make sure Ollama is running: ollama serve")
        return False
    except Exception as e:
        print(f"✗ Error testing Ollama: {e}")
        return False


def build_llm_prompt(student_data):
    """Build prompt for LLM to generate career insights."""
    
    # Parse JSON fields
    technical_skills = json.loads(student_data['technical_skills']) if student_data['technical_skills'] else []
    soft_skills = json.loads(student_data['soft_skills']) if student_data['soft_skills'] else []
    certs_earned = json.loads(student_data['certifications_earned']) if student_data['certifications_earned'] else []
    activities = json.loads(student_data['extracurricular_activities']) if student_data['extracurricular_activities'] else []
    
    prompt = f"""You are an expert career counselor for community college students. Analyze this student's profile and provide career guidance.

STUDENT PROFILE:
- Program: {student_data['primary_program']}
- GPA: {student_data['gpa_cumulative']:.2f}
- Credits Earned: {student_data['total_credits_earned']}
- Internship: {student_data['internship_completed']}
- Work Experience: {student_data['work_experience_years']} years
- Technical Skills: {', '.join(technical_skills)}
- Soft Skills: {', '.join(soft_skills)}
- Certifications: {', '.join(certs_earned) if certs_earned else 'None yet'}
- Activities: {', '.join(activities) if activities else 'None listed'}

PREDICTIONS:
- Top Industry: {student_data['pred_top_industry']}
- Top Job: {student_data['pred_top_job_category']}
- Job Placement Probability: {student_data['pred_job_placement_probability']:.1%}
- Salary Range: ${student_data['pred_salary_range_low']:,} - ${student_data['pred_salary_range_high']:,}
- Industry Readiness: {student_data['pred_industry_readiness_score']:.1%}
- Skill Match: {student_data['pred_skill_match_percentage']:.1%}

TASK:
Provide career guidance in JSON format with these fields:

1. career_summary: 2-3 sentence overview of career prospects (plain language for advisors)
2. strengths: Array of 3-5 key strengths this student has
3. skill_gaps: Array of 2-4 skills they should develop
4. recommended_actions: Array of 3-5 specific, actionable next steps
5. career_pathway: 2-3 sentence description of realistic career progression over 5 years
6. salary_justification: 1-2 sentence explanation of why this salary range is predicted

OUTPUT FORMAT (JSON only, no other text):
{{
  "career_summary": "...",
  "strengths": ["strength 1", "strength 2", ...],
  "skill_gaps": ["gap 1", "gap 2", ...],
  "recommended_actions": ["action 1", "action 2", ...],
  "career_pathway": "...",
  "salary_justification": "..."
}}

IMPORTANT:
- Use plain, professional language suitable for academic advisors
- Be specific and actionable
- Consider the Kentucky job market
- Be realistic but encouraging
- Return ONLY valid JSON, no markdown or extra text
"""
    
    return prompt


def call_ollama(prompt):
    """Call Ollama API to generate career insights."""
    try:
        response = requests.post(
            f"{OLLAMA_URL}/api/generate",
            json={
                "model": MODEL_NAME,
                "prompt": prompt,
                "stream": False,
                "options": {
                    "temperature": 0.4,
                    "num_predict": 1500
                }
            },
            timeout=90
        )
        
        if response.status_code == 200:
            result = response.json()
            generated_text = result.get('response', '').strip()
            
            # Try to extract JSON from response
            try:
                # Try direct JSON parse
                parsed = json.loads(generated_text)
                return parsed
            except json.JSONDecodeError:
                # Try to find JSON in the text
                import re
                json_match = re.search(r'\{.*\}', generated_text, re.DOTALL)
                if json_match:
                    parsed = json.loads(json_match.group())
                    return parsed
                else:
                    print(f"✗ Could not extract JSON from response")
                    return None
        else:
            print(f"✗ Ollama API error: {response.status_code}")
            return None
            
    except requests.exceptions.Timeout:
        print("✗ Ollama request timed out")
        return None
    except Exception as e:
        print(f"✗ Error calling Ollama: {e}")
        return None


def update_llm_columns(cursor, student_guid, llm_output):
    """Update llm_* columns for a student."""
    if not llm_output:
        return False
    
    try:
        sql = """
        UPDATE what_if_data
        SET 
            llm_career_summary = %s,
            llm_strengths = %s,
            llm_skill_gaps = %s,
            llm_recommended_actions = %s,
            llm_career_pathway = %s,
            llm_salary_justification = %s,
            last_updated = CURRENT_TIMESTAMP
        WHERE Student_GUID = %s
        """
        
        values = (
            llm_output.get('career_summary'),
            json.dumps(llm_output.get('strengths', []), cls=DecimalEncoder),
            json.dumps(llm_output.get('skill_gaps', []), cls=DecimalEncoder),
            json.dumps(llm_output.get('recommended_actions', []), cls=DecimalEncoder),
            llm_output.get('career_pathway'),
            llm_output.get('salary_justification'),
            student_guid
        )
        
        cursor.execute(sql, values)
        return True
        
    except Exception as e:
        print(f"  ✗ Error updating database: {e}")
        return False


def enhance_with_llm(limit=None, skip_existing=True):
    """Main function to enhance what_if_data with LLM insights."""
    print(f"\n{'='*80}")
    print(f"ENHANCING WHAT_IF_DATA WITH LLM INSIGHTS")
    print(f"{'='*80}\n")
    
    # Test Ollama
    if not test_ollama():
        print("\n✗ Ollama test failed. Exiting.")
        return
    
    conn = get_db_connection(DATABASE)
    cursor = conn.cursor(dictionary=True)
    
    try:
        # Get students to process
        print("\nFetching students to enhance...")
        
        if skip_existing:
            query = """
                SELECT * FROM what_if_data 
                WHERE llm_career_summary IS NULL
                ORDER BY pred_job_placement_probability DESC
            """
        else:
            query = "SELECT * FROM what_if_data ORDER BY pred_job_placement_probability DESC"
        
        if limit:
            query += f" LIMIT {limit}"
        
        cursor.execute(query)
        students = cursor.fetchall()
        print(f"Found {len(students)} students to process")
        
        if not students:
            print("No students to process")
            return
        
        # Process each student
        success_count = 0
        error_count = 0
        
        for i, student in enumerate(students, 1):
            student_guid = student['Student_GUID']
            print(f"\n[{i}/{len(students)}] Processing {student_guid}...")
            print(f"  Program: {student['primary_program']}")
            print(f"  Predicted Job: {student['pred_top_job_category']}")
            
            try:
                # Build prompt
                prompt = build_llm_prompt(student)
                
                # Call LLM
                llm_output = call_ollama(prompt)
                
                if llm_output:
                    # Validate output structure
                    required_keys = ['career_summary', 'strengths', 'skill_gaps', 
                                   'recommended_actions', 'career_pathway', 'salary_justification']
                    
                    if all(key in llm_output for key in required_keys):
                        # Update database
                        if update_llm_columns(cursor, student_guid, llm_output):
                            conn.commit()
                            success_count += 1
                            print(f"  ✓ Success")
                        else:
                            error_count += 1
                            print(f"  ✗ Failed to update database")
                    else:
                        error_count += 1
                        print(f"  ✗ Invalid LLM output structure")
                else:
                    error_count += 1
                    print(f"  ✗ LLM call failed")
                    
            except Exception as e:
                error_count += 1
                print(f"  ✗ Error: {e}")
        
        # Summary
        print(f"\n{'='*80}")
        print(f"SUMMARY")
        print(f"{'='*80}")
        print(f"Total students: {len(students)}")
        print(f"Successfully enhanced: {success_count}")
        print(f"Errors: {error_count}")
        print(f"{'='*80}\n")
        
    finally:
        cursor.close()
        conn.close()


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(
        description="Enhance what_if_data with LLM-generated career insights"
    )
    parser.add_argument(
        "--limit",
        type=int,
        help="Limit number of students to process"
    )
    parser.add_argument(
        "--all",
        action="store_true",
        help="Process all students, including those already enhanced"
    )
    
    args = parser.parse_args()
    
    enhance_with_llm(limit=args.limit, skip_existing=not args.all)
