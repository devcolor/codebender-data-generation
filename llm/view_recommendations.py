"""
View LLM recommendations from the database.
"""

import sys
import os
import json

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import mysql.connector
from dboperations.db_setup import DB_CONFIG


def view_recommendations(database_name: str, limit: int = 10):
    """View recent recommendations from a database."""
    config = DB_CONFIG.copy()
    config["database"] = database_name
    
    try:
        conn = mysql.connector.connect(**config)
        cursor = conn.cursor(dictionary=True)
        
        query = """
            SELECT 
                Student_GUID,
                Cohort,
                Cohort_Term,
                recommendation_type,
                readiness_score,
                readiness_level,
                rationale,
                risk_factors,
                suggested_actions,
                model_name,
                prompt_version,
                status,
                generated_at
            FROM llm_recommendations
            ORDER BY generated_at DESC
            LIMIT %s
        """
        
        cursor.execute(query, (limit,))
        results = cursor.fetchall()
        
        if not results:
            print(f"No recommendations found in {database_name}")
            return
        
        print(f"\n{'='*80}")
        print(f"LLM RECOMMENDATIONS - {database_name}")
        print(f"{'='*80}\n")
        
        for i, rec in enumerate(results, 1):
            print(f"[{i}] Student: {rec['Student_GUID']}")
            print(f"    Cohort: {rec['Cohort']} ({rec['Cohort_Term']})")
            print(f"    Readiness: {rec['readiness_level'].upper()} (Score: {rec['readiness_score']})")
            print(f"    Status: {rec['status']}")
            print(f"    Generated: {rec['generated_at']}")
            print(f"\n    Rationale:")
            print(f"    {rec['rationale']}")
            
            if rec['risk_factors']:
                risk_factors = json.loads(rec['risk_factors'])
                print(f"\n    Risk Factors:")
                for rf in risk_factors:
                    print(f"      • {rf}")
            
            if rec['suggested_actions']:
                actions = json.loads(rec['suggested_actions'])
                print(f"\n    Suggested Actions:")
                for action in actions:
                    print(f"      → {action}")
            
            print(f"\n    Model: {rec['model_name']} (prompt: {rec['prompt_version']})")
            print(f"{'-'*80}\n")
        
        cursor.close()
        conn.close()
        
    except Exception as e:
        print(f"Error: {e}")


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="View LLM recommendations")
    parser.add_argument("--database", required=True, help="Database name")
    parser.add_argument("--limit", type=int, default=10, help="Number of records to show")
    
    args = parser.parse_args()
    view_recommendations(args.database, args.limit)
