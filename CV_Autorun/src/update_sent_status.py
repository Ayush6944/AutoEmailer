import sqlite3
import logging
from datetime import datetime

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('update_status.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

def update_sent_status(start_id: int, end_id: int):
    """Update status for companies in the given ID range."""
    companies_conn = None
    tracking_conn = None
    try:
        # Connect to both databases
        companies_conn = sqlite3.connect('data/companies.db')
        tracking_conn = sqlite3.connect('data/email_tracking.db')
        
        # Get current timestamp
        current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
        # Update companies.db
        companies_cursor = companies_conn.cursor()
        companies_cursor.execute("""
            UPDATE companies
            SET status = 'sent',
                sent_timestamp = ?
            WHERE id BETWEEN ? AND ?
        """, (current_time, start_id, end_id))
        
        # Get company details for email_tracking.db
        companies_cursor.execute("""
            SELECT id, company_name, hr_email
            FROM companies
            WHERE id BETWEEN ? AND ?
        """, (start_id, end_id))
        
        companies = companies_cursor.fetchall()
        
        # Update or insert in email_tracking.db
        tracking_cursor = tracking_conn.cursor()
        for company_id, company_name, hr_email in companies:
            # Check if record exists
            tracking_cursor.execute("""
                SELECT id FROM sent_emails WHERE company_id = ?
            """, (company_id,))
            
            if not tracking_cursor.fetchone():
                # Insert new record
                tracking_cursor.execute("""
                    INSERT INTO sent_emails 
                    (company_id, company_name, hr_email, status, sent_date)
                    VALUES (?, ?, ?, 'sent', ?)
                """, (company_id, company_name, hr_email, current_time))
            else:
                # Update existing record
                tracking_cursor.execute("""
                    UPDATE sent_emails
                    SET status = 'sent',
                        sent_date = ?
                    WHERE company_id = ?
                """, (current_time, company_id))
        
        # Commit changes
        companies_conn.commit()
        tracking_conn.commit()
        
        # Verify updates
        logger.info("Verifying updates in companies.db...")
        companies_cursor.execute("""
            SELECT id, company_name, status, sent_timestamp
            FROM companies
            WHERE id BETWEEN ? AND ?
        """, (start_id, end_id))
        
        for row in companies_cursor.fetchall():
            logger.info(f"Companies DB - ID {row[0]} ({row[1]}): status={row[2]}, sent={row[3]}")
        
        logger.info("\nVerifying updates in email_tracking.db...")
        tracking_cursor.execute("""
            SELECT company_id, company_name, status, sent_date
            FROM sent_emails
            WHERE company_id BETWEEN ? AND ?
        """, (start_id, end_id))
        
        for row in tracking_cursor.fetchall():
            logger.info(f"Tracking DB - ID {row[0]} ({row[1]}): status={row[2]}, sent={row[3]}")
        
        logger.info(f"\nSuccessfully updated status for companies {start_id} to {end_id}")
        
    except Exception as e:
        logger.error(f"Error updating status: {str(e)}")
        raise
    finally:
        if companies_conn:
            companies_conn.close()
        if tracking_conn:
            tracking_conn.close()

if __name__ == '__main__':
    update_sent_status(232311, 232315) 