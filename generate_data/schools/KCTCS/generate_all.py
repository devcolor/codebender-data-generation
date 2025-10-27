"""
Generate all data types for Kentucky Community and Technical College System (KCTCS)
"""
import cohort
import course
import financial_aid

def main():
    """Run all data generation scripts for KCTCS."""
    print("\n" + "="*70)
    print("GENERATING ALL DATA FOR KENTUCKY COMMUNITY AND TECHNICAL COLLEGE SYSTEM (KCTCS)")
    print("="*70)
    
    cohort.main()
    course.main()
    financial_aid.main()
    
    print("\n" + "="*70)
    print("[OK] ALL DATA GENERATION COMPLETED FOR KCTCS")
    print("="*70 + "\n")

if __name__ == "__main__":
    main()
