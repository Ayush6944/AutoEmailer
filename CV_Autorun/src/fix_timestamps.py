import sqlite3
import logging
from datetime import datetime

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def fix_timestamps():
    """Fix timestamp mismatches between companies.db and email_tracking.db."""
    try:
        # Connect to both databases
        with sqlite3.connect('data/companies.db') as companies_conn, \
             sqlite3.connect('data/email_tracking.db') as tracking_conn:
            
            companies_cursor = companies_conn.cursor()
            tracking_cursor = tracking_conn.cursor()
            
            # Get all sent companies from companies.db
            companies_cursor.execute("""
                SELECT company_name, hr_email, sent_timestamp, status, error_message
                FROM companies
                WHERE sent_timestamp IS NOT NULL
            """)
            sent_companies = companies_cursor.fetchall()
            
            # Update timestamps in email_tracking.db
            updated_count = 0
            for company in sent_companies:
                company_name, hr_email, sent_timestamp, status, error_message = company
                
                # Update the sent_date in email_tracking.db
                tracking_cursor.execute("""
                    UPDATE sent_emails
                    SET sent_date = ?,
                        status = ?,
                        error_message = ?
                    WHERE LOWER(TRIM(company_name)) = LOWER(TRIM(?))
                    AND LOWER(TRIM(hr_email)) = LOWER(TRIM(?))
                """, (sent_timestamp, status, error_message, company_name, hr_email))
                
                if tracking_cursor.rowcount > 0:
                    updated_count += 1
            
            # Commit changes
            tracking_conn.commit()
            
            # Print summary
            print("\n=== Timestamp Fix Summary ===")
            print(f"Total companies processed: {len(sent_companies)}")
            print(f"Successfully updated: {updated_count}")
            
            # Verify the fix
            tracking_cursor.execute("""
                SELECT COUNT(*) FROM sent_emails WHERE sent_date IS NOT NULL
            """)
            total_tracked = tracking_cursor.fetchone()[0]
            
            print(f"\nFinal counts:")
            print(f"Companies.db sent emails: {len(sent_companies)}")
            print(f"Email tracking.db sent emails: {total_tracked}")
            
            if len(sent_companies) == total_tracked:
                print("\nAll timestamps have been synchronized successfully!")
            else:
                print("\nWarning: Some timestamps may still be mismatched.")
                
    except Exception as e:
        logger.error(f"Error fixing timestamps: {str(e)}")
        raise

if __name__ == '__main__':
    fix_timestamps() 