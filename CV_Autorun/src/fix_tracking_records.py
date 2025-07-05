import sqlite3
import logging
from datetime import datetime

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('fix_records.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

def fix_tracking_records(start_id: int, end_id: int):
    """Fix email tracking records by getting company details from companies.db."""
    companies_conn = None
    tracking_conn = None
    try:
        # Connect to both databases
        companies_conn = sqlite3.connect('data/companies.db')
        tracking_conn = sqlite3.connect('data/email_tracking.db')
        
        # Get company details from companies.db
        companies_cursor = companies_conn.cursor()
        companies_cursor.execute("""
            SELECT id, company_name, hr_email
            FROM companies
            WHERE id BETWEEN ? AND ?
        """, (start_id, end_id))
        
        companies = companies_cursor.fetchall()
        
        # Update records in email_tracking.db
        tracking_cursor = tracking_conn.cursor()
        for company_id, company_name, hr_email in companies:
            # Check if record exists
            tracking_cursor.execute("""
                SELECT id FROM sent_emails WHERE company_id = ?
            """, (company_id,))
            
            if tracking_cursor.fetchone():
                # Update existing record
                tracking_cursor.execute("""
                    UPDATE sent_emails
                    SET company_name = ?,
                        hr_email = ?
                    WHERE company_id = ?
                """, (company_name, hr_email, company_id))
                logger.info(f"Updated record for company {company_id} ({company_name})")
            else:
                # Insert new record
                tracking_cursor.execute("""
                    INSERT INTO sent_emails 
                    (company_id, company_name, hr_email, status, sent_date)
                    VALUES (?, ?, ?, 'sent', CURRENT_TIMESTAMP)
                """, (company_id, company_name, hr_email))
                logger.info(f"Inserted record for company {company_id} ({company_name})")
        
        # Commit changes
        tracking_conn.commit()
        
        # Verify updates
        logger.info("\nVerifying updates in email_tracking.db...")
        tracking_cursor.execute("""
            SELECT company_id, company_name, hr_email, status, sent_date
            FROM sent_emails
            WHERE company_id BETWEEN ? AND ?
        """, (start_id, end_id))
        
        for row in tracking_cursor.fetchall():
            logger.info(f"Tracking DB - ID {row[0]} ({row[1]}): email={row[2]}, status={row[3]}, sent={row[4]}")
        
        logger.info(f"\nSuccessfully fixed records for companies {start_id} to {end_id}")
        
    except Exception as e:
        logger.error(f"Error fixing records: {str(e)}")
        raise
    finally:
        if companies_conn:
            companies_conn.close()
        if tracking_conn:
            tracking_conn.close()

if __name__ == '__main__':
    fix_tracking_records(232319, 232321) 