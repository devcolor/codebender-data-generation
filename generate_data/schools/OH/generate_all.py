"""
Generate all data types for University of Akron (OH)
"""
import cohort
import course
import financial_aid

def main():
    """Run all data generation scripts for OH."""
    print("\n" + "="*70)
    print("GENERATING ALL DATA FOR UNIVERSITY OF AKRON (OH)")
    print("="*70)
    
    cohort.main()
    course.main()
    financial_aid.main()
    
    print("\n" + "="*70)
    print("[OK] ALL DATA GENERATION COMPLETED FOR OH")
    print("="*70 + "\n")

if __name__ == "__main__":
    main()
