import os

# Remaining schools
schools = [
    ('KCTCS', 'Kentucky Community and Technical College System'),
    ('KY', 'Thomas More University'),
    ('OH', 'University of Akron')
]

base_path = r'c:\Users\theca\project_repo\devcolor-data-gen\generate_data\schools'

for code, name in schools:
    school_dir = os.path.join(base_path, code)
    os.makedirs(school_dir, exist_ok=True)
    print(f'Created directory: {code}')
