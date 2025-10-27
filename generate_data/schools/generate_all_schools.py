"""
Master script to generate data for all schools.
Runs the generation scripts for AL, CSUSB, KCTCS, KY, and OH.
"""
import sys
import os

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

# Import each school's generate_all module
from AL import generate_all as al_gen
from CSUSB import generate_all as csusb_gen
from KCTCS import generate_all as kctcs_gen
from KY import generate_all as ky_gen
from OH import generate_all as oh_gen

def main():
    """Run data generation for all schools."""
    print("\n" + "="*80)
    print(" "*20 + "DATA GENERATION FOR ALL SCHOOLS")
    print("="*80)
    
    schools = [
        ("AL", "Bishop State Community College", al_gen),
        ("CSUSB", "California State University San Bernardino", csusb_gen),
        ("KCTCS", "Kentucky Community and Technical College System", kctcs_gen),
        ("KY", "Thomas More University", ky_gen),
        ("OH", "University of Akron", oh_gen)
    ]
    
    for code, name, module in schools:
        print(f"\n{'*'*80}")
        print(f"Starting data generation for {code} - {name}")
        print(f"{'*'*80}")
        
        try:
            module.main()
            print(f"\n[SUCCESS] Completed data generation for {code}")
        except Exception as e:
            print(f"\n[ERROR] Failed to generate data for {code}: {e}")
            import traceback
            traceback.print_exc()
    
    print("\n" + "="*80)
    print(" "*15 + "ALL SCHOOLS DATA GENERATION COMPLETED")
    print("="*80 + "\n")

if __name__ == "__main__":
    main()
