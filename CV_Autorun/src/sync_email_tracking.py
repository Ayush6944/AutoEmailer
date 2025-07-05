"""
Sync email_tracking.db with companies that have been marked as sent
"""

import sqlite3
import logging
from datetime import datetime

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def sync_email_tracking():
    """Sync sent_emails table with companies that have been marked as sent."""
    try:
        # Connect to both databases
        with sqlite3.connect('data/companies.db') as companies_conn, \
             sqlite3.connect('data/email_tracking.db') as tracking_conn:
            
            companies_cursor = companies_conn.cursor()
            tracking_cursor = tracking_conn.cursor()
            
            # Get companies that have been marked as sent
            companies_cursor.execute("""
                SELECT id, company_name, hr_email, sent_timestamp, status, error_message
                FROM companies
                WHERE sent_timestamp IS NOT NULL
                AND status = 'sent'
            """)
            sent_companies = companies_cursor.fetchall()
            
            # Count how many companies need to be synced
            count = 0
            for company in sent_companies:
                company_id, company_name, hr_email, sent_timestamp, status, error_message = company
                
                # Check if company already exists in sent_emails
                tracking_cursor.execute("""
                    SELECT id FROM sent_emails 
                    WHERE company_id = ? OR 
                    (LOWER(TRIM(company_name)) = LOWER(TRIM(?)) AND 
                     LOWER(TRIM(hr_email)) = LOWER(TRIM(?)))
                """, (company_id, company_name, hr_email))
                
                if not tracking_cursor.fetchone():
                    # Insert new record
                    tracking_cursor.execute("""
                        INSERT INTO sent_emails 
                        (company_id, company_name, hr_email, sent_date, status, error_message, is_followup)
                        VALUES (?, ?, ?, ?, ?, ?, ?)
                    """, (company_id, company_name, hr_email, sent_timestamp, status, error_message, False))
                    count += 1
            
            # Commit changes
            tracking_conn.commit()
            
            logger.info(f"Successfully synced {count} companies to email_tracking.db")
            
            # Show some examples of synced companies
            tracking_cursor.execute("""
                SELECT company_id, company_name, hr_email, sent_date 
                FROM sent_emails 
                ORDER BY sent_date DESC
                LIMIT 5
            """)
            
            logger.info("\nLast 5 companies in email_tracking.db:")
            for row in tracking_cursor.fetchall():
                logger.info(f"ID: {row[0]}, Company: {row[1]}, Email: {row[2]}, Sent: {row[3]}")
            
    except Exception as e:
        logger.error(f"Error syncing databases: {str(e)}")
        raise

if __name__ == "__main__":
    sync_email_tracking() 