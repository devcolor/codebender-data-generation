"""
Generate all data types for California State University San Bernardino (CSUSB)
"""
import cohort
import course
import financial_aid

def main():
    """Run all data generation scripts for CSUSB."""
    print("\n" + "="*70)
    print("GENERATING ALL DATA FOR CALIFORNIA STATE UNIVERSITY SAN BERNARDINO (CSUSB)")
    print("="*70)
    
    # Generate cohort data
    cohort.main()
    
    # Generate course data
    course.main()
    
    # Generate financial aid data
    financial_aid.main()
    
    print("\n" + "="*70)
    print("[OK] ALL DATA GENERATION COMPLETED FOR CSUSB")
    print("="*70 + "\n")

if __name__ == "__main__":
    main()
