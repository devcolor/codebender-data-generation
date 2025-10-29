"""Quick check of what_if_data record count."""
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))
from shared.config import get_db_connection

conn = get_db_connection("Kentucky_Community_and_Technical_College_System")
cursor = conn.cursor()

try:
    cursor.execute("SELECT COUNT(*) FROM what_if_data")
    count = cursor.fetchone()[0]
    print(f"Records in what_if_data: {count:,}")
    
    if count > 0:
        cursor.execute("SELECT COUNT(*) FROM what_if_data WHERE llm_career_summary IS NOT NULL")
        llm_count = cursor.fetchone()[0]
        print(f"Records with LLM insights: {llm_count:,}")
finally:
    cursor.close()
    conn.close()
