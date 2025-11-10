import pandas as pd

# Check cohort AR seed data
print("="*80)
print("COHORT AR SEED DATA")
print("="*80)
cohort_df = pd.read_csv('data/seed_data01/cohort_AR_data_mock_A.csv')
print(f"Columns: {list(cohort_df.columns)}")
print(f"\nTotal rows: {len(cohort_df)}")
print(f"\nUnique Student IDs: {cohort_df['Student_ID'].nunique() if 'Student_ID' in cohort_df.columns else 'N/A'}")
print("\nFirst 3 rows:")
print(cohort_df.head(3))
