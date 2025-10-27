"""
Generate all data types for Thomas More University (KY)
"""
import cohort
import course
import financial_aid

def main():
    """Run all data generation scripts for KY."""
    print("\n" + "="*70)
    print("GENERATING ALL DATA FOR THOMAS MORE UNIVERSITY (KY)")
    print("="*70)
    
    cohort.main()
    course.main()
    financial_aid.main()
    
    print("\n" + "="*70)
    print("[OK] ALL DATA GENERATION COMPLETED FOR KY")
    print("="*70 + "\n")

if __name__ == "__main__":
    main()
