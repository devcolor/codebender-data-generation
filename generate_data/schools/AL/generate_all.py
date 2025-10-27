"""
Generate all data types for Bishop State Community College (AL)
"""
import cohort
import course
import financial_aid

def main():
    """Run all data generation scripts for AL."""
    print("\n" + "="*70)
    print("GENERATING ALL DATA FOR BISHOP STATE COMMUNITY COLLEGE (AL)")
    print("="*70)
    
    # Generate cohort data
    cohort.main()
    
    # Generate course data
    course.main()
    
    # Generate financial aid data
    financial_aid.main()
    
    print("\n" + "="*70)
    print("✓ ALL DATA GENERATION COMPLETED FOR AL")
    print("="*70 + "\n")

if __name__ == "__main__":
    main()
