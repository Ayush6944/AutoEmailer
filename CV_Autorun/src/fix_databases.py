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

def fix_databases():
    """Fix inconsistencies between companies.db and email_tracking.db."""
    try:
        # Connect to both databases
        with sqlite3.connect('data/companies.db') as companies_conn, \
             sqlite3.connect('data/email_tracking.db') as tracking_conn:
            
            companies_cursor = companies_conn.cursor()
            tracking_cursor = tracking_conn.cursor()
            
            # 1. Fix companies.db
            logger.info("Fixing companies.db...")
            
            # Remove duplicate sent_at column if it exists
            companies_cursor.execute("PRAGMA table_info(companies)")
            columns = [col[1] for col in companies_cursor.fetchall()]
            if 'sent_at' in columns and 'sent_timestamp' in columns:
                logger.info("Removing duplicate sent_at column...")
                companies_cursor.execute("""
                    CREATE TABLE companies_new (
                        id INTEGER PRIMARY KEY,
                        company_name TEXT,
                        hr_email TEXT,
                        website TEXT,
                        industry TEXT,
                        location TEXT,
                        created_at TIMESTAMP,
                        email_sent INTEGER,
                        sent_timestamp DATETIME,
                        status TEXT,
                        error_message TEXT
                    )
                """)
                companies_cursor.execute("""
                    INSERT INTO companies_new 
                    SELECT id, company_name, hr_email, website, industry, location,
                           created_at, email_sent, sent_timestamp, status, error_message
                    FROM companies
                """)
                companies_cursor.execute("DROP TABLE companies")
                companies_cursor.execute("ALTER TABLE companies_new RENAME TO companies")
                companies_conn.commit()
            
            # 2. Fix email_tracking.db
            logger.info("Fixing email_tracking.db...")
            
            # Update sent_date from companies.db
            companies_cursor.execute("""
                SELECT id, sent_timestamp, status, error_message
                FROM companies
                WHERE sent_timestamp IS NOT NULL
            """)
            sent_companies = companies_cursor.fetchall()
            
            for company_id, sent_timestamp, status, error_message in sent_companies:
                tracking_cursor.execute("""
                    UPDATE sent_emails
                    SET sent_date = ?, status = ?, error_message = ?
                    WHERE company_id = ?
                """, (sent_timestamp, status, error_message, company_id))
            
            tracking_conn.commit()
            
            # 3. Verify fixes
            logger.info("Verifying fixes...")
            
            # Check companies.db
            companies_cursor.execute("PRAGMA table_info(companies)")
            columns = [col[1] for col in companies_cursor.fetchall()]
            print("\nCompanies.db columns after fix:", columns)
            
            companies_cursor.execute("""
                SELECT COUNT(*) FROM companies 
                WHERE sent_timestamp IS NOT NULL
            """)
            sent_count = companies_cursor.fetchone()[0]
            print(f"Companies marked as sent: {sent_count}")
            
            # Check email_tracking.db
            tracking_cursor.execute("""
                SELECT COUNT(*) FROM sent_emails 
                WHERE sent_date IS NOT NULL
            """)
            tracked_count = tracking_cursor.fetchone()[0]
            print(f"Emails with sent_date: {tracked_count}")
            
            # Show any remaining discrepancies
            if sent_count != tracked_count:
                print("\nWARNING: Still have discrepancies!")
                print(f"Companies.db sent count: {sent_count}")
                print(f"Email tracking.db count: {tracked_count}")
                
                # Find companies in companies.db but not in tracking.db
                companies_cursor.execute("""
                    SELECT id, company_name, hr_email, sent_timestamp
                    FROM companies
                    WHERE sent_timestamp IS NOT NULL
                """)
                sent_companies = pd.DataFrame(companies_cursor.fetchall(), 
                                           columns=['id', 'company_name', 'hr_email', 'sent_timestamp'])
                
                tracking_cursor.execute("""
                    SELECT company_id, company_name, hr_email, sent_date
                    FROM sent_emails
                """)
                tracked_companies = pd.DataFrame(tracking_cursor.fetchall(),
                                              columns=['id', 'company_name', 'hr_email', 'sent_date'])
                
                missing_in_tracking = sent_companies[~sent_companies['id'].isin(tracked_companies['id'])]
                if not missing_in_tracking.empty:
                    print("\nCompanies missing in tracking.db:")
                    print(missing_in_tracking.to_string())
                
                missing_in_companies = tracked_companies[~tracked_companies['id'].isin(sent_companies['id'])]
                if not missing_in_companies.empty:
                    print("\nCompanies missing in companies.db:")
                    print(missing_in_companies.to_string())
            
    except Exception as e:
        logger.error(f"Error fixing databases: {str(e)}")
        raise

if __name__ == '__main__':
    fix_databases() 