import pandas as pd

# Analyze course seed data to understand student and cohort structure
print("="*80)
print("ANALYZING COURSE SEED DATA - STUDENT AND COHORT STRUCTURE")
print("="*80)

# Load course data
course_df = pd.read_csv('data/seed_data01/course_AR_data_mock.csv')
print(f"Total course enrollment records: {len(course_df):,}")

# Analyze unique students
unique_students = course_df['Student GUID'].nunique()
print(f"Unique students: {unique_students:,}")

# Analyze unique cohorts
unique_cohorts = course_df['Cohort'].nunique()
print(f"Unique cohorts: {unique_cohorts:,}")

# Show cohort breakdown
print(f"\nCohort breakdown:")
cohort_counts = course_df['Cohort'].value_counts()
print(cohort_counts)

# Analyze students per cohort
print(f"\nStudents per cohort:")
students_per_cohort = course_df.groupby('Cohort')['Student GUID'].nunique().sort_values(ascending=False)
print(students_per_cohort)

# Analyze cohort terms
print(f"\nUnique cohort terms: {course_df['Cohort Term'].nunique()}")
print(course_df['Cohort Term'].value_counts())

# Analyze institution IDs
print(f"\nUnique institutions: {course_df['Institution ID'].nunique()}")
print(course_df['Institution ID'].value_counts())

# Show sample data
print(f"\nSample records:")
print(course_df[['Student GUID', 'Cohort', 'Cohort Term', 'Institution ID']].head(10))

print("\n" + "="*80)
print("ANALYZING COHORT SEED DATA")
print("="*80)

# Load cohort data
cohort_df = pd.read_csv('data/seed_data01/cohort_AR_data_mock_A.csv')
print(f"Total cohort records: {len(cohort_df):,}")

# Analyze unique students in cohort data
unique_students_cohort = cohort_df['Student GUID'].nunique()
print(f"Unique students in cohort data: {unique_students_cohort:,}")

# Analyze unique cohorts in cohort data
unique_cohorts_cohort = cohort_df['Cohort'].nunique()
print(f"Unique cohorts in cohort data: {unique_cohorts_cohort:,}")

# Show cohort breakdown from cohort data
print(f"\nCohort breakdown from cohort data:")
cohort_counts_cohort = cohort_df['Cohort'].value_counts()
print(cohort_counts_cohort)

# Compare the two datasets
print(f"\n" + "="*80)
print("COMPARISON BETWEEN COURSE AND COHORT DATA")
print("="*80)
print(f"Students in course data: {unique_students:,}")
print(f"Students in cohort data: {unique_students_cohort:,}")
print(f"Cohorts in course data: {unique_cohorts:,}")
print(f"Cohorts in cohort data: {unique_cohorts_cohort:,}")

# Check for student overlap
course_students = set(course_df['Student GUID'].unique())
cohort_students = set(cohort_df['Student GUID'].unique())
overlap = course_students.intersection(cohort_students)
print(f"Student overlap between datasets: {len(overlap):,}")
print(f"Students only in course data: {len(course_students - cohort_students):,}")
print(f"Students only in cohort data: {len(cohort_students - course_students):,}")
