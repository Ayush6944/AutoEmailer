"""
Fix pending status in email_tracking.db sent_emails table
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

def fix_email_tracking_status():
    """Update status from 'pending' to 'sent' in email_tracking.db."""
    try:
        # Connect to database
        conn = sqlite3.connect('data/email_tracking.db')
        cursor = conn.cursor()
        
        # Get count of records to update
        cursor.execute("""
            SELECT COUNT(*) FROM sent_emails 
            WHERE status = 'pending'
            AND sent_date IS NOT NULL
        """)
        count = cursor.fetchone()[0]
        
        if count == 0:
            logger.info("No records found with pending status and sent_date")
            return
        
        # Update records
        cursor.execute("""
            UPDATE sent_emails 
            SET status = 'sent'
            WHERE status = 'pending'
            AND sent_date IS NOT NULL
        """)
        
        # Commit changes
        conn.commit()
        
        logger.info(f"Successfully updated {count} records from pending to sent status")
        
        # Show some examples of updated records
        cursor.execute("""
            SELECT company_id, company_name, hr_email, sent_date 
            FROM sent_emails 
            WHERE status = 'sent'
            ORDER BY sent_date DESC
            LIMIT 5
        """)
        
        logger.info("\nLast 5 records updated:")
        for row in cursor.fetchall():
            logger.info(f"ID: {row[0]}, Company: {row[1]}, Email: {row[2]}, Sent: {row[3]}")
        
    except Exception as e:
        logger.error(f"Error updating database: {str(e)}")
        raise
    finally:
        conn.close()

if __name__ == "__main__":
    fix_email_tracking_status() 