import mysql.connector
import os
from dotenv import load_dotenv

load_dotenv()

conn = mysql.connector.connect(
    host=os.getenv('DB_HOST'),
    user=os.getenv('DB_USER'),
    password=os.getenv('DB_PASSWORD'),
    port=int(os.getenv('DB_PORT', '3306')),
    database='Bishop_State_Community_College'
)

cursor = conn.cursor()

print("Sample ar_al data:")
cursor.execute('SELECT student_id, years_to_bachelors_cohort, naspa_first_gen, school FROM ar_al LIMIT 5')
rows = cursor.fetchall()
for r in rows:
    print(f"  {r[0]}, {r[1]}, {r[2]}, {r[3]}")

cursor.close()
conn.close()
