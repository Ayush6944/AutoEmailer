import sqlite3
import logging
import pandas as pd
from datetime import datetime
import os

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def analyze_databases():
    """Analyze both companies.db and email_tracking.db databases."""
    try:
        # Ensure data directory exists
        os.makedirs('data', exist_ok=True)
        
        # Connect to both databases
        with sqlite3.connect('data/companies.db') as companies_conn, \
             sqlite3.connect('data/email_tracking.db') as tracking_conn:
            
            companies_cursor = companies_conn.cursor()
            tracking_cursor = tracking_conn.cursor()
            
            print("\n=== Companies Database Analysis ===")
            
            # Get companies table structure
            companies_cursor.execute("PRAGMA table_info(companies)")
            companies_columns = companies_cursor.fetchall()
            print("\nCompanies Table Structure:")
            for col in companies_columns:
                print(f"Column: {col[1]}, Type: {col[2]}")
            
            # Get total companies count
            companies_cursor.execute("SELECT COUNT(*) FROM companies")
            total_companies = companies_cursor.fetchone()[0]
            print(f"\nTotal companies in database: {total_companies}")
            
            # Get sent emails count
            companies_cursor.execute("""
                SELECT COUNT(*) FROM companies 
                WHERE sent_timestamp IS NOT NULL
            """)
            sent_emails = companies_cursor.fetchone()[0]
            print(f"Companies marked as sent: {sent_emails}")
            
            # Get status distribution
            companies_cursor.execute("""
                SELECT status, COUNT(*) 
                FROM companies 
                WHERE status IS NOT NULL 
                GROUP BY status
            """)
            status_dist = companies_cursor.fetchall()
            if status_dist:
                print("\nStatus Distribution:")
                for status, count in status_dist:
                    print(f"{status}: {count}")
            
            # Get recent sent emails
            companies_cursor.execute("""
                SELECT id, company_name, hr_email, sent_timestamp, status, error_message
                FROM companies
                WHERE sent_timestamp IS NOT NULL
                ORDER BY sent_timestamp DESC
                LIMIT 5
            """)
            recent_sent = companies_cursor.fetchall()
            if recent_sent:
                print("\nMost Recent Sent Emails:")
                for email in recent_sent:
                    print(f"ID: {email[0]}, Company: {email[1]}, Email: {email[2]}")
                    print(f"Sent at: {email[3]}, Status: {email[4]}")
                    if email[5]:  # error_message
                        print(f"Error: {email[5]}")
                    print("---")
            
            print("\n=== Email Tracking Database Analysis ===")
            
            # Check if sent_emails table exists
            tracking_cursor.execute("""
                SELECT name FROM sqlite_master 
                WHERE type='table' AND name='sent_emails'
            """)
            if tracking_cursor.fetchone():
                # Get sent_emails table structure
                tracking_cursor.execute("PRAGMA table_info(sent_emails)")
                tracking_columns = tracking_cursor.fetchall()
                print("\nSent Emails Table Structure:")
                for col in tracking_columns:
                    print(f"Column: {col[1]}, Type: {col[2]}")
                
                # Get total sent emails count
                tracking_cursor.execute("SELECT COUNT(*) FROM sent_emails")
                total_tracked = tracking_cursor.fetchone()[0]
                print(f"\nTotal emails tracked: {total_tracked}")
                
                # Get status distribution
                tracking_cursor.execute("""
                    SELECT status, COUNT(*) 
                    FROM sent_emails 
                    WHERE status IS NOT NULL 
                    GROUP BY status
                """)
                tracking_status_dist = tracking_cursor.fetchall()
                if tracking_status_dist:
                    print("\nStatus Distribution:")
                    for status, count in tracking_status_dist:
                        print(f"{status}: {count}")
                
                # Get recent sent emails
                tracking_cursor.execute("""
                    SELECT company_id, company_name, hr_email, sent_date, status, error_message
                    FROM sent_emails
                    ORDER BY sent_date DESC
                    LIMIT 5
                """)
                recent_tracked = tracking_cursor.fetchall()
                if recent_tracked:
                    print("\nMost Recent Tracked Emails:")
                    for email in recent_tracked:
                        print(f"Company ID: {email[0]}, Company: {email[1]}, Email: {email[2]}")
                        print(f"Sent at: {email[3]}, Status: {email[4]}")
                        if email[5]:  # error_message
                            print(f"Error: {email[5]}")
                        print("---")
            else:
                print("\nNo sent_emails table found in email_tracking.db")
            
            # Compare counts
            print("\n=== Database Comparison ===")
            print(f"Companies marked as sent in companies.db: {sent_emails}")
            if tracking_cursor.fetchone():
                print(f"Emails tracked in email_tracking.db: {total_tracked}")
                if sent_emails != total_tracked:
                    print("\nWARNING: Database counts don't match!")
                    print("This indicates potential synchronization issues.")
            else:
                print("No tracking data available in email_tracking.db")
            
    except Exception as e:
        logger.error(f"Error analyzing databases: {str(e)}")
        raise

if __name__ == '__main__':
    analyze_databases() 