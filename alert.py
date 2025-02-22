import json
import smtplib
from email.mime.text import MIMEText
from dotenv import load_dotenv
import os

# Load .env file
load_dotenv()

SMTP_SERVER = os.getenv("SMTP_SERVER", "smtp.gmail.com")
SMTP_PORT = int(os.getenv("SMTP_PORT", 587))
EMAIL_USER = os.getenv("EMAIL_USER", "your_email@gmail.com")
EMAIL_PASS = os.getenv("EMAIL_PASS", "your_email_password")
ALERT_RECIPIENT = os.getenv("ALERT_RECIPIENT", "admin@example.com")

SLOW_QUERY_THRESHOLD = 2000  # Alert threshold in milliseconds

def send_email_alert(slow_queries):
    """Send an email alert for detected slow queries."""
    subject = "⚠️ Slow Query Alert"
    body = "The following **critical slow queries** were detected:\n\n"

    for query in slow_queries:
        body += f"🔹 Query: {query['query']}\n"
        body += f"⏳ Execution Time: {query['execution_time_ms']} ms\n"
        body += f"📅 Timestamp: {query['timestamp']}\n\n"

    msg = MIMEText(body)
    msg["Subject"] = subject
    msg["From"] = EMAIL_USER
    msg["To"] = ALERT_RECIPIENT

    try:
        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
            server.starttls()
            server.login(EMAIL_USER, EMAIL_PASS)
            server.sendmail(EMAIL_USER, ALERT_RECIPIENT, msg.as_string())
        print("✅ Slow query alert sent successfully!")
    except Exception as e:
        print(f"❌ Failed to send alert: {e}")

def check_and_alert():
    """Read the slow query log and send an alert if needed."""
    try:
        with open("slow_queries.json", "r") as f:
            slow_queries = json.load(f)

        # Filter slow queries that exceed the threshold
        alert_queries = [q for q in slow_queries if float(q['execution_time_ms']) > SLOW_QUERY_THRESHOLD]

        if alert_queries:
            send_email_alert(alert_queries)
        else:
            print("✅ No critical slow queries detected.")
    except FileNotFoundError:
        print("❌ No slow query log found. Run the collector first.")

# Run alert agent
check_and_alert()
