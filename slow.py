import mysql.connector
import json
from dotenv import load_dotenv
import os
from datetime import datetime

# Load .env file
load_dotenv()

# Database connection details
DB_CONFIG = {
    "host": os.getenv("DB_HOST", "localhost"),
    "port": int(os.getenv("DB_PORT", 3306)),
    "database": os.getenv("DB_NAME", "test_db"),
    "user": os.getenv("DB_USER", "root"),
    "password": os.getenv("DB_PASSWORD", ""),
}

def fetch_slow_queries():
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        cursor = conn.cursor(dictionary=True)

        # ✅ Corrected SQL Query using `AVG_TIMER_WAIT`
        cursor.execute("""
            SELECT DIGEST_TEXT AS query, 
                   ROUND(AVG_TIMER_WAIT / 1000000000, 2) AS execution_time_ms, 
                   COUNT_STAR AS calls, 
                   NOW() AS timestamp 
            FROM performance_schema.events_statements_summary_by_digest 
            WHERE AVG_TIMER_WAIT / 1000000000 > %s 
            ORDER BY execution_time_ms DESC 
            LIMIT 10
        """, (2000,))  # 2 seconds threshold

        slow_queries = cursor.fetchall()

        # Save results as JSON
        with open("slow_queries.json", "w") as f:
            json.dump(slow_queries, f, indent=4, default=str)

        print("✅ Slow query data saved to slow_queries.json")
        
        cursor.close()
        conn.close()
    except mysql.connector.Error as err:
        print(f"❌ Database error: {err}")

fetch_slow_queries()
